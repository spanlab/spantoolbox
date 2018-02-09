#!/bin/python
import os, sys, argparse
import subprocess
import pandas as pd


class NIMS(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='nims_sync', description='NIMS rsync utility')
        self._setup_parser()

    def _setup_parser(self):
        self.parser.add_argument('--user', metavar='SUID',
                                help='Valid SUNET ID')
        self.parser.add_argument('--pi', metavar='knutson', default='knutson',
                                help = "PI folder in /nimsfs/")
        self.parser.add_argument('--experiment', metavar="Experiment", 
                                 help='Directory in /nimsfs/PI ')
        self.parser.add_argument('--dest', default = 'nims_data', 
                                help = "Destination for nims data")
        self.parser.add_argument('--dry', default=False, action='store_true', 
                                 help = 'Whether to run rsync with --dry-run (copies no files)')
        self.parser.add_argument('--sfile', type=str, 
                                 help="subject csv file specifying folder locations")
        self.args = self.parser.parse_args()

    def sync_dir_command(self, folders = []):
        
        print self.args.user
        source_server = self.args.user + '@cnic-' + self.args.pi + '.stanford.edu'  
        source_path = ':/nimsfs/' + self.args.pi + '/' + self.args.experiment
        if len(folders) > 1:
            source_string = source_server
            for f in folders:
                source_string = source_string + os.path.join(source_path, f) + ' '
            #source_string += '\''
        else:
            source_string = source_path
            source_string = "'{}'".format(source_string)
        dest_path = self.args.dest
        sync_command = [
            'rsync',
            '-Lvrt',
            source_string,
            dest_path
        ]
        return sync_command

    def get_subject_folders(self):
        self.subject_csv = pd.read_csv(self.args.sfile)
        folders = self.subject_csv['Folder']
        return(folders)

    def sync(self):
        try:
            folders = self.get_subject_folders()
            print("Fetching:")
            print(folders)
            command = self.sync_dir_command(folders=folders)
        except NameError:
            command = self.sync_dir_command()
    #     

        if self.args.dry:
            command.insert(1, '--dry-run')
            print("using dry run...")

        cstring = ' '.join(command)
        print("Executing: ")
        print(cstring)
        os.system(cstring)





if __name__ == '__main__':

    nims = NIMS()
    nims.sync()
