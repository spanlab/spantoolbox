#! /bin/csh

set outfiles = ( cue choice feedback buy_vs_not win_lose questions no_bet_down_vs_up  )

@ count = 1

cd permutation_test_stock
foreach outfile (${outfiles})

    @ count = $count + 1

    echo ""
    echo ""
    echo "******* Running One-sample ttest permutation test: ${outfile}  *******"

    RandomiseGroupLevel ${outfile}_coefs.nii -groupmean -output ${outfile}_perm_pval.nii

end

cp ~/abin/TT_N27.nii  .
