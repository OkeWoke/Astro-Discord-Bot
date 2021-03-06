# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 15:52:07 2019

@author: Liam
"""

from scipy import interpolate as ip
from PIL import Image
from PIL import GifImagePlugin
import numpy as np
import time, re

class Curve:

    def __init__(self):
        """Constructs the LUT TABLE needed for making the images"""

        #self.LUT_TABLE = np.array([])

        P = np.array([ # x, y
           [0.00000, 0.00000],
           [0.09975, 0.25581],
           [0.10224, 0.88889],
           [0.13716, 0.00000],
           [0.13965, 0.71576],
           [0.14214, 0.85788],
           [0.28429, 0.00000],
           [0.28678, 0.54005],
           [0.28928, 0.32558],
           [0.29177, 0.58656], #row 10
           [0.32918, 0.70543],
           [0.33167, 0.62532],
           [0.49377, 0.58915],
           [0.49626, 0.20672],
           [0.67830, 0.55297],
           [0.68080, 0.31525],
           [0.68579, 0.13695],
           [0.71072, 0.78295],
           [0.78055, 0.02326],
           [0.78803, 0.58140], # row 20
           [0.80050, 0.00000],
           [1.00000, 1.00000]
        ])

        new_y = ip.Akima1DInterpolator(P[:,0],P[:,1])
        
        
        self.LUT_TABLE = []
        for i in range(0,256):
            new_val  = int(new_y(i/255)*255)
            self.LUT_TABLE = np.append(self.LUT_TABLE,new_val)
                
        self.LUT_TABLE = np.clip(self.LUT_TABLE,0,255)
        self.LUT_TABLE_RGB = np.concatenate([self.LUT_TABLE,self.LUT_TABLE,self.LUT_TABLE])
    
    def curveImg(self,filename):
        """Takes a filename, applies curves to it and overwrites"""
        
        img = Image.open(filename)
        
        def curve(img):
            """Takes PIL image object, performs curve to img and returns ref """
            img = img.convert("RGB")
            img = img.point(self.LUT_TABLE_RGB)
            if img.width > 5000 and img.height<=img.width: #wide or square aspect
                img = img.resize((5000,int(5000*img.height/img.width)))
            elif img.height >5000 and img.height>=img.width: #tall aspect
                img = img.resize((int(img.width*5000/img.height),5000))
            return img
            
        try:
            if img.is_animated:
                
                
                img_list = [ ]
                dur_list = [ ]
                
                for i in range(0,img.n_frames):
                    img.seek(i)
                    dur_list.append(img.info['duration'])
                    img2 = img.copy()
                    img2 = curve(img2)
                    img_list.append(img2)
            
                img_list[0].save(filename, format='GIF', append_images=img_list[1:], duration = dur_list, save_all=True, loop=0)
        except AttributeError as e: # Single static img, not gif
            img = curve(img)   #If quality is bad up quality value or add subsampling=0
            img.save(filename,quality=20)
         
    def percentileClip(self, filename):
        """Takes filename string, performs percentile clipping, replaces original file"""
        img = Image.open(filename)
        hist = np.array(img.histogram())
        cumHist = np.cumsum(hist)

        alph = 0.5 #%
        beta = 100 #%

        i=0
        while i!=256:
            if cumHist[i]*100/(500*500) >=alph:
                break
            i+=1
        j=255
        while j != -1:
            if cumHist[j]*100/(500*500) <= beta:
                break
            j-=1

        LUT = np.array([x for x in range(0,256)])
        LUT = 255*(LUT-i)/(j-i)
        LUT = LUT.astype(int)
        img = img.point(LUT)
        img.save(filename)
        
if __name__=="__main__":
    pass