# casa6 tasks
# Julio Cesar Andrianjafy (andrianjafyjuliocsar@yahoo.fr)
# Affiliations: University of Mauritius, ThunderKAT team (http://www.thunderkat.uct.ac.za/) 
#    and DARA advanced student (https://www.dara-project.org/julio-cesar-andrianjafy)

# load modules
import casatasks as ct
import os
import sys
import setup
from casacore import tables as tb
import numpy as np
from astropy.io import fits

# variables
refant = setup.refant

# Task to perform
task = sys.argv[1]

# mstransform
def mstransform():

    # list  of arguments
    sys_len = len(sys.argv)
    inpms = sys.argv[2]
    outms = sys.argv[3]
    datacol = sys.argv[4]

    if sys_len == 5:
        spww = ''
    elif sys_len == 6:
        spww = sys.argv[5]

    # perform mstransform
    ct.mstransform(vis=inpms,outputvis=outms,datacolumn=datacol,spw=spww)

# evaluate model image
# verify if one needs to solve (bs brightness > the other sources)
def eval_model():

    im1 = sys.argv[2] # bs model
    limit = float(sys.argv[3]) # peak limit to solve

    # imsize
    imsize = 3000

    # load fits images
    def load_fits(fitsname,arshape=imsize):
        myfits = fits.open(fitsname)
        data = myfits[0].data
        return data.reshape(arshape,arshape)

    im1_d = load_fits(im1)

    if np.max(im1_d) >= np.max(limit):
        print(True)
    else:
        print(False)

# create a function to calculate the inverse of the gains and inject the model*invgains to newms
def invegains():

    # length of inputs
    lenin = len(sys.argv)

    # number of bs
    nbs = int(sys.argv[lenin-1])
    mainms = sys.argv[lenin-2]

    # calculate invgains from ms
    def inv(ms0,ms1):

        # loadms (read only)
        tb0 = tb.table(ms0)
        tb1 = tb.table(ms1)

        # extract data and corrected data
        data0 = tb0.getcol('DATA')
        cr_data0 = tb0.getcol('CORRECTED_DATA')

        # extract data and corrected data
        data1 = tb1.getcol('DATA')
        cr_data1 = tb1.getcol('CORRECTED_DATA')

        model_data = tb1.getcol('MODEL_DATA')

        # return inverse
        return (data0/cr_data0)*(data1/cr_data1)*model_data

    # load data and calculate invgains for each bs
    invs = []
    for i in range(nbs):

        m0 = 'bs0_fr'+str(i)+'.ms'
        m1 = 'bs1_fr'+str(i)+'.ms'
        invs.append(inv(m0,m1))

    # final model
    model_mult =  np.concatenate(invs,axis=1)

    # load mainms
    ms3 = tb.table(mainms,readonly=False,lockoptions='user')

    # replace model column to invgains*modeldata
    ms3.lock()
    ms3.putcol('MODEL_DATA',model_mult)
    ms3.unlock()

# create function to solve for G and apply
def cal_apply(antref = refant):

    # list of argumemt
    sys_len = len(sys.argv)
    myms = sys.argv[2] # provide msname
    tbl = sys.argv[3] # provide gaintable name
    myspw = sys.argv[4]
    myuv = '>'+sys.argv[5]+'km'
    solves = eval(sys.argv[6])
    print(solves)
    if solves==True:
        ct.gaincal(vis=myms, caltable=tbl,refant = antref,uvrange=myuv,spw=myspw,solint='2s',minsnr=5,
                  gaintype = 'G',calmode='p',parang=False,append=False)

    if os.path.isdir(tbl):
        ct.applycal(vis=myms,gaintable=[tbl],spw=myspw)

# create function to solve for bandpass
def cal_apply_bp(antref = refant):

    # list of argumemt
    sys_len = len(sys.argv)
    myms = sys.argv[2] # provide msname
    tbl = sys.argv[3] # provide gaintable name
    myspw = sys.argv[4]
    uvs = sys.argv[5]
    solves = eval(sys.argv[6])

    # solve
    if solves==True:
        ct.bandpass(vis=myms, caltable=tbl,
                    refant = antref,
                    solint='inf',
                    solnorm=False,
                    fillgaps =25,
                    minsnr=5.0,
                    bandtype='B',
                    parang=False)

    # applycal
    if os.path.isdir(tbl):
        ct.applycal(vis=myms,gaintable=[tbl],spw=myspw)

# function to subract model
def submodel():
    ct.uvsub(sys.argv[2])

# clear calibration table
def clearcal():
    ct.clearcal(sys.argv[2])

if task == 'mstrans':
    mstransform()
elif task == 'solve':
    cal_apply()
elif task == 'submodel':
    submodel()
elif task == 'invgains':
    invegains()
elif task == 'evalmodel':
    eval_model()
elif task=='solve_bp':
    cal_apply_bp()
elif task=='clearcal':
    clearcal()
else:
    print('option not recognised..')
