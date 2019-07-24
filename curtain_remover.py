# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 11:32:43 2017

@author: Thomas Slater
"""

import cv2
import numpy as np
import scipy.ndimage.filters as filters

def curtain_remover(image,angle,pass_width,pass_start):
    dft = cv2.dft(np.float32(image),flags = cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    
    height = np.shape(dft_shift)[0]
    width = np.shape(dft_shift)[1]
    
    #plt.imshow(dft_shift[:,:,0])
    
    mask = np.ones((height,width,2),np.uint8)
    
    cv2.line(mask,(0,int(height/2-width/2*np.tan(angle/180*np.pi))),(int(width/2-pass_start),int(height/2-pass_start/2*np.tan(angle/180*np.pi))),(0,0,0),pass_width)
    cv2.line(mask,(int(width/2+pass_start),int(height/2+pass_start*np.tan(angle/180*np.pi))),(width,int(height/2+width/2*np.tan(angle/180*np.pi))),(0,0,0),pass_width)
    
    mask = mask*255
    
    #mask = np.float16(mask)
    #mask_blur = cv2.GaussianBlur(mask,(7,7),0)
    mask_blur = filters.gaussian_filter(mask,5)
    mask_blur = np.float32(mask_blur)
    mask_blur = mask_blur/np.max(mask_blur)
    
    #plt.imshow(mask_blur[:,:,0])
    
    fshift = dft_shift*mask_blur
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:,:,0],img_back[:,:,1])
    
    return(img_back)

def curtain_stack(image_stack,angle,pass_width,pass_start):
    new_stack = np.zeros(np.shape(image_stack))
    for x in len(image_stack[2]):
        new_stack[:,:,x] = curtain_remover(image_stack[:,:,x],(-1)**x*angle,pass_width,pass_start)
        
    return(new_stack)