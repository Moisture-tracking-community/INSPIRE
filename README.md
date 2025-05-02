# Moisture_tracking_intercomparison

This repository contains scripts to analyse output from different moisture tracking models in the moisture tracking intercomparison project. This repository was initiated during a [Lorentz workshop during May 2024](https://www.lorentzcenter.nl/moisture-tracking-intercomparison-time-to-address-the-uncertainty.html). The code is maintained by the participants of the project, which can be found in the citation.cff file. You are free to use the code given the Apache-2.0 licence, please check the Contributor_Guidelines.txt. 

## To reproduce the analysis:

```sh
# Clone the repo
git clone ...

# Optional: create dedicated environment e.g. with conda or venv

# Install required python packages
pip install -r requirements.txt

# Optional: adapt paths in paths.py to point to the location 
# where you stored the data and where you want to store the figures.

# Run all notebooks and scripts in one go
bash run_all.sh

# or open/run each notebook/script separately
```

## Formatting

You can use ruff (TODO: run ruff once)
