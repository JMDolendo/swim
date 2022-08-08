# -*- coding: utf-8 -*-
"""

Created on  Wed Jun 10 20:09:09 2020
Edited on Wed Jun 22 13:37:43 2022

Title           :   Inundation Script

Description     :   This script calculates possible coastal inundation depth and extent due to Storm Surge using bath-tub
                    method. It utilizes IFSAR 5-m topographic data as well as the storm surge output of the Japan
                    Meteorological Agency Model.
                    
Outputs         :   a) Map (.png)
                    b) Reclassified inundation shapefile (.shp)
                    c) List of coastal affected communities (.csv)
                    d) Interactive map (.html)
  
                    ------------------------------------------------------------------------
                    Author      : John Mark Dolendo
                    Email       : jmdolendo@dost.pagasa.gov.ph | jmdolendo18@gmail.com
                    Position    : Weather Specialist I
                    Division    : RDTD , PAGASA - DOST
                    ------------------------------------------------------------------------
                    
                    
"""


import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
#from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1.inset_locator import  mark_inset
import folium
#import rioxarray
#import xarray
import shapely.speedups
shapely.speedups.enable()
#import adjustText as aT
import datetime



def proc_inundation(muni_surge, muni_pol_df, crs, topo_crs,
                    ph_brgy,    ph_prov,     ph_city,  tc_track, 
                    tc_track_line, tc_marker, inpdir, outpath, shppath, 
                    pngpath, fname, ss_minx, ss_miny, ss_maxx, ss_maxy,
                    i_cols, cat_name, dates, times, idf1, idf2, idf3, idf4, idf5,sig_ss):
    
   
    # Getting the maximum surge per municipality
    
    mun_code        =   muni_surge.groupby(['Mun_Code', 'Mun_Name', 'Pro_Code', 'Pro_Name'])['z_max'].max()
    mun_code_filter =   mun_code.to_frame()
    mun_code_df     =   mun_code_filter.reset_index()
   

    print('\nAffected Municipalities (' + str(len(mun_code_df)) +')\n' )
    
  
    
    
    nd_df = gpd.GeoDataFrame(columns=['OBJECTID_1', 'Id', 'gridcode', 'Shape_Leng_1', 'Shape_Area_1',
       'OBJECTID_2', 'Reg_Code', 'Reg_Name', 'Pro_Code', 'Pro_Name',
       'Mun_Code', 'Mun_Name', 'Shape_Leng_2', 'Shape_Area_2', 'geometry',
       'i_cols'])
    
    
    print("\nGenerate PNG Maps? \n0 = No \n1 = Yes")
    
    ans=None
    while ans not in (0,1,2):
            ans = int(input("> "))
            counter = 1
            
            for mc, mn in zip(mun_code_df['Mun_Code'], mun_code_df['Mun_Name']):

                    print(str(counter) + '. ' + mn)
                    counter = counter + 1
                   
                   
                    pc              =   mun_code_df[mun_code_df['Mun_Code'] == mc]['Pro_Code'].values.tolist()[0]
                    pn              =   mun_code_df[mun_code_df['Mun_Code'] == mc]['Pro_Name'].values.tolist()[0]
                    
                    prov_shp        =   ph_prov[ph_prov['Pro_Code'] == pc]          # Provincial boundary
                    prov_shp.crs    =   {'init':crs}
                    
                    mun_shp         =  ph_city[ph_city['Mun_Code'] == mc]
                    mun_shp.crs     =   {'init':crs}
                    
                    brgy_shp        =  ph_brgy[ph_brgy['Mun_Code'] == mc]
                    brgy_shp.crs     =   {'init':crs}
                    
                    
                    
                    muni_df = muni_pol_df[muni_pol_df['Mun_Code']==mc]
                    muni_df.crs = {'init':crs}
                    muni_df.reset_index(drop=True,inplace=True)
                    max_ss = mun_code_df[mun_code_df['Mun_Code']==mc]['z_max'].tolist()[0]
                    
                    if max_ss > sig_ss and  max_ss < 1.1 :
                       #print(max_ss,1)
                       #print(str(counter) + '.' + pn + '_' + mn)
                       mask = idf1.intersects(muni_df.loc[0,'geometry'])
                       mask_df = idf1.loc[mask]
                       if mask_df.empty:
                           clip_df = gpd.GeoDataFrame()
                       else:
                           clip_df = gpd.overlay(mask_df, muni_df, how='intersection')
                       
                    elif max_ss > 1.9 and  max_ss < 2.1 :
                       #print(max_ss,2)
                       #print(str(counter) + '.' + pn + '_' + mn)
                       mask = idf2.intersects(muni_df.loc[0,'geometry'])
                       mask_df = idf2.loc[mask]
                       if mask_df.empty:
                           clip_df = gpd.GeoDataFrame()
                       else:
                           clip_df = gpd.overlay(mask_df, muni_df, how='intersection')
                       
                       
                    elif max_ss > 2.9 and  max_ss < 3.1    :
                       #print(max_ss,3)
                       #print(str(counter) + '.' + pn + '_' + mn)
                       mask = idf3.intersects(muni_df.loc[0,'geometry'])
                       mask_df = idf3.loc[mask]
                       if mask_df.empty:
                           clip_df = gpd.GeoDataFrame()
                       else:
                           clip_df = gpd.overlay(mask_df, muni_df, how='intersection')
                      
                       
                    elif max_ss > 3.9 and  max_ss < 4.1 :
                       #print(max_ss,4)
                       #print(str(counter) + '.' + pn + '_' + mn)
                       mask = idf4.intersects(muni_df.loc[0,'geometry'])
                       mask_df = idf4.loc[mask]
                       if mask_df.empty:
                           clip_df = gpd.GeoDataFrame()
                       else:
                           clip_df = gpd.overlay(mask_df, muni_df, how='intersection')
                       
                    elif max_ss > 4.9 and  max_ss <= 5.1 :
                       #print(max_ss,5)
                       #print(str(counter) + '.' + pn + '_' + mn)
                       mask = idf5.intersects(muni_df.loc[0,'geometry'])
                       mask_df = idf5.loc[mask]
                       if mask_df.empty:
                           clip_df = gpd.GeoDataFrame()
                       else:
                           clip_df = gpd.overlay(mask_df, muni_df, how='intersection')
                       
            
                    #elif round(mun_code_df[mun_code_df['Mun_Code']==mc]['max']) == 1 :
                    else: 
                        clip_df = gpd.GeoDataFrame()
            
        
           
                    if clip_df.empty:
                        clip_df = gpd.GeoDataFrame()
                    else:
                        i_class    = []
                        for i_code in clip_df['gridcode']:
                                    if  i_code == 1:
                                        i_class .append('#ffff14')                                          # Yellow for up to to 1-m inundation
                                    elif i_code == 2:
                                        i_class .append('#f97306')                                          # Orange for 1 to 2-m inundation
                                    elif i_code == 3:
                                        i_class .append('#e50000')                                          # Red for for 2 to 3-m inundation
                                    else:
                                        i_class.append('#8E53E5')
                        
                        clip_df['i_cols'] = i_class
                        
                        if ans ==0:
                            None
                        elif ans ==  1:
                         
                            # ********************************************
                            # FIGURE 1 (main plot)
                            # ********************************************
                    
                            fig         =   plt.figure(figsize=(30,15))
                            grid        =   plt.GridSpec(1,7, wspace=0.1)
                            ax1         =   fig.add_subplot(grid[0, 0:4])
                            ax2         =   fig.add_subplot(grid[0, 4:7])
                                        
                                    
                                               
                            m1 = Basemap(llcrnrlon = ss_minx - 2,
                                                llcrnrlat = ss_miny - 2,
                                                urcrnrlon = ss_maxx + 2,
                                                urcrnrlat = ss_maxy + 2,
                                                resolution = 'h',
                                                epsg = topo_crs, ax=ax1)
                                    
                                    
                            m1.shadedrelief(scale=0.7, ax=ax1)
                            m1.drawparallels(np.arange(0,30, 2), labels = [1,0,0,0], ax=ax1, color = 'gray')
                            m1.drawmeridians(np.arange(100,130,2), labels = [0,0,0,1],ax=ax1, color = 'gray')
                                        
                            ph_prov.plot(ax=ax1, facecolor='none', edgecolor = "black")
                            prov_shp.plot(ax=ax1, facecolor='red')
                            tc_track_line.plot(ax=ax1, color = "blue", linewidth=3) 
                            ax1.set_title(pn + " PROVINCE", fontsize=30, fontweight='bold')
                                    
                            # Plotting TC track with logo and dates   
                            
                            def getImage(path):
                                return OffsetImage(plt.imread(path, format='png'), zoom = 0.07)    
                                    
                            marker = inpdir + tc_marker + ".png"
                            for x0, y0, date, time in zip(tc_track['lon'], tc_track['lat'], dates, times):
                                ab = AnnotationBbox(getImage(marker), (x0,y0), frameon=False)
                                ax1.add_artist(ab)
                                ax1.annotate(date+"\n"+time , (x0,y0), textcoords = "offset points",
                                                      xytext = (0,55), ha="center", backgroundcolor = "white",fontsize= 12)
                                        
                                        
                                    
                            
                            # ********************************************
                            # FIGURE 2 (main plot)
                            # ********************************************
                                    
                            pll_min = mun_shp.bounds.miny.tolist()[0]
                            pll_max = mun_shp.bounds.maxy.tolist()[0]
                            mrd_min = mun_shp.bounds.minx.tolist()[0]
                            mrd_max = mun_shp.bounds.maxx.tolist()[0]
                                    
                                    
                            m2 = Basemap( llcrnrlon = mrd_min - 0.001,
                                                  llcrnrlat = pll_min - 0.001,
                                                  urcrnrlon = mrd_max + 0.001,
                                                  urcrnrlat = pll_max + 0.001,
                                                  resolution = 'h',
                                                  epsg = topo_crs, ax=ax2)
                                       
                                        
                            m2.drawmapboundary(fill_color = np.array([0.59375, 0.71484375, 0.8828125]),ax=ax2)
                            m2.drawparallels(np.arange(pll_min,pll_max, 0.1), labels = [0,1,0,0], ax=ax2, color = 'gray')
                            m2.drawmeridians(np.arange(mrd_min,mrd_max, 0.1), labels = [0,0,0,1],ax=ax2, color = 'gray')
                                     
                                               
                            ph_city.plot(ax=ax2, color = np.array([0.9375, 0.9375, 0.859375]), edgecolor = "gray", linestyle='--')           
                            mun_shp.plot(ax=ax2,  facecolor = 'gray', linewidth= 2)
                            brgy_shp.plot(ax=ax2, facecolor = 'none', edgecolor = "white", linestyle = '--', alpha=0.5)
                            mun_shp.plot(ax=ax2,  facecolor = 'none', edgecolor='black', linewidth=2)
                            clip_df.plot(ax=ax2, color = clip_df['i_cols'])
                                    
                                   
                                            
                            ax2.set_title(mn, fontsize=30, fontweight='bold')
                            ax2.set_ylabel('')
                            ax2.set_xlabel('')        
                                                
                                               
                            lines  = [Line2D([0],[0], color=c, linewidth=5, linestyle='-') for c in i_cols]
                            ax2.legend(lines, cat_name, loc = 'lower left', title = "Inundation Height (m)", fontsize='medium')
                                    
                            mark_inset(ax1, ax2, loc1=2, loc2=3, fc='none', ec='black', linestyle='--', linewidth=2)
        
                                    
                            plt.savefig(pngpath + pn + '_' + mn + '.png', dpi=200)
                    
                        else:
                            print('ERROR. Please enter either 0 or 1.') 
                    
                    nd_df = pd.concat([nd_df,clip_df])        
            
                    
                    
              
            # elif ans == 2:
            #         p_list = nd_df['Pro_Code'].unique().tolist()
                        
            #         for prc in p_list:
            #                 prn = ph_prov[ph_prov['Pro_Code'] == prc]['Pro_Name'].tolist()[0]
            #                 prov_shp = ph_prov[ph_prov['Pro_Code'] == prc]
            #                 prov_shp.crs = {'init':crs}
                            
            #                 mun_shp = ph_city[ph_city['Pro_Code'] == prc]
            #                 mun_shp.crs = {'init':crs}
                            
            #                 mun_shp_cp = mun_shp.copy()
            #                 mun_shp_cp['center'] = mun_shp_cp['geometry'].centroid
            #                 mun_pts = mun_shp_cp.copy()
            #                 mun_pts.set_geometry("center", inplace=True)
                                                
            #                 brgy_shp = ph_brgy[ph_brgy['Pro_Code'] == prc]
            #                 brgy_shp.crs = {'init':crs}   
                           
                            
            #                 i_shp = nd_df[nd_df['Pro_Code']==prc]
                            
            #                 fig,ax = plt.subplots(figsize=(20,10))
                            
            #                 pll_min = prov_shp.bounds.miny.tolist()[0]
            #                 pll_max = prov_shp.bounds.maxy.tolist()[0]
            #                 mrd_min = prov_shp.bounds.minx.tolist()[0]
            #                 mrd_max = prov_shp.bounds.maxx.tolist()[0]
                            
                            
            #                 bm = Basemap( llcrnrlon = mrd_min - 0.005,
            #                               llcrnrlat = pll_min - 0.005,
            #                               urcrnrlon = mrd_max + 0.005,
            #                               urcrnrlat = pll_max + 0.005,
            #                               resolution = 'h',
            #                               epsg = topo_crs, ax=ax)
                               
                                
            #                 bm.drawmapboundary(fill_color = np.array([0.59375, 0.71484375, 0.8828125]),ax=ax)
            #                 bm.drawparallels(np.arange(pll_min,pll_max, 1.0), labels = [0,1,0,0], ax=ax, color = 'gray')
            #                 bm.drawmeridians(np.arange(mrd_min,mrd_max, 1.0), labels = [0,0,0,1],ax=ax, color = 'gray')
                             
                                       
            #                 ph_city.plot(   ax=ax, color = np.array([0.9375, 0.9375, 0.859375]), edgecolor = "gray", linestyle='--')           
            #                 mun_shp.plot(   ax=ax,    facecolor = 'gray', linewidth= 2)
            #                 brgy_shp.plot(  ax=ax,    facecolor = 'none', edgecolor = "white", linestyle = '--', alpha=0.5)
            #                 mun_shp.plot(   ax=ax,    facecolor = 'none', edgecolor='black', linewidth=2)
            #                 i_shp.plot(   ax=ax, color = i_shp['i_cols'])
                           
                           
                                    
            #                 ax.set_title( prn + ' PROVINCE', fontsize=30, fontweight='bold')
            #                 ax.set_ylabel('')
            #                 ax.set_xlabel('')        
                                        
                                       
            #                 lines  = [Line2D([0],[0], color=c, linewidth=5, linestyle='-') for c in i_cols]
            #                 ax.legend(lines, cat_name, loc = 'lower left', title = "Inundation Height (m)", fontsize='large') 
                            
            #                 plt.savefig(pngpath + prn + '.png',dpi=200)
            #                 plt.close(fig)
    
                              
                    
        
        
        
     #########################   
        
            
            
        
        
    nd_df.crs={'init':crs}
    
    
    csvfile           = nd_df.groupby(['Pro_Code','Pro_Name', 'Mun_Code', 'Mun_Name'])['gridcode'].max()    
    csvfile           = csvfile.to_frame()
    csvfile           = csvfile.reset_index()
    
    csvfile.to_csv(outpath + "01_Inundation_" + fname + '.csv') 
    nd_df.to_file(shppath   +  '01_Inundation_' + fname +'.shp')
    
    midx = (ss_maxx + ss_minx)/2
    midy = (ss_maxy + ss_miny)/2
        
    i_map = folium.Map([midy, midx], zoom_start=6)
    
    folium.TileLayer('openstreetmap').add_to(i_map)
    folium.GeoJson(nd_df.to_json(), style_function=lambda x:{
                'fillColor':x['properties']['i_cols'], 'color':x['properties']['i_cols'], 'weight': 1}).add_to(i_map)
            
    folium.GeoJson(tc_track_line.to_json(),style_function=lambda x:{
                'color':'blue', 'weight': 2}).add_to(i_map)
    
    for loc in range(0,len(tc_track)):
        folium.Marker(location=[tc_track['lat'][loc], tc_track['lon'][loc]], 
                      popup=    str(datetime.datetime.strptime(str(tc_track['mo'][loc]), "%m").strftime("%b")) + '-' +
                                str(tc_track['dy'][loc]) + ', ' +
                                str(tc_track['hr'][loc]) + '00 UTC\n' +
                                str(tc_track['mslp'][loc]) + ' hPa').add_to(i_map)
    # folium.GeoJson(tc_track.to_json(), popup=tc_track['mslp'], style_function=lambda x:{
    #             'color':'blue', 'weight': 5}).add_to(ss_map)
    i_map.save(outpath + "01_Inundation_" + fname + '.html')   
    
    
        
           
   
        
        
        

            
 

                    
        
        
        