# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 20:09:09 2020
Updated on Wed Jun 22 14:37:48 2022

@author: jmdolendo
"""
from datetime import datetime, timedelta
import pandas as pd
import geopandas as gpd
from netCDF4 import Dataset
import numpy as np
#from shapely.geometry import Point
#import sys
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import folium
#import json
import warnings
import datetime
warnings.filterwarnings('ignore')
#from shapely.geometry import Point, LineString
from matplotlib.ticker import MultipleLocator




def read_nc(outpath, ncdir, fname, ph_coast_df, sig_ss):
    
    muni_pts_df     = pd.read_csv(outpath + '/Station_Philippines.csv')
    muni_pts_id     = muni_pts_df['Mun_Code'].tolist()
    muni_pts_xi     = muni_pts_df['xi'].tolist()
    muni_pts_yi     = muni_pts_df['yi'].tolist()


    nc          = Dataset(ncdir + fname +'.nc', 'r')
    lons        = nc.variables['lon'][:]
    lats        = nc.variables['lat'][:]
    dt          = []


    # Date of the data (0001-1-1 00:00) 
    yr          = nc.variables['time'].units[12]
    mo          = nc.variables['time'].units[14]
    dy          = nc.variables['time'].units[16]
    hh          = nc.variables['time'].units[18:20]
    mm          = nc.variables['time'].units[21:23]

    df0                                 = pd.DataFrame()
    df0[['Mun_Code', 'lon', 'lat']]     = muni_pts_df[['Mun_Code', 'xi', 'yi']]
    
    for i in range(0, len(nc.variables['time'])):
        td                  = int(nc.variables['time'][i].data.tolist())-48
        hr_to_date          = datetime.datetime.strptime(str('000')+ yr +'-'+ mo + '-' + dy + ' ' + hh + ":" + mm, '%Y-%m-%d %H:%M') + timedelta(hours=td)
        dt.append(hr_to_date.strftime( '%Y-%m-%d %H:%M'))
        z                   = nc.variables['z'][i].data
        z_val               = []
        for j in np.arange(0, len(muni_pts_id)):
            sqd_lat         = (lats-muni_pts_yi[j])**2
            sqd_lon         = (lons-muni_pts_xi[j])**2
            min_j_lat       = sqd_lat.argmin()
            min_j_lon       = sqd_lon.argmin()
            z_val.append(z[min_j_lat, min_j_lon])
            
        df0['ft'+ str(i)]= z_val
        


    df0_ts = pd.DataFrame()
    cols = []
    for k in df0.columns[3:]:
        muni_merge              = pd.merge(ph_coast_df, df0[['Mun_Code',k]], on = "Mun_Code", how="inner")
        muni_merge_filter       = muni_merge.groupby('Mun_Code')[k].max()
        df0_ts[k]               = muni_merge_filter.tolist()
        cols.append(k)
    
        
    
    
    # muni_merge_filter.to_frame()
    muni_merge_df           =  muni_merge_filter.reset_index()
    muni_merge_df.columns   = ['Mun_Code', 'z_max']
    
    
    muni_join       = ph_coast_df.merge(muni_merge_df, on="Mun_Code")                       # Merge the attributes of the points to Municipality boundary
    muni_surge      = muni_join[muni_join['z_max']>= sig_ss]
    
    
    df0_ts['z_max']     = df0_ts.max(axis=1)
    
    df0_ts['Mun_Code']  = muni_merge_filter.index.tolist()
    
    df0_ts              = df0_ts[df0_ts['z_max']>=sig_ss]
    
    df0_join            = df0_ts.merge(ph_coast_df, on="Mun_Code")
    df0_join_ts         = df0_join.groupby(cols + ['Pro_Name' , 'Pro_Code', 'Mun_Name', 'Mun_Code'])['z_max'].max()
    df0_join_ts         = df0_join_ts.to_frame()
    df0_join_ts          = df0_join_ts.reset_index()
    

    
    df0_join_ts.to_csv(outpath + '01_' + fname + '_ts.csv' )
    
   
    
    return(muni_surge, df0_join_ts)


def plot_ss(outpath, shppath, ph_coast_df, muni_surge, fname, tc_track,
            ph_prov, tc_track_line, tc_marker, inpdir, cat, loc_name, 
            init_hr, init_dy, init_mo, init_yr, ss_cols, ss_labs, dates, times, tc_track_buff, intl_name, sig_ss):
     
    print(". . . . . Generating the storm surge hazard table (.csv)")
    ss_warning  = gpd.overlay(ph_coast_df, muni_surge, how='intersection')           # Joining the storm surge values to coastal municipalities
    
    # Creating color code warnings
    ss_class    = []
    for ss_max in ss_warning['z_max']:
            if sig_ss <= ss_max < 1:
                ss_class.append('#0000ff')                                          # Blue 0.1 - 1 meter
            elif 1 <= ss_max <= 2:
                ss_class.append('#ffff14')                                          # Yellow for up to to 2-m surge
            elif 2 < ss_max <= 3:
                ss_class.append('#f97306')                                          # Orange for 2 to 3-m surge
            elif ss_max > 3:
                ss_class.append('#e50000')                                          # Red for more than 3-m surge
            else:
                ss_class.append('#000000')                                          # No color for no surge
    
    ss_warning['ss_class']  = ss_class
    ss_warning              = ss_warning[ss_warning['ss_class']!='#000000']
    ss_warning_df           = ss_warning.groupby(['Pro_Name_1','Pro_Code_1', 'Mun_Name_1', 'Mun_Code_1'])['z_max'].max()    
    ss_warning_df           = ss_warning_df.to_frame()
    ss_warning_df           = ss_warning_df.reset_index()
    ss_warning_df2           = ss_warning.groupby(['Pro_Name_1','Pro_Code_1'])['z_max'].max()   
    
    ss_warning_df.to_csv(outpath + "00_Storm_surge_" + fname + '.csv')             # Exporting to CSV
    ss_warning_df2.to_csv(outpath + "00_Storm_surge_" + fname + '_PROV.csv') 
    
    print(". . . . . Generating the storm surge hazard shapefile (.shp)")
    ss_warning.to_file(shppath   +"00_Storm_surge_"  + fname + '.shp')             # Exporting to shapefile
    #ss_warning.to_file(shppath   +"00_Storm_surge_"  + fname + '.geojson', driver="GeoJSON") 
 
    
    # ------------------------------
    # Creating Static Map
    # ------------------------------
    
    print(". . . . . Generating storm surge hazard map (.png)")
    
    fig,ax = plt.subplots(figsize=(30,20))      
    
    
    # Specifiying map boundaries 
    
    ss_minx = ss_warning.bounds.minx.min()
    ss_miny = ss_warning.bounds.miny.min()
    ss_maxx = ss_warning.bounds.maxx.max()
    ss_maxy = ss_warning.bounds.maxy.max()
    
    
    ssm = Basemap(llcrnrlon = ss_minx - 2,
                  llcrnrlat = ss_miny - 2,
                  urcrnrlon = ss_maxx + 2,
                  urcrnrlat = ss_maxy + 2,
                  resolution = 'h',
                  epsg = 4326, ax = ax)

            
    ssm.drawparallels(np.arange(0,30, 2), labels = [1,0,0,0], ax=ax, color = 'gray')
    ssm.drawmeridians(np.arange(100,130,2), labels = [0,0,0,1],ax=ax, color = 'gray')
    ssm.drawmapboundary(fill_color = np.array([0.59375, 0.71484375, 0.8828125]),ax=ax)   
    
        
    ph_prov.plot(ax=ax, facecolor="gray", edgecolor = "white")                      # Plotting provincial boundaries
    ss_warning.plot(ax=ax, color=ss_warning['ss_class'] , linewidth=5)              # Plotting the delineated coastal storm surge affected communities
    tc_track_buff.plot(ax=ax, facecolor = "black", alpha = 0.1, edgecolor="black",  linewidth = 3, linestyle = '-')               # Plotting the Buffer Zone
    tc_track_line.plot(ax=ax, color = "blue", linewidth=3)                          # Plotting TC Track
    
    
    
    ax.set_title(cat + ' ' + loc_name + '(' + intl_name + ')' +' Storm Surge Hazard Map', 
                 fontsize = 35, fontweight = 'bold')
    
    ax.text(0.85, 0.97, 'Initial: ' + init_yr + init_mo  + init_dy + init_hr ,
            transform=ax.transAxes, fontsize = 24, 
            verticalalignment='top', 
            horizontalalignment='center', 
            bbox = dict(boxstyle='round', facecolor = 'wheat', alpha = 0.8))
            
           
            
    def getImage(path):
        return OffsetImage(plt.imread(path, format='png'), zoom = 0.07)
        
    marker = inpdir + tc_marker + ".png"
    for x0, y0, date, time in zip(tc_track['lon'], tc_track['lat'], dates, times):
        ab = AnnotationBbox(getImage(marker), (x0,y0), frameon=False)
        ax.add_artist(ab)
        ax.annotate(date+"\n"+time , (x0,y0), textcoords = "offset points",
                    xytext = (0,55), ha="center", fontsize= 20,
                    bbox = dict(boxstyle='round', facecolor = 'white', alpha = 0.5))
        
    # Customizing the legend
    lines       = [Line2D([0],[0], color=c, linewidth=5, linestyle='-') for c in ss_cols]
    ax.legend(lines, ss_labs, loc = 'lower left', title = "Surge Height (m)", fontsize='xx-large')    
    
 
    fig.savefig(outpath + '00_Storm_Surge_' + fname +'.png', dpi=200)
    plt.close(fig)
    
    
    
    # ------------------------------
    # Creating an Interactive Map
    # ------------------------------
  
    print(". . . . . Generating storm surge hazard interactive map (.html)")
    midx = (ss_maxx + ss_minx)/2
    midy = (ss_maxy + ss_miny)/2
        
    #ss_map = folium.Map([midy, midx], zoom_start=6, tiles="Stamen Terrain")
    ss_map = folium.Map([midy, midx], zoom_start=6)
    
    folium.TileLayer('openstreetmap').add_to(ss_map)
    folium.GeoJson(tc_track_buff.to_json(), style_function=lambda x:{
                'color':'gray', 'weight': 1, 'alpha':0.1}).add_to(ss_map)
    folium.GeoJson(ss_warning.to_json(), style_function=lambda x:{
                'fillColor':x['properties']['ss_class'], 'color':x['properties']['ss_class'], 'weight': 1}).add_to(ss_map)
            
    folium.GeoJson(tc_track_line.to_json(),style_function=lambda x:{
                'color':'blue', 'weight': 2}).add_to(ss_map)
    
    for loc in range(0,len(tc_track)):
        folium.Marker(location=[tc_track['lat'][loc], tc_track['lon'][loc]], 
                      popup=    str(datetime.datetime.strptime(str(tc_track['date'][loc][:2]), "%m").strftime("%b")) + '-' +
                                str(tc_track['date'][loc][2:4]) + ', ' +
                                str(tc_track['date'][loc][4:6]) + '00 UTC\n' +
                                str(tc_track['Pcenter'][loc]) + ' hPa').add_to(ss_map)
    # folium.GeoJson(tc_track.to_json(), popup=tc_track['mslp'], style_function=lambda x:{
    #             'color':'blue', 'weight': 5}).add_to(ss_map)
    ss_map.save(outpath + "00_Storm_surge_" + fname + '.html')   
    
    
    return(ss_warning, ss_minx, ss_miny, ss_maxx, ss_maxy)


def get_ts(df0_join_ts, init_yr, init_mo, init_dy, init_hr, pngpath):
       
    a = df0_join_ts.T
    a.columns = df0_join_ts['Mun_Code'].tolist()
    a = a.reset_index()
    df0_join_ts_T = a.drop(a.index[48:])
    df0_join_ts_T = df0_join_ts_T[1:].replace(-999.0, np.nan)
    
    for i in a.columns[1:]:
       mun              = df0_join_ts[df0_join_ts['Mun_Code']==i]['Mun_Name'].tolist()[0]
       pro              = df0_join_ts[df0_join_ts['Mun_Code']==i]['Pro_Name'].tolist()[0]
       fig,ax          = plt.subplots(figsize=(20,10))
       ax.plot(df0_join_ts_T.index, df0_join_ts_T[i], color='xkcd:dark cyan', marker ='*', linewidth = 2, markersize = 5)
       ax.set_ylabel("Storm Surge (m)",fontsize=25)
       ax.set_xlabel("Forecast Time (hr)",fontsize=25)
       ax.text(0.70, 0.96, "INITIAL = " + init_yr + init_mo + init_dy +  init_hr, 
               transform = ax.transAxes, fontsize=25,verticalalignment='top', 
               bbox = dict(boxstyle='round',facecolor='wheat', alpha=0.5))
       
       ax.xaxis.set_major_locator(MultipleLocator(6))
       ax.xaxis.set_minor_locator(MultipleLocator(1))
       ax.set_ylim(-2.0, 5.0)
       ax.set_xlim(0, 48)
       
       
       ax.set_title(mun + ' (' + pro + ')', fontsize = 20)
       
       ax.grid(b=True, which = 'major', color = '#666666' , linestyle = '--', alpha = 0.6)
       ax.grid(b=True, which = 'minor', color = '#999999' , linestyle = '-', alpha = 0.1)
       
       plt.axhline(y=0, color = "xkcd:coral", linewidth = 2)
       fig.savefig(pngpath + 'ts_'+  pro + '_' + mun +'.png', dpi=300)
       plt.close(fig)
       
       
    return(df0_join_ts_T)
 