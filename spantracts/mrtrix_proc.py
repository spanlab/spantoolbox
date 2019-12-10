#!/usr/bin/python

# filename: mrtrix_proc.py
# script to loop over subjects to process diffusion weighted data using mrtrix3 commands

# see here for more info on mrtrix3: https://github.com/jdtournier/mrtrix3/wiki/Tutorial-DWI-processing

import os
import sys
import glob   # for getting files from a directory using a wildcard 
	

##########################################################################################
# EDIT AS NEEDED:

# set up mrtrix sub directory & make sym links to files
doSetupMrtrixDir = True

# make tensor and FA maps? (useful for general QA)
doTensorFAMaps = True

# estimate response function? for more info: https://github.com/jdtournier/mrtrix3/wiki/dwi2response
doEstimateResponseFxn = True

# display response function? 
doDisplayResponseFxn = False

# estimate fiber orientation distribution? for more info: https://github.com/jdtournier/mrtrix3/wiki/dwi2fod
doEstimateFOD = True

# display FOD? 
doDisplayFOD = False

# do whole-brain fiber tractography? for more info: https://github.com/jdtournier/mrtrix3/wiki/tckgen
doTrackWBFibers = False			

# do whole-brain fiber density? for more info: https://github.com/jdtournier/mrtrix3/wiki/tckmap
doWBFiberDensity = False

# make dilated white matter mask to use for fiber tracking? 
doWMMask = True

print 'execute commands?'
xc = bool(input('enter 1 for yes, or 0 to only print: '))


#############

# relevant vars, files, & directories (relative to subj dir)

#data_dir = os.path.join(os.path.expanduser('~'),'cueexp','data') # main data directory
#data_dir = '/scratch/PI/knutson/cue_dti/data'
os.chdir('../../')
main_dir=os.getcwd()
os.chdir('scripts/dmri')

# data directory
data_dir=main_dir+'/data'


dwi_dir='dti96trilin'

resp_alg = 'fa'		# algorithm for estimating response fxn; some options are tournier, fa, ...
# note: FA method is WAY faster than tournier!! 

mrt_dir = os.path.join(dwi_dir,'mrtrix_'+resp_alg)

ingradfile = dwi_dir+'/bin/b_file'  	# b-vecs and b-vals file in mrtrix format
inmaskfile = dwi_dir+'/bin/brainMask.nii.gz' # binary brain mask
gradfile = mrt_dir+'/b_file'
maskfile = mrt_dir+'/brainMask.nii.gz'

dwifilestr = dwi_dir+'/*_aligned_trilin.nii.gz' # preprocessed dwi data - its ok to use wildcards here

tensorfile = mrt_dir+'/dt.nii' 		# file name for tensor map nifti 
fafile = mrt_dir+'/fa.nii'				# file name for fa map nifti

# variables necessary for estimating the response function and FOD
lmax = '8'									# max harmonic degree of the response fxn (must have at least 45 directions for lmax=8)
sf_file = mrt_dir+'/sf'+str(lmax)+'.mif'	# this will output a mask file showing the voxels used to estimate the single fiber response
respfile = mrt_dir+'/response'+str(lmax)	# name for response file
fod_alg = 'csd'								# algorithm to use for estimating fiber orientaion distribution
fodfile = mrt_dir+'/CSD'+str(lmax)+'.mif'	# name for FOD file


# variables necessary for doing whole-brain fiber tracking & fiber density maps
out_dir = os.path.join('fibers','mrtrix')  # out dir 
ft_input = fodfile					# tensor or CSD file 
wbt_alg = 'iFOD2'						# will do iFOD2 by default
num_fibers = 300000					# number of fiber tracts to generate 
ft_file = out_dir+'/wb.tck' 		# filename for whole-brain fiber tracks file
fd_input = ft_file					# define fiber .tck file to compute density from
templatefile = 't1.nii.gz'			# template file for bounding box and transform
vox_size = '1'						# isotropic voxel size (in mm)
fd_file = out_dir+'/wb_fd.nii.gz' 	# out fiber density file


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
	


######### set up mrtrix directory and files
def setupMrtrix():

	# make mrtrix dir if it doesn't already exist
	if os.path.exists(mrt_dir):
		print '\nmrtrix dir already exists...\n'
	else:	
		print 'making dir for mrtrix files: '+mrt_dir+'\n'
		cmd = 'mkdir '+mrt_dir
		doCommand(cmd)
		#os.makedirs(mrtr_outDir)

	# copy over b_file and brainMask to mrtrix dir (redundant but useful)
	if os.path.exists(gradfile):
		print '\nb_file already copied over...\n'
	else:	
		print 'copying over b_file to mrtrix dir...\n'
		cmd = 'cp '+ingradfile+' '+gradfile
		doCommand(cmd)

	if os.path.exists(maskfile):
		print '\nbrainmask file already copied over...\n'
	else:	
		print 'copying over brainmask to mrtrix dir...\n'
		cmd = 'cp '+inmaskfile+' '+maskfile
		doCommand(cmd)
		


######### set up mrtrix directory and files
def tensorFAMaps():

	# ex: dwi2tensor -grad b_file -mask brainMask.nii.gz ../dwi_aligned_trilin.nii.gz dt.nii; 
	#	  tensor2metric -fa fa.nii dt.nii
		
	# make tensor map
	if os.path.exists(tensorfile):
		print '\ntensor file already exists...\n'
	else:	
		print 'making mrtrix tensor file: '+tensorfile+'\n'
		cmd = 'dwi2tensor -grad '+gradfile+' -mask '+maskfile+' '+dwifile+' '+tensorfile
		doCommand(cmd)

	# make fa map
	if os.path.exists(fafile):
		print '\nfa file already exists...\n'
	else:	
		print 'making mrtrix fa file: '+fafile+'\n'
		cmd = 'tensor2metric -fa '+fafile+' '+tensorfile
		doCommand(cmd)
		


######### estimate response function 
def estimateResponseFxn():

	# ex: dwi2response touriner dwi_aligned_trilin.nii.gz bin/response8 -grad bin/b_file -mask bin/brainMask.nii.gz -lmax 8 -voxels bin/sf.mif
	
	# if resp_alg is fa, the brain mask needs to be eroded, otherwise the 
	# single fiber voxels that are selected are weird fringy voxels at the 
	# edge of the brain...
	if resp_alg is 'fa':
		erodedmaskfile = mrt_dir+'/bmask_erode6.nii'
		if os.path.exists(erodedmaskfile):
			print '\neroded brain mask file already exists...\n'
		else:	
			cmd = 'maskfilter -npass 6 '+maskfile+' erode '+' '+erodedmaskfile
			doCommand(cmd)
		maskToUse = erodedmaskfile
	else: 
		maskToUse = maskfile

	# estimate response function
	if os.path.exists(respfile):
		print '\nresponse file already exists...\n'
	else:	
		print 'estimating response function...\n'
		cmd = 'dwi2response '+resp_alg+' '+dwifile+' '+respfile+' -grad '+gradfile+' -mask '+maskToUse+' -lmax '+str(lmax)+' -voxels '+sf_file
		doCommand(cmd)


######### display response function - should be squatty on the z-axis (axis in blue) and otherwise round
def displayResponseFxn():

	# ex: shview -response response8

	# display response function 
	print 'displaying response function...\n'
	cmd = 'shview -response '+respfile
	doCommand(cmd)



######### estimate FOD
def estimateFOD():

	# ex: dwi2fod -grad bin/b_file -mask bin/brainMask.nii.gz csd dwi_aligned_trilin.nii.gz mrtrix/response8 mrtrix/CSD8.mif
		
	# estimate FOD
	if os.path.exists(fodfile):
		print '\nFOD file already exists...\n'
	else:	
		print 'estimating fiber orientation distribution (FOD)...\n'
		cmd = 'dwi2fod -grad '+gradfile+' -mask '+maskfile+' '+fod_alg+' '+dwifile+' '+respfile+' '+fodfile
		doCommand(cmd)

	
	 
######### display FOD
def displayFOD(): 

	# ex: mrview dwi_aligned_trilin.nii.gz -odf.load_sh CSD8.mif

	# display the FOD
	print 'displaying FOD...\n'
	cmd = 'mrview '+dwifile+' -odf.load_sh '+fodfile
	doCommand(cmd)



######### whole-brain tractography
def trackWBFibers(): 

	# ex: tckgen -alg SD_Stream -grad b_file -mask brainMask.nii.gz -seed_image brainMask.nii.gz -number 300000 CSD8.mif wb.tck

	# track 	
	if os.path.exists(ft_file):
		print '\nwhole-brain fiber pathway file already exists...\n'
	else:	
		print 'tracking whole-brain fibers...\n'
		cmd = 'tckgen -algorithm '+wbt_alg+' -grad '+gradfile+' -mask '+maskfile+' -seed_image '+maskfile+' -number '+str(num_fibers)+' '+ft_input+' '+ft_file
		doCommand(cmd)



######### whole brain fiber density
def wbFiberDensity(): 

	# ex: tckmap -template t1_fs.nii.gz vox 1 wb.tck wb_fd.nii.gz

	# fiber density imaging		
	if os.path.exists(fd_file):
		print '\nwhole-brain fiber density file already exists...\n'
	else:	
		print 'computing whole-brain fiber density...\n'
		cmd = 'tckmap -template '+templatefile+' vox '+vox_size+' '+ft_file+' '+fd_file
		doCommand(cmd)
	
		


######### main deal 
if __name__ == '__main__':

	
	subjects = whichSubs()


	# now loop through subjects	
	for subject in subjects:


		print 'WORKING ON SUBJECT '+subject

		subjDir = os.path.join(data_dir,subject)
		os.chdir(subjDir)
		
		# get this subject's processed diffusion-weighted data file
		dwifilelist = glob.glob(dwifilestr)
		if len(dwifilelist)!=1:
			print 'yikes! either raw data file wasn''t found or more than 1 was found'
		else:
			dwifile=dwifilelist[0]
				
		
		# setup mrtrix dir
		if doSetupMrtrixDir: 
			setupMrtrix()


		# make tensor and fa maps
		if doTensorFAMaps: 
			tensorFAMaps()
			
	
		# estimate response function
		if doEstimateResponseFxn:	
			estimateResponseFxn()


		# display the estimated response 
		if doDisplayResponseFxn:	
			displayResponseFxn()

			
		# estimate FOD
		if doEstimateFOD:
			estimateFOD()
			

		# display the FOD
		if doDisplayFOD:
			displayFOD()
			
		
		# whole-brain tractography
		if doTrackWBFibers:
			trackWBFibers()


		# fiber density imaging
		if doWBFiberDensity:
			wbFiberDensity()
			

		# make dilated white matter mask to use for fiber tracking 
		if doWMMask:
			wmmask_dilated_file=mrt_dir+'/wm_mask_dil2.nii.gz'
			if os.path.exists(wmmask_dilated_file):
				print '\ndilated WM mask already exists...\n'
			else:	
				print 'dilating WM mask for fiber tracking...\n'
				cmd = 'maskfilter -npass 2 t1/wm_mask.nii.gz dilate '+wmmask_dilated_file
				doCommand(cmd)

		
		# dilate putamen, caudate, nacc, and DA ROIs 
		cmd = 'maskfilter -npass 2 ROIs/caudateL.nii.gz dilate ROIs/caudateL_dil2.nii.gz'
		doCommand(cmd)
		cmd = 'maskfilter -npass 2 ROIs/caudateR.nii.gz dilate ROIs/caudateR_dil2.nii.gz'
		doCommand(cmd)
		cmd = 'maskfilter -npass 2 ROIs/naccL.nii.gz dilate ROIs/naccL_dil2.nii.gz'
		doCommand(cmd)
		cmd = 'maskfilter -npass 2 ROIs/naccR.nii.gz dilate ROIs/naccR_dil2.nii.gz'
		doCommand(cmd)
		cmd = 'maskfilter -npass 2 ROIs/putamenL.nii.gz dilate ROIs/putamenL_dil2.nii.gz'
		doCommand(cmd)
		cmd = 'maskfilter -npass 2 ROIs/putamenR.nii.gz dilate ROIs/putamenR_dil2.nii.gz'
		doCommand(cmd)
		cmd = 'maskfilter -npass 2 ROIs/DAL.nii.gz dilate ROIs/DAL_dil2.nii.gz'
		doCommand(cmd)
		cmd = 'maskfilter -npass 2 ROIs/DAR.nii.gz dilate ROIs/DAR_dil2.nii.gz'
		doCommand(cmd)



		print 'FINISHED SUBJECT '+subject
			




