import os
import numpy as np
import pdb

TOP_DIR = '/Users/span/projects/stockmri'
SUBJECT_DIR = os.path.join(TOP_DIR, 'subjects')
TC_FOLDER = 'stock_raw_tcs'

def get_subjects():
    """Return all subjects"""
    with open(
        os.path.join(
            TOP_DIR,
            'pyproject',
            'all_good_subjects.txt'
        )
    ) as good_subjects:
        subjects = [x.strip('\n') for x in good_subjects.readlines()]
    return subjects

SUBJECTS = get_subjects()

MASKS = ['desai_ins', 'nacc_desai_mpm', 'nacc8mm', 'mpfc',
         'acing', 'caudate', 'dlpfc', 'demartino_dmpfc8mm']
SIDES = ['b']


def subj_iterator():
    '''yield subject'''
    curr = os.getcwd()
    for subject in SUBJECTS:
        os.chdir(os.path.join(SUBJECT_DIR, subject))
        if os.path.exists(os.path.join(SUBJECT_DIR, subject, 'stock_matrix.csv')):
            yield subject
    os.chdir(curr)


print ' '.join(["Subject"," TRs-ROI","TRs-Motion", "TRs-Total"])
for s in subj_iterator():
    result = []
    for mask in MASKS:
        for side in SIDES:
            tc_file = s + '_' + side + '_' + mask + '_raw.tc'
            tc_file_path = os.path.join(TC_FOLDER, tc_file)
            tc = np.genfromtxt(tc_file_path)
            tc = (tc-tc.mean())/tc.std()
            # pdb.set_trace()
            if result != []:
                result = np.multiply(result, [tc < 4])
            else:
                result = [tc < 4]

    #save just the ROI Censor
    result = result.astype(int)
    rois_censored = np.sum([result == 0])
    np.savetxt('roi_censor.1D', np.transpose(result), fmt='%i')

    #combine with the motion censor
    motion = np.genfromtxt('stock_censor.1D')
    result = np.squeeze(np.multiply(result, motion))
    np.savetxt('combined_censor.1D', np.transpose(result), fmt='%i')

    print s, rois_censored, np.sum([motion == 0]), np.sum([result == 0])




