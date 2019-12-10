% this script does the following:

% import fibers defined from intersecting 2 rois,
% reorients fibers so they all start from roi1 (roi1),
% will keep only left or right fibers if desired,
% keeps only fibers
% clean the groups using AFQ_removeFiberOutliers(),
% and saves out cleaned L, R fiber groups as well as both L and R merged
% together.
% also saves out a .mat file that has info on the parameters used to
% determine outliers in the cleaning procedure.


% define variables, directories, etc.
clear all
close all


% get experiment-specific paths and cd to main data directory
getCuePaths();
[p,task,subjects,gi]=whichCueSubjects('stim','');

dataDir = p.data;
mainfigDir=p.figures_dti;

seed = 'DA';  % define seed roi
% seed = 'nacc';

targets=input('target name(s): ','s');
targets=splitstring(targets);
% targets = {'caudate','putamen','nacc'};


% LorR = ['L'];
LorR = upper(input('L, R, or both? ','s'));
if strcmp(LorR,'BOTH')
    LorR='LR';
end


savePlots = 1; % 1 to save out plots, otherwise 0

% method = 'conTrack';
method = 'mrtrix_fa';
fstr = '';


% out file name for pruned fibers
outFgStr = [seed '%s_%s%s' fstr '_autoclean']; %s: LorR, target, LorR

plotToScreen = 0; % don't plot to screen

saveOutFGMeasures=1; % 1 to compute and save out fiber group measures (fa,md,etc.), otherwise, 0
dt6file = 'dti96trilin/dt6.mat'; % filepath relative to subject's directory

%% get pruning params based on tractography method

switch method
    
    case 'conTrack'
        
        fgStr = ['scoredFG_' seed '%s_%s%s_top1000.pdb']; %s: LorR, target, LorR
        box_thresh = 8;
        maxIter = 5;
        
    case {'mrtrix','mrtrix_orig','mrtrix_fa','mrtrix_tournier'}
        
        fgStr = [seed '%s_%s%s' fstr '.tck']; % %s: target, LorR
        box_thresh = 5;
        maxIter = 5;  %
        
end

% additional non-method specific pruning params
maxDist=4; % threshold for eliminating based on mahalanobis distance
maxLen=4;  % " " for pathway length
numNodes=100;
M='mean';
count = 0;
show = 0; % 1 to plot each iteration, 0 otherwise


%% DO IT


for j=1:numel(targets)
    
    target = targets{j};
    
    for lr=LorR
        
        fgName=sprintf(fgStr,lr,target,lr);
        outFgName = sprintf(outFgStr,lr,target,lr);
        
        if savePlots
            figDir = fullfile(mainfigDir,'cleaned_fgs',method,outFgName);
            if ~exist(figDir,'dir')
                mkdir(figDir);
            end
        end
        
        
        fprintf('\n\n working on %s fibers for roi %s%s...\n\n',method,target,lr);
        
        i=1
        for i=1:numel(subjects)
            
            subject = subjects{i};
            fprintf(['\n\nworking on subject ' subject '...\n\n'])
            subjDir = fullfile(p.data,subject);
            cd(subjDir);
            
            % load seed and target rois
            roi1 = roiNiftiToMat(['ROIs/' seed lr '.nii.gz']);
            roi2 = roiNiftiToMat(['ROIs/' target lr '.nii.gz']);
            
            
            % load fiber groups
            cd(fullfile(subjDir,'fibers',method));
            if exist(fgName,'file')
                fg = fgRead(fgName);
                
                
                if numel(fg.fibers)<2
                    
                    fprintf(['\n\nfiber group is empty for subject, ' subject '\n\n']);
                    
                else
                    
                    % reorient fibers so they all start in DA ROI
                    [fg,flipped] = AFQ_ReorientFibers(fg,roi1,roi2);
                    
                    % remove crazy fibers that deviate outside area defined by box_thresh
                    fg = pruneFG(fg,roi1,roi2,0,box_thresh);
                    
                    % remove outliers and save out cleaned fiber group
                    if numel(fg.fibers)<2
                        
                        fprintf(['\n\nfiber group is empty for subject, ' subject '\n\n']);
                        
                    else
                        
                        [~, keep]=AFQ_removeFiberOutliers(fg,...
                            maxDist,maxLen,numNodes,M,count,maxIter,show);     % remove outlier fibers
                        
                        fprintf('\n\n final # of %s cleaned fibers: %d\n\n',fg.name, numel(find(keep)));
                        
                        cleanfg = getSubFG(fg,find(keep),outFgName);
                        
                        nFibers_clean(i,1) = numel(cleanfg.fibers); % keep track of the final # of fibers
                        
                        
                        AFQ_RenderFibers(cleanfg,'tubes',0,'color',[1 0 0],'plottoscreen',plotToScreen);
                        title(gca,subject);
                        if savePlots
                            print(gcf,'-dpng','-r300',fullfile(figDir,subject));
                        end
                        
                        mtrExportFibers(cleanfg,cleanfg.name);  % save out cleaned fibers
                        
                        close all
                        
                        if saveOutFGMeasures
                            dt = dtiLoadDt6(fullfile(dataDir,subject,dt6file));
                            saveOutSubjFGMeasures(cleanfg,dt,roi1,roi2,pwd);
                        end
                        
                        
                    end % empty fibers
                    
                end % empty fibers
                
            end % if fg exists
            
        end % subjects
        
    end % LorR
    
end % targets
