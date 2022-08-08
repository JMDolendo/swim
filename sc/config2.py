#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 11:37:14 2020
Updated on Wed Jun 22 14:37:48 2022


    Description :   This is the configuration file wherein the parameters required to run the main program
                    are defined. It includes tropical cyclone information, coastal administrative boundaries, 
                    significant storm surge height and map visualization parameters.
        
                    
                    Author      : John Mark Dolendo
                    Email       : jmdolendo@dost.pagasa.gov.ph | jmdolendo18@gmail.com
                    Position    : Weather Specialist I
                    Division    : RDTD, DOST-PAGASA

"""


def tc_info():
    
    
    cat             = input("TC Category (e.g. TD, TS, STS, TY, STY)               :   ")
    loc_name        = input("TC Local Name (e.g. Yolanda)                          :   ")
    intl_name       = input("TC International Name (e.g. Haiyan)                   :   ")
    init_date       = input("Initialization date  (e.g. yyyymmddhh)                :   ")
    init_hr         = init_date[8:]
    init_dy         = init_date[6:8]
    init_mo         = init_date[4:6]
    init_yr         = init_date[:4]
    
        
    return(cat, loc_name, intl_name, init_hr, init_dy, init_mo, init_yr)


def infiles():    

       
    crs             = "epsg:4326"               # Projection: WGS84
    topo_crs        = 4326
    ph_coast        = "ph_coast_merge2"          # Philippine Coastline shapefile
    prov_bound      = "prov_bound_psa2016"      # Provincial boundary from PSA shapefile
    city_bound      = "city_bound_psa2016"      # Municipality boundary from PSA shapefile
    brgy_bound      = "brgy_bound_psa2016"      # Brgy boundary form PSA shapefile
    muni_coast      = "muni_coast2"             # Municipality coastal boundary shapefile
    tc_marker       = "tc_marker_b"             # TC symbols
    sig_ss          = 0.1
    
    return(crs, topo_crs, ph_coast, prov_bound, city_bound,  brgy_bound, 
           muni_coast, tc_marker, sig_ss) 


def map_aes():
    
    ss_cols     = ['blue', 'yellow', 'orange', 'red']                           # Storm Surge Map Color Legend
    ss_labs     = ['less than 1m', '1 to 2m', '2 to 3m', 'more than 3m']               # Storm Surge Map Labels 
    
    i_cols      = ['yellow','orange','red', 'purple']                   # Inundation warning colors
    cat_name    = [ "up to 1 m",    "1 - 2 m",
                   "2 - 3 m",      "more than 3 m", ""]                 # Inundation labels 
    
    return(ss_cols, ss_labs, i_cols, cat_name)
