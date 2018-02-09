#!/bin/csh
# For a normal set of vois and a set of whole_brain images, render to image. 

set underlay = TT_N27.nii

foreach overlay ( choice_z feedback_z inflection_z )

    # Left Nacc
    
    set outfile = nacc8mml_${overlay}

    @afni_image -u TT_N27.nii -o ${overlay}+tlrc -dxyz 10 -12 -2 \
                -prefix $outfile -no-montage

    # Right Nacc 
    set outfile = nacc8mmr_${overlay}

    @afni_image -u TT_N27.nii -o ${overlay}+tlrc -dxyz -10 -12 -2 \
                -prefix $outfile -no-montage

    # Left mpfc
    
    set outfile = mpfcl_${overlay}

    @afni_image -u TT_N27.nii -o ${overlay}+tlrc -dxyz 4 -47 0 \
                -prefix $outfile -no-montage

    # Right mpfc 
    set outfile = mpfcr_${overlay}

    @afni_image -u TT_N27.nii -o ${overlay}+tlrc -dxyz -4 -47 0 \
                -prefix $outfile -no-montage

    # Left Insula - Desai 
    
    set outfile = desai_insl_${overlay}

    @afni_image -u TT_N27.nii -o ${overlay}+tlrc -dxyz 32 -30 -2 \
                -prefix $outfile -no-montage

    # Right Insula - Desai
    set outfile = desai_insr_${overlay}

    @afni_image -u TT_N27.nii -o ${overlay}+tlrc -dxyz -32 -30 -2 \
                -prefix $outfile -no-montage
end


