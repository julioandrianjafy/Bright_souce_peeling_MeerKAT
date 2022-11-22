# Config file for input parameters
# Julio Cesar Andrianjafy (andrianjafyjuliocsar@yahoo.fr)
# University of Mauritius, ThunderKAT team (http://www.thunderkat.uct.ac.za/), DARA advanced student (https://www.dara-project.org/julio-cesar-andrianjafy)

# import modules
import os

# containers (casa and wsclean)
casa6_cont = '/idia/users/julioanj/containers/casa-6.1-2020-08-27.simg'
wsclean_cont = '/idia/users/julioanj/containers/wsclean_1.6.3.sif'

# python file
cur_dir = os.getcwd() + '/' # current directory
casapy = cur_dir+'casa6_tasks.py' # relevant casa tasks
maskpy = cur_dir+'make_mask.py' # script to mask the rest of the field to solve for bright source only
maskpy_inv = cur_dir+'make_mask_inv.py' # script to mask the bright source (to get the model of the field)
## the bs position needs to be set manually in the make_maskscripts (This can be automated from setup.py in future)

# create new directory
create_dir = True
newdir = 'Bright_source_peeling'

# ms file (the data column should contain the calibrated data after 1GC)
# no corrected data and no model yet
msfile = 'main.ms'

# selfcal information
#sol_int = '4s' # solution interval for calibration
refant = 'm007,m002,m004,m006'

# spws
sp = [0,3699] # this is in casa term (inclusive)
joins = True # to use join channels during deconv
subchan = 4
nchan = 7 # number of spw to apply selfcal independently

# number of selfcal round
limitphase = 0.04 # solve only if bs flux density > limitphase
limitbp = 0.05 # # solve only if bs flux density > limitbp
rfield = 0.0005 # model of the fields to remove from the data (in mJy)
rbs = 0.01 #threshold during selfcal of the bright source
rbslast = 4 # use of automask at the end
uvmin = False # minimum baseline length to deconvolve
solveuv = 0 # minimum baseline length to solve
