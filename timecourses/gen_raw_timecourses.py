
import glob
import os, pdb
import subprocess
import shutil
import numpy as np
import pandas as pd


TOP_DIR = '/Users/span/projects/stockmri'
TASKS = ['stock','bias']
SCANS = ['T1w_9mm_BRAVO', 'STOCK_1', 'STOCK_2', 'BIAS']
SCAN_NAMES = ['anat', 'stock_1', 'stock_2', 'bias']

def get_subjects():
    with open(os.path.join(TOP_DIR, 'pyproject', 'all_good_subjects.txt')) as f:
        subjects = [x.strip('\n') for x in f.readlines()]
    return subjects

subjects = get_subjects()

output_dir = 'timecourses'

masks = ['mirre_r_acc', 'mirre_b_dlpfc', 'mirre_acc', 'mirre_r_insula', 'vlpfc']

# masks = ['demartino_dmpfc8mm', 'nacc8mm', 'mpfc', 'caudate',
#          'acing', 'dlpfc', 'desai_ins', 'nacc_desai_mpm']

# NOT relative to scripts:
TASK = 'stock'
tr_lag = 16
dataset_name = TASK + '_mbnf+orig'
anat_name = 'anat+tlrc'
tmp_tc_dir = TASK + '_raw_tcs/'

def master():
    subjects = get_subjects()
    scriptsdir = '/Users/span/projects/stockmri/scripts'
    topdir = '/Users/span/projects/stockmri/' #os.path.split(os.getcwd())[0]
    mask_dir = '/Users/span/projects/stockmri/scripts'#'/Users/span/Dropbox/SPAN/masks'
    subjectdirs = find_subject_dirs(topdir, subjects)

    os.chdir(scriptsdir)

    maskdump(mask_dir, subjectdirs, subjects, dataset_name, anat_name, masks,
         scriptsdir, tmp_tc_dir)





def fractionize_mask(mask, dataset_name, anat_name, scriptsdir):
    # function assumes to be located within subject directory

    # PRINT OUT:
    print 'fractionizing', mask

    # define scriptsdir mask location
    scripts_mask = os.path.join(scriptsdir, mask+'+tlrc.')

    # attempt to remove old fractionized mask files:
    # if os.path.exists(mask+'r+orig.HEAD'):
    #     return
    try:
        os.remove(mask+'r+orig.HEAD')
        os.remove(mask+'r+orig.BRIK')
    except:
        pass

    # fractionize the mask to the functional dataset
    cmd = ['3dfractionize', '-overwrite','-template', dataset_name, '-input', scripts_mask,
           '-warp', anat_name, '-clip', '0.1', '-preserve', '-prefix',
           mask+'r+orig']
    subprocess.call(cmd)



def mask_average(subject, mask, dataset_name, tmp_tc_dir):
    # function assumes within subject folder

    # PRINT OUT:
    print 'maskave', subject, mask

    # define left, right, both:
    areas = ['l','r','b']
    area_codes = [[1,1],[2,2],[1,2]]

    '''
    tcfiles = glob.glob(os.path.join(tmp_tc_dir, '*.tc'))
    removed_count = 0
    for tcf in tcfiles:
        try:
            os.remove(tcf)
            removed_count += 1
        except:
            print 'could not remove:', tcf

    print 'tcfiles removed:', removed_count
    '''

    # iterate areas, complete mask ave:
    for area, codes in zip(areas, area_codes):
        # define the name of the raw tc file:
        raw_tc = '_'.join([subject, area, mask, 'raw.tc'])

        # attempt to remove the file if it already exists here or in the
        # temporary directory:
        # if os.path.exists(raw_tc):
        #     continue
        try:
            os.remove(raw_tc)
        except:
            pass
        try:
            os.remove(os.path.join(tmp_tc_dir, raw_tc))
        except:
            pass

        cmd = ['3dmaskave', '-overwrite','-mask', mask+'r+orig', '-quiet', '-mrange',
               str(codes[0]), str(codes[1]), dataset_name]#, '>', raw_tc]
        #subprocess.call(cmd)

        fcontent = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        fcontent.wait()
        fcontent = fcontent.communicate()[0]

        fid = open(raw_tc,'w')
        fid.write(fcontent)
        fid.close()


        # move the raw tc file to the tmp tc directory:
        shutil.move(raw_tc, tmp_tc_dir)




def maskdump(topdir, subjdirs, subjects, dataset_name, anat_name, masks,
             scriptsdir, tmp_tc_dir):

    # PRINT OUT:
    print 'mask dump', subjects

    # iterate over subjects:
    for subjdir, subject in zip(subjdirs, subjects):
        # enter the subject directory:
        os.chdir(subjdir)

        # create the directory for raw tc files, if necessary:
        if not os.path.exists(tmp_tc_dir):
            os.mkdir(tmp_tc_dir)

        # tcs = glob.glob(os.path.join(tmp_tc_dir,'*.tc'))
        # for tcf in tcs:
        #     try:
        #         os.remove(tcf)
        #     except:
        #         pass


        # iterate over masks:
        for mask in masks:
            # fractionize the masks
            fractionize_mask(mask, dataset_name, anat_name, scriptsdir)

            # create the raw timecourses:
            mask_average(subject, mask, dataset_name, tmp_tc_dir)

    # return to the topdir (just in case):
    os.chdir(topdir)




def find_subject_dirs(topdir, subjects):
    
    print subjects
    subjdirs = []
    for subject in subjects:
        dir = glob.glob(os.path.join(topdir,'subjects',subject))[0]
        if dir:
            subjdirs.append(dir)
    return subjdirs



if __name__ == '__main__':
    master()
