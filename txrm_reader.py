# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 16:28:19 2016

@author: hmxf
"""

import olefile as olef
import numpy as np 
#import math
import struct
#import hyperspy.api as hs
#import tools_3d

class XTomoReader():
    '''Object for reading txrm files'''
    
    def __init__(self, 
                    file_name,
                    apply_ref=True,
                    logger=None, 
                    color_log=True, 
                    stream_handler=True,
                    log='INFO'):

        self.file_name = file_name
        self.apply_ref = apply_ref
        self.load()
        self.set_metadata()
    
    def get_ref(self, ole):
        '''Function to load the white(gain) reference from file'''
            
        if ole.exists('ReferenceData/Image'):
            stream = ole.openstream('ReferenceData/Image')
            data = stream.read()
            struct_fmt = "<{}f".format(self.n_cols*self.n_rows)
            refdata = struct.unpack(struct_fmt, data)
            # 10 float; 5 uint16 (unsigned 16-bit (2-byte) integers)
            '''if self.datatype == 10:
                struct_fmt = "<{}f".format(self.n_cols*self.n_rows)
                refdata = struct.unpack(struct_fmt, data)
            elif self.datatype == 5:                   
                struct_fmt = "<{}h".format(self.n_cols*self.n_rows)
                refdata = struct.unpack(struct_fmt, data)
            else:                            
                self.logger.error("Wrong data type")
                return'''
            refim = np.asarray(refdata)
            refdata = np.empty((self.n_cols,self.n_rows))
            refdata[:,:] = np.reshape(refim, (self.n_cols, self.n_rows), order='F')
              
        ole.close()
        
        self.ref = refdata
    
    def load(self):
            """ 
            Read 3-D tomographic projection data from a TXRM file 
            
            Parameters
            
            file_name : str
                Input txrm file.
            
            x_start, x_end, x_step : scalar, optional
                Values of the start, end and step of the
                slicing for the whole array.
            
            y_start, y_end, y_step : scalar, optional
                Values of the start, end and step of the
                slicing for the whole array.
            
            z_start, z_end, z_step : scalar, optional
                Values of the start, end and step of the
                slicing for the whole array.
            
            Returns
            
            out : array
                Returns the data as a matrix.
            """
            try:
                olef.isOleFile(self.file_name)              

                ole = olef.OleFileIO(self.file_name)
                datasize = np.empty((3), dtype=np.int)
                if ole.exists('ImageInfo/ImageWidth'):                 
                    stream = ole.openstream('ImageInfo/ImageWidth')
                    data = stream.read()
                    nev = struct.unpack('<I', data)
                    #self.logger.info("ImageInfo/ImageWidth = %i", nev[0])
                    datasize[0] = np.int(nev[0])
                    self.n_cols = datasize[0]

                if ole.exists('ImageInfo/ImageHeight'):                  
                    stream = ole.openstream('ImageInfo/ImageHeight')
                    data = stream.read()
                    nev = struct.unpack('<I', data)
                    #self.logger.info("ImageInfo/ImageHeight = %i", nev[0])
                    datasize[1] = np.int(nev[0])
                    self.n_rows = datasize[1]

                if ole.exists('ImageInfo/ImagesTaken'):                  
                    stream = ole.openstream('ImageInfo/ImagesTaken')
                    data = stream.read()
                    nev = struct.unpack('<I', data)
                    #self.logger.info("ImageInfo/ImagesTaken = %i", nev[0])
                    nimgs = nev[0]
                    datasize[2] = np.int(nimgs)
                    n_images = datasize[2]

                # 10 float; 5 uint16 (unsigned 16-bit (2-byte) integers)
                if ole.exists('ImageInfo/DataType'):                  
                    stream = ole.openstream('ImageInfo/DataType')
                    data = stream.read()
                    struct_fmt = '<1I'
                    datatype = struct.unpack(struct_fmt, data)
                    self.datatype = int(datatype[0])
                    #self.logger.info("ImageInfo/DataType: %f ", datatype)
                    
                #self.logger.info("Reading images - please wait ...")
                absdata = np.empty((n_images, self.n_cols, self.n_rows), dtype=np.float32)
                #Read the images - They are stored in ImageData1, ImageData2... Each
                #folder contains 100 images 1-100, 101-200...           
                for i in range(1, nimgs+1):
                    img_string = "ImageData%i/Image%i" % (np.ceil(i/100.0), i)
                    stream = ole.openstream(img_string)
                    data = stream.read()
                    # 10 float; 5 uint16 (unsigned 16-bit (2-byte) integers)
                    if self.datatype == 10:
                        struct_fmt = "<{}f".format(self.n_cols*self.n_rows)
                        imgdata = struct.unpack(struct_fmt, data)
                    elif self.datatype == 5:                   
                        struct_fmt = "<{}h".format(self.n_cols*self.n_rows)
                        imgdata = struct.unpack(struct_fmt, data)
                    else:                            
                        #self.logger.error("Wrong data type")
                        return
                    absdata[i-1,:,:] = np.reshape(imgdata, (self.n_cols, self.n_rows), order='F')
              
                if self.apply_ref == True:
                    self.get_ref(ole)
                    self.data = absdata / self.ref
                else:
                    self.data = absdata
                
                ole.close()
                
            except KeyError:
                #self.logger.error("FILE DOES NOT CONTAIN A VALID TOMOGRAPHY DATA SET")
                absdata = None
    
            return
            
    def set_metadata(self):
        '''Return a list of angles'''
        ole = olef.OleFileIO(self.file_name)
        if ole.exists('ImageInfo/ImagesTaken'):                  
            stream = ole.openstream('ImageInfo/ImagesTaken')
            data = stream.read()
            nev = struct.unpack('<I', data)
            #self.logger.info("ImageInfo/ImagesTaken = %i", nev[0])
            n_images = nev[0]
        if ole.exists('ImageInfo/Angles'):                  
            #self.logger.info("Reading Angles")
            stream = ole.openstream('ImageInfo/Angles')
            data = stream.read()
            struct_fmt = "<{}f".format(n_images)
            self.angles = struct.unpack(struct_fmt, data)
        if ole.exists('ImageInfo/StoRADistance'):
            stream = ole.openstream('ImageInfo/StoRADistance')
            data = stream.read()
            struct_fmt = "<f".format(n_images)
            self.source_dist = struct.unpack_from(struct_fmt, data)
        if ole.exists('ImageInfo/DtoRADistance'):
            stream = ole.openstream('ImageInfo/DtoRADistance')
            data = stream.read()
            struct_fmt = "<f".format(n_images)
            self.detector_dist = struct.unpack_from(struct_fmt, data)
        if ole.exists('ImageInfo/PixelSize'):
            stream = ole.openstream('ImageInfo/PixelSize')
            data = stream.read()
            struct_fmt = "<f".format(n_images)
            self.im_pix_size = struct.unpack_from(struct_fmt, data)
            
        ole.close()
            
        return
    
    def centreshift(start,stop):
        None