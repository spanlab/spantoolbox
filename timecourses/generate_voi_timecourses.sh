#!/bin/csh 
# warp and dump out timecourses for volumes o finterest(functionally defined)
# by knutson et al (2004)
# last modified by nb 1/18
#

set anatfile = anat
set masks = ( nacc8mm  mpfc ins antins_desai_mpm nacc_desai_mpm caudate )

set regfiles = ( stock_mbnf skew_mbnf )
set root = /Users/span/projects/stock/voi/voi_cvs/stock_2/stock_2_subjects.txt

foreach subject (  `cat  /Users/span/projects/stock/voi/voi_csv/subjects.txt` )   
    cd ${root}/subjects/${subject}*  
    echo masking ${subject}
    

    foreach regfile (${regfiles})
        mkdir ${regfile}_timecourse

        foreach mask ( ${masks} )

            3dfractionize -overwrite -template ${regfile}+orig -input ${root}/masks/${mask}+tlrc -warp ${anatfile}+tlrc -clip 0.1 -preserve -prefix ${mask}r+tlrc
            
            if ( -e l${mask}.tc ) then
                rm l${regfile}_${mask}.1D
            endif
            if ( -e r${mask}.tc ) then
                rm r${regfile}_${mask}.1D
            endif
            if ( -e b${mask}.tc ) then
                rm b${regfile}_${mask}.1D
            endif

            3dmaskave -mask ${mask}r+orig -quiet -mrange 1 1 ${regfile}+orig > ${regfile}_timecourse/l${regfile}_${mask}.1D
            3dmaskave -mask ${mask}r+orig -quiet -mrange 2 2 ${regfile}+orig > ${regfile}_timecourse/r${regfile}_${mask}.1D
            3dmaskave -mask ${mask}r+orig -quiet -mrange 1 2 ${regfile}+orig > ${regfile}_timecourse/b${regfile}_${mask}.1D
        end
        
    end
end
