# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 13:33:35 2022

@author: jmdolendo
"""
from datetime import datetime, timedelta
import pandas as pd
import geopandas as gpd
from netCDF4 import Dataset
import numpy as np
from shapely.geometry import Point
import sys
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import folium
import json
import warnings
import datetime
warnings.filterwarnings('ignore')
from shapely.geometry import Point, LineString



ncdir       = "C:/Users/htmirds/Downloads/"
ncfile      = "ty_haiyan2013.nc"
munidir     = "C:/swim/output/STY_Yolanda_20130110700/"

munpts      = "Station_Philippines.csv"

mun_shp_dir =  "C:/swim/input/"
mun_pts_shp = "ph_coast_merge2.shp"
   
crs         = "epsg:4326"               # Projection: WGS84
topo_crs    = 4326   

sig_ss      = 0.1


muni_pts_gdf = gpd.read_file(mun_shp_dir + mun_pts_shp)
muni_pts_gdf = muni_pts_gdf.to_crs(epsg=topo_crs)


muni_pts_df = pd.read_csv(munidir + munpts)


muni_pts_id = muni_pts_df['Mun_Code'].tolist()
muni_pts_xi = muni_pts_df['xi'].tolist()
muni_pts_yi = muni_pts_df['yi'].tolist()


nc          = Dataset(ncdir + ncfile, 'r')
lons        = nc.variables['lon'][:]
lats        = nc.variables['lat'][:]
dt          = []


# Date of the data (0001-1-1 00:00) 
yr      = nc.variables['time'].units[12]
mo      = nc.variables['time'].units[14]
dy      = nc.variables['time'].units[16]
hh      = nc.variables['time'].units[18:20]
mm      = nc.variables['time'].units[21:23]

df0 = pd.DataFrame()
df0[['Mun_Code', 'lon', 'lat']]= muni_pts_df[['Mun_Code', 'xi', 'yi']]
for i in range(0, len(nc.variables['time'])):
    td              = int(nc.variables['time'][i].data.tolist())-48
    hr_to_date      = datetime.datetime.strptime(str('000')+ yr +'-'+ mo + '-' + dy + ' ' + hh + ":" + mm, '%Y-%m-%d %H:%M') + timedelta(hours=td)
    dt.append(hr_to_date.strftime( '%Y-%m-%d %H:%M'))
    z               = nc.variables['z'][i].data
    z_val           = []
    for j in np.arange(0, len(muni_pts_id)):
        sqd_lat     = (lats-muni_pts_yi[j])**2
        sqd_lon     = (lons-muni_pts_xi[j])**2
        min_j_lat   = sqd_lat.argmin()
        min_j_lon   = sqd_lon.argmin()
        z_val.append(z[min_j_lat, min_j_lon])
        
    df0['ft'+ str(i)]= z_val



for k in df0.columns[3:]:
    muni_merge = pd.merge(muni_pts_gdf, df0[['Mun_Code',k]], on = "Mun_Code", how="inner")
    muni_merge_filter = muni_merge.groupby('Mun_Code')[k].max()
muni_merge_filter.index.tolist()
muni_merge_filter.to_frame()
muni_merge_df =  muni_merge_filter.reset_index()
muni_merge_df.columns = ['Mun_Code', 'z_max']


muni_join   = muni_pts_gdf.merge( muni_merge_df, on="Mun_Code")                       # Merge the attributes of the points to Municipality boundary
muni_surge  = muni_join[muni_join['z_max']>=sig_ss]       
muni_surge.plot()    
    
    