# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:48:42 2022

@author: jmdolendo
"""

def tc_info():
    cat         = input("TC Category (e.g. TD, TS, STS, TY, STY)               :   ")
    loc_name    = input("TC Local Name (e.g. Yolanda)                          :   ")
    intl_name   = input("TC International Name (e.g. Haiyan)                   :   ")
    init_date   = input("Initialization date  (e.g. yyyymmddhh)                :   ")
    tc_rad_km   = input("Buffer Zone  (unit: km)                               :   ")
    tc_rad_km   = float(tc_rad_km)                      # Radius of the TC (unit: km)
    tc_rad_deg  = tc_rad_km / 111    
    init_hr     = init_date[8:]
    init_dy     = init_date[6:8]
    init_mo     = init_date[4:6]
    init_yr     = init_date[:4]    
    
    return(cat, loc_name, intl_name, tc_rad_deg, init_hr, init_dy, init_mo, init_yr)


def infiles():
    
    crs         = "epsg:4326"               # Projection: WGS84
    topo_crs    = 4326                      # Projection: WGS84
    tcfile      = "TC_Condition"            # Text file containing the input TC data in the JMA Model  
    muni_pts    = "muni_pts3"               # Shapefile that will be used to store storm surge output of JMA
    stn_ph      = "Station_Philippines"     # Output name of this program

    return(crs, topo_crs, tcfile,  muni_pts, stn_ph) 




    