#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 20:09:09 2020
Editted on Wed Jun 22 14:37:48 2022

Title           :   Read input script

Description     :   This script reads the input vector files such as the administrative boundary shapefiles. In addition, 
                    it also creates geospatial information for the tropical cyclone and produces a buffer zone to be used
                    in creating storm surge warning signals.
                    
Outputs         :   a) Geospatial information of administrative boundaries
                    b) Tropical Cyclone Track
                    c) Tropical Cyclone Buffer Zone

                    NOTE    :   Outputs herein are not exported. They are only used for calculations, analyses and mapping
                                purposes.
  
                    ------------------------------------------------------------------------
                    Author      : John Mark Dolendo
                    Email       : jmdolendo@dost.pagasa.gov.ph | jmdolendo18@gmail.com
                    Position    : Weather Specialist I
                    Division    : RDTD , PAGASA - DOST
                    ------------------------------------------------------------------------
"""

from shapely.geometry import Point, LineString
import geopandas as gpd
import pandas as pd


def read_bdy(input_dir, topo_crs, muni_coast, prov_bound, city_bound,  brgy_bound, ph_coast, inundation_dir):
    
    
    # Reading input vector files
    print(". . . . . Adding coastal municipal boundary shapefile")
    muni_pol_df = gpd.read_file(input_dir + muni_coast + ".shp")
    muni_pol_df = muni_pol_df.to_crs(epsg=topo_crs)
    
    print(". . . . . Adding brgy boundary shapefile")
    ph_brgy     = gpd.read_file(input_dir + brgy_bound + ".shp")
    ph_brgy     = ph_brgy.to_crs(epsg=topo_crs)
    
    print(". . . . . Adding municipal boundary shapefile")
    ph_city     = gpd.read_file(input_dir + city_bound + ".shp")
    ph_city     = ph_city.to_crs(epsg=topo_crs)
    
    print(". . . . . Adding provincial boundary shapefile")
    ph_prov     = gpd.read_file(input_dir + prov_bound + ".shp")
    ph_prov     = ph_prov.to_crs(epsg=topo_crs)

    print(". . . . . Adding country boundary shapefile")
    ph_coast_df = gpd.read_file(input_dir + ph_coast + ".shp")
    ph_coast_df = ph_coast_df.to_crs(epsg=topo_crs)
    
    print(". . . . . Adding other geospatial data")
    idf1 = gpd.read_file(inundation_dir + "inundation_ss1m.shp")
    idf1 = idf1.to_crs(epsg=topo_crs)
    
    idf2 = gpd.read_file(inundation_dir + "inundation_ss2m.shp")
    idf2 = idf2.to_crs(epsg=topo_crs)
    
    idf3 = gpd.read_file(inundation_dir + "inundation_ss3m.shp")
    idf3 = idf3.to_crs(epsg=topo_crs)
    
    idf4 = gpd.read_file(inundation_dir + "inundation_ss4m.shp")
    idf4 = idf4.to_crs(epsg=topo_crs)
    
    idf5 = gpd.read_file(inundation_dir + "inundation_ss5m.shp")
    idf5 = idf5.to_crs(epsg=topo_crs)
    
    
    
    return(muni_pol_df, ph_prov, ph_city, ph_brgy, ph_coast_df,
           idf1, idf2, idf3, idf4, idf5)




def proc_tc(outpath, fname, topo_crs):
    
    print(". . . . . Creating geospatial information of tropical cyclone")
    # Geospatial information of the tropical cyclone
    tc_track            = gpd.read_file(outpath + '/inifiles/' + fname + "_track.shp")  
    tc_track            = tc_track.to_crs(epsg=topo_crs)                   
    
    tc_track_line       = gpd.read_file(outpath+ '/inifiles/' + fname + "_track_line.shp")
    tc_track_line       = tc_track_line.to_crs(epsg=topo_crs)
    
    tc_track_buff       = gpd.read_file(outpath + '/inifiles/' + fname + "_buff.shp")
    tc_track_buff       = tc_track_buff.to_crs(epsg=topo_crs) 
  
  
    return (tc_track, tc_track_line, tc_track_buff)
 


def tc_dates(tc_track):
    
    dates = []
    times = []
        
    for date in range(len(tc_track['date'])):
        mm = tc_track['date'][date][:2]
        dd = tc_track['date'][date][2:4]
        hh = tc_track['date'][date][4:]
        dates.append(mm + '-' + dd)
        times.append( hh + ' UTC')
            
    return(dates,times)
    