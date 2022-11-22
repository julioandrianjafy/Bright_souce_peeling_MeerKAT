# script to mask the model image
# the bs position needs to be set manually (This can be automated from setup.py in future)
# Julio Cesar Andrianjafy (andrianjafyjuliocsar@yahoo.fr)
# Affiliations: University of Mauritius, ThunderKAT team (http://www.thunderkat.uct.ac.za/) 
#    and DARA advanced student (https://www.dara-project.org/julio-cesar-andrianjafy)

import sys
from astropy.io import fits
import numpy as np

# the inputs must be python argv[0] model_name new_name n_chans
model_name = sys.argv[1]
new_model = sys.argv[2]
n_chans = int(sys.argv[3])
bs_sources = [[2261,5656]] # bs position in pixel

imsize = 3000

# load fits images
def load_fits(fitsname,arshape=imsize):
    myfits = fits.open(fitsname)
    data = myfits[0].data
    return data.shape,data.reshape(arshape,arshape)

# convert an array to fits file
def array_to_fits(my_array,arr_name):
    hdu = fits.PrimaryHDU(my_array)
    hdu.writeto(arr_name)

# create data cube for a given position
def cube(position,size=100):

    xx = [position[0]-int(size/2),position[0]+int(size/2)]
    yy = [position[1]-int(size/2),position[1]+int(size/2)]

    return xx,yy

# mask a given model
# assume that the model is already an array
def mask_model(positions,arshape=imsize):

    # create array of zeros
    myarray = np.zeros(shape=[arshape,arshape])

    # change area of interests to 1
    for i in range(len(positions)):

        # get cube
        cubes = cube(positions[i])

        # change my array
        myarray[cubes[0][0]:cubes[0][1],cubes[1][0]:cubes[1][1]] = 1

    return myarray

# add header (unit)
def add_bunit(image):

    # open file
    myfits = fits.open(image,mode='update')

    myfits[0].header.append(('BUNIT','Jy/beam'))
    myfits.close()

# make masks
# it is the same for all channels (we only do this operation one time)
mymask = mask_model(bs_sources)

if n_chans == 1:

    imname = model_name+'-model.fits'
    newname = new_model+'-model.fits'
    myfits = load_fits(imname)

    # multiply
    newarray = mymask*myfits[1]
    newarray = np.reshape(newarray,newshape=myfits[0])
    array_to_fits(newarray,newname)
    add_bunit(newname)

else:
    # loop over all images
    for i in range(n_chans):

        torev = '000' + str(i)
        torev = torev[::-1][0:4][::-1]

        imname = model_name+'-'+torev+'-model.fits'
        newname = new_model+'-'+torev+'-model.fits'

        # multiply
        myfits = load_fits(imname)
        newarray = mymask*myfits[1]
        newarray = np.reshape(newarray,newshape=myfits[0])
        array_to_fits(newarray,newname)
        add_bunit(newname)
