% resample a fiber group into N nodes for a set of subjects and calculate
% diffusion properties for each node (e.g., md, fa, etc.) and save out a
% .mat file with these measures.

clear all
close all

p = getCuePaths;
[subjects,gi] = getCueSubjects('dti');
% subjects={'zl150930','dw151003'}

dataDir = p.data;


% define fiber group to load
% method = 'conTrack';
method = 'mrtrix_fa';

fgMLabels = {'FA','MD','RD','AD'};


% left and/or right hemisphere?
LorR = ['L','R'];
% LorR = ['R'];

combineLR = 1; % 1 to combine L and R, otherwise, 0

seeds = {'DA','DA','DA','DA','DA'};
targets = {'nacc','nacc','nacc','caudate','putamen'};
versionStrs = {'belowAC_autoclean','aboveAC_autoclean','autoclean','autoclean','autoclean'};


% seeds = {'DA'};
% targets = {'nacc'};
% versionStrs = {'aboveAC_autoclean'};


% 
% seeds = {'DA','DA'};
% targets = {'caudate','putamen'};
% versionStrs = {'dil2_autoclean','dil2_autoclean'};

% fiber group file strings
inDir = fullfile(dataDir,'%s','fibers',method); %s: subject
inStr = '%s%s_%s%s_%s.mat'; %s: seed,lr,target,lr,versionStr

% out file name string
outDir = fullfile(dataDir,'fgMeasures',method);
outStr = '%s%s_%s%s_%s.mat'; %s: seed,lr,target,lr,versionStr


nNodes=100;

%% do it

j=1
for j=1:numel(targets) % target rois loop
    
    % get seed, target, and version string for this fg
    seed = seeds{j};
    target = targets{j};
    versionStr = versionStrs{j};
    
   
    for lr=LorR  % L/R loop
        
        fgName = sprintf(inStr,seed,lr,target,lr,versionStr); %  fg file name
        
        err_subs = {}; % keep track of which subjects throw an error on dtiCompute... function
        
        i=1
        for i = 1:numel(subjects)
            
            subject = subjects{i};
            
            fprintf(['\n\nworking on subject ',subject,'\n\n']);
            
            fgPath = fullfile(sprintf(inDir,subject),fgName);
            
            if ~exist(fgPath,'file')
                
                fprintf(['\nno fiber group found for subject ' subject '\n\n']);
                
                err_subs=[err_subs {subject}];
                eigVals(i,:,:) = nan(1,nNodes,3);
                fgMeasures{1}(i,:) = nan(1,nNodes);
                fgMeasures{2}(i,:) = nan(1,nNodes);
                fgMeasures{3}(i,:) = nan(1,nNodes);
                fgMeasures{4}(i,:) = nan(1,nNodes);
                
            else
                
                subj=load(fgPath);
                 
                fgMeasures{1}(i,:) = subj.fa;
                fgMeasures{2}(i,:) = subj.md;
                fgMeasures{3}(i,:) = subj.rd;
                fgMeasures{4}(i,:) = subj.ad;
                eigVals(i,:,:) = permute(subj.eigVals,[3 1 2]);
                SuperFibers(i)=subj.SuperFiber;
                
                clear subj
                
            end
            
        end % subjects
        
        
        %% save out fg measures
        
        if ~exist(outDir,'dir')
            mkdir(outDir)
        end
        
        outName = sprintf(outStr,seed,lr,target,lr,versionStr);
        outPath = fullfile(outDir,outName);
        
        if exist('gi','var')
            save(outPath,'subjects','gi','seed','target','lr',...
                'fgName','nNodes','fgMeasures','fgMLabels','SuperFibers','eigVals','err_subs');
        else
            save(outPath,'subjects','seed','target','lr',...
                'fgName','nNodes','fgMeasures','fgMLabels','SuperFibers','eigVals','err_subs');
        end
        
        fprintf(['\nsaved out file ' outName '\n\n']);
        
        clear fgMeasures SuperFibers eigVals
        
    end % L/R
    
end % targets


%% combine L and R

if combineLR
    
    for j=1:numel(targets) % target rois loop
        
        % get seed, target, and version string for this fg
        seed = seeds{j};
        target = targets{j};
        versionStr = versionStrs{j};
        
        outNameL = sprintf(outStr,seed,'L',target,'L',versionStr);
        outNameR = sprintf(outStr,seed,'R',target,'R',versionStr);
        outNameLR = sprintf(outStr,seed,'LR',target,'LR',versionStr);
        
        combineLRFgMeasures(fullfile(outDir,outNameL),fullfile(outDir,outNameR),...
            fullfile(outDir,outNameLR));
        
         fprintf(['\nsaved out file ' outNameLR '\n\n']);
    end
    
end