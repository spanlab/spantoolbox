'''
Nick Borg - 7/26/16
With large datasets storing the entire training matrix in memory is
prohibitively expensive. We can get around this by using stochastic
gradient descent. This module should include everything needed.
The 'kktools' package is bloated for these purposes.
'''
from __future__ import unicode_literals, print_function, division
import os, time
from random import sample
from math import floor
import cPickle as pickle


import numpy as np
import nibabel as nib
from sklearn import preprocessing
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, r2_score
from sklearn.linear_model import SGDClassifier, ElasticNet
from sklearn.svm import SVC, LinearSVC
import sklearn.utils as skutils
# from nilearn.decoding import SpaceNetClassifier
#import pdb

class OutOfSubjects(Exception):
    pass


class SubjectData(object):
    """Wrapper class for reading trial data for one subject."""

    def __init__(self, nii_path, beh_path, trs, lag=2):
        self.nii_path = nii_path
        self.behavioral = np.loadtxt(beh_path)
        self.trs = trs
        self.lag = lag
        self.trial_index = 0  # current index in the niftii file
        self.nii_proxy = nib.load(nii_path)
        self.nii_shape = np.array(self.nii_proxy.shape)
        self.nii_shape[3] = len(trs)
        self._read_behavior()

    def _read_behavior(self):
        trial_onset_idx = []
        trial_types = []
        for tr, val in enumerate(self.behavioral):
            if val != 0:
                trial_onset_idx.append(tr)
                trial_types.append(val)
        self.onset_idx = trial_onset_idx
        self.trial_types = trial_types

    def get_trial(self):
        if self.trial_index >= len(self.trial_types):
            return None
        ix = self.onset_idx[self.trial_index]
        tr_idx = [ix + self.lag + x - 1 for x in self.trs]
        X = np.squeeze(self.nii_proxy.dataobj[..., tr_idx[0]:tr_idx[-1]+1])
        X = np.reshape(X, np.product(X.shape))
        y = self.trial_types[self.trial_index]
        self.trial_index += 1
        return [X, y]

    def reset(self):
        self.trial_index = 0


class ClassifierData(object):
    """
    Container for multiple SubjectData objects
    Used for the construction of X and Y matrices from our array
    """

    def __init__(self, project, niftii, behavioral, trs, test_subj=None, lag=2):
        self.project = project
        self.niftii = niftii
        self.behavioral = behavioral
        self.training_subjects = [
            x.name for x in project.subjects if x.name != test_subj]
        self.trs = trs
        self.lag = lag
        self.test_subj = test_subj
        self.nii_shape = None
        self._init_subjects()

        if test_subj is not None and test_subj not in [x.name for x in project.subjects]:
            print(test_subj, [x.name for x in project.subjects])
            raise(ValueError, "Test subject not in project.subjects")

        # self.get_xstats()

        self.training_subjects_left = list(self.training_subjects)
        # sort the training subjects randomly
        self.training_subjects_left = sample(self.training_subjects_left,
                                             len(self.training_subjects_left))

        self.total_trials = None

    def _init_subjects(self):
        """Create a dictionary of SubjectData objects for every subject"""
        self.subject_data = {}
        for s in self.project.subjects:
            if s.has_file(self.niftii) and s.has_file(self.behavioral):
                nii_path = s.file_path(self.niftii)
                beh_path = s.file_path(self.behavioral)
                subdata = SubjectData(nii_path, beh_path, self.trs, self.lag)
                self.subject_data[s.name] = subdata
            else:
                print(s.name, "is missing data at", s.file_path(self.niftii), ", excluding...")
                if s.name == self.test_subj:
                    raise(ValueError, "test_subj data not found, exiting...")
                self.training_subjects.remove(s.name)
            try:
                self.nii_shape = subdata.nii_shape
            except UnboundLocalError:
                print("No subjects found!")

    def get_xstats(self):
        """Calculate the column sum/std of all data without loading all into memory
        together. Note that we don't need to normalize within subjects, as
        that should have already been done in the preprocessing stage.
        This will allow us to perform SGD while only having subsets of the data
        in RAM. Also collect num total trials
        TODO this is technically not working, but unused...
        """
        print("Collecting normalization data...")
        X_sum = np.zeros((np.product(self.nii_shape)))
        var_sum = np.zeros_like(X_sum)
        num_trials = 0
        for name in self.training_subjects:
            subdata = self.subject_data[name]
            for trial in subdata.trial_types:
                X_sum += subdata.get_trial()[0]
                num_trials += 1
            subdata.reset()

        mu = X_sum / num_trials
        for name in self.training_subjects:
            subdata = self.subject_data[name]
            for trial in subdata.trial_types:
                var_sum += np.power((subdata.get_trial()[0]-mu), 2)
            subdata.reset()

        std_dev = np.sqrt(var_sum/(num_trials))

        self.total_trials = num_trials
        self.colmean = mu
        self.colstd = std_dev

        return self.colmean, self.colstd

    def scale_matrix(self, X, normalization='row', mu=None, std=None):

        if normalization == 'row' and mu is not None:
            raise(ValueError, "Can't use both row and user defined mu")

        if normalization == 'column':
            if mu is None:
                mu = X.mean(axis=0)
                std = X.std(axis=0)
            try:
                # don't normalize things so that they are huge when std is
                # zero...
                std_no_zeros = np.squeeze(np.array(std))
                std_no_zeros[np.isclose(std_no_zeros, 0)] = 1
                X = (X - mu) / (std_no_zeros)
            except AttributeError:
                raise(AttributeError, "Cannot normalize, exiting...")

        if normalization == 'row':
            row_mean = X.mean(axis=1)
            row_std = X.std(axis=1)
            for row in range(X.shape[0]):
                X[row, :] = (X[row, :]-row_mean[row])/row_std[row]
        return X

    def get_subject_xy(self, sub_name):
        """Return X, Y for a single subject's worth of data"""
        print("Loading data for subject ", sub_name)
        subject_data = self.subject_data[sub_name]
        subject_data.reset()
        y = subject_data.trial_types
        X = np.zeros((len(subject_data.trial_types),
                      np.product(self.nii_shape)))
        for i in range(len(y)):
            X[i, ...] = subject_data.get_trial()[0]

        return X, y

    def count_trials(self):
        total_trials = 0
        for sub in self.training_subjects:
            subbeh = self.subject_data[sub].behavioral
            total_trials += np.count_nonzero(subbeh != 0)
        self.total_trials = total_trials

    def get_training_batch(self, split="subject", shuffle=False):
        """
        Get a batch of training data.
        Params:
        split: subject or all
               if subject, get one subject's worth of data
               if all, get all training subjects
        shuffle: If true, shuffle the rows of final X, y pair
                Currently makes a copy, need to rewrite inplace...
        Returns: X, y"""
        if split == "subject":
            # Build X,Y using one subject's data
            try:
                sub_name = self.training_subjects_left.pop()
            except IndexError:
                raise(OutOfSubjects)
            X, y = self.get_subject_xy(sub_name)

        if split == "all":
            if self.total_trials is None:
                self.count_trials()

            X = np.zeros((self.total_trials, np.product(self.nii_shape)))
            y = np.zeros((self.total_trials))
            ind1 = 0
            for sub_name in self.training_subjects:
                sub_x, sub_y = self.get_subject_xy(sub_name)
                ind2 = ind1 + len(sub_y)
                X[ind1:ind2, ...], y[ind1:ind2] = sub_x, sub_y
                ind1 = ind2

        if shuffle:
            X, y = skutils.shuffle(X, y)

        return X, y


class ReducibleClassifierData(ClassifierData):
    """A subclass of CD that allows us to shrink our X matrix, then back project
       the remaining columns to the the original niftii shape.

       The first n_coef columns are ones we pass to the classifier, and the
       columns in the tail after it are not used. On downsizing, we move
       columns we don't keep to the back.
    """

    def __init__(self, project, niftii, behavioral, trs, test_subj=None, lag=2,
                 cut=.05):
        super(ReducibleClassifierData, self).__init__(project, niftii,
                                                      behavioral, trs,
                                                      test_subj, lag=2)
        self.n_features = int(np.product(self.nii_shape))
        self.orig_n_features = int(self.n_features)
        self.orig_feature_index = np.arange(self.n_features)
        self.tail_start = self.n_features  # the index of the first column we don't keep
        self.cut = cut

    def build_xy(self, method="all", mask=None):
        """helper call to ClassifierData get batch method"""
        if method == "all":
            self.X, self.y = self.get_training_batch(split="all")

            mu = self.X.mean(axis=0)
            std = self.X.std(axis = 0)
            self.X = self.scale_matrix(self.X, normalization='column', mu=mu, std=std)
            # track columns
            self.Xview = self.X.view()
            print("test subject: ", self.test_subj)
            if self.test_subj is not None:
                self.X_test, self.y_test = self.get_subject_xy(self.test_subj)
                self.X_test = self.scale_matrix(self.X_test, normalization='column', mu=mu, std=std)
                self.X_testview = self.X_test.view()


            if mask is not None:
                self.mask_data(mask)


    def mask_data(self, mask_name='tt29.nii'):
        if self.X.ndim==1:
            self.X = np.expand_dims(self.X, 0)
            self.Xview = self.X.view()[:, :self.n_features]
            print("Padding x, new shape", self.Xview.shape)
            # if self.test_subj is not None:
            #     self.Xtest = np.expand_dims(self.Xtest, 0)
            #     self.Xtestview = self.Xtest.view()[:, :self.n_features]

        print("Masking data...")
        mask = nib.load(mask_name).get_data()
        which = (mask>0).astype(float)

        tiled_mask = np.zeros(self.nii_shape)
        for i in range(self.nii_shape[3]):
            tiled_mask[:,:,:,i] = mask>0


        #tiled_mask = np.tile(which, (self.nii_shape[3],1,1,1)).reshape(self.nii_shape)
        #pdb.set_trace()
        print("Tiled mask shape", tiled_mask.shape)
        coefs = np.reshape(tiled_mask.astype(float), np.product(self.nii_shape))
        print("Coefs, nonzero coefs, shape", coefs, np.count_nonzero(coefs), coefs.shape)

        n_keep = np.sum(coefs)

        pct_cut = (self.n_features-n_keep) / coefs.shape[0]
        print(pct_cut)

        self.downsize(coefs, cut=pct_cut, verbose=True)
        self.orig_n_features = n_keep
        #self.coefs_to_niftii(self.Xview[0,:], nii_name='onetrialmasked.nii.gz')



    def downsize(self, coefs, cut=None, verbose=True):
        """
        Given a set of coefs, sort the coefs and get rid of the bottom cut
        percent of variables with lowest cut coefs. Return the new coefs.
        """

        #make sure we've got enough dimensions in X:
        #pdb.set_trace()


        downsized_coefs = np.squeeze(np.array(coefs))

        if cut is None:
            cut = self.cut

        n_trash = int(floor(cut * self.n_features))

        if verbose:
            print("Downsampling...")
            print("Current shape:", self.Xview.shape)
            print("Removing {} columns... ".format(n_trash))


        self.tail_start -= n_trash

        if self.tail_start <= 0:
            raise ValueError("Trying to downsize more variables than present")

        # get sorted order of coefs
        csort = np.squeeze(np.argsort(np.argsort(np.absolute(coefs))))
        keep_feature = np.squeeze(csort >= n_trash)

        tail_start = self.tail_start

        # columns in the tail we want to keep
        keep_idx = np.squeeze(
            np.where(keep_feature[tail_start:tail_start+n_trash]))
        keep_idx += tail_start

        # columns we want to move to the tail
        trash_idx = np.squeeze(np.where(keep_feature[0:tail_start] == False))
        if len(trash_idx) != len(keep_idx):
            raise ValueError("trash_idx and keep_idx not the same length")

        # swap the columns
        for trash, keep in zip(trash_idx, keep_idx):
            #print(keep, trash)
            keep_col = self.X[:, keep].copy()
            self.X[:, keep] = self.X[:, trash]
            self.X[:, trash] = keep_col
            self.orig_feature_index[trash], self.orig_feature_index[keep] = self.orig_feature_index[keep], self.orig_feature_index[trash]
            downsized_coefs[trash], downsized_coefs[keep] = downsized_coefs[keep], downsized_coefs[trash]
            if self.test_subj is not None:
                self.X_test[:, (trash, keep)] = self.X_test[:, (keep, trash)]

        self.n_features -= n_trash
        self.Xview = self.X.view()[:, :self.n_features]
        if self.test_subj is not None:
            self.X_testview = self.X_test.view()[:, :self.n_features]

        # pdb.set_trace()
        print("New Xview shape:", self.Xview.shape)

        return downsized_coefs[:-n_trash]

    def restore_coefs(self, coefs, dtype=np.float64):
        new_coefs = np.zeros(self.orig_n_features, dtype=dtype)
        new_coefs[self.orig_feature_index[:self.n_features]] = coefs.astype(dtype)
        #new_coefs[np.isclose(new_coefs, 0)] = 0.00000000000
        #pdb.set_trace()
        return new_coefs

    def coefs_to_niftii(self, coefs, nii_name='coefs.nii.gz'):
        """

        """

        print(coefs)
        if self.n_features != len(coefs):
            print("Num features {} does not match coef size {}. Did you downsize?".format(
                self.n_features, len(coefs)))
            raise(ValueError)

        restored_coefs = self.restore_coefs(coefs)
        print("restoring... num non-zero",np.count_nonzero(restored_coefs) )

        try:
            restored_coefs = restored_coefs.reshape(np.array(self.nii_shape))
            print("Restored shape:", restored_coefs.shape)
        except IndexError:
            raise(IndexError, "Coefs don't match niftii shape")



        sample_img = nib.load('tt29.nii')
        affine = sample_img.affine.copy()
        header = sample_img.header.copy()

        header.set_data_dtype(np.float64)
        assert(header.get_data_dtype()==np.float64)

        print("Saving coefs as datatype", header.get_data_dtype())
        i = nib.Nifti1Image(restored_coefs.astype(np.float64), affine, header)
        nib.save(i, nii_name)

        return restored_coefs



class SGDRFE(object):
    """The classifier object"""

    def __init__(self, project, niftii, behav, trs, lag=2, test_subj=None, record=None, clftype="sgd", cut=.05, C=1.0, stop_threshold=.025, mask='tt29.nii', descriptor=''):
        self.project = project
        self.niftii = niftii
        self.behav = behav
        self.trs = trs
        self.C = C
        self.stop_threshold = stop_threshold
        self.mask=mask

        if record is None:
            record = '_'.join([test_subj,
                               'lag', str(lag),
                               'trs', ''.join([str(x) for x in self.trs]),
                               'cut', str(cut)])
            record += descriptor + '.csv'
            print("record :", record)
        self.record = record
        self.test_subj = test_subj
        self.clftype = clftype
        self.rcd = ReducibleClassifierData(
            project, niftii, behav, trs, test_subj, cut)
        self.init_coefs = np.squeeze(np.ones(self.rcd.n_features))

        print("Building x, y matrices...")
        self.rcd.build_xy(mask=self.mask)
        # picklefile = 'pickled_rcd.p'
        # if os.path.exists(picklefile):
        #     with open(picklefile, 'r') as f:
        #         print("Loading pickle...")
        #         self.rcd = pickle.load(f)
        #         print("... done.")
        # else:
        #     self.rcd.build_xy(mask=self.mask)
        #     with open(picklefile, 'w') as f:
        #         pickle.dump(self.rcd, f)



    def test_accuracy(self):
        train_predictions = np.squeeze(self.clf.predict(self.rcd.Xview))
        print("Train Accuracy:", np.sum(
            train_predictions == self.rcd.y)/float(len(self.rcd.y)))
        if self.test_subj is not None:
            predictions = np.squeeze(self.clf.predict(self.rcd.X_testview))
        accuracy = np.sum(predictions == self.rcd.y_test)/float(len(self.rcd.y_test))

        metrics = {}

        ytrue = self.rcd.y_test

        metrics['f1'] = f1_score(ytrue, predictions)
        metrics['precision'] = precision_score(ytrue, predictions)
        metrics['recall'] = recall_score(ytrue, predictions)
        metrics['roc_auc'] = roc_auc_score(ytrue, predictions)
        metrics['r2'] = r2_score(ytrue, predictions)

        return accuracy, metrics

    def train_batch(self):
        # fit the model
        print("Fitting the model")
        if self.clftype == "sgd":
            self.clf = SGDClassifier(loss="log", n_iter=50)
        elif self.clftype == "svc":
            self.clf = SVC()
        elif self.clftype == "linearsvc":
            self.clf = LinearSVC(penalty='l2', loss='squared_hinge', dual=True, tol=0.0001, C=self.C)
        elif self.clftype == "elasticsgd":
            self.clf = SGDClassifier(penalty="elasticnet")
        elif self.clftype == "elasticnet":
            self.clf = SGDClassifier(loss="log", penalty="elasticnet")
        elif self.clftype == "graphnet":
            self.clf = SpaceNetClassifier(memory="nilearn_cache",
                                          penalty='graph-net')
        else:
            print(self.clftype)
            raise(ValueError, "clftype unknown...")

        # print("Training with self.Xview.shape = ", self.Xview.shape)
        # print("Underlying X shape = ", self.X.shape)
        if self.clftype == 'sgd':
            self.clf.fit(self.rcd.Xview, self.rcd.y, coef_init=self.init_coefs)
        else:
            self.clf.fit(self.rcd.Xview, self.rcd.y)
        accuracy, metrics = self.test_accuracy()
        print("Test Accuracy:", accuracy)

        classifier_string = str(self.clftype)
        if self.clftype == 'linearsvc':
            classifier_string += '_C' + str(self.C)
        # save the current result

        # result format should be:
        # test_subject, clftype, n_features, %features, accuracy, f1, precision, recall, roc_auc, r2
        with open(self.record, 'a') as f:
            f.write(','.join([self.test_subj,
                              str(classifier_string),
                              str(self.rcd.n_features),
                              str(self.rcd.n_features / float(self.rcd.orig_n_features)),
                              str(accuracy),
                              str(metrics['f1']),
                              str(metrics['precision']),
                              str(metrics['recall']),
                              str(metrics['roc_auc']),
                              str(metrics['r2'])]) + '\n')

        # eliminate the smallest coefs
        coef = np.squeeze(self.clf.coef_ + 0)
        if self.clftype == "sgd":
            self.init_coefs = coef
        self.current_coefs = coef
        return coef


    def run(self):
        start = time.time()
        print("Beginning RFE...")
        stop_num =  floor(self.stop_threshold * self.rcd.orig_n_features)
        while self.rcd.n_features > stop_num:
            self.train_batch()
            self.current_coefs = self.rcd.downsize(self.current_coefs)
            # pdb.set_trace()
        print("Finished rfe in {}(s)".format(time.time() - start))


    def save_nii(self, savename="my_coefs.nii"):
        """Used for saving coesf to niftii"""
        print("Saving coefs to niftii.")
        try:
            self.rcd.coefs_to_niftii(self.current_coefs, savename)
        except AttributeError:
            raise(AttributeError, "Cannot save after 0 training instances.")
