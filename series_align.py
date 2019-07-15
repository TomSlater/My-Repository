# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 14:40:33 2018

@author: qzo13262
"""
from skimage.feature import register_translation
from scipy.ndimage import interpolation, filters
import numpy as np

def series_align(im_series,align_output=[],start='Mid',smooth=True,smooth_window='3',sobel=True):
    '''Function to align a series of images.'''
    if align_output == []:
        series_dim = len(im_series)
        
        filtered_series = []
        
        for i in range(series_dim):
            filtered_series.append(im_series[i].copy())
        
        align_output = []
        
        if smooth == True:
            for i in range(series_dim):
                filtered_series[i] = filters.gaussian_filter(filtered_series[i],3)
        
        if sobel == True:
            for i in range(series_dim):
                filtered_series[i] = filters.sobel(filtered_series[i])
        
        #Align from first image
        if start == 'First':
            align_output.append(register_translation(filtered_series[0], filtered_series[0],100))
            for i in range(series_dim-1):
                align_output.append(register_translation(filtered_series[i], filtered_series[i+1],100))
                align_output[i+1][0][0] = align_output[i+1][0][0] + align_output[i][0][0]
                align_output[i+1][0][1] = align_output[i+1][0][1] + align_output[i][0][1]
        
        #Align from mid-image
        if start == 'Mid':
            
            #Ensure compatibility with Python 2 and 3
            if series_dim % 2 == 0:
                mid_point = np.uint16(series_dim / 2)
            else:
                mid_point = np.uint16(series_dim // 2)
            
            align_output.append(register_translation(filtered_series[mid_point], filtered_series[mid_point], 100))
            
            for i in range(mid_point,0,-1):
                align_output.append(register_translation(filtered_series[i], filtered_series[i-1], 100))
                align_output[mid_point-i+1][0][0] = align_output[mid_point-i+1][0][0] + align_output[mid_point-i][0][0]
                align_output[mid_point-i+1][0][1] = align_output[mid_point-i+1][0][1] + align_output[mid_point-i][0][1]
                
            align_output = list(reversed(align_output))
            
            for i in range(mid_point,series_dim-1):
                align_output.append(register_translation(filtered_series[i], filtered_series[i+1], 100))
                align_output[i+1][0][0] = align_output[i+1][0][0] + align_output[i][0][0]
                align_output[i+1][0][1] = align_output[i+1][0][1] + align_output[i][0][1]
        
    #Apply calculated shifts to the image series
    shifted_im_series = []
    im_count = 0
    for im in im_series:
        shifted_im_series.append(interpolation.shift(im,align_output[im_count][0]))
        im_count = im_count + 1
        
    shifted_im_series = np.asarray(shifted_im_series)
        
    return(shifted_im_series, align_output)