import pdb
import os
import glob
import subprocess
import numpy as np
import pandas as pd
from project import Project

"""
Todo: 
generalize the location of the behavioral data

"""

PROJECT_DIR = '/Users/span/projects/stockmri'

def master():
    p = Project(PROJECT_DIR)
    #gather_raw(p, dry=False)
    print p.subjects_missing_directory()
    move_raws(p)
    move_behaviorals(p)

def gather_raw(p, dry=True):
    '''Rsync raw files from the nimsfs server'''
    dry_com = '--dry-run ' if dry else ''
    os.system(
        'rsync -Lvrt --no-perms ' +
        dry_com +
        'nickborg@cnic-knutson.stanford.edu:/nimsfs/knutson/' +
        p.project + '/ ' + p.top_dir + '/raw_scans'
    )

def get_best_scan(proj, subject, scan, name):
    '''Return the most likely scan path, requires user input '''
    print 'User', subject.name, 'is missing', scan
    possible_dirs = [f for f in os.listdir(subject.raw_path) if scan in f]
    possible_niis = []
    best_nii = 0
    for d in possible_dirs:
        nii = [
            os.path.join(subject.raw_path, d, f)
            for f in os.listdir(os.path.join(subject.raw_path, d))
            if '.nii' in f
        ][0]
        possible_niis.append(nii)
        if len(possible_dirs) > 1:
            print str(len(possible_niis)) + '.)', nii, os.stat(nii).st_size
    if len(possible_dirs) > 1:
        error_message = (
            "Sorry, that is not a valid input. Please enter one of the above."
        )
        print '0.) to skip. '
        while True:
            try:
                best_nii = int(input('Select which of the above to copy: '))

                if best_nii not in range(0, len(possible_dirs) + 2):
                    print error_message
                    continue
                else:
                    best_nii -= 1
                    break
            except ValueError:
                print error_message
                continue
            except NameError:
                print error_message
                continue
            except SyntaxError:
                print error_message
                continue

    if best_nii < 0:
        print 'Skipping ' + subject.name + '...'
        return False

    try:
        best_path = possible_niis[best_nii]
        print 'Copying ' + best_path + '\n'
        return best_path
    except IndexError:
        print 'No niftis found!'
        return False


def move_raws(p):
    ''' Copy files from raw directory to subject folders if needed. '''

    for subject in p.subjects_missing_directory():
        os.mkdir(subject.path)

    for scan, name in zip(p.scans, p.scan_names):
        nii_name = name + '.nii'
        missing_the_scan = p.subjects_missing_file(nii_name)

        if not missing_the_scan:
            print "All subjects have a copy of " + nii_name + ' in place.'
        for subject in missing_the_scan:
            if not subject.has_scan(scan):
                continue
            best_scan_path = get_best_scan(p, subject, scan, name)
            if best_scan_path:
                new_file_path = os.path.join(subject.path, nii_name)
                subprocess.call(['cp', best_scan_path, new_file_path + '.gz'])
                try:
                    path_head = os.path.split(best_scan_path)[0]
                    png = glob.glob(path_head + '/*.png')[0]
                    new_im_path = os.path.join(subject.path, name + '_qa.png')
                    subprocess.call(['cp', png, new_im_path])
                except IndexError:
                    continue



def move_behaviorals(p):
    for task, behavioral in zip(p.tasks, p.behaviorals):
        missing_b = p.subjects_missing_file(behavioral)
        if not missing_b:
            print "All subjects have", behavioral
        for s in missing_b:
            print s.name, 'missing', behavioral
            bpath = (
                '/Users/span/Google Drive/BehavData/' + task +
                'MRI/' + s.name + '_' + behavioral
            )
            #print str(os.path.exists(bpath)) + ' ' + bpath
            subprocess.call(['cp', bpath, os.path.join(s.path, behavioral)])

if __name__ == "__main__":
    master()