# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 13:10:11 2018

@author: qzo13262
"""

import glob
import hyperspy.api as hs
import series_align
from scipy.ndimage import interpolation
import numpy as np

dir = r"Z:\data\2018\cm19688-7\raw\raw\autoSTEM tests\4 SI/"
haadf_files = []
for filename in glob.glob(dir+"SI-*/*HAADF Image.dm4"):
    #print(filename)
    haadf_files.append(filename)
    
haadf_ims = hs.load(haadf_files,stack=True)

aligned_series,shifts = series_align.series_align(haadf_ims.data,start='First')

shifted_ims = hs.signals.Signal2D(aligned_series)

si_files = []
for filename_si in glob.glob(dir+"SI-*/*Spectrum Image.dm4"):
    #print(filename_si)
    si_files.append(filename_si)
    
si = hs.load(si_files)

sidata = si[0].data
sinew = np.zeros_like(sidata)

for i in range(len(haadf_files)):
    sidata = si[i].data
    for j in range(sidata.shape[2]):
        sinew[:,:,j]=sinew[:,:,j]+interpolation.shift(sidata[:,:,j],shifts[i][0])