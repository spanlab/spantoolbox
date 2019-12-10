function outCoords = xformCoordsANTs(inCoords,xform_aff,xform_invWarp)
% -------------------------------------------------------------------------
% usage: this function calls ANTs software to transform a moving file to a
% reference file 
% 
% INPUT:
%   inCoords - Mx3 matrix of coordinates in real space; each row is a 3d coord
%              OR a filepath that contains coords in rows (i.e., each row
%              has an x,y,z coordinate)
%   xform_aff - filename of affine xform from inCoords to outCoords space
%   xform_invWarp (optional) - filename of inverse warp xform from inCoords to outCoords space
% 
% OUTPUT:
%   outCoords - xformed coords
% 
% NOTES: ANTs command for performing this has a couple weird aspects: 
%  for whatever reason, it performs the xforms using the *inverse* of the
%  affine and warps that xform inCoords to outCoords space. Also, they
%  require coords to be in a csv file and in ITK style (LPS
%   orientation). So, these things must be accomodated. 

% see here for more info: http://manpages.org/antsapplytransformstopoints
% 
% author: Kelly, kelhennigan@gmail.com, 16-Dec-2016

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 

if notDefined('xform_invWarp')
    xform_invWarp = '';
end

% if inCoords is a file name, load it
if isstr(inCoords)
    inCoords=dlmread(inCoords);
end

% in case coords appear to be listed in columns, flip them to be in rows
if size(inCoords,2)~=3
   if size(inCoords,1)==3
       inCoords=inCoords';
   else
    error('inCoords must be 3d.')
   end
end


% define temporary files for writing out inCoords & outCoords
inFile = [tempname '.csv']; 
outFile = [tempname '.csv']; 


%%%%%%%%%%  convert inCoords to ITK style (LPS format)
inCoordsITK = [inCoords(:,1:2).*-1 inCoords(:,3)];

%%%%%%%%%% write out inCoords to temp file
csvwrite_with_headers(inFile,[inCoordsITK zeros(size(inCoordsITK,1),1)],{'x','y','z','t'})
% csvread(inFile,1,0)


%%%%%%%%% get part of the command that specifies xforms
xform_str = [' -t [' xform_aff ',1]'];
if ~isempty(xform_invWarp) % add inv warp xform first, if given
   xform_str = [' -t ' xform_invWarp xform_str];
end


%%%%%%%%%  add ants directory to path 
system('export PATH=$PATH:~/repos/antsbin/bin');

% note: for some reason exporting ants path isn't working here - 
% the antsApplyTransformsToPoints command isn't found,
% even though it works for xformANTS and xformInvANTS functions. So, for
% now just define the ants directory and explicitly add that to the
% command:
antspath = '~/repos/antsbin/bin';

%%%%%%%%%  define and execute ants command
cmd = [antspath '/antsApplyTransformsToPoints -d 3 -i ' inFile ' -o ' outFile xform_str];
cmd
system(cmd);


%%%%%%%%%  read in xformed coords
outCoordsITK = csvread(outFile,1,0);


%%%%%%%%%%  convert back to nifti (as opposed to ITK) format 
outCoords = [outCoordsITK(:,1:2).*-1 outCoordsITK(:,3)];



