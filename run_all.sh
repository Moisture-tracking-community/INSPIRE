# Single command to re-run all notebooks/scripts to reproduce figures:
# bash run_all.sh

set -e  # exit immediately if one of the commands fails
set -x  # print executed commands to terminal

# Comment/uncomment to rerun or exclude from run as seen fit.
jupyter nbconvert --execute --to notebook --inplace Figure3_Global_map.ipynb
python Figure4_plotting_all_cases.py
jupyter nbconvert --execute --to notebook --inplace Figure5_BeeswarmAndBoxPlots_AllCases.ipynb
jupyter nbconvert --execute --to notebook --inplace Figure6_Correlation_matrix.ipynb
jupyter nbconvert --execute --to notebook --inplace Figure7_barplots_all_cases.ipynb