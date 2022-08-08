# -*- coding: utf-8 -*-
"""
Created on Tue May 26 11:19:43 2020
Updated on Wed Jun 22 13:37:43 2022


    Title       : Storm Surge Warning and Inundation Module (SWIM)

    Description :   This is the main program to generate storm surge and inundation maps of a tropical cyclone.
                    The program takes the JMA storm surge netcdf (nc) output and IFSAR topographic data to
                    determine the potential flooding it may cause for a particular tropical cyclone. The 
                    methodology follows the simple bath-tub approach wherein the difference between the surge
                    height and the topography is expected to inundate the coastal communities.

    CAUTION     :  The program does not take into account 
                    a) Wave set-up
                    b) Astronomical tide 
                    c) Freshwater flooding from rainfall
                    d) River discharge
                    e) Flooding inside levees
                    f) Overtopping of levees
                    g) Forecast track uncertainty
        
                    
                    Author      : John Mark Dolendo
                    Email       : jmdolendo@dost.pagasa.gov.ph | jmdolendo18@gmail.com
                    Position    : Weather Specialist I
                    Division    : RDTD, DOST-PAGASA
"""


#-----------------------------------------------------------
#***** IMPORTING LIBRARIES AND SETTING DIRECTORIES *****
#-----------------------------------------------------------
import os
import sys
import shutil
import datetime
begin_time = datetime.datetime.now()
path = 'D:/Projects/SWIM/swim-2.0/'

scdir               = path      + "sc/v2/"
ncdir               = path      + "data/"
inpdir              = path      + "input/"
outdir              = path      + "output/"
inudir              = inpdir    + "inundation_shp/"



sys.path.append(scdir)
import config2 as config
import read_input2 as ri
import sswarn2 as ssw
import iwarn2 as iw


#-----------------------------------------------------------
#***** READING CONFIGURATION FILES *****
#-----------------------------------------------------------

(cat,   loc_name,   intl_name,  init_hr, 
        init_dy,    init_mo,    init_yr)                    = config.tc_info()
(crs, topo_crs, ph_coast, prov_bound, city_bound,  brgy_bound, 
       muni_coast, tc_marker, sig_ss)                               = config.infiles()

(ss_cols, ss_labs, i_cols, cat_name)                        = config.map_aes()

fname = cat + "_" + loc_name + "_" + init_yr + init_mo + init_dy + init_hr


outpath     = outdir    + fname +'/'
shppath     = outpath   + "shapefile/"
pngpath     = outpath   + "maps/"


if os.path.exists(outpath):
    if os.path.exists(shppath):
        shutil.rmtree(shppath)
        os.mkdir(shppath)
        
        if os.path.exists(pngpath):
            shutil.rmtree(pngpath)
            os.mkdir(pngpath)
             
        else:
            os.mkdir(pngpath)    

        
    else:
        os.mkdir(shppath)
        if os.path.exists(pngpath):
            shutil.rmtree(pngpath)
            os.mkdir(pngpath)
             
        else:
            os.mkdir(pngpath)    
else:
    os.mkdir(outpath)
    os.mkdir(shppath)
    os.mkdir(pngpath)


#-----------------------------------------------------------
#***** 1. GENERATE GEOSPATIAL INFORMATION FOR INPUT FILES *****
#-----------------------------------------------------------

step1_start = datetime.datetime.now()

print("\n(1/3) PROCESSING INPUT FILES:" )

(muni_pol_df, ph_prov, ph_city, ph_brgy, ph_coast_df, idf1, idf2, idf3, idf4, idf5)     = ri.read_bdy(inpdir, topo_crs, muni_coast, prov_bound, city_bound, brgy_bound, ph_coast, inudir)
(tc_track, tc_track_line, tc_track_buff)                                                = ri.proc_tc(outpath, fname, topo_crs)
(dates,times)                                                                           = ri.tc_dates(tc_track)

step1_end = datetime.datetime.now()

print( '***** DONE *****                       Elapsed time: ' + str( step1_end - step1_start))

#-----------------------------------------------------------
#***** 2. PROCESS STORM SURGE *****
#-----------------------------------------------------------

step2_start = datetime.datetime.now()

print("\n(2/3) CALCULATING STORM SURGE:")

muni_surge, df0_join_ts                                 = ssw.read_nc(outpath, ncdir, fname, ph_coast_df, sig_ss)




(ssurge_warn, ss_minx, ss_miny, ss_maxx, ss_maxy)       = ssw.plot_ss(outpath, shppath, ph_coast_df, muni_surge, fname, tc_track, 
                                                                      ph_prov, tc_track_line, tc_marker, inpdir, cat, loc_name, 
                                                                      init_hr, init_dy, init_mo, init_yr, ss_cols, ss_labs, dates, 
                                                                      times, tc_track_buff, intl_name, sig_ss)

df0_join_ts_T                                           = ssw.get_ts(df0_join_ts, init_yr, init_mo, init_dy, init_hr, pngpath)

                                          
step2_end= datetime.datetime.now()


print( '***** DONE *****                       Elapsed time: ' + str( step2_end - step2_start))
   


#-----------------------------------------------------------
#***** 3. PROCESS INUNDATION DUE TO STORM SURGE *****
#-----------------------------------------------------------
step3_start = datetime.datetime.now()
print('----------')

print("\nWOULD YOU LIKE TO CALCULATE INUNDATION (1: Yes, 2: No)?:" )
print('----------')

ans=None
while ans not in (1,2):
    ans = int(input("> "))
    if ans == 1:
        print('\n(3/3) CALCULATING INLAND FLOODING DUE TO STORM SURGE')
        iw.proc_inundation(muni_surge, muni_pol_df, crs, topo_crs,
                            ph_brgy,    ph_prov,     ph_city,  tc_track, 
                            tc_track_line, tc_marker, inpdir, outpath, shppath, 
                            pngpath, fname, ss_minx, ss_miny, ss_maxx, ss_maxy,
                            i_cols, cat_name, dates, times, idf1, idf2, idf3, idf4, idf5, sig_ss)

    elif ans==2:
        print('\n(3/3) INUDATION IS NOT CALCULATED')
    
    else:
        print('ERROR. Please enter 1 for Yes or 2 for No.')


step3_end= datetime.datetime.now()   


print( '\n***** DONE *****                        Elapsed time: ' +str( step3_end - step3_start))
 



#-----------------------------------------------------------
#***** DISCLAIMER *****
#-----------------------------------------------------------
print('\n\n----------')
print( "CAUTION :  The program does not take into account:")
print("             a) Wave set-up")
print("             b) Astronomical tide") 
print("             c) Freshwater flooding from rainfall")
print("             d) River discharge")
print("             e) Flooding inside levees")
print("             f) Overtopping of levees")
print("             g) Forecast track uncertainty")
print("             h) Climatological data")
print("             i) Landcover characteristics")

print('++++++++++++++++++++++++++++++++++++++++++++++++++')
print('NOTE: Output files are stored at ' + outpath)
print('++++++++++++++++++++++++++++++++++++++++++++++++++')



end_time = datetime.datetime.now()


print('Total runtime: ' +  str(end_time-begin_time))