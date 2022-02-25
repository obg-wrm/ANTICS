# -*- coding: utf-8 -*-
"""
Created on Wed Feb  23 10:27:15 2022

@author: wilmaj
"""
import time
import datetime
startTime = time.perf_counter()


import os
import glob
import holopy as hp
import numpy as np
import pandas as pd


#%%  working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
wd = os.getcwd() # get current directory / directory where original pgm files are saved

# event number
event = [input('Enter the three-digit cast number:').zfill(3)]

# create a list of every nth .PGM file in current working directory
files = glob.glob(wd + '\\*.PGM')
n = 10
filein = []
for file in files[0::n]:
    filein.append(file)    


## image propogation: define distance between image plane and reconstruction plane
array_zstack = np.linspace(0, 100000, 20)
# create a list of numbers for sliced hologram filenames
num_list = [str(i).zfill(3) for i in range(1,21)]

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

def hologram_greyness(filename):
    # load in the and propogate hologram
    raw_holo = hp.load_image(filename, spacing=4.4, medium_index = 1, illum_wavelen = 0.658)
    # propagate the hologram
    rec_vol = hp.propagate(raw_holo, array_zstack, cfsp = 3)
    # sum of hologram slices
    z_sum = np.abs(rec_vol).min(axis=0)
    # return the mean of the sum
    grey_mean = float(str(z_sum.mean())[39:44])
    return grey_mean   

# create an empty file for summary data
data = []

for jlop in range(len(filein)):
    
    # output file name
    fout2 = filein[jlop].split("\\")
    file_n = fout2[-1][0:-4]
    

    depth = hologram_depth(filein[jlop])
    
    # if depth is less than 0 then NaN
    if (float(depth) <= 0):
        greyness = np.nan           
    else: 
        greyness = hologram_greyness(filein[jlop])
    print("For file", str(file_n), "depth =", depth, "m and greyscale =", greyness)  
    row = [event, file_n, depth, greyness]
    data.append(row)
 
# turn data into dataframe
df = pd.DataFrame(data, columns=['Event', 'Filename', 'Depth', 'Greyscale'])


# create plot
import matplotlib.pyplot as plt
from matplotlib import rcParams

y = df.Depth.astype(float)
x = df.Greyscale

rcParams.update({'font.size': 16})
fig = plt.figure(figsize=(8,8))
plt.plot(x, y, linestyle="None", marker='.', color='b')
ax = plt.subplot(111)
ax.set(xlim=(10, 30), ylim=(0, 600))
ax.set_xlabel("Greyscale")
ax.set_ylabel("Depth (m)")
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()
plt.gca().invert_yaxis()
plt.show()

# time the code
endTime = time.perf_counter()
runTime = endTime - startTime
print("The run time of this script is " + str(datetime.timedelta(seconds=runTime))[:7])
### -- end -- ##
