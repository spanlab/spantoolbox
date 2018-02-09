'''
Simple script to set up SVM folder structure...
'''
import os

SUBJ_DIR = '/Users/span/projects/stockmri/subjects'
SVM_DIR = '/Users/span/projects/stocksvm/biassvm'

def get_subjects():
    '''Return a list of all subjects to use in SVM'''
    with open(os.path.join('/Users/span/projects/stockmri/', 'pyproject','all_good_subjects.txt')) as f:
        subjects = [x.strip('\n') for x in f.readlines()]
    return subjects

SUBJECTS = get_subjects()

if not os.path.exists(SVM_DIR):
    os.mkdir(SVM_DIR)

for s in SUBJECTS:
    os.chdir(os.path.join(SUBJ_DIR, s))
    os.system('adwarp -overwrite -apar anat+tlrc -dpar bias_mbnf+orig -dxyz 2.9')
    os.system('3dAFNItoNIFTI bias_mbnf+tlrc')
    result_dir = os.path.join(SVM_DIR, s)
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    os.system('cp -f bias_mbnf.nii ' + result_dir)
    os.system('python /usr/local/bin/makeVec.py /Users/span/projects/stockmri/scripts/bias_vecs.txt')
    os.system('cp -f stock_vs_bond_onset.1D ' + result_dir)
    # os.system('cp -f stockup_onset.1D ' + result_dir)
