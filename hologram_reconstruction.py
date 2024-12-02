# -*- coding: utf-8 -*-
"""
Created on Tue Jun 07 11:34:13 2022

@author: William Major

"""

# time the script
import time
timer1 = time.perf_counter()

import holopy as hp
import numpy as np
import os
import glob
import shutil
import pandas as pd


#%%  set working directory as file directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
wd = os.getcwd()

filein = glob.glob(wd + '\\*.PGM') # list of all holograms in the current working directory

def downcast_filelist(filelist):
    
    for item in range(len(filelist)):
        file_n= filelist[item].split("\\")
        file_n= file_n[-1][0:0]
        file_meta = open(filelist[item], 'rb') 
        # read last 1024 bytes
        file_meta.seek(-1024, 2)
        file_bytes = file_meta.read()
        # convert bytes and return depth
        file_str = file_bytes.decode()
        file_spl = file_str.split()
        depth = file_spl[11]        
        row = [file_n, depth]
        if depth > 10:
            data.append(row)
        else:
            next
    # create dataframe for holograms and depths    
    file_depths = pd.DataFrame(data, columns=['Filename', 'Depth'])
    return file_depths

    # find the maximum depth value to determine upcast data
    column = file_depths['Depth']
    column = [float(value) for value in column]
    max_depth = str(max(column))
    max_depth_file = file_depths.loc[file_depths['Depth'] == max_depth].index[0]
    downcast = list(df.iloc[0:(max_depth_file + 1), 0])
    return downcast
    
    
    
        

def hologram_depth(filename):
    # --- Open file ---
    file_meta = open(filename, 'rb') 
    # read last 1024 bytes
    file_meta.seek(-1024, 2)
    file_bytes = file_meta.read()
    # convert bytes and return depth
    file_str = file_bytes.decode()
    file_spl = file_str.split()
    depth = file_spl[11]
    return depth


    
    



## create a file list of every nth hologram to reconstruct
# n = 80                            # every nth hologram to select
# filein = []
# for file in files[0::n]:
#     filein.append(file)


# create an empty file for summary data
data = []

#%% Hologram selection
for jlop in range(len(filein)):
    
    # output filename
    fileout= filein[jlop].split("\\")
    fileout= fileout[-1][0:-4]
    print(fileout)
    depth = hologram_depth(filein[jlop])
    row = [fileout, depth]
    data.append(row)

df = pd.DataFrame(data, columns=['Filename', 'Depth'])






#%% Reconstruction
## image propogation: define distance between image plane and reconstruction plane
zstack = np.linspace(0, 100000, 217)

# create a list of numbers for sliced hologram filenames
num_list = [str(i).zfill(3) for i in range(1,218)]


for jlop in range(len(filein)):
    
    # output filename
    fileout= filein[jlop].split("\\")
    fileout= fileout[-1][0:-4]
    print(fileout)
    depth = hologram_depth(filein[jlop])    
 
    # create individual filenames for each slice
    fileout3=[]
    for ilop in num_list:
        a=fileout+"\\"+fileout+"_" + ilop +".png"
        fileout3.append(a)
    os.mkdir(fileout)
    
    # load in the and propogate hologram
    raw_holo = hp.load_image(filein[jlop], spacing=4.4, medium_index = 1, illum_wavelen = 0.658)
    rec_vol = hp.propagate(raw_holo, zstack, cfsp = 3)
    
    
    # save 217 images slices in hologram-specific directory
    hp.core.save_images(fileout3, rec_vol, scaling=('auto'), depth=8)
    shutil.move(filein[jlop], fileout+"\\")
    
    # for f in fileout[101:]: # [:13] deletes the first 13, current deletes the last 13
    #    os.remove(f)

    
timer2 = time.perf_counter()
total_time = timer2 - timer1
print("This script has taken " + str(total_time) + " seconds to run")
