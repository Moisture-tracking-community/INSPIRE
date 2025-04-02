import numpy as np
import cartopy.crs as crs
import cartopy
from cartopy.mpl.ticker import LongitudeFormatter
from cmocean import cm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def grid_cell_area(latitude, longitude):
    """Return grid cell area"""
    erad = 6.371e6  # [m] Earth radius

    dx = np.abs(longitude[1] - longitude[0])  # [degrees] grid cell size

    # new area size calculation:
    lat_n_bound = np.minimum(90.0, latitude + 0.5 * dx)
    lat_s_bound = np.maximum(-90.0, latitude - 0.5 * dx)

    a_gridcell = np.zeros([len(latitude), 1])
    a_gridcell[:, 0] = (
        (np.pi / 180.0)
        * erad**2
        * abs(np.sin(lat_s_bound * np.pi / 180.0) - np.sin(lat_n_bound * np.pi / 180.0))
        * dx
    )

    return a_gridcell


def calc_fractional_sources(
    sources, precipitation=None, lon_name="lon", lat_name="lat"
):
    """Returns fractional moisture sources

    Standard assumes that the names of longitude and latitude
    dimension are "lon" and "lat" respectively. If this is not the case
    lon_name and lat_name should be used.

    Input:
    sources: (xarray) array containing the moisture sources
    lon_name: Name of longitude dimension
    lat_name: Name of latitude dimension
    precipitation: Optional array containing the precipitation of the model

    If no precipitation array is provided, thre fractional sources will be caluclated
    with respect to the total moisture sources

    Otherwise it will calculate fractional sources with respect to the total precipitation
    of the event*
    *DOES NOT WORK YET!"""

    if precipitation == None:
        a_gridcell_new, l_ew_gridcell, l_mid_gridcell = get_grid_info_new(
            sources[lat_name], sources[lon_name]
        )
        sources_frac = (
            sources
            * a_gridcell_new
            / ((sources * a_gridcell_new).sum((lon_name, lat_name)))
            * 100.0
        )
    else:
        """ Should be adapted so that the area-weighted precipitation can be used to bias correct
        moisture sources """

    return sources_frac


def calc_regional_sources(
    sources, regions, weights=None, lon_name="lon", lat_name="lat"
):
    """Returns regional moisture sources

    Standard assumes that the names of longitude and latitude
    dimension are "lon" and "lat" respectively. If this is not the case
    lon_name and lat_name should be used.

    Weights can be re-used for different ensemble memebers per model"""

    if weights is not None:
        sources_per_region = sources.weighted(weights).sum(dim=(lat_name, lon_name))
    else:
        mask_3D = regions.mask_3D(sources, lon_name=lon_name, lat_name=lat_name)
        # Use equal weights for each region as we are already using area-weighted fractional sources.
        # Effectively, the weighting is only used to group grid points of the same region together.
        weights = mask_3D.fillna(0)
        sources_per_region = sources.weighted(weights).sum(dim=(lat_name, lon_name))

    return sources_per_region, weights

# Get grid info
def get_grid_info_new(latitude, longitude):
    """Return grid cell area and lenght sides."""
    dg = 111089.56  # [m] length of 1 degree latitude
    erad = 6.371e6  # [m] Earth radius

    gridcell = np.abs(longitude[1] - longitude[0])  # [degrees] grid cell size

    # new area size calculation:
    lat_n_bound = np.minimum(90.0, latitude + 0.5 * gridcell)
    lat_s_bound = np.maximum(-90.0, latitude - 0.5 * gridcell)

    a_gridcell = np.zeros([len(latitude), 1])
    a_gridcell[:, 0] = (
        (np.pi / 180.0)
        * erad ** 2
        * abs(np.sin(lat_s_bound * np.pi / 180.0) - np.sin(lat_n_bound * np.pi / 180.0))
        * gridcell
    )

    l_ew_gridcell = gridcell * dg  # [m] length eastern/western boundary of a cell
    l_n_gridcell = (
        dg * gridcell * np.cos((latitude + gridcell / 2) * np.pi / 180)
    )  # [m] length northern boundary of a cell
    l_s_gridcell = (
        dg * gridcell * np.cos((latitude - gridcell / 2) * np.pi / 180)
    )  # [m] length southern boundary of a cell
    l_mid_gridcell = 0.5 * (l_n_gridcell + l_s_gridcell)
    return a_gridcell, l_ew_gridcell, l_mid_gridcell

def plot_single_map(ax, data, mask, title, map_lons_extend, map_lats_extend, vmax=5, xlabel="Longitude", ylabel="Latitude"):

    data.plot(ax=ax,vmin=0,vmax=vmax,robust=False,cmap=cm.rain,
              cbar_kwargs=dict(fraction=0.05, shrink=0.5,label=None),)
    ax.set_title(title, loc="left")
    ax.contour(mask['lon'].values, mask['lat'].values, np.squeeze(mask['mask'].values),colors=["r"])
    ax.add_feature(cartopy.feature.COASTLINE, linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, linestyle='-', linewidth=.2)

    ax.set_xticks(np.arange(-180, 181, 20))
    ax.set_yticks(np.arange(-90, 91, 10))
    ax.set_xlim(map_lons_extend[0], map_lons_extend[1])
    ax.set_ylim(map_lats_extend[0], map_lats_extend[1])

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

def plotting_sources(ds_data, mask, ens_names, casename, figwidth=24, figheight=14, vmax=5, central_longitude=0, figrows=5, figcols=5, map_lons_extend=None, map_lats_extend=None, fname="fig"):

    # set map extent if it is not set
    if map_lons_extend is None:
        if casename == "Pakistan":
            map_lons_extend = [0, 140]
        elif casename == "Scotland":
            map_lons_extend = [-85, 40]
        elif casename == "Australia":
            map_lons_extend = [120, 240]

    if map_lats_extend is None:
        if casename == "Pakistan":
            map_lats_extend = [-40,50]
        elif casename == "Scotland":
            map_lats_extend = [10, 80]
        elif casename == "Australia":
            map_lats_extend = [-65, 10]

    my_projection = crs.PlateCarree(central_longitude=central_longitude)

    # Make figure
    fig, axs = plt.subplots(figrows, figcols, figsize=(figwidth, figheight),subplot_kw={'projection': crs.PlateCarree()},sharey=False)

    for n,ens in enumerate(ens_names):

        print("------  Plotting", ens)

        i = n//figcols
        j = n%figcols

        # Dismiss label of y-axis, except for left most column
        if(j > 0):
            ylabel=""
        else:
            ylabel="Latitude"

        # Dismiss label of x-axis except for bottom row
        if(i < figrows-1):
            xlabel=""
        else:
            xlabel="Longitude"

        plot_single_map(axs[i,j], ds_data[ens], mask, ens, map_lons_extend, map_lats_extend, vmax=vmax, xlabel=xlabel, ylabel=ylabel)

    # Remove axes from empty subplots
    for n in range(len(ens_names), figrows*figcols):
        i = n//figcols
        j = n%figcols
        plt.sca(axs[i,j])
        plt.axis("off")

    fig.savefig(fname, dpi=300,  bbox_inches="tight")



def plotting_sources_cases(ds_data, mask, ens_names, figwidth=24, figheight=14, vmax=5, central_longitude=0, figrows=5, figcols=5, map_lons_extend=[-85, 40], map_lats_extend=[10,80], glons=[0,10,20],    fsize=15, cblabel=True, cm=cm.rain, fname="fig"):


    my_projection = crs.PlateCarree(central_longitude=central_longitude)
    rows=figrows
    cols=figcols
    # Make figure
    fig, axs = plt.subplots(rows, cols, figsize=(figwidth, figheight),subplot_kw={'projection': my_projection})
    i=0
    j=0

    labels=["(a)","(b)","(c)","(d)","(e)","(f)","(g)","(h)","(i)","(j)","(k)","(l)","(m)","(n)","(o)","(p)","(q)","(r)","(s)","(t)","(u)","(v)","(w)","(x)","(y)","(z)"]

    for iens, ens in enumerate(ens_names):
        print("------  Plotting", ens)

        filtered_data = ds_data[ens].where(ds_data[ens] >0.001 , np.nan)
        cb =  filtered_data.plot(ax=axs[i,j],vmin=0,vmax=vmax,robust=False,cmap=cm,transform = crs.PlateCarree(),extend="max", add_colorbar=False, add_labels=False)
        axs[i,j].set_title(f" {labels[iens]} {ens}", loc="left", fontsize=fsize+1)


        if len(mask['mask'].values.shape)>2:
            maskvals=mask['mask'].values[0,:]
        else:
            maskvals=mask['mask'].values

        axs[i,j].contour(mask['lon'].values, mask['lat'].values, maskvals ,colors=["r"],transform = crs.PlateCarree())
        axs[i,j].add_feature(cartopy.feature.COASTLINE, linewidth=0.8)
        axs[i,j].add_feature(cartopy.feature.BORDERS, linestyle='-', linewidth=.2)


        lon_formatter = LongitudeFormatter(direction_label=False, degree_symbol='')
        axs[i,j].xaxis.set_major_formatter(lon_formatter)
        fig.axes[iens].set_extent([map_lons_extend[0], map_lons_extend[1], map_lats_extend[0], map_lats_extend[1]],crs.PlateCarree())


        gl = axs[i,j].gridlines(draw_labels=True, linewidth=0)
        gl.top_labels = False
        gl.right_labels = False


        if glons.max()>180:
            glons = (glons + 180) % 360 - 180

        gl.xlocator =  mticker.FixedLocator(glons)
        gl.ylocator = mticker.MultipleLocator(20)
        gl.xlabel_style = {'size': fsize, 'color': 'k'}
        gl.ylabel_style = {'size': fsize, 'color': 'k'}




        #Dismiss label of y-axis, except for left most column

        if(j > 0):
            axs[i,j].set_ylabel("")
        else:
            axs[i,j].set_ylabel("Latitude")


        if i==rows-1:
            axs[i,j].set_xlabel("Longitude")
        else:
            axs[i,j].set_xlabel("")

        if j<cols-1:
            i=i
            j=j+1
        else:
            i=i+1
            j=0


    cbar = fig.colorbar(cb, ax=axs, orientation='horizontal', fraction=0.05, pad=0.035, aspect=50)

    if  cblabel:
        cbar.set_label('(mm)',size=fsize+1)
    cbar.ax.tick_params(labelsize=fsize+1)


    fig.savefig(fname,dpi=300,  bbox_inches="tight")
    plt.close()



def plotting_sources_one_case(ds_data, mask, ens_names, figwidth=24, figheight=14, vmax=5, central_longitude=0, figrows=1, figcols=1, map_lons_extend=[-85, 40], map_lats_extend=[10,80], glons=[0,10,20],    fsize=15, cblabel=True, cm=cm.rain, fname="fig"):


    my_projection = crs.PlateCarree(central_longitude=central_longitude)
    rows=figrows
    cols=figcols
    for iens, ens in enumerate(ens_names):
        fig, axs = plt.subplots(rows, cols, figsize=(figwidth, figheight),subplot_kw={'projection': my_projection})

        print("------  Plotting", ens)

        if ens=="WRF-WVT":
            ds_data[ens] = ds_data[ens] * vmax

        filtered_data = ds_data[ens].where(ds_data[ens] >0.001 , np.nan)
        cb = filtered_data.plot(ax=axs,vmin=0,vmax=vmax,robust=False,cmap=cm,transform = crs.PlateCarree(), extend="max",add_colorbar=False)

        axs.set_title(ens, loc="left", fontsize=fsize+2)


        if len(mask['mask'].values.shape)>2:
            maskvals=mask['mask'].values[0,:]
        else:
            maskvals=mask['mask'].values

        axs.contour(mask['lon'].values, mask['lat'].values, maskvals ,colors=["r"],transform = crs.PlateCarree())
        axs.add_feature(cartopy.feature.COASTLINE, linewidth=0.8)
        axs.add_feature(cartopy.feature.BORDERS, linestyle='-', linewidth=.2)

        lon_formatter = LongitudeFormatter(direction_label=False, degree_symbol='')
        axs.xaxis.set_major_formatter(lon_formatter)
        fig.axes[0].set_extent([map_lons_extend[0], map_lons_extend[1], map_lats_extend[0], map_lats_extend[1]],crs.PlateCarree())

        #Dismiss label of y-axis, except for left most column
        gl = axs.gridlines(draw_labels=True, linewidth=0)
        gl.top_labels = False
        gl.right_labels = False

        #glons=np.arange(map_lons_extend[0]+5,map_lons_extend[1]+25,20)

        if glons.max()>180:
            glons = (glons + 180) % 360 - 180

        gl.xlocator =  mticker.FixedLocator(glons)
        gl.ylocator = mticker.MultipleLocator(20)
        gl.xlabel_style = {'size': fsize+1, 'color': 'k'}
        gl.ylabel_style = {'size': fsize+1, 'color': 'k'}


        cbar = fig.colorbar(cb, ax=axs, orientation='horizontal', fraction=0.05, pad=0.035, aspect=50)

        if  cblabel:
            cbar.set_label('(mm)',size=fsize+2)
        cbar.ax.tick_params(labelsize=fsize+2)



        fig.savefig(fname+"_"+ens+".png",dpi=300,  bbox_inches="tight")
        plt.close()
