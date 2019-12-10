
function figH = plotMotionParams(mp)
% -------------------------------------------------------------------------
% usage: plot head movement parameters
% 
% INPUT:
%   mp - nVols x 6 matrix with the following columns:
%        dx - displacement along x-axis
%        dy - " " y-axis
%        dz - " " z-axis
%        roll - rotation along z-axis
%        pitch - rotation along x-axis
%        yaw - rotation along y-axis


% OUTPUT:
%     figH - figure handle

% 
% author: Kelly, kelhennigan@gmail.com, 07-Jan-2016

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% colors
c = [    0.7961    0.2941    0.0863
    0.5216    0.6000         0
    0.1490    0.5451    0.8235
    0.8627    0.1961    0.1843
    0.7098    0.5373         0
    0.1647    0.6314    0.5961];

% define figure 
figH = figure('Visible','off');
% figH = figure;
set(gcf,'Color','w','InvertHardCopy','off','PaperPositionMode','auto');


% subplot with motion displacement params
subplot(2,1,1); hold on
title('motion estimates')
for i=1:3
    plot(mp(:,i),'color',c(i,:),'linewidth',1.2);
end
ylabel('translation (mm)')
legend({'x','y','z'});

% subplot with motion rotation params
subplot(2,1,2); hold on
for i=4:6
    plot(mp(:,i),'color',c(i,:),'linewidth',1.2);
end
% title('Rotation')
ylabel('rotation (degrees)')
xlabel('acquired image number')
legend({'roll','pitch','yaw'});



