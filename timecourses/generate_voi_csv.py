"""Script for taking matric.csv files and combining them with VOI data into 
   large csv files for all subjects. """
import os
import numpy as np
import pandas as pd
import pdb

BEHAVIORAL = 'stock_matrix.csv'
TC_FOLDER = 'stock_raw_tcs'
WIDE_OUTFILE = 'stock_voi_wide_1.csv'
TOP_DIR = '/Users/span/projects/stock/voi/raw_timecourses/stock_1'

with open(os.path.join('/Users/span/projects/stock/voi/voi_csv', 'stock_1_subjects.txt')) as f:
    SUBJECTS = [x.strip('\n') for x in f.readlines()]
#'mirre_r_acc', 'mirre_b_dlpfc', 'mirre_acc', 'mirre_r_insula', 'mirre_vlpfc', 
MASKS = ['demartino_dmpfc8mm', 'nacc8mm', 'mpfc', 'acing', 
         'dlpfc', 'desai_ins', 'nacc_desai_mpm']

SIDES = ['b', 'l', 'r']
TR_DELAY = xrange(16)

def get_tc_file(subject, mask, side):
    tc_file = subject + '_' + side + '_' + mask + '_raw.tc'
    tc_file_path = os.path.join(TOP_DIR, subject, TC_FOLDER, tc_file)
    return np.genfromtxt(tc_file_path)

AGGREGATE = []
for subject in SUBJECTS:
    bpath = os.path.join(TOP_DIR, subject, BEHAVIORAL)
    data_matrix = pd.read_csv(bpath)
    data_matrix['Subject'] = np.tile([subject], (data_matrix.shape[0], 1))
    #data_matrix['Censor'] =  pd.Series(np.genfromtxt('stock_censor.1D'))
    data_matrix['Previous_Choice'] = pd.Series(data_matrix['Choice']).shift(1)

    for mask in MASKS:
        for side in SIDES:            
            tc = get_tc_file(subject, mask, side)
            for tr in TR_DELAY:
                data_matrix[mask + side + '_TR_' + str(1 + tr)] = pd.Series(tc).shift(-tr)
                
    data_matrix = data_matrix[data_matrix['TR'] == 1]
    if isinstance(AGGREGATE, list):
        AGGREGATE = data_matrix
    else:
        AGGREGATE = AGGREGATE.append(data_matrix)
AGGREGATE.to_csv(os.path.join('/Users/span/projects/stock/voi/voi_csv/', WIDE_OUTFILE))
