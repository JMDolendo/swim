# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 16:06:49 2022

@author: jmdolendo
"""

import pandas as pd
from shapely.geometry import Point, LineString
import geopandas as gpd



def read_tc(tcdir, tcfile, loc_name):
    
    with open(tcdir + tcfile + ".txt", 'r') as tcinfo:
        readtc = tcinfo.readlines()
        colnames = readtc[3].split()
        tc_data = pd.DataFrame(columns=colnames)
        
        for i in range(4, len(readtc)):
            tc_data.loc[i-4] = readtc[i].split()
        tc_data["loc_name"] = loc_name
        tc_data[colnames[1:]] = tc_data[colnames[1:]].astype(float)
        
    return(tc_data)


def geo_tc(tc_data, outdirname, inifilepath, crs, tc_rad_deg):
    
    tc_geom             = [Point(xy) for xy in zip(tc_data.lon, tc_data.lat)]      
    tc_track            = gpd.GeoDataFrame(tc_data, geometry = tc_geom)
    tc_track.crs        = {'init': crs}
    tc_track.to_file(inifilepath + outdirname + '_track.shp')
   
    
    tc_track_line       = tc_track.groupby(['loc_name'])['geometry'].apply(lambda x: LineString(x.tolist()))
    tc_track_line       = gpd.GeoDataFrame(tc_track_line, geometry='geometry')
    tc_track_line.crs   = {'init':crs}
    tc_track_line.to_file(inifilepath + outdirname  + '_track_line.shp')

    
    tc_buff             = tc_track_line.copy()
    tc_buff['geometry'] = tc_buff.apply(lambda x: x.geometry.buffer(tc_rad_deg), axis=1)
    tc_buff.crs            ={'init':crs}
    tc_buff.to_file(inifilepath + outdirname + '_buff.shp')  
    
    
    return(tc_buff)