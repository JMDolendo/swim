# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 16:36:41 2022

@author: jmdolendo
"""

import geopandas as gpd

def read_municoast(munidir, muni_pts, crs, topo_crs):
    
    muni_df = gpd.read_file(munidir + muni_pts + ".shp")
    muni_df = muni_df.to_crs(epsg=topo_crs)
    muni_df.crs     = {'init': crs}
    
    return(muni_df)

def select_municoast(muni_df, tc_buff, stn_ph, outpath):
    
    muni_select = gpd.overlay(muni_df, tc_buff, how='intersection')
    muni_select = muni_select[['xi', 'yi', 'Mun_Code']]
    muni_csv = muni_select[['xi', 'yi', 'Mun_Code']]
    muni_csv.to_csv(outpath + stn_ph + ".csv")
    
    stnfile = open(outpath + stn_ph + '.txt', "w")
    stnfile.writelines(str(len(muni_select)) + "\t :Number of Station\n")
    stnfile.writelines(str(1) + "\t :Unit of Lat/Lon (0: ddmm, 1: degree)\n")
    stnfile.writelines("Latitude\t Longitude\t point name\n")
    for i in range(0, len(muni_select)):
        
        stnfile.writelines((str('{:9.6f}'.format(muni_select.iloc[i].tolist()[1])))+ '\t')
        stnfile.writelines((str('{:9.6f}'.format(muni_select.iloc[i].tolist()[0])))+ '\t')
        stnfile.writelines((str(muni_select.iloc[i].tolist()[2]))+ '\n')
    
    stnfile.close()
    
    return(stnfile)