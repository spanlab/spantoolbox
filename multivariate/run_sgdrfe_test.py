"""
Script to run svmrfe on a given subject with a number of different parameters.

usage: python run_sgdrfe.py [test subject id]
"""
import os
import sys
from sgdrfe import SGDRFE
import pdb
######################### USER PARAMS #################################
SUBJECT_BASE_PATH = '/Users/span/spantoolbox/tests/test_data/svm_test_data' #where we find subj folder
SUBJECT_FILE = '/Users/span/spantoolbox/tests/test_data/svm_test_data/test_subjects.txt'
NIFTII = 'pp_cue_tlrc_afni.nii.gz'
BEHAVIORAL = 'drugs_vs_neutral_trial_onsets.1D'
NIFTII_OUT_NAME = 'cue_drug_trial_vs_neutral_elastic_masked.nii.gz'
TRS = [1, 2]
LAG = 2 # so really we're looking at trs 2+trs = [3, 4] of every trial (1-indexed)
CLASSIFIER = 'elasticnet' #linear svm
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
        test_subject = sys.argv[1]

    with open(SUBJECT_FILE, 'r') as f:
        subjects = [x for x in f.read().split('\n') if len(x) == 8]


    if not TEST and test_subject not in subjects:
        print("No test subject found, using all subjects...")
        test_subject = None

    if TEST:
        #just use the first two subjects
        test_subject = subjects[2]
        subjects = subjects[:3]        

    for cval in [.0001,.001,.01,.1,1.,10.,100.,1000.]:
        project = Project(subjects)
        rfe = SGDRFE(project, NIFTII, BEHAVIORAL, TRS,
                     test_subj=test_subject, lag=LAG, clftype=CLASSIFIER, cut=CUT,
                     C=cval, stop_threshold=STOP_THRESHOLD, max_iter=5, l1_ratio=.09)

        rfe.run()

        test_sub_name = test_subject if test_subject is None else 'all_subjects'
        
        if TEST:
            test_sub_name = '3subjecttest'
        
        niftii_name = '_'.join([test_sub_name, str(cval), NIFTII_OUT_NAME ])
        rfe.save_nii(savename=niftii_name)

        if TEST:
            break
