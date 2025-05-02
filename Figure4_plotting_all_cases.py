#### Necessary libraries ####
import numpy as np  # Numpy is the fundamental package for scientific computing in Python.
import xarray as xr
import argparse

from Functions import plotting_sources_cases, plotting_sources_one_case
from combine_data import read_data
from paths import basedir, figure_path


##################
# Example for running this code

# python Figure4_plotting_all_cases.py
# python Figure4_plotting_all_cases.py --casename Australia --plot_all t --plot_model_member f  --model_member_number 5

#

# General options
cases = ["Pakistan", "Australia", "Scotland"]


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plot_all",
        help="set --plot_all t to plot all ensemble members. Default --plot_all t",
        type=convert_to_boolean,
        default=True,
    )

    parser.add_argument(
        "--casename",
        help="set --casename Pakistan or Australia or Scotland",
        type=str,
        default="",
    )

    parser.add_argument(
        "--plot_model_member",
        help="set --plot_model_member t to plot a single member. Default --plot_model_member f",
        type=convert_to_boolean,
        default=False,
    )

    parser.add_argument(
        "--model_member_number",
        help="set --model_member_number -> Number of the member for plotting. It is only needed if --plot_model_member t",
        type=int,
        default=0,
    )
    args = parser.parse_args()
    return args


def convert_to_boolean(var):
    if str(var.lower()) in ("yes", "true", "t", "y", "1"):
        return True
    elif str(var.lower()) in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("True or False value expected")


masks = {
    "Pakistan": "Mask_PakistanFlood_box_lon-180to180.nc",
    "Scotland": "mask_scotland_box_lon-180to180.nc",
    "Australia": "mask_australia_box_lon0to360.nc",
}


maps_features = {
    # case: [central_longitude, lonmin, lonmax, latmin, latmax]
    "Scotland": [0, -85, 40, 10, 80],
    "Pakistan": [0, 0, 140, -40, 50],
    "Australia": [180, 120, 240, -60, 10],
}

fig_features = {
    # case:[figwidth, figheight, figrows, figcols , vmax, vmax_frac]
    "Scotland": [32, 20, 3, 5, 5, 0.02],  # [25,11,3,5,5, 0.02]
    "Pakistan": [32, 20, 3, 5, 20, 0.02],  # [25,12,3,5,20, 0.02]
    "Australia": [32, 20, 3, 5, 25, 0.02],  # [24,11,3,5,25, 0.02],
}


fig_features_one = {
    # Figure details to plot individual cases
    # case:[figwidth, figheight, figrows, figcols , vmax, vmax_frac]
    "Scotland": [12, 10, 1, 1, 5, 0.02],
    "Pakistan": [12, 10, 1, 1, 20, 0.02],
    "Australia": [12, 10, 1, 1, 25, 0.02],
}


fig_lon_ticks = {
    "Scotland": np.array([-70, -40, -10, 20]),
    "Pakistan": np.array([30, 70, 110]),
    "Australia": np.array([140, 180, 220]),
}


args = read_args()
if args.casename == "":
    cases = ["Pakistan", "Australia", "Scotland"]
else:
    cases = [args.casename]
if args.plot_all:
    for case in cases:
        ds_data = read_data(basedir, case)

        # Select one ensemble member per method
        drop_list = [
            "UTrack Ens1",
            "UTrack Ens3",
            "UTrack Ens4",
            "UTrack Ens5",
            "FLEXPART-HAMSTER Ens1",
            "FLEXPART-HAMSTER Ens2",
            "FLEXPART-HAMSTER Ens3",
            "FLEXPART-HAMSTER Ens4",
            "FLEXPART-WaterSip (HKUST) Ens1",
            "FLEXPART-WaterSip (HKUST) Ens3",
        ]
        ds_data = ds_data.drop_vars(drop_list)

        mask = xr.open_dataset(f"{basedir}/{case}/{masks[case]}")

        mean = ds_data.to_array(dim="mean").mean("mean")

        ds_data["Multi-method mean"] = mean

        print("--> Plotting sources")
        plotting_sources_cases(
            ds_data.where(ds_data > 0.1),
            mask,
            ds_data.keys(),
            figwidth=fig_features[case][0],
            figheight=fig_features[case][1],
            vmax=fig_features[case][4],
            central_longitude=maps_features[case][0],
            figrows=fig_features[case][2],
            figcols=fig_features[case][3],
            map_lons_extend=[maps_features[case][1], maps_features[case][2]],
            map_lats_extend=[maps_features[case][3], maps_features[case][4]],
            glons=fig_lon_ticks[case],
            fsize=12,
            fname=f"{figure_path}/Figure4_AbsoluteMoistureSources_{case}",
        )

        # quit()

        # print("--> PLotting fraction")
        # ds_data_frac = xr.Dataset(coords=ds_data.coords, attrs=ds_data.attrs)
        # for ens in ds_data.keys():
        #    ds_data_frac[ens] = calc_fractional_sources(ds_data[ens])

        # plotting_sources_cases(ds_data_frac, mask, ds_data.keys(), figwidth=fig_features[case][0], figheight=fig_features[case][1], vmax=fig_features[case][5], central_longitude=maps_features[case][0], figrows=fig_features[case][2], figcols=fig_features[case][3], map_lons_extend=[maps_features[case][1], maps_features[case][2]], map_lats_extend=[maps_features[case][3],maps_features[case][4]], glons=fig_lon_ticks[case], cblabel=False, cm=cm.ice_r, fname=f"./OUTPUTS/FractionMoistureSources_{case}.png")

        print()

if args.plot_model_member:
    for case in cases:
        ds_data = read_data(basedir, case)
        mask = xr.open_dataset(f"{basedir}/{case}/{masks[case]}")

        print("\n--> Plotting one case")
        ens_names = list(ds_data.keys())

        plotting_sources_one_case(
            ds_data,
            mask,
            [ens_names[args.model_member_number]],
            figwidth=fig_features_one[case][0],
            figheight=fig_features_one[case][1],
            vmax=fig_features_one[case][4],
            central_longitude=maps_features[case][0],
            figrows=fig_features_one[case][2],
            figcols=fig_features_one[case][3],
            map_lons_extend=[maps_features[case][1], maps_features[case][2]],
            map_lats_extend=[maps_features[case][3], maps_features[case][4]],
            glons=fig_lon_ticks[case],
            fname=f"{figure_path}/Figure4_AbsoluteMoistureSources_{case}",
        )

        # quit()
        # ds_data_frac = xr.Dataset(coords=ds_data.coords, attrs=ds_data.attrs)
        # for ens in ds_data.keys():
        #    ds_data_frac[ens] = calc_fractional_sources(ds_data[ens])

        # plotting_sources_one_case(ds_data_frac, mask, [ens_names[args.model_member_number]],  figwidth=fig_features_one[case][0], figheight=fig_features_one[case][1], vmax=fig_features_one[case][5], central_longitude=maps_features[case][0], figrows=fig_features_one[case][2], figcols=fig_features_one[case][3], map_lons_extend=[maps_features[case][1], maps_features[case][2]], map_lats_extend=[maps_features[case][3],maps_features[case][4]], glons=fig_lon_ticks[case], cblabel=False, cm=cm.ice_r, fname=f"./OUTPUTS/FractionMoistureSources_{case}")

        print()
