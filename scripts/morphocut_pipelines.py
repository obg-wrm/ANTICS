# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 13:02:20 2022

@author: slcg
"""

# Note, this code requires the installation of MorhoCut developers version.
# https://morphocut.readthedocs.io/en/stable/introduction.html

# Python 3.7
# pip install -U git+https://github.com/morphocut/morphocut.git
 
# ---- Required packages ----
import os, os.path
import tkinter as tk
from tkinter import filedialog
from morphocut.core import Pipeline, Call
from morphocut.file import Find, Glob
from morphocut.image import ImageProperties, ImageReader
from morphocut.stream import Progress
from morphocut.str import Format
from morphocut.contrib.ecotaxa import EcotaxaWriter
from morphocut.contrib.zooprocess import CalculateZooProcessFeatures

def make_ecotaxa_folder(folder_name, lat = None, lon = None, date = None, ext = ".png"):
    """
    Make ecotaxa table and pack table and all images into folder (zipped) for direct upload into Ecotaxa.
    
    Parameters
    ----------
    folder_name: str
        Name to be used for output folder. E.g. "Event1".
    lat: float
        Latitude (with South being negative)
    lon: float
        Longitude (with West being negative)
    date: str of format "YYYY-MM-DD"
        Date of sampling
    ext: str
        Extension of images (e.g. ".bmp", ".png")
    
    Returns
    --------
    Folder
        Saves EcoTaxa table and all images in zipped folder
    
    Note
    -------
    Masks for particles are produced using a threshold of 120. This fixed threshold may not be appropriate for your data.
    """
    
    # prompt for choosing folder
    root = tk.Tk()
    root.attributes('-topmost', 1)
    root.withdraw()
    raw_folder_path = filedialog.askdirectory()
    root.update()
    os.chdir(raw_folder_path)
    
    # make directory for extraction
    output_path = os.path.join(os.path.dirname(raw_folder_path), "morphocut")
    if not os.path.exists(output_path): os.mkdir(output_path)
    
    # print folder names
    print("Selected folder: " + raw_folder_path)
    print("Files will be extracted to: " + output_path)
    
    # MorphoCut pipeline
    if __name__ == "__main__":
    
        with Pipeline() as p:
    
            # [Stream] Find path of .bmp files in input path
            fn = Find(raw_folder_path, [ext])
    
            # --- metadata table ---
            # Extract file path (Corresponds to `for path in glob(pattern):`)
            path = Glob(fn)
            
            # Remove path and extension from the filename
            basename = Call(lambda x: os.path.splitext(os.path.basename(x))[0], path)
            
            thisdict = {
              "id": Format("{object_id}", object_id = basename),
              "lat": lat,
              "lon": lon,
              "date": date,
            }
    
            # --- image processing ---
            # [Stream] Read and open image from path. Note, it's already black-and-white
            img = ImageReader(fn)
                      
            # Make object mask
            mask = img < 120
          
            # Calculate object properties (area, eccentricity, equivalent_diameter, mean_intensity, ...). See skimage.measure.regionprops.
            regionprops = ImageProperties(mask, img)           
       
            # Append object properties to metadata in a ZooProcess-like format
            meta = CalculateZooProcessFeatures(regionprops, thisdict)
            # End of parallel execution
    
            # [Stream] Here, three different versions are written. Remove what you do not need.
            EcotaxaWriter(
                os.path.join(output_path, "EcoTaxa_" + folder_name + ".zip"),
                [
                    # The original RGB image
                    (Format("{object_id}.jpg", object_id = basename), img),
                ],
                object_meta = meta,
            )
    
            # Progress bar
            Progress(fn)
    
        p.run()# Requires MorphoCut developer version.