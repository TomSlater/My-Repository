# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 16:38:40 2017

@author: Thomas Slater
"""

import glob
import hyperspy.api as hs
import numpy as np
import tools_3d as t3d

'''dir = 'C:/Users/Thomas Slater/Desktop/AZ31_2'

series = []

for filename in glob.glob(dir+'/*.dm3'):
    series.append(hs.load(filename).data)
    
im_array = np.asarray(series)'''

class xum(object):
    '''Class to handle XuM data series'''
    
    def __init__(self,filename):
        self.load(filename)
        self._get_metadata(filename)
        
    def _get_metadata(self,filename):
        '''Function to get the metadata'''
        
        meta_image = hs.load(filename)
        self.metadata = {}

        #Get the angles of the projections
        delta_angle = meta_image.original_metadata.ImageList.TagGroup0.ImageTags.XuM.Tomo.as_dictionary()['Delta Angle']
        angles = np.arange(0,360,delta_angle)
        self.metadata['angles'] = angles
        
        #Get geometry of the X-ray system
        distance_dict = {}
        distance_dict['so_dist'] = meta_image.original_metadata.ImageList.TagGroup0.ImageTags.XuM.Calibration.as_dictionary()['R1 (mm)']
        distance_dict['od_dist'] = meta_image.original_metadata.ImageList.TagGroup0.ImageTags.XuM.Calibration.as_dictionary()['R2 (mm)']
        self.metadata['distance_dict'] = distance_dict
        
    def load(self,filename):
        '''Function to load XuM data'''
        
        directory = filename.rpartition('/')[0]
        
        series = []
        for filename in glob.glob(directory+'/*.dm3'):
            series.append(hs.load(filename).data)
            
        self.data = np.asarray(series)
        
    def reconstruct(self):
        '''Function to reconstruct XuM data using Tools3D'''
        
        self.recon = t3d.astrarecon(self.data,self.metadata['angles'],geometry='cone',
                                    SO_dist=self.metadata['distance_dict']['so_dist'],
                                    OD_dist=self.metadata['distance_dict']['od_dist'])