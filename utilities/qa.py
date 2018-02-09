import pdb
import os
import time
import subprocess
import numpy as np
import pandas as pd
from project import Project

'''
Assorted QA functions
ToDo:
motion check - keep working on it

qa scripts to write:
motion by hand: check motion, record in autolog, in qa. csv


'''
PROJECT_DIR = '/Users/span/projects/stockmri'

def test():
    proj = Project(PROJECT_DIR)
    check_behaviorals(proj)
    # check_motion_graphs(proj)
    # check_motion(proj)

def check_behaviorals(proj):
    '''Check to see if there are multiple headers in .csvs'''
    for beh in proj.behaviorals:
        any_bad = False
        for sub in proj.subjects:
            if sub.has_file(beh):
                bfile = os.path.join(sub.path, beh)
                with open(bfile) as f:
                    header = f.readline()
                    for line in f:
                        # if sub.name == 'lc160417':
                        #     print list(line)
                        if line == header or all([z==',' for z in list(line.strip())]):
                            any_bad = True
                            print sub.name + ' has a broken ' + beh
                            fix_behavioral(sub.path, beh)
                            continue

        if not any_bad:
            print 'No broken ' + beh + 's'


def fix_behavioral(subpath, bname):

    old_b = os.path.join(subpath, 'old_' + bname)
    new_b = os.path.join(subpath, bname)

    subprocess.call(['mv', new_b, old_b])
    with open(old_b) as o:
        with open(new_b, 'w') as n:
            header = o.readline()
            n.write(header)
            for line in o:
                if line == header or all([z==',' for z in list(line.strip())]):
                    continue
                n.write(line)

# class SimpleGui(App):

#     def build(self):
#         return Button(text='hello')

def basic_ui(options_to_print):
    num_options = len(options_to_print)
    for i, opt in enumerate(options_to_print):
        print str(i+1) + '.)', opt
    print "0.) Comment on this subject."

    error_message = (
        "Sorry, that is not a valid input. Please enter one of the above."
    )

    while True:
        try:
            result = int(input('Which option best describes the motion: '))
            if result not in range(0, num_options + 1):
                print error_message
                continue
            elif result == 0:
                print "Comment below:"
                comment = raw_input()
                result = comment
                break
            else:
                result -= 1
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
    print "Returning", result
    return result

def motion_ui(image_path):
    motion_options = [
        "Motion looks good.",
        "Movement between concatenated scans",
        "Some spikes, censor should fix. ",
        "Worrisome: Needs more attention--check censor.",
        "Unacceptable motion, should exclude."
    ]
    return basic_ui(motion_options)

def motion_update_csv(proj, sub, column, comment):
    csv_path = os.path.join(proj.top_dir, "subject_qa.csv")
    df = pd.read_csv(csv_path)
    column = "motion_" + column
    try:
        col = df[column]
    except KeyError:
        nrow = len(df['Subject'])
        df[column] = pd.Series(
            np.tile(["NO QA"], nrow), index = df.index
        )
    sidx = df['Subject'] == sub.name
    df.loc[sidx,column] = comment
    df.to_csv(csv_path, index = False)


def check_motion_graphs(proj):
    '''
    Implement this--display each subjects motion plots for each scan
    If the scan seems questionable, record that in the subject_qa.csv file in
    the top directory
    '''
    for sub in proj.subjects:
        for scan, name in zip(proj.scans, proj.scan_names):
            if scan == "T1w_9mm_BRAVO":
                continue
            image_path = os.path.join(sub.path, name + '_qa.png')
            if os.path.exists(image_path):
                print image_path
                os.system("open " + image_path)

                os.system("open -a iTerm")
                result = motion_ui(image_path)
                motion_update_csv(proj, sub, name, result)
                os.system("osascript -e 'quit app \"Preview\"'")

            else:
                print image_path, "not found"

        for task in proj.tasks:
            task_file_name = task + '_afni_qa.png'
            afni_qa = os.path.join(sub.path, task_file_name)
            # if not os.path.exists(afni_qa):
            print "Making", afni_qa
            motion_file = '3dmotion' + task + '.1D'
            if sub.has_file(motion_file):
                mf_path = os.path.join(sub.path, motion_file)
                censor_path = os.path.join(sub.path, task + '_censor.1D')
                subprocess.call(
                    ['1dplot','-png', afni_qa, mf_path + '[1..3]', censor_path]
                )
                if sub.has_file(task_file_name):
                    print afni_qa, "made successfully..."
            if os.path.exists(afni_qa):
                os.system("open " + afni_qa)
                os.system("open -a iTerm")
                result = motion_ui(image_path)
                motion_update_csv(proj, sub, task, result)
                os.system("osascript -e 'quit app \"Preview\"'")






def check_motion(proj, verbose=False):
    """
    performs various motion checks on each subject
    todo: record in subject_qa.csv
    """
    max_displace_list = ["-show_max_displace"]
    censor_list = ["-quick_censor_count", ".5"]
    mmm_list = ["-show_mmms"]

    for task in proj.tasks:
        questionable = []
        bad = []

        for sub in proj.subjects:
            if sub.has_task(task):

                motion_name = "3dmotion" + task + ".1D"
                motion_path = os.path.join(sub.path, motion_name)
                censor_path = os.path.join(sub.path, task + "_censor.1D")

                if not sub.has_file(motion_name):
                    print sub.name, "is missing", motion_name
                    continue

                motion_base = [
                    "1d_tool.py",
                    "-infile",
                    motion_path + "[1..6]"
                ]

                max_displace = motion_base + max_displace_list
                censor_count = motion_base + censor_list
                mmms  = motion_base + mmm_list

                censor_infile = [
                    "-censor_infile",
                    censor_path
                ]

                task_name = os.path.join(sub.path, task + '_mbnf+orig')
                task_length_com = ["3dinfo", "-nv", task_name]
                task_length = subprocess.check_output(task_length_com)

                try:
                    max_move = subprocess.check_output(max_displace)
                    mmm_out = subprocess.check_output(mmms)
                    cc_out = subprocess.check_output(censor_count).strip()
                    percent_censored = 100 * int(cc_out)/float(task_length)
                    percent_censored = (100 * percent_censored // 1)/100
                except subprocess.CalledProcessError:
                    print sub.name, "failed on", motion_name, ", file exists"
                    continue

                if float(max_move.split("=")[1]) > 1.5:
                    questionable.append(sub.name)
                    if verbose:
                        print (
                            "questionable movement in " +
                            sub.name, max_move, task
                        )

                if int(percent_censored > 5):
                    bad.append(sub.name)
                    if verbose:
                        print "motion looks bad:", sub.name, task
                        print str(percent_censored) + "\% TRs censored"
                        print mmm_out

        if not bad:
            "There were no subjects with > 5 percent TRs censored."
        if not questionable:
            "There were no subjects with > 1.5mm movement."
        print "Subjects with > 1.5mm movement, " + task + ':'
        print [x for x in questionable if x not in bad]
        print ">5 percent TRs censored, " + task + ':'
        print bad


if __name__ == "__main__":
    test()
