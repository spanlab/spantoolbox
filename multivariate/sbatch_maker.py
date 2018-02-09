import os

################## USER PARAMS #####################
SUBJECT_FILE = '/scratch/PI/knutson/cuesvm/cue_patients_subjects.txt'
JOB_STRING   = 'cue_relapseds'
MEMORY       = '32gb'
TIME         = '48:00:00'
NODES        =  '1'
QOS          = 'normal'#must be 'long' if TIME > than 48 hours
EXEC_DIR     = "/scratch/PI/knutson/cuesvm/svmrfe/"
EXECUTABLE   = 'srun python run_sgdrfe_relapse.py' # takes subject as argv[1]
VENV         = '/scratch/PI/knutson/cuesvm/svmrfe/venv'
################## END PARAMS #####################


def make_batch(subject):
    sbatch = [
          "#!/bin/bash",
          "#",
          "",
          "#all commands that start with SBATCH contain commands that are just  used by SLURM for scheduling",
          "#################",
          "#set a job name",
          "#SBATCH --job-name=" + subject + JOB_STRING,
          "#################",
          "#a file for job output, you can check job progress",
          "#SBATCH --output=" + subject + JOB_STRING + ".out",
          "#################",
          "# a file for errors from the job",
          "#SBATCH --error=" + subject + JOB_STRING + ".err",
          "#################",
          "#time you think you need; default is one hour",
          "#in minutes in this case",
          "#SBATCH --time=" + TIME,
          "#################",
          "#quality of service; think of it as job priority",
          "#SBATCH --qos=" + QOS,
          "#################",
          "#number of nodes you are requesting",
          "#SBATCH --nodes=" + NODES,
          "#################",
          "#memory per node; default is 4000 MB per CPU",
          "#SBATCH --mem=" + MEMORY,
          "#you could use --mem-per-cpu; they mean what we are calling cores",
          "#################",
          "#tasks to run per node; a \"task\" is usually mapped to a MPI  processes.",
          "# for local parallelism (OpenMP or threads),use \"--ntasks-per-node=1 --cpus-per-tasks=16\" instead",
          "",
          "#################",
          "",
          "#now run normal batch commands",
          "ml load python/2.7.5",
          "cd " + EXEC_DIR,
          "source " + VENV,
          EXECUTABLE + ' '  + subject,
    ]

    fname = JOB_STRING + '_' +  subject + ".sbatch"

    with open(fname, 'w') as f:
        for i, line in enumerate(sbatch):
            f.write(line + '\n')
    return fname

if __name__ == "__main__":

    with open(SUBJECT_FILE, 'r') as f:
        subjects = [x for x in f.read().split('\n') if len(x) == 8]

    for s in subjects:
        f = make_batch(s)
        os.system('sbatch ' + f)
