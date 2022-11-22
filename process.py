# Direction independent calibration (MeerKAT data and ilifu cluster)
# Julio Cesar Andrianjafy (andrianjafyjuliocsar@yahoo.fr)
# University of Mauritius, ThunderKAT team (http://www.thunderkat.uct.ac.za/), DARA advanced student (https://www.dara-project.org/julio-cesar-andrianjafy)

import os
import gen_job
import setup

# variables
casapy = setup.casapy
orgms = setup.msfile
dirname = setup.newdir
nchan = setup.nchan
sp = setup.sp
joins = setup.joins
subchan = setup.subchan
nchan = setup.nchan
rfield = setup.rfield
rbs = setup.rbs
rbslast = setup.rbslast
uvmin = setup.uvmin
solveuv = setup.solveuv
maskpy = setup.maskpy
maskpy_inv = setup.maskpy_inv

# spectral divisions
def spws():
    chant = sp[1] - sp[0] + 1
    sporg = '0:'+str(sp[0])+'~'+str(sp[1])
    sptrans = '0:'+str(0)+'~'+str(chant-1)
    step = int(chant/nchan)

    spclean = []
    for i in range(0,chant,step):

        if (i+step)<=chant:
            sp0 = i
            limit = step*nchan-step
            if i!=(limit):
                sp1 = i+step
            else:
                sp1 = chant
            spclean.append([sp0,sp1])

    spclean2 = []
    for i in range(0,chant,step):

        if (i+step)<=chant:
            sp0 = i
            limit = step*nchan-step
            if i!=(limit):
                sp1 = i+step
            else:
                sp1 = chant
            spclean2.append('0:0~'+str(sp1-1-sp0))

    spclean3 = []
    for i in range(len(spclean)):

        sp0 = spclean[i][0]+sp[0]
        sp1 = spclean[i][1]-1+sp[0]
        spclean3.append('0:'+str(sp0)+'~'+str(sp1))

    spsolve = []
    for i in range(len(spclean)):

        sp0 = spclean[i][0]
        sp1 = spclean[i][1]-1
        spsolve.append('0:'+str(sp0)+'~'+str(sp1))

    spcleanws = []
    for i in range(len(spclean)):

        chans = str(spclean[i][0])+' '+str(spclean[i][1])
        spcleanws.append(chans)

    return spclean,spclean2,spclean3, spsolve, sptrans, sporg

spw_conf = spws()
spclean = spw_conf[0]
spclean2 = spw_conf[1]
spclean3 =spw_conf[2]
spsolve = spw_conf[3]
sptrans = spw_conf[4]
sporg = spw_conf[5]

###########################################################################
#### create directory cp casapy to the directory
def create_dir(create=setup.create_dir,bnames = dirname):
    if create:
        if os.path.isdir(dirname):
            os.system('rm -rf '+bnames)
        os.system('mkdir '+bnames)
create_dir()
##########################################################################

# create bash
def create_bash(mysh):
    # create bash file
    mybash = mysh
    gen_job.genjobs(bashname = mybash)

# create function to peel in each spws
def peel(msname,bashfile,index):

    # open file
    f = open(bashfile,'a+')

    # extract orgms
    myms = msname
    f.writelines([gen_job.casa6(casapy)+' mstrans '+orgms+' '+myms+' corrected '+spclean3[index]+'\n\n'])


    #################################################################################
    ####################### step1: remove model of the rest of the field ###########

    # clean deeply
    field = 'field_deep_fr'+str(index)
    f.writelines([gen_job.wsclean(myms,field,smooth=joins,immask=False,ismask=3,chanout=subchan)+'\n\n'])

    # mask bright source from the model
    mask = 'mask_field_fr'+str(index)
    f.writelines([gen_job.casa6(maskpy_inv)+ ' '+ field +' '+mask+' '+str(subchan)+'\n\n'])

    # predict to ms
    f.writelines([gen_job.wsclean(myms,mask,predict=True,ismask=3,update=True,chanout=subchan)+'\n\n'])

    # subtract field_mod from the data
    # these are all approximation and some faint sources might not be removed
    # but bright enough sources should have been removed
    f.writelines([gen_job.casa6(casapy)+' submodel '+myms+'\n\n'])

#####################################################################################
############# Step2: perform gain phase self calibration ############################
    # extract data
    bs0 = 'bs0_fr'+str(index)+'.ms'
    f.writelines([gen_job.casa6(casapy)+' mstrans '+myms+' '+bs0+' corrected '+spclean2[index]+'\n\n'])

    # clear calibration table (add corrected data)
    f.writelines([gen_job.casa6(casapy)+' clearcal '+bs0+'\n\n'])

    # clean deep and use the rbs model image as a fits mask
    # this required two runs but it is important to avoid (or minimize) false sources in the model
    field = 'field_fr_'+str(index)
    f.writelines([gen_job.wsclean(bs0,field,smooth=joins,immask=False,ismask=5,chanout=subchan,minuv=uvmin)+'\n\n'])

    # use mask that only contains bs
    # normally the rbs choosen should not allow other sources (apart from the bs) in the model images
    # but this is a cautionary measure
    mask = 'field_mod_fr_'+str(index)
    f.writelines([gen_job.casa6(maskpy)+ ' '+ field +' '+mask+' '+str(subchan)+'\n\n'])

    # predict model of the bs in the data
    f.writelines([gen_job.wsclean(bs0,mask,predict=True,ismask=5,update=True,minuv=uvmin,chanout=subchan)+'\n\n'])

    # solve if the source in the model is bright enough (good SNR)
    # this can be tuned with limit
    msk = field + '-MFS-image.fits'
    f.writelines(['state=$('+gen_job.casa6(casapy)+' evalmodel '+msk+' '+str(setup.limitphase)+')\n\n'])

    tbname = 'gain_phase_fr'+str(index)+'.G0'
    f.writelines([gen_job.casa6(casapy)+' solve '+bs0+' '+tbname+' '+spclean2[index]+' '+str(solveuv)+' $state\n\n'])

#####################################################################################
############# Step3: perform bandpass self calibration ############################

    # extract data
    bs1 = 'bs1_fr'+str(index)+'.ms'
    f.writelines([gen_job.casa6(casapy)+' mstrans '+bs0+' '+bs1+' corrected '+spclean2[index]+'\n\n'])

    # clear calibration table (add corrected data)
    f.writelines([gen_job.casa6(casapy)+' clearcal '+bs1+'\n\n'])

    # clean using automask
    field = 'field_fr_bp_'+str(index)
    f.writelines([gen_job.wsclean(bs1,field,smooth=joins,ismask=4,chanout=subchan,minuv=uvmin)+'\n\n'])

    # use mask that only contains bs (same as in phase self cal)
    mask = 'field_mod_fr_bp_'+str(index)
    f.writelines([gen_job.casa6(maskpy)+ ' '+ field +' '+mask+' '+str(subchan)+'\n\n'])

    # predict model of the bs in the data
    f.writelines([gen_job.wsclean(bs1,mask,predict=True,ismask=4,update=True,minuv=uvmin,chanout=subchan)+'\n\n'])

    # solve if the source in the model is bright enough (good SNR)
    # this can be tuned with limit
    msk = field + '-MFS-image.fits'
    f.writelines(['state=$('+gen_job.casa6(casapy)+' evalmodel '+msk+' '+str(setup.limitbp)+')\n\n'])

    tbname = 'bp_fr'+str(index)+'.B0'
    f.writelines([gen_job.casa6(casapy)+' solve_bp '+bs1+' '+tbname+' '+spclean2[index]+' '+str(solveuv)+' $state\n\n'])

## run functions
bashes = []
for i in range(nchan):

    # create bash
    soloname = 'peel'+str(i)+'.sh'
    bashn = dirname+'/'+soloname
    bashes.append(soloname)
    create_bash(bashn)

    # peel
    msn = 'ms_temp_'+str(i)+'.ms'
    #spsolv = spsolve[i]
    #spextract = spclean[3]
    peel(msn,bashn,i)

# create mainbash
mainbash = dirname+'/mainbash.sh'
create_bash(mainbash)

# open file
f = open(mainbash,'a+')
for i in range(nchan):
    f.writelines(['sbatch '+bashes[i]+'\n\n'])

# create newms
mainms = 'main.ms'
f.writelines([gen_job.casa6(casapy)+' mstrans '+orgms+' '+mainms+' corrected '+sporg+'\n\n'])

# clear calibration table (add corrected data)
mask = 'field_fr_0'
f.writelines([gen_job.wsclean(mainms,mask,predict=True,ismask=4,update=True,chanout=subchan)+'\n\n'])
# use invgains module to calculate the inverse of the bs gains and inject it to mainms
# bs0mss
f.writelines([gen_job.casa6(casapy)+' invgains '+mainms+' '+str(nchan)+'\n\n'])

# subtract model from mainms
f.writelines([gen_job.casa6(casapy)+' submodel '+mainms+'\n\n'])

# showcase image
im_peel = 'peeled_image'
f.writelines([gen_job.wsclean(mainms,im_peel,ismask=4,chanout=1,weight='natural')])
