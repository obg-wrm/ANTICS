# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 13:09:06 2022

@author: sarigiering
"""

# ---- Required packages ----
import os
import datetime
import struct
import re
import pandas as pd
from pathlib import Path, PurePath
from dateutil.parser import parse
import holopy as hp
import numpy as np
from skimage import io
from PIL import Image
from skimage.util import img_as_ubyte
from skimage.exposure import rescale_intensity

# ---- Functions and Classes ----

class HoloMetadata:
    """
    Extract metadata from LISST-Holo hologram. Updated to be compatible with LISST-Holo2.
    
    Attributes
    ----------
    metadata: metadata values
    var_name: variable names in metadata

    Parameters
    ----------
    image_fn: str
        The file location of the raw holograms
    
    Returns
    --------
    metadata
        metadata for a hologram as pandas dataframe
    var_name
        names of variables
    
    Background
    -----------
    The LISST-Holo holograms are saved in .pgm format and are composed of three parts. 
    
    The first block of bytes in a hologram is the standard PGM format, as follows:
    P5<lf>1600 1200 255<lf> plus 1600 ×1200 bytes containing the hologram data.
    
    The second block of bytes has a size of 1024 bytes and follows immediately after the hologram data. This block holds binary data indlcuding date, temperature and depth. Data are saved as described in the manual using C structs.
    
    The third block has a size of 1024 bytes and contains a text file version of the metadata, including the converted temperature and depth values (in degC and m, respectively).

    This functions extracts the metadata from the second and third block from all images in one table ("_metadata_overview_*.csv"). In addition, this function saves the third block of each hologram as a separate file.
    
    (Source: LISST-Holo manual v3, p.69)

    """
    def __init__(self, image_fn, cruise = None, event = None):
              # ---- Read meta data ----
        # LISST-Holo manual v3 describes the sturcture.
        # The metadata is saved as additional bytes after the image.
        # The first set of 1024 bytes save data as described in the manual using C structs.
        # The second set of 1024 bytes contains a text file version of the metadata, including
        # the converted temperature and depth counts.

        START_metadata = 1600*1200+18-1
        block_meta = open(image_fn, 'rb')
        block_meta.seek(START_metadata)

        # first set
        block2_byte = block_meta.read(1024)

        # second set
        block3_byte = block_meta.read(1024)

        # ---- Fill metadata table ---
        # prepare row
        meta = [None] * 36

        # --- General info ---
        meta[0] = cruise
        meta[1] = event
        meta[2] = PurePath(image_fn).stem

        # --- Extract info from block 2 ---
        #0-7 
        #Seconds since epoch. Time stamp indicating when image was obtained. Unsigned long integer.
        e = struct.unpack("LL", block2_byte[0:8])[0]
        meta[3] = str(datetime.datetime.fromtimestamp(e))

        #8-15
        #Pressure in counts. Unsigned long integer.
        meta[6] = struct.unpack("LL", block2_byte[8:16])[0]

        #16-17
        #Temperature in counts.
        meta[7] = struct.unpack("H", block2_byte[16:18])[0]

        #18-19
        #Battery/power supply voltage in counts
        meta[8] = struct.unpack("H", block2_byte[18:20])[0]

        #20-21
        #Exposure time in 600ns increments.
        meta[9] = struct.unpack("H", block2_byte[20:22])[0]

        #22-23
        #Laser power in counts.
        meta[10] = struct.unpack("H", block2_byte[22:24])[0]

        #24-25
        #Laser photo diode reading, in counts.
        meta[11] = struct.unpack("H", block2_byte[24:26])[0]

        #26-27
        #Camera brightness.
        meta[12] = struct.unpack("H", block2_byte[26:28])[0]

        #28-29
        #Camera brightness, minimum value.
        meta[13] = struct.unpack("H", block2_byte[28:30])[0]

        #30-31
        #Camera brightness, maximum value.
        meta[14] = struct.unpack("H", block2_byte[30:32])[0]

        #32-33
        #Camera shutter.
        meta[15] = struct.unpack("H", block2_byte[32:34])[0]

        #34-35
        #Camera shutter, minimum value.
        meta[16] = struct.unpack("H", block2_byte[34:36])[0]

        #36-37
        #Camera shutter, maximum value.
        meta[17] = struct.unpack("H", block2_byte[36:38])[0]

        #38-39
        #Camera gain.
        meta[18] = struct.unpack("H", block2_byte[38:40])[0]

        #40-41
        #Camera gain, minimum value.
        meta[19] = struct.unpack("H", block2_byte[40:42])[0]

        #42-43
        #Camera gain, maximum value. 
        meta[20] = struct.unpack("H", block2_byte[42:44])[0]

        #44-115
        #Not used

        #116-119
        #Depth coefficient, DepthA. Floating point number.
        meta[21] = struct.unpack("f", block2_byte[116:120])[0]

        #120-123
        #Depth coefficient, DepthB. Floating point number.
        meta[22] = struct.unpack("f", block2_byte[120:124])[0]

        #124-127
        #Depth coefficient, DepthC. Floating point number.
        meta[23] = struct.unpack("f", block2_byte[124:128])[0]

        #128-131
        #Temperature coefficient, TemperatureA. Floating point number.
        meta[24] = struct.unpack("f", block2_byte[128:132])[0]

        #132-135
        #Temperature coefficient, TemperatureB. Floating point number.
        meta[25] = struct.unpack("f", block2_byte[132:136])[0]

        #136-139
        #Temperature coefficient, TemperatureC. Floating point number.
        meta[26] = struct.unpack("f", block2_byte[136:140])[0]

        #140-143
        #Temperature coefficient, TemperatureSlope. Floating point number.
        meta[27] = struct.unpack("f", block2_byte[140:144])[0]

        #144-147
        #Temperature coefficient, TemperatureOffset. Floating point number.
        meta[28] = struct.unpack("f", block2_byte[144:148])[0]

        #148-151
        #Auxiliary input A/D channel 2. 8 bits, 0 to 255.
        meta[29] = struct.unpack("I", block2_byte[148:152])[0]

        #152-155
        #Auxiliary input A/D channel 3. 8 bits, 0 to 255.
        meta[30] = struct.unpack("I", block2_byte[152:156])[0]

        #156-159
        #Auxiliary input A/D channel 4. 8 bits, 0 to 255.
        meta[31] = struct.unpack("I", block2_byte[156:160])[0]

        #160-163
        #Auxiliary input A/D channel 5. 12 bits, 0 to 4095.
        meta[32] = struct.unpack("I", block2_byte[160:164])[0]

        #164-167
        #Auxiliary input A/D channel 6. 12 bits, 0 to 4095.
        meta[33] = struct.unpack("I", block2_byte[164:168])[0]

        #168-171
        #Not used

        #172-173
        #Inter-frame delay in milliseconds.
        meta[34] = struct.unpack("H", block2_byte[172:174])[0]

        #174-181
        #Millisecond time stamp. Use to determine time between previous or following hologram.
        meta[35] = struct.unpack("LL", block2_byte[174:182])[0]

        #182-1023
        #Unassigned, set to 0

        # --- Calculate final values from block 2 ---
        # Depth in m
        meta[4] = meta[6] * meta[22] + meta[23] 

        # ---- prepare column names ----
        coln = [None] * 36

        # ---- general ----
        coln[0] = "Cruise"
        coln[1] = "Event"
        coln[2] = "Image"

        # ---- calculated ----
        coln[4] = "Depth"
        coln[5] = "Temperature"

        # ---- block 2 ----
        coln[3] = "Datetime"
        coln[6] = "Pressure counts"
        coln[7] = "Temperature counts"
        coln[8] = "Power supply voltage counts"
        coln[9] = "Exposure time in 600ns increments"
        coln[10] = "Laser power counts"
        coln[11] = "Laser photo diode reading counts"
        coln[12] = "Camera brightness"
        coln[13] = "Camera brightness min"
        coln[14] = "Camera brightness max"
        coln[15] = "Camera shutter"
        coln[16] = "Camera shutter min"
        coln[17] = "Camera shutter max"
        coln[18] = "Camera gain"
        coln[19] = "Camera gain min"
        coln[20] = "Camera gain max"
        coln[21] = "Depth coef A"
        coln[22] = "Depth coef B"
        coln[23] = "Depth coef C"
        coln[24] = "Temp coef A"
        coln[25] = "Temp coef B"
        coln[26] = "Temp coef C"
        coln[27] = "Temp coef slope"
        coln[28] = "Temp coef offset"
        coln[29] = "Aux channel 2"
        coln[30] = "Aux channel 3"
        coln[31] = "Aux channel 4"
        coln[32] = "Aux channel 5" 
        coln[33] = "Aux channel 6"
        coln[34] = "Inter-frame delay msec"
        coln[35] = "Timestamp msec"

        # --- return ---
        self.metadata = meta
        self.var_name = coln

def export_metadata_batch(raw_folder_path, cruise, event, ext = '*.pgm'):
    """
    Extract metadata from all LISST-Holo hologram in folder.
    
    Parameters
    ----------
    raw_folder_path: str
        The file location of the raw holograms
    cruise: str
        Name of cruise. E.g. "DY086"
    event: str
        Name of event, deployment or profile. E.g. "034"
    ext : str
        Extension of the file to be found. Default: '*.pgm'
    
    Returns
    --------
    Overview table
        Saves selected metadata for all holograms in folder as table
    Metadata files
        Saves all metadata for a hologram as separate file
    
    Note
    -------
    I added the "ext" argument as holograms may be saved as .PGM or .pgm. The function is case-insensitive on Windows, but may not be on Linux or Mac, in which case the exact extension can be changed to match the project files.
    """

    # --- make directory if not exist ---
    output_path = Path(raw_folder_path).parent.joinpath("metadata")
    if not output_path.exists(): output_path.mkdir()
    print("Metadata will be saved to: " + str(output_path))
    
    # --- prepare overview table ---
    overview = []
    overview_fn = output_path.joinpath("_metadata_overview_" + cruise + "_event" + event + ".csv")

    # note files
    file_list = []

    # ---- find images ----
    # Find .pgm files in input path            
    for image_fn in Path(raw_folder_path).glob(ext):
        file_list.append(image_fn.stem)

        # extract metadata
        meta = HoloMetadata(image_fn, cruise = cruise, event = event)

        # append to previous metadata
        overview.append(meta.metadata)

    df = pd.DataFrame(overview, columns = meta.var_name)

    # save metadata to new file    
    df.to_csv(overview_fn, index = False)

    print("Number of images analyzed:", len(file_list))
    print("Overview saved as:", overview_fn)

def zmin_batch(raw_folder_path, n = 51, ext = '*.pgm'):
  """Generate z-min image for hologram

  The z-min image shows the darkest value for a given pixel within the frame.
  Function reads in all holograms in folder,
  reconstructs the images with the given spacing,
  and calculates the minimum value for each pixel.
  Results are saved in a separate folder.
  
  Parameters
  ----------
  raw_folder_path : str
      the file location of the raw holograms
  n : integer
      number of focus planes. Default: 51
  ext : str
      extension of the file to be found. Default: '*.pgm'
    
  Returns
  -------
  image (.png)
      saves z-min for all images in separate folder
  
  """
    
  # --- function details ---
  # The z-min image shows the darkest value for a given pixel within the frame.
  # Function reads in all holograms in folder,
  # reconstructs the images with the given spacing,
  # and calculates the minimum value for each pixel.
  # Results are saved in a separate folder.
  
  # This function 
  # (1) saves z-min for all images in separate folder
  #
  # n: number of focus planes. Default: 51
  # ext: extension of the file to be found. Default: '*.pgm'

  # Note. I added the ext argument as holograms may be saved as .PGM or .pgm
  # The function is case-insensitive on Windows, but may not be on Linux or Mac,
  # in which case the exact extension can be changed to match the project files.

  # --- make directory if not exist ---
  output_zmin_path = Path(raw_folder_path).parent.joinpath("z_min")
  if not output_zmin_path.exists(): output_zmin_path.mkdir()

  # print folder names
  print("Images read from: " + str(raw_folder_path))
  print("z-min images will be saved to: " + str(output_zmin_path))

  # --- find images ---
  # Find .pgm files in input path

  for image_fn in Path(raw_folder_path).glob(ext):
      # make z_min file name
      z_min_fn = Path(output_zmin_path).joinpath(PurePath(image_fn).stem + "_z_min.png")

      # check whether image already exists
      if z_min_fn.exists():
        print("Z_min of file already exists and is skipped: " + str(PurePath(image_fn).name))
        continue

      # ---- Load hologram ----
      raw_holo = hp.load_image(image_fn, spacing=4.4, medium_index = 1.333, illum_wavelen = 0.658)
      
      # All values based on LISST-Holo manual
      # spacing: pixel size in um
      # medium index: refractory index of water
      # illumination wavelength: 658 nm
      
      # ---- Calculate focus stack ----
      # Next, we use numpy’s linspace to define a set of distances between the 
      #image plane and the reconstruction plane. We space the 51 planes evenly 
      #throughout the sampling window. Note, in the LISST-Holo manual, the range 
      #is 0 - 50 mm + 28 mm offset between window and CCD array.
       
      zstack = np.linspace(0, 100000, n)
      focal_planes = hp.propagate(raw_holo, zstack, cfsp = 3)
      
      # ---- Calculate z_min ----
      z_min = np.abs(focal_planes).min(axis=0) 
      
      # rescale and save as uint8
      z_min = img_as_ubyte(rescale_intensity(z_min))

      # save
      io.imsave(z_min_fn, z_min)

def reconstruct_batch(raw_folder_path, n = 51, ext = '*.pgm', make_stack = True, make_gif = True, make_z_min = True):
  """Reconstruct raw LISST-Holo hologram
  
  Steps
  ------
  1 : Reconstruct focal planes

  2 : Save focal planes (optional)
  
  3 : Compile gif (optional)
  
  4 : Generate z-min image (optional)
 
  Parameters
  ----------
  raw_folder_path : str
      The file location of the raw holograms
  n : integer
      Number of focus planes. Default: 51
  ext : str
      Extension of the file to be found. Default: '*.pgm'
  make_stack : boolean
      Save all reconstructed focal planes. Default = True.
  make_gif : boolean
      Save reconstructed focal planes as gif. Default = True.
  make_z_min : boolean
      Save z_min. Default = True.
    
  Returns
  -------

  stacks : img (.png)
      Reconstructed focal planes for each hologram are saved in a separate subfolder in the folder 'stacks' in the parent directory.

  gif :
      A compilation of all focal planes is saved as gif for easy viewing. One gif file per hologram, saved in the folder 'gifs' in the parent directory.
      
  z-min : img (.png)
      The z-min image shows the darkest value for a given pixel within the frame. Function reads in all holograms in folder, reconstructs the images with the given spacing, and calculates the minimum value for each pixel. Results are saved in the folder 'z_min' in the parent directory.
  
  Note
  -------
  I added the ext argument as holograms may be saved as .PGM or .pgm. The function is case-insensitive on Windows, but may not be on Linux or Mac, in which case the exact extension can be changed to match the project files.
  
  For the stack, only the images from 19 - 51 are in the sampling volume (i.e. image the water).
  """

  print("Images read from: " + str(raw_folder_path))
  
  # --- make directory if not exist ---
  if make_stack:
      output_stack_path = Path(raw_folder_path).parent.joinpath("stacks")
      if not output_stack_path.exists(): output_stack_path.mkdir()
      print("stack images will be saved to: " + str(output_stack_path))
  
  if make_gif:
      output_gif_path = Path(raw_folder_path).parent.joinpath("gifs")
      if not output_gif_path.exists(): output_gif_path.mkdir()
      print("gifs will be saved to: " + str(output_gif_path))
  
  if make_z_min:
      output_zmin_path = Path(raw_folder_path).parent.joinpath("z_min")
      if not output_zmin_path.exists(): output_zmin_path.mkdir()
      print("z-min images will be saved to: " + str(output_zmin_path))

  # --- find images ---
  # Find .pgm files in input path

  for image_fn in Path(raw_folder_path).glob(ext):
      
      # ---- Load hologram ----
      raw_holo = hp.load_image(image_fn, spacing=4.4, medium_index = 1.333, illum_wavelen = 0.658)
      
      # All values based on LISST-Holo manual
      # spacing: pixel size in um
      # medium index: refractory index of water
      # illumination wavelength: 658 nm
      
      # ---- Calculate focus stack ----
      # Next, we use numpy’s linspace to define a set of distances between the 
      #image plane and the reconstruction plane. We space the n planes evenly 
      #throughout the sampling window. Note, in the LISST-Holo manual, the range 
      #is 0 - 50 mm + 28 mm offset between window and CCD array.
       
      zstack = np.linspace(0, 100000, n)
      focal_planes = hp.propagate(raw_holo, zstack, cfsp = 3)
      
      # correct intensities
      focal_planes_abs = np.abs(focal_planes)
          
      # convert to uint8
      focal_planes_uint = img_as_ubyte(rescale_intensity(focal_planes_abs))
      
      # ---- Save focal planes ----
      if make_stack:
          # make subfolder
          output_stack_subfolder_path = output_stack_path.joinpath(PurePath(image_fn).stem)
          if not output_stack_subfolder_path.exists(): output_stack_subfolder_path.mkdir()
          
          # save focal planes
          for i in np.arange(0, n):
              
              # define file name
              plane_fn = output_stack_subfolder_path.joinpath(PurePath(image_fn).stem + 
                                                              "_plane" + str(i).zfill(2) + ".png")
              
              # save
              io.imsave(plane_fn, focal_planes_uint[i,:,:])
            
      # --- Make gif stack ---
      if make_gif:
          # define gif file name
          gif_fn = output_gif_path.joinpath(PurePath(image_fn).stem + ".gif")
        
          # save
          gif_frames = [Image.fromarray(f) for f in focal_planes_uint]
          gif_frames[0].save(fp=gif_fn, format='GIF', append_images=gif_frames[1:],
                             save_all=True, duration=200, loop=0)
          
      # ---- Calculate z_min ----
      if make_z_min:
          z_min = focal_planes_abs.min(axis=0) 
          
          # rescae and convert to uint8
          z_min = img_as_ubyte(rescale_intensity(z_min))
       
          # define z_min file name
          z_min_fn = Path(output_zmin_path).joinpath(PurePath(image_fn).stem + "_z_min.png")
    
          # save
          io.imsave(z_min_fn, z_min)