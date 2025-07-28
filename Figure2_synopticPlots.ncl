;*****************************************************************************************
; PLOT DAILY PRECIPITATION from ERA5 or GPM IMERG, and MSLP, Z500 or V300, and IVT from ERA5 cases 
;*****************************************************************************************

;***********************************************************************************************************************************************
; SETTINGS
;***********************************************************************************************************************************************

plot_version 		= "v1"                                                           ; plot_version of visualization

;**********************************************************************************************************************************************************
; CASE SPECIFICATIONS
;**********************************************************************************************************************************************************

region          	= (/"Pakistan","Australia","Scotland"/)
yyyy_sel        	= (/2022,2022,2023/)
m_sel           	= (/8,2,10/)
d_start         	= (/10,22,6/)
d_end           	= (/24,28,8/)
d_sel         		= (/18,24,7/)

minlon          	= (/30,115,-55/)
maxlon          	= (/105,190,20/)
minlat          	= (/-10,-60,15/)
maxlat          	= (/50,0,75/)

lat_S                   = (/24,-32,52/)
lat_N                   = (/30,-22,60/)
lon_W                   = (/67,149,352/)
lon_E                   = (/71,158,359/)

;***********************************************************************************************************************************************
; ELSE 
;***********************************************************************************************************************************************

mm_sel			= sprinti("%0.2i",m_sel)
dd_start		= sprinti("%0.2i",d_start)
dd_end			= sprinti("%0.2i",d_end)

plev_sel1		= 50000
plev_sel2		= 30000

g_const 		= 9.81

;***********************************************************************************************************************************************
; SETTINS PRECIPITATION
;***********************************************************************************************************************************************

precip_source 		= "ERA5"
;;precip_source 	= "GPM"

resolution_era5		="reg05"
step_era5		="1to12"

GPM_version 		= 6                                                                 ; version of GPM IMERG

;***********************************************************************************************************************************************
; PLOT SETTINGS
;***********************************************************************************************************************************************

dash_pattern		= 1

smt_fct			= 3

cnlevels_mslp		= tofloat(ispan(990,1025,5))

cnlevels_z500		= fspan(5520,5910,14)


ivt_dm_thresh		= 200
ivt_dm_thresh2		= 200

vec_int1                = 8
vec_int2                = 8

font_hgt0		= 0.018
font_hgt1		= 0.012
font_hgt2 		= 0.010
font_hgt3 		= 0.008

line_thk		= 0.1

line_lgt		= 0.01

pm_pos_x1               = 0.075
pm_pos_y1               = 0.28

pm_pos_x2               = 0.570
pm_pos_y2               = 0.28

mp_gray                 = 0.85

;***********************************************************************************************************************************************
; SET IN & OUTPUT DIRECTORIES
;***********************************************************************************************************************************************

dir_in1a 		= "/work/FAC/FGSE/IDYST/ddomeise/default/DATA/ERA5/eth/fcst/"					; from eth
dir_in1b 		= "/work/FAC/FGSE/IDYST/ddomeise/default/DATA/GPM/GPM_3IMERGDL/"				; original daily data at r0.1 degree
dir_in2  		= "/work/FAC/FGSE/IDYST/ddomeise/default/andries/DATA/ERA5-MOD/DAYMEAN/"			; monthly files with daily mean data

dir_out  		= "/work/FAC/FGSE/IDYST/ddomeise/default/andries/PLOTS/MoistTrack_Pak2022/"

;*****************************************************************************************
load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/calendar_decode2.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"
load "~/PROGRAMMES/NCL/lib/ncarg/nclscripts/csm/contributed_ajv.ncl"
;*****************************************************************************************

begin

;*****************************************************************************************
; OPEN PDF
;*****************************************************************************************

wks 			= gsn_open_wks("pdf",dir_out+"precip_"+precip_source+"_synop_avg_"+region(0)+"_"+yyyy_sel(0)+mm_sel(0)+dd_start(0)+"to"+dd_end(0)+"_"+region(1)+"_"+yyyy_sel(1)+mm_sel(1)+dd_start(1)+"to"+dd_end(1)+"_"+region(2)+"_"+yyyy_sel(2)+mm_sel(2)+dd_start(2)+"to"+dd_end(2)+"_smt"+smt_fct+"_"+plot_version)               ; open a pdf file

cmap3 			= read_colormap_file("CBR_wet_av2")
cmap4 			= read_colormap_file("lajolla_10_av2")

;***********************************************************************************************************************************************
; PART I: PLOT SETTINGS
;***********************************************************************************************************************************************

;***********************************************************************************************************************************************
; SHADING 
;***********************************************************************************************************************************************

res 				= True

res@mpOutlineOn  		= True                                                  ; turn the map outline on
;res@mpOutlineOn 		= False                                                  ; turn the map outline on
;res@mpGeophysicalLineThicknessF= 1.0

res@mpGeophysicalLineThicknessF                                = 1.5
;res@mpGeophysicalLineColor                                      = "gray70"
res@mpGeophysicalLineThicknessF	= 1.
res@mpGeophysicalLineColor     	= "grey85"

res@gsnDraw  			=  False                                                    ; do not draw the plot
res@gsnFrame 			=  False                                                   ; do not advance the frame

res@gsnLeftString  		= ""
res@gsnRightString  		= ""


;res@tmXBOn              	= False
res@tmXTOn              	= False
;res@tmYLOn              	= False
res@tmYROn              	= False


res@tmXBLabelFontHeightF	= font_hgt1 
res@tmYLLabelFontHeightF	= font_hgt1

res@tmXBMajorLengthF 		= line_lgt
res@tmYLMajorLengthF 		= line_lgt

res@tmXBMajorThicknessF 	= line_thk
res@tmYLMajorThicknessF 	= line_thk
res@tmXBMinorThicknessF 	= line_thk
res@tmYLMinorThicknessF 	= line_thk

res@tmBorderThicknessF 		= line_thk


res1				= res
res1@cnLineLabelsOn 		= False                                              ; do not use line labels
res1@cnFillOn       		= True                                              ; color fill
res1@cnLinesOn       		= False                                             ; do not draw contour lines
res1@cnFillDrawOrder 		= "Draw"
res1@gsnSpreadColors 		= False                                             ; automatically choose the fill colors
res1@cnMissingValFillColor 	= "gray"

res1@gsnCenterStringFontHeightF = font_hgt0 
res1@gsnCenterStringOrthogonalPosF= 0.02

res1@lbLabelBarOn		= False                                         ; turn off individual cb's

res1@mpFillOn 			= True
res1@mpFillColors 		= (/-1,-1,13,-1/)                                     ; 14 = gray82, as gray 82 is added to the end of precip_11lev
res1@mpFillDrawOrder 		= "PreDraw"                                        ; tell NCL to map fill first

res1@cnLevelSelectionMode 	= "ExplicitLevels"                            ; use explicit levels

res1@cnLevels 			= (/10,25,50,75,100,150,200,250,300,400/)

res1@cnFillColors 		= (/-1,3,4,5,6,7,8,9,10,11,12/)                   ; note: values less that 1 are set to transparent

res2				= res1
res2@cnLevels 			= res1@cnLevels 

;***********************************************************************************************************************************************
; CONTOURS 
;***********************************************************************************************************************************************
;***********************************************************************************************************************************************
; DAILY MEANS 
;***********************************************************************************************************************************************

r0				= True

r0@gsnAddCyclic 		= True
;;r0@gsnAddCyclic 		= False

r0@gsnDraw          		= False                                    ; don't draw
r0@gsnFrame 			= False                                            ; do not advance the frame
r0@gsnLeftString  		= ""
r0@gsnRightString  		= ""

r0@gsnLeftString  		= ""
r0@gsnRightString  		= ""

r0@lbLabelBarOn 		= False                                 ; turn off individual cb's

;r0@cnLineLabelsOn 		= True                                    ; do not use line labels
r0@cnLineLabelPlacementMode 	= "Computed"
;r0@cnLineLabelInterval 	= 1
;r0@cnLineLabelDensityF 	= 2.
;;;r0@cnLineLabelFontHeightF 	= 0.0075
r0@cnLineLabelFontHeightF 	= 0.01
r0@cnLineLabelBackgroundColor 	= -1

r0@cnLevelSelectionMode 	= "ExplicitLevels"                   ; use explicit levels

r0@cnInfoLabelOn      		= False       ; Turn off info label

r0@cnMonoLineThickness 		= False

;;r0gsnContourNegLineDashPattern= 1

r0@cnLineDrawOrder                      = "PostDraw"


r1				= r0
r1@cnLevels 			= cnlevels_mslp
r1@cnLineColor 			= tofloat((/ 84,39,136/))/255.
r1@cnLineThicknesses            = fspan(0.6,2.0,8)
r1@cnLineLabelFontColor		= r1@cnLineColor 

r2				= r0
r2@cnLevels 			= cnlevels_z500
r2@cnLineColor 			= tofloat((/224,130,20/))/255.
r2@cnLineThicknesses 		= fspan(0.6,2.0,14)
r2@cnLineLabelFontColor		= r2@cnLineColor 


;***********************************************************************************************************************************************
; VECTORS 
;***********************************************************************************************************************************************

vcres 				= True
vcres@gsnDraw          		= False                                    ; don't draw
vcres@gsnFrame 			= False                                            ; do not advance the frame
vcres@gsnLeftString  		= ""
vcres@gsnRightString  		= ""
vcres@gsnAddCyclic 		= True

vcres@vcVectorDrawOrder 	= "PostDraw"

vcres@vcRefMagnitudeF 		= 1
vcres@vcGlyphStyle 		= "CurlyVector"
vcres@vcRefLengthF 		= 0.025

vcres@vcLineArrowThicknessF 	= 1.

vcres@vcRefAnnoOn               = True

vcres@vcRefAnnoString2          = "IVT"
vcres@vcRefAnnoFontHeightF      = 0.015
;vcres@vcRefAnnoPerimOn         = False
vcres@vcRefAnnoArrowSpaceF      = 1.
vcres@vcRefAnnoPerimThicknessF	= line_thk 

;;vcres@vcFillArrowFillColor    = "red"
vcres@vcRefAnnoOrthogonalPosF  	= -1.0
;vcres@vcRefAnnoParallelPosF    = 0.1

vcres1				= vcres
;vcres1@vcLineArrowColor 	= "red"

vcres2				= vcres
;vcres2@vcLineArrowColor 	= "red"

;***********************************************************************************************************************************************
; POLYLINE 
;***********************************************************************************************************************************************

resp                            = True                      ; polyline mods desired
resp@gsLineDashPattern          = 0
resp@tfPolyDrawOrder            = "PostDraw"
;resp@gsLineThicknessF           = 1.5                       ; thickness of lines
resp@gsLineThicknessF           = 0.5                       ; thickness of lines
resp@gsLineColor                = "red"                     ; color of lines

;***********************************************************************************************************************************************
; TEXT SETTINGS
;***********************************************************************************************************************************************

txres               		= True
txres@txFontHeightF 		= 0.012
txres@txJust			= "CenterLeft"

txres1 				= txres
txres1@txFontColor 		= r1@cnLineColor 

txres2 				= txres
txres2@txFontColor 		= r2@cnLineColor 

txres3 				= txres
txres3@txFontColor 		= "red"

;txres4 				= txres
;txres4@txFontColor 		= r4@cnLineColor 

;***********************************************************************************************************************************************
; PANEL SETTINGS
;***********************************************************************************************************************************************

pnlres 				= True
pnlres@gsnFrame               	= False   ; Don't advance frame

pnlres@amJust                   = "TopLeft"
pnlres@gsnPanelFigureStringsFontHeightF=0.01
pnlres@gsnPanelFigureStringsPerimOn=False
pnlres@gsnPanelFigureStrings   = (/"(a)","(b)","(c)","(d)","(e)","(f)"/)      ; add strings to pane
pnlres@gsnPanelFigureStringsBackgroundFillColor               = -1

pnlres@gsnPanelXWhiteSpacePercent=1

pnlres@gsnPanelLabelBar 	= True                    ; add common colorbar
pnlres@lbLabelFontHeightF  	= font_hgt3 
pnlres@lbTitlePosition 		= "Bottom"
pnlres@lbTitleDirection 	= "Across"
pnlres@lbTitleExtentF 		= 0.05
pnlres@lbTitleFontHeightF	= font_hgt3 
pnlres@lbBoxEndCapStyle       = "TriangleBothEnds"
pnlres@lbBoxLineThicknessF       = line_thk

pnlres@pmLabelBarOrthogonalPosF= -0.01

pnlres@pmLabelBarWidthF 	= 0.40
pnlres@pmLabelBarHeightF 	= 0.04


pnlres1 			= pnlres
pnlres1@lbTitleString 		= "precipitation "+precip_source+" (mm)"

pnlres2 			= pnlres
pnlres2@gsnPanelTop       	= 0.50
pnlres2@gsnPanelBottom       	= 0.02
;pnlres2@gsnPanelLeft		= 0.0
;pnlres2@gsnPanelRight		= 0.5
pnlres2@lbTitleString 		= "precipitation "+precip_source+" (mm)"

;***********************************************************************************************************************************************
; INITIALISE PLOTS 
;***********************************************************************************************************************************************

plot1	 			= new(dimsizes(region),graphic) 
plot1_mslp 			= new(dimsizes(region),graphic) 
plot1_z500 			= new(dimsizes(region),graphic) 
plot1_ivt 			= new(dimsizes(region),graphic) 

dum_pln1			= new(dimsizes(region),graphic)

plot2	 			= new(dimsizes(region),graphic) 
plot2_mslp 			= new(dimsizes(region),graphic) 
plot2_z500 			= new(dimsizes(region),graphic) 
plot2_ivt 			= new(dimsizes(region),graphic) 

do n=0,dimsizes(region)-1

  ;***********************************************************************************************************************************************
  ; PART II: READ IN FILES & VARIABLES 
  ;***********************************************************************************************************************************************
  
  res1@mpMinLonF 		= minlon(n)+5                                                    ; specify the plot domain
  res1@mpMaxLonF 		= maxlon(n)-5
  res1@mpMinLatF 		= minlat(n)+5
  res1@mpMaxLatF 		= maxlat(n)-5

  res2@mpMinLonF 		= minlon(n)+5                                                    ; specify the plot domain
  res2@mpMaxLonF 		= maxlon(n)-5
  res2@mpMinLatF 		= minlat(n)+5
  res2@mpMaxLatF 		= maxlat(n)-5
  
  ;***********************************************************************************************************************************************
  ; READ IN FILES
  ;***********************************************************************************************************************************************
  
  if (precip_source.eq."ERA5") then
    a1 				= addfile(dir_in1a+"era5_fc_totprec_"+resolution_era5+"_step"+step_era5+"_ds_"+yyyy_sel(n)+mm_sel(n)+".nc","r")
  
    time_ds			= a1->time
    date_ds 			= calendar_decode2(time_ds(:),0)
    time_ds_ind			= ind(date_ds(:,0).eq.yyyy_sel(n) .and. date_ds(:,1).eq.m_sel(n) .and. date_ds(:,2).ge.d_start(n) .and. date_ds(:,2).le.d_end(n))
    time_ds_ind2		= ind(date_ds(:,0).eq.yyyy_sel(n) .and. date_ds(:,1).eq.m_sel(n) .and. date_ds(:,2).eq.d_sel(n))
  
    precip_era5_temp 		= a1->var228(time_ds_ind,{minlat(n):maxlat(n)},:)
    precip_era5			= precip_era5_temp*1000
    copy_VarMeta(precip_era5_temp,precip_era5)
    delete(precip_era5_temp)

    precip2_era5_temp 		= a1->var228(time_ds_ind2,{minlat(n):maxlat(n)},:)
    precip2_era5		= precip2_era5_temp*1000
    copy_VarMeta(precip2_era5_temp,precip2_era5)
    delete(precip2_era5_temp)

  elseif (precip_source.eq."GPM") then
    if (maxlon(n).gt.180) then
      minlon2			= minlon(n)-360
      maxlon2			= maxlon(n)-360
    else
      minlon2			= minlon(n)
      maxlon2			= maxlon(n)
    end if 
  
    dateoffiles=systemfunc("ls "+dir_in1b+"3B-DAY-L.MS.MRG.3IMERG."+yyyy_sel(n)+mm_sel(n)+"{"+dd_start(n)+".."+dd_end(n)+"}-S000000-E235959.V0"+GPM_version+".nc4")
    fall 				= addfiles(dateoffiles,"r")                 ; read in the topo
  
    precip_gpm_temp     		= fall[:]->precipitationCal(:,{minlon2:maxlon2},{minlat(n):maxlat(n)})
  
  
    time_gpm 			= fall[:]->time
    time_gpm@calendar   		= "proleptic_gregorian"                                 ; CAREFUL; OVERWRITING OF UNITS MAY BE A PROBLEM, HAVENT CHECKED
    delete(time_gpm&time)
    time_gpm&time       		= time_gpm
    delete(precip_gpm_temp&time)
    precip_gpm_temp&time		= time_gpm
    precip_gpm          		= precip_gpm_temp(time|:,lat|:,lon|:)
    delete(precip_gpm_temp)
    
    date_gpm 			= calendar_decode2(time_gpm(:),0)
  end if
  
  ;*****************************************************************************************
  ; ERA5 DAILY MEAN 
  ;*****************************************************************************************
  
  b1 				= addfile(dir_in2+"era5_an_mslp_"+resolution_era5+"_dm_"+yyyy_sel(n)+mm_sel(n)+".nc4","r")
  c1 				= addfile(dir_in2+"era5_an_geopot_"+resolution_era5+"_dm_"+yyyy_sel(n)+mm_sel(n)+".nc4","r")
  e1 				= addfile(dir_in2+"era5_an_ewvf_"+resolution_era5+"_dm_"+yyyy_sel(n)+mm_sel(n)+".nc4","r")
  f1 				= addfile(dir_in2+"era5_an_nwvf_"+resolution_era5+"_dm_"+yyyy_sel(n)+mm_sel(n)+".nc4","r")
  
  time_dm 			= b1->time
  
  date_dm 			= calendar_decode2(time_dm(:),0)
  time_dm_ind			= ind(date_dm(:,0).eq.yyyy_sel(n) .and. date_dm(:,1).eq.m_sel(n) .and. date_dm(:,2).ge.d_start(n) .and. date_dm(:,2).le.d_end(n)) 
  time_dm_ind2			= ind(date_dm(:,0).eq.yyyy_sel(n) .and. date_dm(:,1).eq.m_sel(n) .and. date_dm(:,2).eq.d_sel(n)) 
  
  mslp_temp			= b1->var151(time_dm_ind,{minlat(n):maxlat(n)},:)
  mslp2_temp			= b1->var151(time_dm_ind2,{minlat(n):maxlat(n)},:)
  
  mslp				= mslp_temp/100.						; convert from Pa to hPa
  copy_VarMeta(mslp_temp,mslp)
  delete(mslp_temp)

  mslp2				= mslp2_temp/100.						; convert from Pa to hPa
  copy_VarMeta(mslp2_temp,mslp2)
  delete(mslp2_temp)
  
  z500_temp			= c1->var129(time_dm_ind,{plev_sel1},{minlat(n):maxlat(n)},:)
  z500_2_temp			= c1->var129(time_dm_ind2,{plev_sel1},{minlat(n):maxlat(n)},:)
  
  z500				= z500_temp/g_const
  copy_VarMeta(z500_temp,z500)
  delete(z500_temp)

  z500_2			= z500_2_temp/g_const
  copy_VarMeta(z500_2_temp,z500_2)
  delete(z500_2_temp)
  
  eivt				= e1->var71(time_dm_ind,0,{minlat(n):maxlat(n)},:)
  nivt				= f1->var72(time_dm_ind,0,{minlat(n):maxlat(n)},:)

  eivt2				= e1->var71(time_dm_ind2,0,{minlat(n):maxlat(n)},:)
  nivt2				= f1->var72(time_dm_ind2,0,{minlat(n):maxlat(n)},:)
  
  ;*****************************************************************************************
  ; FILTER IVT (ONLY PLOT VECTORS WHERE IVT > THRESH )
  ;*****************************************************************************************
  
  ivt 				= (eivt^2+nivt^2)^0.5
  ivt2 				= (eivt2^2+nivt2^2)^0.5
  
  copy_VarMeta(eivt,ivt)
  copy_VarMeta(eivt2,ivt2)
  
  ;*****************************************************************************************
  ; AVG CIRCULATION 
  ;*****************************************************************************************
  
  if (precip_source.eq."ERA5") then
    precip_era5_sum			= dim_sum_n_Wrap(precip_era5,0)
  elseif (precip_source.eq."GPM") then
    precip_gpm_sum			= dim_sum_n_Wrap(precip_gpm,0)
  end if
  
  mslp_avg				= dim_avg_n_Wrap(mslp,0)
  z500_avg				= dim_avg_n_Wrap(z500,0)
  
  eivt_avg				= dim_avg_n_Wrap(eivt,0)
  nivt_avg				= dim_avg_n_Wrap(nivt,0)
  
  ivt_avg					= (eivt_avg^2+nivt_avg^2)^0.5
  
  copy_VarMeta(eivt_avg,ivt_avg)
  
  eivt_avg_sel 				= where(ivt_avg.ge.ivt_dm_thresh,eivt_avg,0)
  nivt_avg_sel 				= where(ivt_avg.ge.ivt_dm_thresh,nivt_avg,0)
  
  copy_VarMeta(eivt_avg,eivt_avg_sel)
  copy_VarMeta(nivt_avg,nivt_avg_sel)

  eivt2_sel 				= where(ivt2.ge.ivt_dm_thresh2,eivt2,0)
  nivt2_sel 				= where(ivt2.ge.ivt_dm_thresh2,nivt2,0)
  
  copy_VarMeta(eivt2,eivt2_sel)
  copy_VarMeta(nivt2,nivt2_sel)
  
  ;*****************************************************************************************
  ; SMOOTHING 
  ;*****************************************************************************************
  
  wrf_smooth_2d(mslp_avg,smt_fct)
  wrf_smooth_2d(mslp2,smt_fct)
;  wrf_smooth_2d(z500_avg,smt_fct)
  
  ;*****************************************************************************************
  ; PLOT DAILY MEAN / SUMS 
  ;*****************************************************************************************

  inFormat 				= "%c"
  mm_string 				= cd_string(time_ds,inFormat)
 
  vcres1@vcRefMagnitudeF 		= ivt_dm_thresh
  vcres2@vcRefMagnitudeF 		= ivt_dm_thresh2
  
  gsn_define_colormap(wks,"CBR_wet")
  nr = NhlNewColor(wks,mp_gray,mp_gray,mp_gray)   ; add gray80, a lighter gray
  
  if (precip_source.eq."ERA5") then
;;    res1@gsnCenterString= "mean "+sprinti("%0.2i",toint(date_dm(time_dm_ind(0),2)))+" to "+sprinti("%0.2i",toint(date_dm(time_dm_ind(dimsizes(time_dm_ind)-1),2)))+" "+sprinti("%0.2i",toint(date_dm(time_dm_ind(0),1)))+"-"+sprinti("%0.2i",toint(date_dm(time_dm_ind(0),0)))                ; set the main title
    res1@gsnCenterString= region(n)+" "+date_dm(time_dm_ind(0),2)+" to "+date_dm(time_dm_ind(dimsizes(time_dm_ind)-1),2)+" "+mm_string(time_dm_ind(0))+" "+date_dm(time_dm_ind(0),0)                ; set the main title
    res2@gsnCenterString= region(n)+" "+date_dm(time_dm_ind2(0),2)+" "+mm_string(time_dm_ind(0))+" "+date_dm(time_dm_ind(0),0)                ; set the main title
    plot1(n) 		= gsn_csm_contour_map(wks,precip_era5_sum,res1)
    plot2(n) 		= gsn_csm_contour_map(wks,precip2_era5,res2)
  elseif (precip_source.eq."GPM") then
    res1@gsnCenterString= "mean "+sprinti("%0.2i",toint(date_gpm(0,2)))+" to "+sprinti("%0.2i",toint(date_gpm(dimsizes(date_gpm(:,2))-1,2)))+" "+sprinti("%0.2i",toint(date_gpm(0,1)))+"-"+date_gpm(0,0)                ; set the main title
    plot1(n)	 	= gsn_csm_contour_map(wks,precip_gpm_sum,res1)
  end if
  
  plot1_mslp 		= gsn_csm_contour(wks,mslp_avg,r1)
  plot1_z500 		= gsn_csm_contour(wks,z500_avg,r2)
  plot1_ivt 		= gsn_csm_vector(wks,eivt_avg_sel(::vec_int1,::vec_int1),nivt_avg_sel(::vec_int1,::vec_int1),vcres1)

  dum_pln1(n) 		= gsn_add_polyline(wks,plot1(n),(/lon_W(n),lon_E(n),lon_E(n),lon_W(n),lon_W(n)/),(/lat_S(n),lat_S(n),lat_N(n),lat_N(n),lat_S(n)/),resp)
  
  overlay(plot1(n),plot1_mslp(n))
  overlay(plot1(n),plot1_z500(n))
  overlay(plot1(n),plot1_ivt(n))
  
  plot2_mslp 		= gsn_csm_contour(wks,mslp2,r1)
  plot2_z500 		= gsn_csm_contour(wks,z500_2,r2)
  plot2_ivt 		= gsn_csm_vector(wks,eivt2_sel(::vec_int2,::vec_int2),nivt2_sel(::vec_int2,::vec_int2),vcres2)
  
  overlay(plot2(n),plot2_mslp(n))
  overlay(plot2(n),plot2_z500(n))
  overlay(plot2(n),plot2_ivt(n))
  
  ;*****************************************************************************************
  ; DELETE VARIABLES 
  ;*****************************************************************************************
  
  if (precip_source.eq."ERA5") then
    delete(time_ds)
    delete(date_ds)	
    delete(time_ds_ind)
    delete(time_ds_ind2)
    delete(precip_era5)	
  elseif (precip_source.eq."GPM") then
    delete(dateoffiles)
    delete(fall)
    delete(time_gpm)
    delete(precip_gpm)
    delete(date_gpm)
  end if
  
  delete(b1)
  delete(c1)
  delete(e1)
  delete(f1)

  delete(time_dm)
  delete(date_dm)
  delete(time_dm_ind)
  delete(time_dm_ind2)

  delete(mslp)
  delete(z500)
  delete(eivt)
  delete(nivt)
  
  delete(ivt)

  delete(eivt_avg_sel)
  delete(nivt_avg_sel)
  delete(eivt2_sel)
  delete(nivt2_sel)  

  delete(mm_string)

  delete(mslp2)
  delete(z500_2)
  delete(eivt2)
  delete(nivt2)
  delete(ivt2)

end do

;*****************************************************************************************
; PLOT 
;*****************************************************************************************

gsn_define_colormap(wks,"CBR_wet")
nr = NhlNewColor(wks,mp_gray,mp_gray,mp_gray)   ; add gray80, a lighter gray
gsn_panel(wks,((/plot1(0),plot1(1),plot1(2),plot2(0),plot2(1),plot2(2)/)),(/2,3/),pnlres1)

frame(wks)

;*****************************************************************************************
; PANEL PLOT 
;*****************************************************************************************

end
