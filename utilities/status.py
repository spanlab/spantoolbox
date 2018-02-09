import pdb
import os
import glob
import subprocess
import numpy as np
import pandas as pd
from project import Project
from qa import check_behaviorals

"""
The status module provides functions for determining which parts of the
analysis pipeline have completed successfully.

Todo:
implement automated QA elsewhere.
"""

SPLITTER = "+++++++++++++++++++++++++++++++++++++++++++++++"

def test():
    print SPLITTER
    os.system('lolcat ~/nyanascii.txt')
    print SPLITTER
    p = Project(PROJECT_DIR)
    print p.top_dir
    # print [x for x in p.subjects if x.name=='jg151121'][0].has_file('cue.nii')
    # print condition counts
    try:
        for condition in p.conditions:
            print(
                condition +
                ': ' +
                str(sum([s.condition == condition for s in p.subjects]))
            )
    except AttributeError:
        print "There are", len(p.subjects), "subjects."

    print check_all(p, True)

def unfinished(prj, task, file, todo_name=''):
    missing_task = prj.subjects_missing_task(task)
    missing = [
        s.name for s in prj.subjects_missing_file(file)
        if s not in missing_task
    ]
    missing_list_print(file, list(missing))

    if todo_name:
        write_todo(todo_name, missing)

    return missing

def missing_list_print(what, l):
    l = [ x for x in l if x ]
    print SPLITTER
    if len(l) > 0:
        print('The following subjects are missing ' + what)
        print l#'\n'.join(l)
    else:
        print "No subjects missing", what


def write_todo(filename, lines_to_write):
    lines_to_write = [ x for x in lines_to_write if x ]
    with open(filename, 'w') as f:
        f.write('\n'.join(lines_to_write))

def check_prep_reg(prj, task, todo_files=False):
    pp_name = task + '_mbnf+orig.BRIK'
    reg_name = 'z' + task + '_reg_csfwm+orig.BRIK'

    unfinished(prj, task, pp_name, 'todo_prep_' + task + '.txt')
    unfinished(prj, task, reg_name, 'todo_reg_' + task + '.txt')

def check_all(prj, todo_files=False):
    '''
    Check all subjects for all tasks in PROJECT_DIR.
    If todo_files = true, writes todo txt files for each subject.
    '''
    #Check if subject has a directory
    print missing_list_print(
        'a directory',
        [s.name for s in prj.subjects_missing_directory()]
        )

    # check for anat.nii
    for scan in prj.scan_names:
        task = scan.split('=')[0].lower()
        unfinished(prj, task, scan + '.nii')


    #check preprocessing and regression results for all tasks
    for task in prj.get_tasks():
        check_prep_reg(prj, task, todo_files)

    #check if behavioral is in place.
    for beh in prj.behaviorals:
        unfinished(prj, beh.split('_')[0], beh)
    check_behaviorals(prj)

if __name__ == "__main__":
    PROJECT_DIR = os.path.split(os.getcwd())[0]
    test()
