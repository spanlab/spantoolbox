#!/usr/bin/python

# filename: fibertrack_subs.py
# this script loops over subjects to perform fiber tracking using the mrtrix command tckgen

# see here for more info on tckgen: https://github.com/jdtournier/mrtrix3/wiki/tckgen


import os
import sys


##########################################################################################
# EDIT AS NEEDED:

#dataDir = os.path.join(os.path.expanduser('~'),'cueexp','data')	# experiment main data directory
	
os.chdir('../../')
main_dir=os.getcwd()
os.chdir('scripts/dmri')

# data directory
dataDir=main_dir+'/data'


# define input directory and files relative to subject's directory 
method = 'mrtrix_fa'
inDir = 'dti96trilin/'+method	# directory w/in diffusion data and b-gradient file and mask
infile = 'CSD8.mif'					# tensor or CSD file 
alg = 'iFOD2'						# will do iFOD2 by default
gradfile = 'b_file' 				# b-gradient encoding file in mrtrix format
#maskfile = 'brainMask.nii.gz' 		# this should be included
maskfile = 'wm_mask_dil2.nii.gz' 		# this should be included

# define ROIs 
roiDir = 'ROIs' 					# directory w/ROI files
#seedStr = 'mpfc8mm'						# if false, will use the mask as seed ROI by default
#seedStr = 'nacc'					# if false, will use the mask as seed ROI by default
seedStr = 'DA'

targetStrs = ['caudate','putamen','nacc']		# can be many or none; if not defined, fibers will just be tracked from the seed ROI
#targetStrs = ['PVT']		
#targetStrs = ['nacc']		
excPath = ''
#excPath = '/home/hennigan/cueexp/data/ROIs/ACabove_mask.nii.gz'

LR = ['L','R'] # 'L' for left and/or 'R' for right

# fiber tracking options; leave blank or comment out to use defaults:
number = '1000'						# number of tracks to produce
maxnum = str(int(number)*10000)		# max number of candidate fibers to generate (default is number x 1000)
#maxattempts = '1'					# max # of times the tracking alg should attempt to find an appropriate tracking dir from a given seed
maxlength = '50'					# max length (in mm) of the tracks
stop = True							# stop track once it has traversed all include ROIs
step_size = ''						# define step size for tracking alg (in mm); default is .1* voxel size
#cutoff = '.05'					# determine FA cutoff value for terminating tracks (default is .1)
cutoff = ''						# FA (or FOD amplitude) cutoff for initializing tracks 
#init_cutoff = '.05'				# initial cutoff for initializing tracks 
init_cutoff = ''				
initdir = '0,1,0.5' 		        # vector specifying the initial direction to track fibers from seed to target
initdir = ''			
nthreads = 8						# of threads to use for tractography
dilateRoiStr = '_dil2' 			# if ROI is dilated, add dilation string here
#dilateRoiStr = '' 					
force = True						# if true, the command will save over a pre-existing output file with the same name

# define directory for resulting fiber files (relative subject's directory)
outDir = 'fibers/'+method			# directory for saving out fiber file

#outFileStr = '_v2'  # out file name suffix? Leave blank if not desired
outFileStr = ''  # out file name suffix? Leave blank if not desired

print 'execute commands?'
xc = bool(input('enter 1 for yes, or 0 to only print: '))



###############################################################################
############################### DO IT #########################################
###############################################################################


#########  print commands & execute if xc is True, otherwise just print them
def doCommand(cmd):
	
	print cmd+'\n'
	if xc is True:
		os.system(cmd)


#########  get main data directory and subjects to process	
def whichSubs():
	
	from getCueSubjects import getsubs 
	subjects,gi = getsubs()

	print ' '.join(subjects)

	input_subs = raw_input('subject id(s) (hit enter to process all subs): ')
	print '\nyou entered: '+input_subs+'\n'

	if input_subs:
		subjects=input_subs.split(' ')

	return subjects


######### produce command for fiber tracking	
if __name__ == '__main__':
    
	subjects = whichSubs()

	for subject in subjects:  	# subject loop
	
		print '\nWORKING ON SUBJECT '+subject+'...\n'

		subjDir = os.path.join(dataDir,subject)
		os.chdir(subjDir)
		
		if not os.path.exists(outDir):
			os.makedirs(outDir)

	 	# target ROI loop	
		for roi in targetStrs:

			# L and/or R loop
			for LorR in LR:

				print '\nWORKING ON TRACKING '+LorR+' '+seedStr+' and '+roi+'...\n'
			
				outfile = seedStr+LorR+'_'+roi+LorR+outFileStr+'.tck'  # out file name

				cmd = 'tckgen'
				if alg:
					cmd = cmd+' -algorithm '+alg
				if gradfile: 
					cmd = cmd+' -grad '+os.path.join(inDir,gradfile)
				if maskfile: 
					cmd = cmd+' -mask '+os.path.join(inDir,maskfile)
				if seedStr:
					cmd = cmd+' -seed_image '+os.path.join(roiDir,seedStr+LorR+dilateRoiStr+'.nii.gz')
				if roi:
					cmd = cmd+' -include '+os.path.join(roiDir,roi+LorR+dilateRoiStr+'.nii.gz')
				if excPath:
					cmd = cmd+' -exclude '+excPath
				#if number:
				#	cmd = cmd+' -number '+str(number)
				if number:
				 	cmd = cmd+' -select '+str(number)
				# if maxnum:
				# 	cmd = cmd+' -maxnum '+str(maxnum)
				if maxnum:
					cmd = cmd+' -seeds '+str(maxnum)
				# if maxattempts:
				# 	cmd = cmd+' -max_attempts_per_seed '+str(maxattempts)
				if maxlength:
					cmd = cmd+' -maxlength '+str(maxlength)
				if stop:
					cmd = cmd+' -stop'
				if step_size:
					cmd = cmd+' -step '+str(step_size)
				if cutoff:
					cmd = cmd+' -cutoff '+str(cutoff)
				# if init_cutoff:
				# 	cmd = cmd+' -initcutoff '+str(init_cutoff)
				if init_cutoff:
					cmd = cmd+' -seed_cutoff '+str(init_cutoff)
				# if initdir:
				# 	cmd = cmd+' -initdirection '+str(initdir)
				if initdir:
					cmd = cmd+' -seed_direction '+str(initdir)
				if nthreads:
					cmd = cmd+' -nthreads '+str(nthreads)
				if force:
					cmd = cmd+' -force'
			
				cmd = cmd+' -info '+os.path.join(inDir,infile)+' '+os.path.join(outDir,outfile)
				
				print 'fiber tracking command:\n'
				doCommand(cmd)
				
		
		print '\nFINISHED SUBJECT '+subject+'\n'
			




