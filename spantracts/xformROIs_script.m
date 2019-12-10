% script to xform ROIs from tlrc group space to subjects' % t1-acpc aligned
% native space

clear all
close all


[p,task,subjects,gi]=whichCueSubjects('stim','');
dataDir = p.data;

inRoiFile = fullfile(dataDir,'ROIs','%s.nii.gz'); % directory with tlrc space ROIs
roiNames = {'DA','PVT'};
% roiNames = {'mpfc8mmL','mpfc8mmR'};

outRoiFile = fullfile(dataDir,'%s','ROIs','%s.nii.gz'); % %s is subject & roiName

refFile = fullfile(dataDir,'%s','t1.nii.gz'); % reference file - out roi will be in this space

xform_aff = fullfile(dataDir,'%s','t1','t12tlrc_xform_Affine.txt'); % acpc aligned t1 > tlrc space affine xform (estimated with ANTs)

xform_invWarp = fullfile(dataDir,'%s','t1','t12tlrc_xform_InverseWarp.nii.gz'); % acpc aligned t1 > tlrc space affine xform (estimated with ANTs)



%% do it

for j=1:numel(roiNames)
    
    this_inRoiFile = sprintf(inRoiFile,roiNames{j});
    
    for i=1:numel(subjects)
        
        subject = subjects{i};
        
        fprintf(['\n\nworking on subject ' subject '...\n\n']);
        
        this_outRoiFile = sprintf(outRoiFile,subject,roiNames{j});
        
        this_refFile = sprintf(refFile,subject);
        
        this_xform_aff = sprintf(xform_aff,subject);
        
        this_xform_invWarp = sprintf(xform_invWarp,subject);
        
        
        % xform tlrc roi to subject's native space using ANTs inverse xform
        roi = xformInvANTs(this_inRoiFile,this_outRoiFile,this_refFile,this_xform_aff,this_xform_invWarp);
        
        % binarize to make it an roi mask
        roi.data(roi.data<.5)=0;
        roi.data(roi.data>=.5)=1;
        
        % save binary mask
        writeFileNifti(roi);
        
        % save out L and R versions
        [roiL,roiR]=roiSplitLR(roi,1);
        
        % save out .mat versions of L and R ROIs for contrack
        roiNiftiToMat(roiL,1);
        roiNiftiToMat(roiR,1);
        
    end
    
end






