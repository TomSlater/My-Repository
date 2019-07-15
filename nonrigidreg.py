# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:14:55 2019

@author: qzo13262
"""

import numpy as np
import SimpleITK as sitk

def nonrigid(im_stack, demons_it = 20, filter_size = 5.0, max_it = 3):
    
    demons = sitk.DemonsRegistrationFilter()
    demons.SetNumberOfIterations( demons_it )
    # Standard deviation for Gaussian smoothing of displacement field
    demons.SetStandardDeviations( filter_size )
    
    for j in range(max_it):
        #Get stack average
        av_im = sitk.GetImageFromArray(np.float32(sum(im_stack)/len(im_stack))) #Faster than numpy.mean for small arrays?
        
        #Get gradient images of stack average
        '''avgrad = np.gradient(av_im)
        normavgradx = avgrad[0]/np.sqrt(np.square(avgrad[0])+np.square(avgrad[1]))
        normavgrady = avgrad[1]/np.sqrt(np.square(avgrad[0])+np.square(avgrad[1]))'''
        
        out_stack = []
        
        for i in range(len(im_stack)):
            
            #print(im_stack[i])
            
            moving = sitk.GetImageFromArray(np.float32(im_stack[i]))
            
            displacementField = demons.Execute( av_im, moving )
            
            dispfield = sitk.GetArrayFromImage(displacementField)
            #print(dispfield)
            
            '''if dispconstraint == 'rwo-locked':
                disp_contrained = '''
            
            outTx = sitk.DisplacementFieldTransform( displacementField )
            
            resampler = sitk.ResampleImageFilter()
            resampler.SetReferenceImage(av_im);
            resampler.SetInterpolator(sitk.sitkLinear)
            resampler.SetDefaultPixelValue(100)
            resampler.SetTransform(outTx)
            
            out_stack.append(sitk.GetArrayFromImage(resampler.Execute(moving)))
            
            '''grad = np.gradient(im_stack[i])
            normgradx = grad[0]/np.sqrt(np.square(grad[0])+np.square(grad[1]))
            normgrady = grad[1]/np.sqrt(np.square(grad[0])+np.square(grad[1]))
            
            transform_x = (av_im-im_stack[i])*(normgradx+normavgradx)
            transform_y = (av_im-im_stack[i])*(normgrady+normavgrady)
            
            tx_filtered = ndimage.filters.gaussian_filter(transform_x,sigma=10)
            ty_filtered = ndimage.filters.gaussian_filter(transform_y,sigma=10)
            
            t_filtered = np.stack((ty_filtered,tx_filtered))
            
            im_t = transform.warp(im_stack[i],t_filtered)'''
            
        im_stack = out_stack
        
        #dispfield = sitk.GetArrayFromImage(displacementField)
        #print(dispfield)
        max_disp = np.max(dispfield)
            
        if max_disp < 1.0:
            print("NRR stopped after "+j+" iterations.")
            break
    
    return(out_stack)