# Moisture_tracking_intercomparison

This repository contains scripts to analyse output from different moisture tracking models in the moisture tracking intercomparison project. This repository was initiated during a [Lorentz workshop during May 2024](https://www.lorentzcenter.nl/moisture-tracking-intercomparison-time-to-address-the-uncertainty.html). The code is maintained by the participants of the project, which can be found in the citation.cff file. You are free to use the code given the Apache-2.0 licence, please check the Contributor_Guidelines.txt. 

# Scripts to make figures in the repository

_barplots_all_cases.ipynb_ creates a plot to plot the relative moisture sources compared to the input (precipitation)

_Global_map.ipynb_ Plots the multi-method mean of the moisture sources for all three cases in one map

_BeeswarmAndBoxPlots_AllCases.ipynb_ Makes a figure which shows the difference in regional contributions for all ensemble members (including the extra ensemble members for some methods)

_plotting_all_cases.py_ is a script to load in data for the all three cases and make a plot of the moisture sources of all (selected) members, or a method specifically. 

_Correlation_matrix.ipynb_ is a script to plot the correlation between all methods for all three cases

# Other files in the repository

_Contributing_models.txt_ is a text file containing the models contributing the intercomparison project. 

_Function.py_ contains function to load in tagging region, calculate area of grids, and to determine fractional and regional moisture sources.

_IPCCregions_Pakistancase.nc_ is a netcdf file containing the IPCC regions for the Pakistan case. 

