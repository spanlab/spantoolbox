#!/bin/bash

# `which Xvfb` :1 -screen 0 1024x768x24

# set DISPLAY=1:0

# export DISPLAY

mkdir full_snapshots
afni -yesplugouts & sleep 4
plugout_drive -com 'OPEN_WINDOW A.axialimage mont=8x8:2 geom=600x600+800+600' \
-com "SWITCH_UNDERLAY TT_N27+tlrc" \
-quit
for overlay in cue choice feedback buy_vs_not win_lose questions no_bet_down_vs_up
 do
 outputName=`basename $overlay .nii`
 plugout_drive -com "SET_FUNC_RANGE A.10" \
 -com "SWITCH_OVERLAY ${overlay}_z" \
 -com 'SET_THRESHOLD A.2575 1' \
 -com "SET_SUBBRICKS A -1 1 1" \
 -com 'SET_FUNC_RANGE 10' \
 -com 'SET_XHAIRS OFF' \
 -com 'SET_FUNC_RESAM A.NN.Cu' \
 -com 'SET_PBAR_ALL A.-9 1.000=yellow .386973=yell-oran .325670=orange .25000=red .05000=none -.05000=dk-blue -.250000=lt-blue1 -.325670=blue-cyan -.394636=cyan' \
  -com "SAVE_JPEG A.axialimage full_snapshots/${outputName}_full_axial_snapshot.jpg" \
  -quit
  done
  plugout_drive -com "QUIT"

afni -yesplugouts & sleep 4
plugout_drive -com 'OPEN_WINDOW A.sagittalimage mont=8x8:2 geom=600x600+800+600' \
-com "SWITCH_UNDERLAY TT_N27+tlrc" \
-quit
for overlay in cue choice feedback buy_vs_not win_lose questions no_bet_down_vs_up
 do
 outputName=`basename $overlay .nii`
 plugout_drive -com "SET_FUNC_RANGE A.10" \
 -com "SWITCH_OVERLAY ${overlay}_z" \
 -com 'SET_THRESHOLD A.2575 1' \
 -com "SET_SUBBRICKS A -1 1 1" \
 -com 'SET_FUNC_RANGE 10' \
 -com 'SET_XHAIRS OFF' \
 -com 'SET_FUNC_RESAM A.NN.Cu' \
 -com 'SET_PBAR_ALL A.-9 1.000=yellow .386973=yell-oran .325670=orange .25000=red .05000=none -.05000=dk-blue -.250000=lt-blue1 -.325670=blue-cyan -.394636=cyan' \
  -com "SAVE_JPEG A.sagittalimage full_snapshots/${outputName}_full_sagittal_snapshot.jpg" \
  -quit
  done
  plugout_drive -com "QUIT"


afni -yesplugouts & sleep 4
plugout_drive -com 'OPEN_WINDOW A.coronalimage mont=8x8:2 geom=600x600+800+600' \
-com "SWITCH_UNDERLAY TT_N27+tlrc" \
-quit
for overlay in cue choice feedback buy_vs_not win_lose questions no_bet_down_vs_up
do
 outputName=`basename $overlay .nii`
 plugout_drive -com "SET_FUNC_RANGE A.10" \
 -com "SWITCH_OVERLAY ${overlay}_z" \
 -com 'SET_THRESHOLD A.2575 1' \
 -com "SET_SUBBRICKS A -1 1 1" \
 -com 'SET_FUNC_RANGE 10' \
 -com 'SET_FUNC_RESAM A.NN.Cu' \
 -com 'SET_XHAIRS OFF' \
 -com 'SET_PBAR_ALL A.-9 1.000=yellow .386973=yell-oran .325670=orange .25000=red .05000=none -.05000=dk-blue -.250000=lt-blue1 -.325670=blue-cyan -.394636=cyan' \
  -com "SAVE_JPEG A.coronalimage full_snapshots/${outputName}_full_coronal_snapshot.jpg" \
  -quit
done
plugout_drive -com "QUIT"


cd full_snapshots
