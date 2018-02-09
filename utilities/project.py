import pdb
import os
import glob
import subprocess
import numpy as np
import pandas as pd

"""
Todo:

implement subject logging
"""

class Subject(object):
    '''
    A micro class for subject info.
    '''
    def __init__(self, subj_id, raw, path, tasks, scans, condition=False, excluded=[]):
        self.name = subj_id
        self.raw_path = raw
        self.path = path
        self.tasks = tasks
        self.scans = scans
        self.excluded = excluded
        if condition:
            self.condition = condition

    def has_directory(self):
        return os.path.exists(self.path)

    def has_file(self, filename):
        if self.has_directory():
            if filename in os.listdir(self.path):
                return True
            elif filename + '.gz' in os.listdir(self.path):
                return True
        return False

    def has_task(self, task):
        return task in self.tasks

    def has_scan(self, scan):
        return scan in self.scans

    def excluded_in_task(self, task):
        return task in self.excluded

    def file_path(self, file):
        return os.path.join(self.path, file)



class Project(object):
    """
    The project module provides basic helper functions used in many scripts.
    The module requires there to exist a project_spec file in the current directory
    """

    def __init__(self, project_dir):
        self.top_dir = project_dir
        self._update_specs()
        self._build_subject_list()

    def __str__(self):
        return '\n'.join(
            [p + '=' + str(getattr(self, p)) for p in self.set_properties]
            )

    def _update_specs(self):
        ''' Read the project spec file line by line'''
        required = ['project', 'tasks', 'scans', 'scan_names', 'behaviorals']
        optional = ['conditions']
        self.set_properties = [] # used by __str__
        used = set(required)
        with open(os.path.join(self.top_dir, 'project_spec')) as fname:
            for line in fname:
                props = line.strip('\n').split('=')
                var_name = props[0].strip()
                if var_name in required or var_name in optional:
                    setattr(self, var_name, eval(props[1]))
                    self.set_properties.append(var_name)
                    if var_name in required:
                        used.remove(var_name)
        if used:
            raise ValueError("Error: missing " + ', '.join(used))

    def _check_csv(self, row, column):
        accept_strings = ['x', '1']
        if column == 'Market':
            return True
        return any(
            [
                x in str(self.subject_csv[column][row])
                for x in accept_strings
            ]
        )

    def _build_subject_list(self):
        '''Used for get subjects, sets self.subjects, list of class Subject'''
        self.subject_csv = pd.read_csv(self.top_dir + '/subject.csv')
        self.subjects = []
        for i, folder in enumerate(self.subject_csv['Folder']):

            ### read off subject properties from csv
            try:
                subject_string = self.subject_csv['Subject'][i]
                if 'phantom' in subject_string:
                    continue

                subject_string = subject_string[0:8]

                if not folder or pd.isnull(folder):
                    print "No folder found for " + subject_string
                    continue

                subject_raw_path = os.path.join(
                    self.top_dir, 'raw_scans', folder)
                subject_path = os.path.join(
                    self.top_dir, 'subjects', subject_string).strip()


                subject_tasks = [
                    task for task in self.tasks
                    if self._check_csv(row=i, column='task_' + task)
                ]
                #update subject scans
                subject_scans = [
                    scan for scan in self.scans
                    if self._check_csv(row=i, column=scan)
                ]

                if 'Condition' in self.subject_csv:
                    subject_condition = self.subject_csv['Condition'][i]
                else:
                    subject_condition = False

                subject_exclude = []
                for task in self.tasks:
                    #print self.subject_csv['Exclude'][i]
                    exclusion = self.subject_csv['Exclude'][i]
                    if not pd.isnull(exclusion) and task in exclusion:
                        subject_exclude.append(task)


            except TypeError:
                print "Error reading subject: ", self.subject_csv['Subject'][i]
                # print self.subject_csv.iloc[i]
                continue

            self.subjects.append(
                Subject(
                    subject_string,
                    subject_raw_path,
                    subject_path,
                    subject_tasks,
                    subject_scans,
                    subject_condition,
                    subject_exclude
                )
            )

    def get_subjects(self):
        '''Return all subjects in the project'''
        return [s for s in self.subjects]

    def get_tasks(self):
        return self.tasks

    def subjects_missing_directory(self):
        return [s for s in self.subjects if not s.has_directory()]

    def subjects_missing_task(self, task):
        ''''''
        return [s for s in self.subjects if not s.has_task(task)]

    def subjects_missing_scan(self, scan):
        ''''''
        return [s for s in self.subjects if not s.has_scan(scan)]

    def subjects_missing_file(self, fn):
        ''''''
        return [
            s for s in self.subjects
            if s.has_directory() and
            not s.has_file(fn)
        ]
