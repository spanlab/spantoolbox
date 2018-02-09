import os, glob
import subprocess, sys, stat

def find_folders(topdir):
	possible = glob.glob(os.path.join(topdir,'*'))
	dirs = [x for x in possible if os.path.isdir(x)]
	return dirs


def pair_names_ttests(curdir):
	ttests = glob.glob(os.path.join(curdir,'*_tvalues.nii'))
	onlyttests = [os.path.split(x)[1] for x in ttests]
	names = [x.split('+')[0] for x in onlyttests]
	return zip(names, onlyttests)


def write_clustcommands(curdir, pairs):
	cc = os.path.join(curdir, 'clustcommand')
	try:
		os.remove(cc)
	except:
		pass
	fid = open(cc,'w')
	for name, ttest in pairs:
		print name, ttest
		fid.write('3dclust -1Dformat -nosum -1dindex 0 -1tindex 0 -2thresh -2.805 2.805 -dxyz=1 0 3 '+ttest+' > '+name+'.1D\n\n')

	fid.close()

def run_clustcommands(curdir):
	os.chdir(curdir)
	cc = os.path.join(curdir, 'clustcommand')
	#subprocess.call(['chmod','+x',cc])
	subprocess.call(cc, shell=True)
	os.chdir('..')

def run_tabledump_on1d(curdir, tabledump_path):
	os.chdir(curdir)
	files = glob.glob('*.1D')
	for fid in files:
		subprocess.call([tabledump_path, fid])
	os.chdir('..')

if __name__ == "__main__":
	top = os.getcwd()
	#ttest_dirs = find_folders(top)
	ttest_dirs = [os.getcwd()]
	for tdir in ttest_dirs:
		pairs = pair_names_ttests(tdir)
		# FIRST: comment out the two run_ commands, leaving only the write_ command
		# then chmod +x */* from ttest directory
		write_clustcommands(tdir, pairs)
                os.system('chmod +x clustcommand')
		# THEN: comment out write command, run with two run_ commands
		run_clustcommands(tdir)
		run_tabledump_on1d(tdir, os.path.join(top,'tableDump.py'))
