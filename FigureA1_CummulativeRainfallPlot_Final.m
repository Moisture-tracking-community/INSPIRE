%% DEFINING VARIABLES ==================================================
% Defining paths and directories --------------------------------------
outdir = '/Users/andrea/OneDrive - UNSW/';
dirfig = [outdir,'CONFERENCES/MOISTURE_WORKSHOP2024/FIGURES/'];
dirdata = [outdir,'CONFERENCES/MOISTURE_WORKSHOP2024/DATA/'];
timestamp = {'Jan','Feb','Mar','Apr','May','Jun','Jul',...
    'Aug','Sep','Oct','Nov','Dec'};
months = char(timestamp); 
daymon = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];


%% LOADING FILES (ERA5 daily sum precipitation data) ===================

% Australian Case (22-28 February 2022) ================================
Aus = getnc([dirdata,'Aus_daily_rainfall_1940_2023.nc'],'Average_daily_rainfall');
timera = timenc([dirdata,'Aus_daily_rainfall_1940_2023.nc']);
Ausevent = getnc([dirdata,'Aus_daily_rainfall_event.nc'],'Daily_rainfall');
Auseventtime = timenc([dirdata,'Aus_daily_rainfall_event.nc'],'time');
% Full years
LastDec = find(timera(:,2)==12);
years = timera(1,1):timera(LastDec(end),1);
% Removing leap day (29 Feb) to have exactly 84 years ------------------
timenew = timera;
timenew(timera(:,2)==2 & timera(:,3)==29,:) = [];
Aus(timera(:,2)==2 & timera(:,3)==29,:) = []; 
% Calculating cummulative precipitation --------------------------------
Auspre = reshape(Aus,365,length(Aus)/365);
Ausprecum = cumsum(Auspre);      

% Pakistan Case (10-24 August 2022) ====================================
Pak = getnc([dirdata,'Pak_daily_rainfall_1940_2023.nc'],'Average_daily_rainfall');
Pakevent = getnc([dirdata,'Pak_daily_rainfall_event.nc'],'Daily_rainfall');
Pakeventtime = timenc([dirdata,'Pak_daily_rainfall_event.nc'],'time');
% Removing leap day (29 Feb) to have exactly 84 years ------------------
Pak(timera(:,2)==2 & timera(:,3)==29,:) = []; 
% Calculating cummulative precipitation --------------------------------
Pakpre = reshape(Pak,365,length(Pak)/365);
Pakprecum = cumsum(Pakpre);      

% Scotland Case (6-8 October 2023) =====================================
Scot = getnc([dirdata,'Scot_daily_rainfall_1940_2023.nc'],'Average_daily_rainfall');
Scotevent = getnc([dirdata,'Scot_daily_rainfall_event.nc'],'Daily_rainfall');
Scoteventtime = timenc([dirdata,'Scot_daily_rainfall_event.nc'],'time');
% Removing leap day (29 Feb) to have exactly 84 years ------------------
Scot(timera(:,2)==2 & timera(:,3)==29,:) = []; 
% Calculating cummulative precipitation --------------------------------
Scotpre = reshape(Scot,365,length(Scot)/365);
Scotprecum = cumsum(Scotpre);      

%% Finding the dates of extreme events =================================
% 15 days for Pakistan
Pakyr = 2022;
Pakday1 = find(timera(:,2)==Pakeventtime(1,2) & timera(:,3)==Pakeventtime(1,3),1);
Pakday2 = find(timera(:,2)==Pakeventtime(end,2) & timera(:,3)==Pakeventtime(end,3),1);
% 7 days for Australia
Ausyr = 2022;
Ausday1 = find(timera(:,2)==Auseventtime(1,2) & timera(:,3)==Auseventtime(1,3),1);
Ausday2 = find(timera(:,2)==Auseventtime(end,2) & timera(:,3)==Auseventtime(end,3),1);
% 3 days for Scotland
Scotyr = 2023;
Scotday1 = find(timera(:,2)==Scoteventtime(1,2) & timera(:,3)==Scoteventtime(1,3),1);
Scotday2 = find(timera(:,2)==Scoteventtime(end,2) & timera(:,3)==Scoteventtime(end,3),1);

%% Calculating the cummulative precipitation over the period of extreme
% 7 days for Australia, 3 days for Scotland, 15 days for Pakistan

% Pakistan --------------------------------
Pakeventdays = movsum(Pak,size(Pakeventtime,1));
Pakeventdaysr = reshape(Pakeventdays,365,length(Pakeventdays)/365);
Pakeventdayscum = cumsum(Pakeventdaysr);      

% Australia --------------------------------
Auseventdays = movsum(Aus,size(Auseventtime,1));
Auseventdaysr = reshape(Auseventdays,365,length(Auseventdays)/365);
Auseventdayscum = cumsum(Auseventdaysr);      

% Scotland --------------------------------
Scoteventdays = movsum(Scot,size(Scoteventtime,1));
Scoteventdaysr = reshape(Scoteventdays,365,length(Scoteventdays)/365);
Scoteventdayscum = cumsum(Scoteventdaysr);      


%% FIGURE =============================================================
% Ploting cumulative pdf for the regions

figure
set(gcf,'Position',[1200 110 465 980])
subplot(3,1,1)
[lh, ph] = fanChart(1:365, Pakprecum(:,1:near(years,Pakyr-1)), 'median', [10 25 50 75 90], ...
'alpha', .2, 'colormap', {'shadesOfColor', [0 0.3 .1]}); hold on;
set(lh,'color',[0 0.3 .1],'linewidth',1);
set(ph,'Edgecolor','none')
plot(1:365, Pakprecum(:,near(years,Pakyr)), '-.','color',[0.55 0.2 0.15],'linewidth',1.5)
plot(ones(1,600)*Pakday1,1:600,'--','color',[0.8 0.8 0.8]);
plot(ones(1,600)*Pakday2,1:600,'--','color',[0.8 0.8 0.8]);
legend('10th and 90th percentiles', ...
    '25th and 75th percentiles', 'median', num2str(years(near(years,Pakyr))),...
    'Location','NorthWest','Color','none','EdgeColor','none')
ylabel('mm'); 
set(gca,'xlim',[1 365],'xtick',15:30:365,'xticklabel',months,'fontsize',14);
title('(a) Pakistan cumulative precipitation','fontsize',16)

subplot(3,1,2)
[lh, ph] = fanChart(1:365, Ausprecum(:,1:near(years,Ausyr-1)), 'median', [10 25 50 75 90], ...
'alpha', .2, 'colormap', {'shadesOfColor', [0 0.3 .1]}); hold on;
set(lh,'color',[0 0.3 .1],'linewidth',1);
set(ph,'Edgecolor','none')
plot(1:365, Ausprecum(:,near(years,Ausyr)), '-.','color',[0.55 0.2 0.15],'linewidth',1.5)
plot(ones(1,1500)*Ausday1,1:1500,'--','color',[0.8 0.8 0.8]);
plot(ones(1,1500)*Ausday2,1:1500,'--','color',[0.8 0.8 0.8]);
legend('10th and 90th percentiles', ...
    '25th and 75th percentiles', 'median', num2str(years(near(years,Ausyr))),...
    'Location','NorthWest','Color','none','EdgeColor','none')
ylabel('mm'); 
set(gca,'xlim',[1 365],'xtick',15:30:365,'xticklabel',months,'fontsize',14);
title('(b) Australia cumulative precipitation','fontsize',16)

subplot(3,1,3)
[lh, ph] = fanChart(1:365, Scotprecum(:,1:near(years,Scotyr-1)), 'median', [10 25 50 75 90], ...
'alpha', .2, 'colormap', {'shadesOfColor', [0 0.3 .1]}); hold on;
set(lh,'color',[0 0.3 .1],'linewidth',1);
set(ph,'Edgecolor','none')
plot(1:365, Scotprecum(:,near(years,Scotyr)), '-.','color',[0.55 0.2 0.15],'linewidth',1.5)
plot(Scotday1:Scotday2, Scotprecum(Scotday1:Scotday2,near(years,Scotyr)), '-','color',[0.2 0.2 0.2],'linewidth',1.5)
plot(ones(1,1500)*Scotday1,1:1500,'--','color',[0.8 0.8 0.8]);
plot(ones(1,1500)*Scotday2,1:1500,'--','color',[0.8 0.8 0.8]);
legend('5th and 95th percentiles', '10th and 90th percentiles', ...
    'median', num2str(years(near(years,Scotyr))),...
    'Location','NorthWest','Color','none','EdgeColor','none')
ylabel('mm'); 
set(gca,'xlim',[1 365],'xtick',15:30:365,'xticklabel',months,'fontsize',14);
title('(c) Scotland cumulative precipitation','fontsize',16)
%print('-depsc','-vector',[dirfig,'CumulativeRainfall_Pak_Aus_Scot.eps']);


