% script to save out csv files with fg measures

clear all
close all

fgName = 'DAL_putamenL_autoclean';

method = 'conTrack';

fgPath = fullfile('/Users/kelly/cueexp/data/fgMeasures',method,[fgName '.mat']);


%% 

load(fgPath)


% define out vars
out_subjects = repmat(subjects,numel(fgMLabels),1);

out_fgName = repmat([fgName '_' method],numel(out_subjects),1);

out_fgMName = [];
for i=1:numel(fgMLabels)
    out_fgMName = [out_fgMName; repmat(lower(fgMLabels{i}),numel(subjects),1)];
end

out_fgMeasure = array2table(cell2mat(fgMeasures'));

T = [table(out_subjects,out_fgName,out_fgMName) out_fgMeasure];
    
% save out
outPath = fullfile('/Users/kelly/Google Drive/cuefmri/fg_measures/', [fgName '_' method '.csv']);
writetable(T,outPath,'WriteVariableNames',0); 

