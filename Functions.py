import numpy as np
import cartopy.crs as crs
import cartopy
from cartopy.mpl.ticker import LongitudeFormatter
from cmocean import cm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib as mpl
import xarray as xr
import datetime                 # Datetime is a package to deal with dates.
import regionmask
import os

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
        mask_3D = regions.mask_3D(sources)
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


def calculate_region_attr(all_maps,csv_wrf_wvt,case,path_to_data):
    
    #### grid cell areas ####
    
    a_gridcell_new, l_ew_gridcell, l_mid_gridcell = get_grid_info_new(all_maps.lat.values, all_maps.lon.values) #Calcluate grid cell area for global domain
    if case=='Pakistan':
        a_gridcell_newp, l_ew_gridcellp, l_mid_gridcellp = get_grid_info_new(np.arange(24,30.1,0.25), np.arange(67,71.1,0.25)) #Calcluate grid cell area for case domain
        ll=17
        area_chc=286280.17*10**6
    elif case=='Scotland':
        a_gridcell_newp, l_ew_gridcellp, l_mid_gridcellp = get_grid_info_new(np.arange(52,60.1,0.25), np.arange(-8,-0.9,0.25))
        ll=29
        area_chc=411007.96*10**6
    elif case=='Australia':
        a_gridcell_newp, l_ew_gridcellp, l_mid_gridcellp = get_grid_info_new(np.arange(-32,-21.9,0.25), np.arange(149,158.1,0.25))
        ll=37
        area_chc=1097376.96*10**6
        
    '''Define regions, also provides an example how to define them using the regionmask package. 
    
    In the plots below, 'rest of the world' is not included (it is in the netcdf file). Furthermore it would be nice/logical 
    to include the event region, for the Pakistan case this is now part of the SAS region. 
    '''
    
    #### Sources per region, import necessary libraries ####
    my_projection = crs.PlateCarree(central_longitude=0)
    
    source_regions = xr.open_dataset(path_to_data+'/'+case+"/IPCCregions_"+case+"case.nc")
    
    ar6_all = regionmask.defined_regions.ar6.all
    if case=='Pakistan':
        selected_regions = ar6_all[['NEAF', 'SEAF', 'WCA', 'TIB', 'ARP', 'SAS', 'ARS', 'BOB', 'EIO', 'SIO']]
    elif case=='Scotland':
        selected_regions = ar6_all[['ENA','CAR','NEU','WCE','MED','NAO']]
    elif case=='Australia':
        selected_regions = ar6_all[['NAU','CAU','EAU','SAU','NZ','EPO','SPO','SOO']]
    
    #### calculate regional attributions ####
    
    all_maps_frac={}
    all_maps_abs={}
    all_maps_frac_regional={}
    all_maps_regional={}
    
    for kk in list(all_maps.keys()):
        if kk=='LAGRANTO-WaterSip (CHc)':area_target=area_chc
        else: area_target=(a_gridcell_newp[:].sum()*ll)
        all_maps_frac[kk] = calc_fractional_sources(all_maps[kk])
        all_maps_frac_regional[kk] = calc_regional_sources(all_maps_frac[kk],selected_regions)[0]
        all_maps_abs[kk] = ( all_maps[kk] * a_gridcell_new[:] ) / area_target
        all_maps_regional[kk] = calc_regional_sources(all_maps_abs[kk],selected_regions)[0]
        
    #### sum of absolute moisture sources (should be equal to precipitation in sink region) ####
    
    precip_sums = np.array([np.sum(all_maps_abs[k]) for k in list(all_maps_abs.keys())])
    if case=='Pakistan':
        precip_sums = np.concatenate([precip_sums[:-1],[csv_wrf_wvt.loc['2022-08-10_2022-08-25'][0]],[precip_sums[-1]]])
    elif case=='Scotland':
        precip_sums = np.concatenate([precip_sums[:-1],[csv_wrf_wvt.loc['2023-10-06_2023-10-09'][0]],[precip_sums[-1]]])
    elif case=='Australia':
        precip_sums = np.concatenate([precip_sums[:-1],[csv_wrf_wvt.loc['2022-02-22_2022-02-28'][0]],[precip_sums[-1]]])

    return all_maps_frac_regional,all_maps_regional,precip_sums
    


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


    fig.savefig(fname,dpi=600,  bbox_inches="tight")
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

def plot_precip(precip_era5,case,outpath,closeplot):

    if case=='Pakistan':
        startdate=datetime.datetime(2022,8,22,0)
        length=15*24
    elif case=='Scotland':
        startdate=datetime.datetime(2023,10,6,0)
        length=3*24
    elif case=='Australia':
        startdate=datetime.datetime(2022,2,22,0)
        length=7*24
    
    n_lines = len(precip_era5)
    cmap = mpl.colormaps['tab10']
    # Take colors at regular intervals spanning the colormap.
    colors = cmap(np.linspace(0, 1, n_lines+1))
    
    dt=[startdate+datetime.timedelta(hours=i) for i in range(length)]
    f,ax=plt.subplots(1,2,figsize=(18,10),gridspec_kw={'width_ratios': [4, 1]})
    ls=[':','-','--',':','-','--',':','-','--',':','-','--',':','-','--']
    lw=2.0

    A=[]
    for nn,i in enumerate(precip_era5):
        print(i)
        if i=='UTrack Ens2':
            A.append(float(precip_era5[i][:length].sum().values)) 
        else:
            A.append(float(precip_era5[i].sum().values))        

        if precip_era5[i].shape[0]==length/24:
            ax[0].plot(dt[0::24],precip_era5[i],label=i+', 24h',linestyle=ls[nn],color=colors[nn])
            ax[1].scatter(1,A[-1],color=colors[nn],label=i)
        elif precip_era5[i].shape[0]==length:
            precip_era5[i]['time']=np.arange(0,length,1)
            ax[0].plot(dt[0::24],precip_era5[i].groupby_bins('time',np.arange(0,length+1,24),right=False).sum(...),label=i+', 1h',linewidth=lw,linestyle=ls[nn],color=colors[nn])
            ax[1].scatter(1,A[-1],color=colors[nn],label=i)
        elif precip_era5[i].shape[0]==length+1:
            precip_era5[i]['time']=np.arange(0,length+1,1)
            ax[0].plot(dt[0::24],precip_era5[i].groupby_bins('time',np.arange(0,length+2,24),right=False).sum(...),label=i+', 1h',linestyle=ls[nn],linewidth=lw,color=colors[nn])
            ax[1].scatter(1,A[-1],color=colors[nn],label=i)
        elif precip_era5[i].shape[0]==length/6:
            precip_era5[i]['time']=np.arange(0,length,6)
            ax[0].plot(dt[0::24],precip_era5[i].groupby_bins('time',np.arange(0,length+2,24),right=False).sum(...),label=i+', 6h',linestyle=ls[nn],linewidth=lw,color=colors[nn])
            ax[1].scatter(1,A[-1],color=colors[nn],label=i)
        elif precip_era5[i].shape[0]==length/6+1:
            precip_era5[i]['time']=np.arange(0,length+1,6)
            ax[1].scatter(1,A[-1],color=colors[nn],label=i)
            ax[0].plot(dt[0::24],precip_era5[i].groupby_bins('time',np.arange(0,length+2,24),right=False).sum(...),label=i+', 6h',linestyle=ls[nn],linewidth=lw,color=colors[nn])
        else:
            ax[1].scatter(1,A[-1],color=colors[nn],label=i)           

    ax[1].boxplot(A,zorder=0)
    
    #ax[0].legend(frameon=False,fontsize=14)
    ax[1].legend(frameon=False,fontsize=14,bbox_to_anchor=(1.1, 1.01))

    ax[0].set_ylabel(u'ERA5 precipitation [mm$\,$24h$^{-1}$]')

    ax[1].set_xlim([0.8,1.2])
    ax[1].set_ylabel(u'ERA5 precipitation event sum [mm / event]')
    plt.setp( ax[1].get_xticklabels(), visible=False)
    
    xt=ax[0].set_xticks(dt[0::24])
    plt.setp(ax[0].get_xticklabels(), rotation=45, ha='right')
    
    plt.suptitle(case+' case')

    
    plt.savefig(outpath+'era5_precip_model_input_'+case+'.png',dpi=300)
    if closeplot==True: plt.close()

def plot_frac_regional(all_maps_frac_regional,csv_wrf_wvt,list_reordered,outpath,closeplot,case):

    #### preparing arrays to plot ####
    srcs_wrf_wvt=all_maps_frac_regional['FLEXPART-Stohl (UVigo)'].copy()
    srcs_wrf_wvt.values=csv_wrf_wvt.loc['fractions'][1:-2].values
    
    srcs_regional_frac_combined = xr.concat([all_maps_frac_regional[kk].expand_dims(ensemble=1) for kk in list(all_maps_frac_regional.keys())[:-1]
                        ],dim='ensemble')
    srcs_regional_frac_combined = xr.concat([srcs_regional_frac_combined,
                      srcs_wrf_wvt.expand_dims(ensemble=1)
                        ],dim='ensemble')
    srcs_regional_frac_combined = xr.concat([srcs_regional_frac_combined,
                      all_maps_frac_regional['FLEXPART-Stohl (UVigo)'].expand_dims(ensemble=1)
                        ],dim='ensemble')
    
    modelnames=np.concatenate([list_reordered[:-1],["WRF_WVT"],[list_reordered[-1]]])

    n_lines = len(srcs_regional_frac_combined['region'])
    cmap = mpl.colormaps['RdYlBu_r']
    # Take colors at regular intervals spanning the colormap.
    colors = cmap(np.linspace(0, 1, n_lines+1))
    
    fig, ax = plt.subplots(figsize=(20,10))
    bottom = np.zeros(len(modelnames))
    for ii in range(n_lines+1):# srcs_Vigo_e1_Stohl_regional:
        if ii!=n_lines:
            p = ax.bar(modelnames, srcs_regional_frac_combined[:,ii].values, 0.5, color=colors[n_lines-ii], label=srcs_regional_frac_combined.names.values[ii], bottom=bottom)
            bottom += srcs_regional_frac_combined[:,ii].values
        else:
            p = ax.bar(modelnames, np.array([100 for i in range(len(modelnames))])-bottom, 0.5, label='Rest', bottom=bottom, color='lightgrey')
            #bottom += [100 for i in range(18)]
    plt.xticks(rotation=45, ha='right')
    
    ax.set_ylabel('fraction of moisture uptake [%]')
    ax.legend(bbox_to_anchor=(1.01, 1.01),fontsize=16,frameon=False)
    
    plt.savefig(outpath+'bar_plots_frac_'+case+'.png',bbox_inches='tight', dpi=300)
    if closeplot==True: plt.close()

def plot_abs_regional(all_maps_regional,csv_wrf_wvt,precip_sums,precip_era5,list_reordered,outpath,closeplot,case):

    #### preparing arrays to plot ####

    srcs_wrf_wvt=all_maps_regional['FLEXPART-Stohl (UVigo)'].copy()
    if case=='Pakistan':
        srcs_wrf_wvt.values=csv_wrf_wvt.loc['2022-08-10_2022-08-25'][1:-2].values
    elif case=='Scotland':
        srcs_wrf_wvt.values=csv_wrf_wvt.loc['2023-10-06_2023-10-09'][1:-2].values
    elif case=='Australia':
        srcs_wrf_wvt.values=csv_wrf_wvt.loc['2022-02-22_2022-02-28'][1:-2].values
        
    
    srcs_regional_combined = xr.concat([all_maps_regional[kk].expand_dims(ensemble=1) for kk in list(all_maps_regional.keys())[:-1]
                        ],dim='ensemble')
    srcs_regional_combined = xr.concat([srcs_regional_combined,
                      srcs_wrf_wvt.expand_dims(ensemble=1)
                        ],dim='ensemble')
    srcs_regional_combined = xr.concat([srcs_regional_combined,
                      all_maps_regional['FLEXPART-Stohl (UVigo)'].expand_dims(ensemble=1)
                        ],dim='ensemble')

    if case=='Pakistan':
        texty=338
        ylimx=350
        leg2h=0.54
        length=15*24
    elif case=='Scotland':
        texty=41
        ylimx=42.5
        leg2h=0.71
        length=3*24
    elif case=='Australia':
        texty=156
        ylimx=162
        leg2h=0.6
        length=7*24  
        
    n_lines = len(srcs_regional_combined['region'])
    cmap = mpl.colormaps['RdYlBu_r']
    # Take colors at regular intervals spanning the colormap.
    colors = cmap(np.linspace(0, 1, n_lines+1))
    
    modelnames=np.concatenate([list_reordered[:-1],["WRF_WVT"],[list_reordered[-1]]])
    
    fig, ax = plt.subplots(figsize=(20,10))
    ax2 = ax.twinx()
    bottom = np.zeros(len(modelnames)-2)
    bottom2 = np.zeros(1)
    bottom3 = np.zeros(1)
    for ii in range(n_lines+1):# srcs_Vigo_e1_Stohl_regional:
        if ii!=n_lines:
            p = ax.bar(range(len(modelnames)-2), srcs_regional_combined[:-2,ii].values, 0.5, color=colors[n_lines-ii], label=srcs_regional_combined.names.values[ii], bottom=bottom)
            bottom += srcs_regional_combined[:-2,ii].values
            p = ax2.bar(len(modelnames)-1, srcs_regional_combined[-1,ii].values, 0.5, color=colors[n_lines-ii], bottom=bottom2)
            bottom2 += srcs_regional_combined[-1,ii].values
            p = ax.bar(len(modelnames)-2, srcs_regional_combined[-2,ii].values, 0.5, color=colors[n_lines-ii], bottom=bottom3)
            bottom3 += srcs_regional_combined[-2,ii].values    
    
        else:
            p = ax.bar(range(len(modelnames)-2), precip_sums[:-2]-bottom, 0.5, label='Other regions', bottom=bottom, color='lightgrey')
            p = ax2.bar(len(modelnames)-1, precip_sums[-1]-bottom2, 0.5,  bottom=bottom2, color='lightgrey')
            p = ax.bar(len(modelnames)-2, precip_sums[-2]-bottom3, 0.5, bottom=bottom3, color='lightgrey')
    
    
    for nn,mname in enumerate(modelnames):
        if mname in precip_era5:
            if mname=='UTrack Ens2':
                pr_sum=precip_era5[mname][:length].sum().values
            else:
                pr_sum=precip_era5[mname].sum().values
            ax.hlines(pr_sum,nn-0.3,nn+0.3,color='k',linestyle=':',linewidth=3.0)
            ax.text(nn,texty,"{:.0f}".format(precip_sums[nn]/pr_sum*100)+'%',ha='center')
            if mname=='FLEXPART-LATTIN (UVigo)':
                nn=len(modelnames)-1
                ax2.hlines(pr_sum,nn-0.3,nn+0.3,color='k',linestyle=':',linewidth=3.0,label='ERA5 precipitation')
                ax.text(nn,texty,"{:.0f}".format(precip_sums[nn]/pr_sum*100)+'%',ha='center')
    
    ax.axvline(x=len(modelnames)-1.5,color='grey',linestyle='--',linewidth=2.0)
    
    ax.set_xticks(range(len(modelnames)))
    ax.set_xticklabels(modelnames, rotation=45, ha='right')
    ax.set_ylabel('moisture source contribution to precipitation [mm]')
    ax2.set_ylabel('moisture source contribution to precipitation [mm] (FLEXPART-Stohl)')

    
    ax.set_ylim(0,ylimx)
    ax.legend(bbox_to_anchor=(1.3, 1.01),fontsize=16,frameon=False)
    ax2.legend(bbox_to_anchor=(1.3, leg2h),fontsize=16,frameon=False)

    plt.title(case)
    
    plt.savefig(outpath+'bar_plots_abs_'+case+'.png',bbox_inches='tight', dpi=300)
    if closeplot==True: plt.close()
