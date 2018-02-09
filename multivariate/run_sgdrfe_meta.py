"""
Script to run svmrfe on a given subject with a number of different parameters.

usage: python run_sgdrfe.py [test subject id]
"""
import os
import sys
from sgdrfe import SGDRFE

######################### USER PARAMS #################################
SUBJECT_BASE_PATH = '/Users/span/spantoolbox/tests/test_data/svm_test_data' #where we find subj folder
SUBJECT_FILE = '/Users/span/spantoolbox/tests/test_data/svm_test_data/test_subjects.txt'
NIFTII = 'pp_cue_tlrc_afni.nii.gz'
BEHAVIORAL = 'drugs_vs_neutral_trial_onsets.1D'
NIFTII_OUT_NAME = 'cue_drug_trial_vs_neutral.nii.gz'
TRS = [1, 2, 3, 4]
LAG = 2 # so really we're looking at trs 2+trs = [3, 4] of every trial (1-indexed)
CLASSIFIERS = ['linearsvc', 'elasticnet']
CUT = .05 # throw out the bottom cut % of features every iteration
STOP_THRESHOLD = .025 # stop at this % of features out of what we start with
TEST = True
######################################################################

class Subject(object):
    def __init__(self, name):
        self.name = name
        self.path = os.path.join(SUBJECT_BASE_PATH, name)
    def file_path(self, filename):
        return os.path.join(self.path, filename)
    def has_file(self, filename):
        return os.path.exists(self.file_path(filename))

class Project(object):
    def __init__(self, subs):
        self.subjects = [Subject(x) for x in subs]


if __name__=="__main__":
    if not TEST:
        try:
            test_subject = sys.argv[1]
        except IndexError:
            test_subject = None


    with open(SUBJECT_FILE, 'r') as f:
        subjects = [x for x in f.read().split('\n') if len(x) == 8]


    if not TEST and test_subject not in subjects:
        print("No test subject found, using all subjects...")
        test_subject = None

    if TEST:
        test_subject = subjects[2]
        subjects = subjects[:3]

    # for clf in ['linearsvc']:
    #     for cval in [.0001,.001,.01,.1,1.,10.,100.,1000.]:

    #         project = Project(subjects)
    #         rfe = SGDRFE(project, NIFTII, BEHAVIORAL, TRS,
    #                      test_subj=test_subject, lag=LAG, clftype=clf, cut=CUT,
    #                      C=cval, stop_threshold=STOP_THRESHOLD)
    #         rfe.run()

    #         test_sub_name = test_subject if test_subject is not None else 'all_subjects'
    #         # niftii_name = '_'.join([test_sub_name, str(cval), clf, NIFTII_OUT_NAME ])
    #         # rfe.save_nii(savename=niftii_name)

    #         if TEST:
    #             break

    for clf in ['elasticnet']:
        for max_iter in [5, 25, 100, 200, 500, 1000, 10000]:
            for l1_ratio in [.001, .05, .15, .25, .5, .75, .85, 95,.999]:
                project = Project(subjects)
                rfe = SGDRFE(project, NIFTII, BEHAVIORAL, TRS,
                             test_subj=test_subject, lag=LAG, clftype=clf, cut=CUT,
                             stop_threshold=STOP_THRESHOLD, l1_ratio=l1_ratio, max_iter=max_iter)
                rfe.run()

                test_sub_name = test_subject if test_subject is not None else 'all_subjects'
                # niftii_name = '_'.join([test_sub_name, str(cval), clf, NIFTII_OUT_NAME ])
                # rfe.save_nii(savename=niftii_name)

                if TEST:
                    break
