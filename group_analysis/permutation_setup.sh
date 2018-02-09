#! /bin/csh
#nb 10/16/15
#

#################### Set user (via proxy) defined variables: #################
###
set regfile = zstock_reg_csfwm_masked
set resampdim = 2.9
#rp160214 rp160215 ew160226
set subjects = ( lc160210 rp160214 rp160215 fv160223 mp160223 as160224 ew160226 ar160321 aa160408 mk160409 rf160409 bg160410 rm160410 mm160410 mm160411 kl160412 jk160415 lt160415 cm160416 ol160416 at160417 lc160417 kk160420 cl160422 sp160423 sh160424 ar160429 hh160430 bc160430 jr160430 rw160501 jr160501 yw160502 ez160504 kw160505 mt160514 gs160514 ac160515 ry160515 )
set outfiles = ( cue choice feedback buy_vs_not win_lose questions no_bet_down_vs_up  )
set parentfile = anat
set stats = ( 25 28 31 34 37 40 43 )
###
########################## talairach warp datasets: ##########################

foreach sub ( ${subjects} )
        cd /Users/span/projects/stockmri/subjects/${sub}
        if ( -e ${regfile}+tlrc.BRIK ) then
                rm -rf ${regfile}+tlrc.*
        endif
        adwarp -apar ${parentfile}+tlrc -dpar ${regfile}+orig -dxyz ${resampdim} -prefix ${regfile}
end

#########################       run the ttest:      ##########################

@ count = 1

# rm -rf  /Users/span/projects/stockmri/scripts/permutation_test_stock
# mkdir /Users/span/projects/stockmri/scripts/permutation_test_stock

cd /Users/span/projects/stockmri/scripts/permutation_test_stock

foreach outfile (${outfiles})

        set stat = $stats[${count}]
        @ count = $count + 1

	echo ""
	pwd
	echo ""
        echo "******* ${outfile} (${stat}) *******"


	3dtcat -prefix ./${outfile}_coefs \
                "/Users/span/projects/stockmri/subjects/lc160210/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/rp160214/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/rp160215/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/fv160223/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/mp160223/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/as160224/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/ew160226/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/ar160321/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/aa160408/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/mk160409/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/rf160409/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/bg160410/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/rm160410/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/mm160410/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/mm160411/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/kl160412/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/jk160415/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/lt160415/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/cm160416/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/ol160416/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/at160417/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/lc160417/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/kk160420/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/cl160422/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/sp160423/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/sh160424/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/ar160429/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/hh160430/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/bc160430/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/jr160430/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/rw160501/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/jr160501/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/yw160502/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/ez160504/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/kw160505/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/mt160514/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/gs160514/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/ac160515/zstock_reg_csfwm_masked+tlrc[${stat}]" \
                "/Users/span/projects/stockmri/subjects/ry160515/zstock_reg_csfwm_masked+tlrc[${stat}]"


        3dAFNItoNIFTI ${outfile}_coefs+tlrc


end

rm *tlrc*
cp ~/abin/TT_N27.nii  .



