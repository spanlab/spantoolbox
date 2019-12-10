function xformed_file = xformInvANTs(inFile,outFile,refFile,xform_aff,xform_invWarp)
% -------------------------------------------------------------------------
% usage: this function calls ANTs software to transform a moving file to a
% reference file using an inverse transform
% 
% INPUT:
%   inFile - filepath to data to be xformed
%   outFile - name for saving out xformed data. 
%   refFile - reference file; xformed data will take this file's dimensions
%   xform_aff - filepath to affine text file, estimated with ANTs
%   xform_invWarp - filepath to inverse warp nifti file, estimated with ANTs

% 
% OUTPUT:
%   xformed_file - will return loaded nifti outFile, but only if output is desired
% 
% NOTES:
% 
% author: Kelly, kelhennigan@gmail.com, 16-Dec-2016

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 
		

%%%%%%%%%  add ants directory to path
system('export PATH=$PATH:~/repos/antsbin/bin')


%%%%%%%%% ANTs command for applying an xform
cmd = ['WarpImageMultiTransform 3 ' inFile ' ' outFile ' -R ' refFile ' -i ' xform_aff ' ' xform_invWarp];
system(cmd)


%%%%%%%%% if output is desired, load xformed file and return it
if nargout==1
    xformed_file = niftiRead(outFile);
end
