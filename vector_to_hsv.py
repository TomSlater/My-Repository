# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 14:22:38 2019

@author: qzo13262
"""

import math
import numpy as np
from matplotlib.colors import hsv_to_rgb

def vector_to_rgb(x,y,max_r):
    mag = math.sqrt(x**2+y**2)
    ang = math.atan2(y,x)
    
    V = mag/max_r
    H = (ang+np.pi)/(2*np.pi)
    S = 1.0
    
    HSV = np.dstack((H,S,V))
    RGB = hsv_to_rgb(HSV)
    
    return(RGB)