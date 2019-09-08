from urllib.request import urlretrieve

import astropy.units as u
from astroquery.skyview import SkyView
from astropy.io import fits
from astropy.coordinates import name_resolve
from PIL import Image
import numpy as np
import time, os


def reqImg(objname, radii):
    """Takes astro object name as string, radius of fov float, and saves a fits file, returns string filename"""
    try:
        url = SkyView.get_image_list(position=objname, survey=['DSS'], pixels="500,500",radius=radii*u.deg)[0]
    except name_resolve.NameResolveError:
        return "Error: Object name unabled to be resolved in simbad"
    filename = str(int(time.time()*1000000))+'.fits'
    urlretrieve(url, filename)
    return filename


def fitToJpg(filename):
    """Takes a fits filename string, opens fits and saves as 8 bit jpeg, deletes fits returns new filename string"""
    image_data = fits.getdata(filename,ext=0)
    maxVal = image_data.max()
    image_data*=255/maxVal
    image = Image.fromarray(np.uint8(image_data),mode="L")
    newFilename = filename.rstrip('.fits')+'.jpg' #Assume ends with .fits and not .FIT etc
    image.save(newFilename)

    return newFilename

if __name__ == "__main__":
    #Example usage
    f1 = reqImg("M20",1)
    f2 = fitToJpg(f1)
    os.remove(f1)
