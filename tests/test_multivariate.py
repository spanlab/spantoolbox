from __future__ import unicode_literals, print_function, division
import os
import unittest
import pdb

import numpy as np
import numpy.testing as npt
from nose import SkipTest
import nose.tools as nt
from sklearn.preprocessing import scale, normalize

#from ..utilities import Project
from ..multivariate.sgdrfe import *
# TODO: Uuse utilities.project


class Subject(object):

    def __init__(self, name):
        self.name = name
        self.path = os.path.join('tests/test_data/svm_test_data', name)

    def file_path(self, filename):
        return os.path.join(self.path, filename)

    def has_file(self, filename):
        return os.path.exists(self.file_path(filename))


class Project(object):

    def __init__(self, subs):
        self.subjects = [Subject(x) for x in subs]


class BaseMVTest(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        cls.test_data_path = 'tests/test_data/svm_test_data'
        cls.subjects = ['ag151024', 'al170316', 'as160317']
        cls.nii_name = 'pp_cue_tlrc_afni.nii.gz'
        cls.beh_name = 'drugs_vs_neutral_trial_onsets.1D'
        cls.trs = [1, 2]

    @classmethod
    def teardown_class(cls):
        pass


class TestSubjectData(BaseMVTest):

    @classmethod
    def setup_class(cls):
        super(TestSubjectData, cls).setup_class()
        cls.path = os.path.join(cls.test_data_path, cls.subjects[0])
        nii = os.path.join(cls.path, cls.nii_name)
        beh = os.path.join(cls.path, cls.beh_name)
        cls.sd = SubjectData(nii, beh, trs=cls.trs)

    def test_read_behavioral(self):
        npt.assert_equal(np.squeeze(
            np.where(self.sd.behavioral != 0)), np.array(self.sd.onset_idx))
        nt.assert_equal(len(self.sd.trial_types), len(self.sd.onset_idx))

    def test_get_trial(self):
        num_trials = len(self.sd.trial_types)

        # check we always return a full trial for the num trials we have
        for _ in range(num_trials):
            trial = self.sd.get_trial()
            assert(trial[0].shape == np.product(self.sd.nii_shape))
            nt.assert_equal(trial[1], -1.0)

        # when out of trials, return None
        nt.assert_equal(self.sd.get_trial(), None)

    def test_reset(self):
        self.sd.reset()
        self.sd.get_trial()

        nt.assert_equal(self.sd.trial_index, 1)
        self.sd.reset()

        nt.assert_equal(self.sd.trial_index, 0)


class TestClassifierData(BaseMVTest):

    @classmethod
    def setup_class(cls):
        super(TestClassifierData, cls).setup_class()
        cls.project = Project(cls.subjects)
        cls.cd = ClassifierData(cls.project, cls.nii_name, cls.beh_name, cls.trs,
                                test_subj=cls.subjects[1], lag=2)

    def test_init(self):
        nt.assert_equal(len(self.cd.subject_data), 3)
        # print(self.cd.mu)
        # print(self.cd.std)
        # vars()

    def test_scale_matrix(self):
        x = np.random.random(size=(1000, 1000))
        col_normed = scale(x, axis=0)
        row_normed = scale(x, axis=1)

        npt.assert_almost_equal(
            col_normed, self.cd.scale_matrix(x, normalization='column'))
        npt.assert_almost_equal(
            row_normed, self.cd.scale_matrix(x, normalization='row'))

    def test_count_trials(self):
        self.cd.count_trials()
        nt.assert_equal(self.cd.total_trials, 36)

    def test_get_training_batch(self):
        pass
        # X,y = self.cd.get_training_batch(split='subject')
        # print(X,y)

    def test_get_xstates(self):
        cd = ClassifierData(self.project, self.nii_name, self.beh_name, self.trs,
                            test_subj=self.subjects[1], lag=2)
        colmean, colstd = cd.get_xstats()

        X, y = self.cd.get_training_batch(split='all')
        npt.assert_almost_equal(colmean, X.mean(axis=0))
        npt.assert_almost_equal(colstd, X.std(axis=0))
        Xnormed = cd.scale_matrix(X, normalization='column')
        Xnormed2 = cd.scale_matrix(
            X, normalization='column', mu=colmean, std=colstd)

        npt.assert_almost_equal(Xnormed, Xnormed2)


class TestReducibleCD(BaseMVTest):

    @classmethod
    def setup_class(cls):
        super(TestReducibleCD, cls).setup_class()
        cls.project = Project(cls.subjects)
        cls.cd = ReducibleClassifierData(cls.project, cls.nii_name, cls.beh_name, cls.trs,
                                         test_subj=cls.subjects[1])

    def test_build_xy(self):
        # this would just be a smoketest
        pass

    def test_save_nii(self):
        pass

    def test_downsize(self):

        cd = ReducibleClassifierData(
            self.project, self.nii_name, self.beh_name, self.trs)

        X = np.random.random((10, 100))
        good_columns = [1, 13, 15, 68, 29, 27, 95, 92, 54, 88]
        expected_new_columns = [13,  1, 15, 27, 29, 54, 68, 88, 92, 95]

        expectedX = np.squeeze(X[:, expected_new_columns])
        coefs = np.zeros((100))
        coefs[good_columns] = [12345*x for x in good_columns]

        expected_new_coefs = [12345*x for x in expected_new_columns]

        cd.X = X.copy()
        cd.Xview = cd.X.view()
        cd.n_features = 100
        cd.orig_n_features = 100
        cd.orig_feature_index = np.arange(100)
        cd.tail_start = 100

        new_coefs = cd.downsize(coefs, cut=.9)
        npt.assert_almost_equal(new_coefs, expected_new_coefs)
        npt.assert_almost_equal(expectedX.shape, cd.Xview.shape)
        npt.assert_almost_equal(expectedX, cd.Xview)

        pass

    def test_restore_coefs(self):

        indices = np.random.permutation(np.arange(100))

        cd = ReducibleClassifierData(
            self.project, self.nii_name, self.beh_name, self.trs)
        cd.n_features = 10
        cd.orig_n_features = 100
        cd.orig_feature_index = indices.copy()
        cd.tail_start = 100

        coefs = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        expected_new_coefs = np.zeros(100)
        expected_new_coefs[indices[:10]] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        npt.assert_almost_equal(cd.restore_coefs(coefs), expected_new_coefs)

    def test_coefs_to_niftii_one_volume(self):
        cd = ReducibleClassifierData(
            self.project, self.nii_name, self.beh_name, self.trs)

        # get a single trials worth of real data to save to nii
        sd = cd.subject_data['ag151024']
        sd.reset()

        coefs = sd.nii_proxy.get_data()[:, :, :, 0]
        cd.nii_shape = coefs.shape
        coefs = coefs.reshape(np.product(coefs.shape))
        cd.n_features = coefs.shape[0]
        cd.orig_n_features = coefs.shape[0]

        print("Coef shape:", coefs.shape)

        # save to nii
        test_nii = 'testcoefs.nii.gz'
        restored = cd.coefs_to_niftii(coefs, nii_name=test_nii)
        npt.assert_almost_equal(sd.nii_proxy.get_data()[:, :, :, 0], restored)

        #load and compare
        new_nifti_data = nib.load(test_nii).get_data()

        nt.assert_equal(np.count_nonzero(new_nifti_data),
                        np.count_nonzero(coefs))
        npt.assert_almost_equal(
            new_nifti_data, sd.nii_proxy.get_data()[:, :, :, 0])

        os.remove(test_nii)

    def test_coefs_to_niftii(self):

        cd = ReducibleClassifierData(
            self.project, self.nii_name, self.beh_name, self.trs)

        # get a single trials worth of real data to save to nii
        sd = cd.subject_data['ag151024']
        sd.reset()

        one_trial = sd.get_trial()[0]
        sd.reset()
        shape = one_trial.shape

        # pick only 100 values to save, the rest should be zero. (we might save
        # some zeros)
        coefs = np.zeros_like(one_trial)
        which = np.random.random_integers(0, high=len(one_trial), size=100)
        small_coefs = one_trial[which]
        coefs[which] = small_coefs
        cd.n_features = 100
        cd.orig_feature_index[:100] = which

        # save to nii
        test_nii = 'testcoefs.nii.gz'

        # the coefs we're saving should be the same...
        restored = cd.coefs_to_niftii(small_coefs, nii_name=test_nii)
        lr = restored.reshape(np.product(restored.shape))
        nt.assert_equal(np.count_nonzero(lr), np.count_nonzero(small_coefs))

        # load the niftii
        new_nifti_data = nib.load(test_nii).get_data()

        unwound_new_nifti_data = new_nifti_data.reshape(
            np.product(one_trial.shape))
        unw = unwound_new_nifti_data

        # we should have saved a float
        nt.assert_equal(nib.load(test_nii).get_data_dtype(), float)

        # most values should be zero - otherwise likely problems with dtype
        most_common = max(
            map(lambda val: (list(unw).count(val), val), set(unw)))[1]
        npt.assert_almost_equal(most_common, 0)

        nt.assert_equal(np.count_nonzero(new_nifti_data),
                        np.count_nonzero(small_coefs))
        npt.assert_almost_equal(unwound_new_nifti_data, coefs)
        npt.assert_almost_equal(new_nifti_data, coefs.reshape(sd.nii_shape))

        os.remove(test_nii)

    def test_mask_data(self):
        cd = ReducibleClassifierData(
            self.project, self.nii_name, self.beh_name, self.trs)

        mask_name = 'tt29.nii'
        mask = nib.load(mask_name).get_data()
        if mask.ndim == 3:
            mask = np.expand_dims(mask, 3)

        # start with all ones, two trs worth
        nii_shape = np.array(mask.shape)
        nii_shape[3] = 2

        all_ones = np.ones(2*np.product(mask.shape))
        # set up the cd TODO set as method
        mask_n = np.product(mask.shape)

        cd.X = all_ones
        cd.Xview = cd.X.view()
        cd.test_subj = None
        cd.nii_shape = nii_shape
        cd.n_features = mask_n * 2
        cd.orig_n_features = mask_n * 2
        cd.orig_features_index = np.arange(mask_n * 2)
        cd.tail_start = mask_n * 2
        which = mask > 0

        print("Xshape", cd.X.shape)
        print("Mask shape", mask.shape, np.product(mask.shape), mask_n)
        print("nonzero shape, #nonzero", which.shape, np.sum(which))
        cd.mask_data(mask_name)

        # save to nii
        test_nii = 'testcoefs.nii.gz'
        cd.coefs_to_niftii(cd.Xview[0, :], nii_name=test_nii)
        # visual inspection should look like tt29 without blur

    def test_downsample_data(self):
        from collections import Counter
        from sklearn.datasets import make_classification
        X, y = make_classification(n_samples=5000, n_features=2, n_informative=2,
                                   n_redundant=0, n_repeated=0, n_classes=3,
                                   n_clusters_per_class=1,
                                   weights=[0.01, 0.05, 0.94],
                                   class_sep=0.8, random_state=0)
        cd = ReducibleClassifierData(
            self.project, self.nii_name, self.beh_name, self.trs)
        cd._set_xy(X, y)
        cd.downsample()
        print(cd.Xview.shape, Counter(cd.y))


class TestSGDRFE(BaseMVTest):

    @classmethod
    def setup_class(cls):
        super(TestSGDRFE, cls).setup_class()
        cls.project = Project(cls.subjects)
        cls.cd = SGDRFE(cls.project, cls.nii_name, cls.beh_name, cls.trs,
                        test_subj=cls.subjects[1], lag=2, clftype="linearsvc", cut=.05)

    def test_train_sgd(self):
        nt.assert_equal(False, self.subjects[
                        1] in self.cd.rcd.training_subjects)
        self.cd.run()
        self.cd.save_nii()
