# function to generate jobs to ilifu cluster
# Julio Cesar Andrianjafy (andrianjafyjuliocsar@yahoo.fr)
# Affiliations: University of Mauritius, ThunderKAT team (http://www.thunderkat.uct.ac.za/) 
#    and DARA advanced student (https://www.dara-project.org/julio-cesar-andrianjafy)

# import modules
import setup
import os

# define a function to generate jobs
def genjobs(bashname,jobname='selfcal',mem=164,nodes=1,runtime='3:00:00'):
    bashfile = open(bashname,'w+')
    bashfile.writelines(['#!/bin/bash\n\n',
                         '#SBATCH --job-name=\''+jobname+'\'\n',
                         '#SBATCH --cpus-per-task=32\n',
                         '#SBATCH --mem='+str(mem)+'GB\n',
                         '#SBATCH --output=testjob-%j-stdout.log\n',
                         '#SBATCH --error=testjob-%j-stderr.log\n',
                         '#SBATCH --time='+runtime+'\n',
                         '#SBATCH --nodes='+str(nodes)+'\n\n'])
    bashfile.close()
    os.system('chmod +x '+bashname)

# casa6
def casa6(pyfile,container=setup.casa6_cont):
    return 'singularity exec '+container+' python3 '+pyfile

# image with wsclean
def wsclean(ms,name,immask = False,ismask = False,smooth=False,threshval=False, minuv = False,predict=False,update=False,chanrg=False,chanout=1,weight='natural',container=setup.wsclean_cont):
    outreturn = 'singularity exec '+container+' wsclean '
    if predict:
        outreturn += '-predict '

    if immask!=False:
        outreturn += '-fits-mask '+immask+' '

    if ismask!=False:
        outreturn += '-auto-mask '+str(ismask)+' -auto-threshold 0.1 '
    if threshval!=False:
        outreturn += '-threshold '+str(threshval)+' '

    if update==False:
        outreturn += '-no-update-model-required '
    outreturn +='-use-wgridder -no-negative -no-dirty -size 3000 3000 -scale 3asec '
    outreturn += '-weight '+weight+' '
    if minuv!= False:
        outreturn += '-minuvw-m '+str(minuv)+' '
    if smooth:
        outreturn += '-join-channels -fit-spectral-pol 4 '
    else:
        outreturn += '-no-mf-weighting '
    if chanrg!=False:
        outreturn += '-channel-range '+chanrg+' '
    outreturn += '-channels-out '+str(chanout)+' '
    outreturn += '-intervals-out 1 -mgain 0.85 -niter 120000 '
    outreturn += '-name '+name+' '+ms
    return outreturn
