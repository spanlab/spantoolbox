import os
import numpy as np
import pandas as pd
import pdb

BEHAVIORAL = 'stock_matrix.csv'
TOP_DIR = '/Users/span/projects/stockmri'
SUBJECT_DIR = os.path.join(TOP_DIR, 'subjects')
TC_FOLDER = 'stock_raw_tcs'
OUTFILE = '/Users/span/projects/stockmri/tc/stocks/stock_master.csv'

def get_subjects():
    with open(os.path.join(TOP_DIR, 'pyproject','all_good_subjects.txt')) as f:
        subjects = [x.strip('\n') for x in f.readlines()]
    return subjects

subjects = get_subjects() # just make a list of your subjects

MASKS = ['nacc8mm','ins','mpfc','acing','caudate','dlpfc'] + ['mirre_r_acc', 'mirre_b_dlpfc', 'mirre_acc', 'mirre_r_insula', 'vlpfc'] # fix this to be whaever yours are...
SIDES = ['b']#,'l','r']

def subj_iterator():
    curr = os.getcwd()
    for subject in subjects:
       os.chdir(os.path.join(SUBJECT_DIR, subject))
       if os.path.exists(os.path.join(SUBJECT_DIR, subject, 'stock_matrix.csv')):
           yield subject
    os.chdir(curr)

TR_DELAY = xrange(16)
MASTER = []

for mask in MASKS:
    for side in SIDES:
        for s in subj_iterator():
            data_matrix = pd.read_csv(BEHAVIORAL)
            data_matrix['Subject'] = np.tile([s], (data_matrix.shape[0],1))
            data_matrix['ROI'] = np.tile(
              [mask + side], (data_matrix.shape[0],1)
            )

            # data_matrix = data_matrix.rename(columns = {data_matrix.columns[2] : 'Timestamp'})
            tcdf = data_matrix#[['ROI','Subject', 'Condition', 'TR', 'Trial_type','Choice']]
            tc_file = s + '_' + side + '_' + mask + '_raw.tc'
            tc_file_path = os.path.join(TC_FOLDER, tc_file)

            tc = np.genfromtxt(tc_file_path)
            tc = (tc-tc.mean())/tc.std() #z-score
            for tr in TR_DELAY:
                tcdf['TR_' + str(1 + tr)] = pd.Series(tc).shift(-tr)
            tcdf = tcdf[tcdf['TR'] == 1]
            if isinstance(MASTER, list):
                MASTER = tcdf
            else:
                MASTER = MASTER.append(tcdf)

MASTER.to_csv(OUTFILE)
