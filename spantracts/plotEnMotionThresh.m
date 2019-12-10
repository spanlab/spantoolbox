function figH = plotEnMotionThresh(en,en_thresh,ts,ts_str)
% -------------------------------------------------------------------------
% usage: say a little about the function's purpose and use here
%
% INPUT:
%   en - euclidean norm
%   en_thresh - threshold for determining "bad" movement
%   ts (optional) - time series from the scan. Plotting this along with the
%      euclideam norm can help determine how movement effects the MR signal
%   ts_str (optional) - string identifying time series ts (e.g., 'nacc')

% OUTPUT:
%   figH - figure handle

% NOTES:

% here's a  excerpt from AFNI documentation regarding the use of euclidean
% norm, found here:
% https://afni.nimh.nih.gov/pub/dist/doc/program_help/1d_tool.py.html

% Consideration of the euclidean_norm method:
%
%            For censoring, the euclidean_norm method is used (sqrt(sum squares)).
%            This combines rotations (in degrees) with shifts (in mm) as if they
%            had the same weight.
%
%            Note that assuming rotations are about the center of mass (which
%            should produce a minimum average distance), then the average arc
%            length (averaged over the brain mask) of a voxel rotated by 1 degree
%            (about the CM) is the following (for the given datasets):
%
%               TT_N27+tlrc:        0.967 mm (average radius = 55.43 mm)
%               MNIa_caez_N27+tlrc: 1.042 mm (average radius = 59.69 mm)
%               MNI_avg152T1+tlrc:  1.088 mm (average radius = 62.32 mm)
%
%            The point of these numbers is to suggest that equating degrees and
%            mm should be fine.  The average distance caused by a 1 degree
%            rotation is very close to 1 mm (in an adult human).
%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% if ts isn't given, define it as empty
if ~exist('ts','var')
    ts ='';
end
if notDefined('ts_str')
    ts_str ='MR';
end


[max_en,max_TR]=max(en);


% plot
figH = figure('Visible','off');
% figH = figure
set(gcf,'Color','w','InvertHardCopy','off','PaperPositionMode','auto');

% make 2 plots if ts is given, otherwise plot just the euclidean norm
if ~isempty(ts)
    subplot(2,1,1)
end

hold on
plot(en,'color',[.15 .55 .82],'linewidth',1.5)
set(gca,'box','off');
plot(ones(numel(en),1).*en_thresh,'color',[.86 .2 .18]);
ylabel('head motion (in ~mm units)','FontSize',12)

title(sprintf('max movement: ~%.2f mm, at TR=%d',max_en,max_TR),'FontSize',14);

if ~isempty(ts)
    subplot(2,1,2)
    plot(ts,'color',[.16 .63 .6],'linewidth',1.5)
    set(gca,'box','off');
    ylabel('MR signal','FontSize',12)
    xlabel('TRs','FontSize',12)
    title([ts_str ' time series'],'FontSize',14)
end

