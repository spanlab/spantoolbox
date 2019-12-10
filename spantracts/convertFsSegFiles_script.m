% convertFsSegFiles_script
% -------------------------------------------------------------------------
% usage: this script takes segmentation files made using freesurfer in
% .mgz format and converts them to nifti files. Also changes some of the
% segmentation indices for better functionality with mr vista software.

% the script takes in files created from Freesurfer's "recon-all" call, and
% converts them to nifti files.


% t1.class.nii.gz - segmentation file with the following indices:
% white matter L: 3
% white matter R: 4
% gray matter L: 5
% gray matter R: 6
% unlabeled: either 1 or 0

% aparc_aseg - segmentation of cortex and sub-cortical structures. See here
% for look up table of segmentation indices:
%     https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all
close all


p=getFmrieatPaths;
subjects=getFmrieatSubjects();

dataDir = p.derivatives;

!source $FREESURFER_HOME/SetUpFreeSurfer.sh
fshome = getenv('FREESURFER_HOME');
% setenv('FREESURFER_HOME',fshome);  % this to tell where FS folder is


for s=1:numel(subjects)
    
    subject = subjects{s};
    
    fprintf(['\n\nworking on subject ' subject '...\n\n']);
    
    
    inDir = ['/usr/local/freesurfer/subjects/' subject '/mri']; % freesurfer subject mri dir
    subjDir = ['/home/span/lvta/fmrieat/derivatives/' subject ];
    outDir = [subjDir '/anat_proc']; % dir for out nifti files
    
    
    %% do it
    
    if ~exist(inDir,'dir')
        fprintf(['\nskipping subject ' subject ' because no freesurfer file found...\n\n']);
        
    else
        
        % make out directory if it doesnt already exist
        if ~exist(outDir, 'dir')
            mkdir(outDir)
        end
        
        % Convert freesurfer t1 to nifti
        cmd = [fshome '/bin/mri_convert --out_orientation RAS -i ' inDir '/T1.mgz -o ' outDir '/t1_fs.nii.gz'];
        unix_wrapper(cmd);
        
        
        % Convert ribbon.mgz to a nifti class file
        outfile     = [outDir '/t1_class.nii.gz'];
        resample_type = 'weighted';
        fillWithCSF = true;
        cmd = [fshome '/bin/mri_convert --out_orientation RAS -rt ' resample_type ' -i ',...
            inDir '/ribbon.mgz -o ' outfile];
        unix_wrapper(cmd);
        
        
        % Convert aparc+aseg.mgz file
        outfile2     = [outDir '/aparc+aseg.nii.gz'];
        resample_type = 'weighted';
        cmd = [fshome '/bin/mri_convert --out_orientation RAS -rt ' resample_type ' -i ',...
            inDir '/aparc+aseg.mgz -o ' outfile2];
        unix_wrapper(cmd);
        
        
        % make symbolic link to subject's fs t1 file in main subject dir
%         cmd = ['ln -s ' outDir '/t1_fs.nii.gz ' subjDir '/t1.nii.gz'];
%         unix_wrapper(cmd);
        
        
        
        %% Convert freesurfer label values to itkGray label values
        % We want to convert
        %   Left white:   2 => 3
        %   Left gray:    3 => 5
        %   Right white: 41 => 4
        %   Right gray:  42 => 6
        %   unlabeled:    0 => 0 (if fillWithCSF == 0) or 1 (if fillWithCSF == 1)
        
        % read in the nifti
        ni = niftiRead(outfile);
        
        % check that we have the expected values in the ribbon file
        vals = sort(unique(ni.data(:)));
        if ~isequal(vals, [0 2 3 41 42]')
            warning('The values in the ribbon file - %s - do no match the expected values [2 3 41 42]. Proceeding anyway...') %#ok<WNTAG>
        end
        
        % map the replacement values
        invals  = [3 2 41 42];
        outvals = [5 3  4  6];
        labels  = {'L Gray', 'L White', 'R White', 'R Gray'};
        
        fprintf('\n\n****************\nConverting voxels....\n\n');
        for ii = 1:4;
            inds = ni.data == invals(ii);
            ni.data(inds) = outvals(ii);
            fprintf('Number of %s voxels \t= %d\n', labels{ii}, sum(inds(:)));
        end
        
        if fillWithCSF,
            ni.data(ni.data == 0) = 1;
        end
        
        % write out the nifti
        writeFileNifti(ni)
        
        % done.
        fprintf('\n\ndone.\n');
        
        
        % also save out a wm mask
        fprintf('\n\nsaving out a white matter mask....\n\n');
        
        wmmask = zeros(size(ni.data));
        wmmask(ni.data==3)=1;  wmmask(ni.data==4)=1;
        
        wmNi =ni;
        wmNi.fname = fullfile(outDir,'wm_mask.nii.gz');
        wmNi.data = wmmask;
        writeFileNifti(wmNi);
        
        fprintf('\n\ndone.\n');
    end
    
    fprintf(['done with subject ' subject '.\n\n']);
end
