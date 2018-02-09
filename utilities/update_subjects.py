import pdb
import os
import glob
import subprocess
import numpy as np
import pandas as pd
from project import Project
from place_data import move_raws, move_behaviorals
from status import write_todo

"""
Todo:
Fix parallel subprocess command, at least at some point.

"""

PROJECT_DIR = '/Users/span/projects/stockmri'

def test():
    p = Project(PROJECT_DIR)
    print p.top_dir
    move_raws(p)
    # move_behaviorals(p)

def move_parallel_outputs():
    '''Implement this'''
    pass

def parallelize_undone(proj, task, script, to_do):
    '''todo: implement logging on each subject'''
    '''Runs the parallel cshell scripts'''
    script_path = os.path.join(
        proj.top_dir, 'scripts', task + '_' + script + '_parallel'
    )

    os.system('chmod +x ' + script_path)
    subject_folder = os.path.join(proj.top_dir, 'pyproject',to_do)

    num_lines = sum(1 for line in open(subject_folder))
    if num_lines == 0:
        return

    #for 1 through 10, this returns [8.0, 4.0, 3.0, 2.0, 2.0, 1, 1, 1, 1]
    n_jobs = str(int(max(1, (8.0/num_lines + .5) // 1)))

    cat_command = ['cat', subject_folder]

    parallel_command = ' '.join(
        ["time parallel --bar --results /Users/span/projects/stockmri/pyproject/" + task + '_' + script + " --tag", script_path, "{}", n_jobs]).split()

    return ' '.join(cat_command + ['|'] + parallel_command)

    # this is broken right now...
    #ps = subprocess.Popen(cat_command, stdout=subprocess.PIPE)
    #output = subprocess.check_output(parallel_command, stdin=ps.stdout)
    #ps.wait()


if __name__ == "__main__":
    # update_files()
    proj = Project(PROJECT_DIR)
    gnu_par = []
    print proj
    for task in proj.tasks:
        for script, abbr in zip(['preprocess', 'reg_csfwm'], ['prep', 'reg']):
            gnu_par.append(
                parallelize_undone(
                    proj,task, script, 'todo_' + abbr + '_' + task + '.txt'
                )
            )
    for x in gnu_par:
        print x
    write_todo('gnup.sh', gnu_par)


