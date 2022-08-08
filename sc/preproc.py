# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:45:27 2022

@author: jmdolendo
"""


# -----------------------------------------------------------
# Setting important directories
# -----------------------------------------------------------

path            = 'D:/Projects/SWIM/swim-2.0/'
scdir           = path + "sc/"
tcdir           = path + "data/"
munidir         = path + "input/"
outdir          = path + "output/"

# -----------------------------------------------------------
# Import necessary libraries
# -----------------------------------------------------------

import os
import sys
import shutil
import warnings
warnings.filterwarnings('ignore')
sys.path.append(scdir)

import preconf as config
import pretc as ptc
import precoast as pc


cat, loc_name, intl_name, tc_rad_deg, init_hr, init_dy, init_mo, init_yr    = config.tc_info()
crs, topo_crs, tcfile,  muni_pts, stn_ph                                    = config.infiles()


outdirname  = cat + '_' + loc_name + '_' + str(init_yr) + str(init_mo) + str(init_dy) + str(init_hr)
outpath     = outdir + outdirname + '/'
inifilepath = outpath + "inifiles/"


if os.path.exists(outpath):
    if os.path.exists(inifilepath):
        shutil.rmtree(inifilepath)
        os.mkdir(inifilepath)
    else:
        os.mkdir(inifilepath)
        
else:
    os.mkdir(outpath)
    os.mkdir(inifilepath)
    

# -----------------------------------------------------------
# Preprocess the input TC Data
# -----------------------------------------------------------
tc_data     = ptc.read_tc(tcdir, tcfile, loc_name)
tc_buff     = ptc.geo_tc(tc_data, outdirname, inifilepath, crs, tc_rad_deg)


# -----------------------------------------------------------
# Filter the municipality coastal data within the buffer zone
# -----------------------------------------------------------
muni_df     = pc.read_municoast(munidir, muni_pts, crs, topo_crs)
stnfile     = pc.select_municoast(muni_df, tc_buff, stn_ph, outpath)



print('\n\n********** Succefully generated the filtered coastal municipality points. ********** ')
print('Output path:\t' + outpath)
print("Filename:\t\t" + stn_ph +".txt")
print("************************************************************************************")





