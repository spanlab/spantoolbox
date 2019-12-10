function xformed_file = xformANTs(inFile,outFile,xform_aff,xform_warp)
% -------------------------------------------------------------------------
% usage: this function calls ANTs software to transform a moving file to a
% reference file 
% 
% INPUT:
%   inFile - filepath to data to be xformed
%   outFile - name for saving out xformed data. 
%   xform_aff - filepath to affine text file, estimated with ANTs
%   xform_warp - filepath to warp nifti file, estimated with ANTs

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
cmd = ['WarpImageMultiTransform 3 ' inFile ' ' outFile ' ' xform_warp ' ' xform_aff];
system(cmd)


%%%%%%%%% if output is desired, load xformed file and return it
if nargout==1
    xformed_file = niftiRead(outFile);
end
