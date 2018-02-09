#! /bin/csh
# This is the base preprocessing script to preprocess all subjects for multiple 
# tasks and dump ROI timecoureses. Note that the syntax is cshell and not bash!

############## User Params #############
set TOPDIR=/Users/span/projects/natgeo
set MASKS=${TOPDIR}/masks
set SCANS=( instagram campaign )
set ROI_MASKS=( nacc8mm nacc_desai_mpm caudate ins desai_ins mpfc amyg_mask )

# also change the subject file name below:

foreach subject ( ` tail -n +2 /Users/span/projects/natgeo/subject.csv | cut -d ',' -f2 ` ) #should be +2 for all

	cd ${TOPDIR}/subjects/$subject

	if (! -e csf_mask+tlrc.BRIK) then
	    cp ${MASKS}/csf_mask+tlrc* .
	endif

	if (! -e wm_mask+tlrc.BRIK) then
	    cp ${MASKS}/wm_mask+tlrc* .
	endif


	# ##### rename anatomical scan #####

	if ( -e anat+orig.HEAD ) then
	  rm -rf anat+orig*
	endif

	3dcopy anat.nii.gz anat


	if (! -e anat+tlrc.HEAD ) then
	    @auto_tlrc -warp_orig_vol -suffix NONE -base '/Users/span/abin/TT_N27+tlrc' -input anat+orig.
	endif


	foreach fname ( $SCANS ) 
	#     ### convert the files to AFNI, cut off leadin/leadout #####

	    if ( -e "$fname"_epi+orig.HEAD ) then
	      rm -rf "$fname"_epi+orig*
	    endif


	    3dTcat -overwrite -prefix "$fname"_epi "$fname"'.nii.gz[6..$]'


	    ## ##### refitting + slice time correction #####

	    3drefit -TR 2.0 "$fname"_epi+orig.

	    rm "$fname"+orig*
	    3dTshift -slice 0 -tpattern altplus -overwrite -prefix "$fname" "$fname"_epi+orig.

	    #rm -rf "$fname"_epi+orig*


	    ### correct for motion ####


	    if ( -e "$fname"_m+orig.HEAD ) then
	      rm -rf "$fname"_m+orig*
	    endif


	    if ( -e 3dmotion"$fname".1D ) then
	      rm -rf 3dmotion"$fname".1D
	    endif


	    3dvolreg -Fourier -twopass -overwrite -prefix "$fname"_m -base 3 -dfile 3dmotion"$fname".1D "$fname"+orig

	    #### censor motion ####

	    1d_tool.py -overwrite -infile  '3dmotion'"$fname"".1D[1..6]" -set_nruns 1 \
	                        -show_censor_count \
	                        -censor_motion .25 "$fname" \
	                        -censor_prev_TR

	    ##### smooth spatially #####


	    if ( -e "$fname"_mb+orig.HEAD ) then
	      rm -rf "$fname"_mb+orig*
	    endif


	    3dmerge -overwrite -prefix "$fname"_mb -1blur_fwhm 4 -doall "$fname"_m+orig


	    ##### normalize (calculate pct signal change / average) and filter ####


	    if ( -e "$fname"_mbn+orig.BRIK ) then
	      rm -rf "$fname"_mbn+orig.*
	    endif

	    if ( -e "$fname"_ave+orig.BRIK ) then
	      rm -rf "$fname"_ave+*
	    endif




	    3dTstat -overwrite -prefix "$fname"_ave "$fname"'_mb+orig[0..$]'


	    3drefit -abuc "$fname"_ave+orig


	    3dcalc -datum float -a "$fname"'_mb+orig[0..$]' -b "$fname"_ave+orig -expr "((a-b)/b)*100" -overwrite -prefix "$fname"_mbn

	    if (-e "$fname"_mbnf+orig.HEAD ) then
	      rm -rf "$fname"_mbnf+orig.*
	    endif

	    3dFourier  -prefix "$fname"_mbnf -highpass .011 "$fname"_mbn+orig


	    ###### set the epi parent to the auto-warped anat ######

	    3drefit -apar anat+orig "$fname"_mbnf+orig


	    # ####                                                                  ####
	    # ########################## create csf and wm #############################
	    # ####                                                                  ####

	    set anatfile = anat
	    set masks = ( wm_mask csf_mask )
	    set regfiles = ( "$fname"_mbnf )


	    foreach regfile (${regfiles})

	        foreach maskname ( ${masks} )
	            if( -e ${regfile}_${maskname}r+orig.HEAD) then
	                rm ${regfile}_${maskname}r+orig.*
	            endif
	        end

	        3dfractionize -template ${regfile}+orig -input wm_mask+tlrc -warp ${anatfile}+tlrc -clip 0.1 -preserve -prefix ${regfile}_wm_maskr+tlrc
	        3dfractionize -template ${regfile}+orig -input csf_mask+tlrc -warp ${anatfile}+tlrc -clip 0.1 -preserve -prefix ${regfile}_csf_maskr+tlrc

	        foreach mask ( ${masks} )

	            if ( -e l${mask}.tc ) then
	                rm l${regfile}_${mask}.1D
	            endif
	            if ( -e r${mask}.tc ) then
	                rm r${regfile}_${mask}.1D
	            endif
	            if ( -e b${mask}.tc ) then
	                rm b${regfile}_${mask}.1D
	            endif

	            3dmaskave -mask ${regfile}_${mask}r+orig -quiet -mrange 1 1 ${regfile}+orig > l${regfile}_${mask}.1D
	            3dmaskave -mask ${regfile}_${mask}r+orig -quiet -mrange 2 2 ${regfile}+orig > r${regfile}_${mask}.1D
	            3dmaskave -mask ${regfile}_${mask}r+orig -quiet -mrange 1 2 ${regfile}+orig > b${regfile}_${mask}.1D

	        end
	    end

	    # regression vecs
	    mkdir processed_tcs
	    set regfiles = ( "$fname"_mbnf )
	    set masks = ( $ROI_MASKS )

	    foreach maskname ( ${masks} )
	        cp ${MASKS}/${maskname}+tlrc* .
	    end

	    foreach regfile (${regfiles} )

	        foreach maskname ( ${masks} )
	            if( -e ${regfile}_${maskname}r+orig.HEAD) then
	                rm ${regfile}_${maskname}r+orig.*
	            endif
	            3dfractionize -overwrite -template ${regfile}+orig -input ${maskname}+tlrc -preserve -warp anat+tlrc -clip 0.1  -prefix ${maskname}r+orig


	            if ( -e l${maskname}.tc ) then
	                rm l${regfile}_${maskname}.1D
	            endif
	            if ( -e r${maskname}.tc ) then
	                rm r${regfile}_${maskname}.1D
	            endif
	            if ( -e b${maskname}.tc ) then
	                rm b${regfile}_${maskname}.1D
	            endif

	            3dmaskave -mask ${maskname}r+orig -quiet -mrange 1 1 ${regfile}+orig > processed_tcs/l${regfile}_${maskname}.1D
	            3dmaskave -mask ${maskname}r+orig -quiet -mrange 2 2 ${regfile}+orig > processed_tcs/r${regfile}_${maskname}.1D
	            3dmaskave -mask ${maskname}r+orig -quiet -mrange 1 2 ${regfile}+orig > processed_tcs/b${regfile}_${maskname}.1D


	        end
	    end
	end
end