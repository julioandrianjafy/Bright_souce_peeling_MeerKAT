# Bright souce peeling with MeerKAT data 

This repository provides simple codes to remove spurious bright sources with MeerKAT data (Could be adapted to other instruments) using only python scripts, CASA (https://casa.nrao.edu/casa_obtaining.shtml) and WSClean (https://wsclean.readthedocs.io/en/latest/). There are many efficient way to perfom peeling but our simple approach (inspired by the procedures described in  [Williams et al. 2019](https://iopscience.iop.org/article/10.3847/2515-5172/ab35d5)) was sufficient for such task in our recent work ([Andrianjafy et al. 2022](https://academic.oup.com/mnras/advance-article-abstract/doi/10.1093/mnras/stac3348/6832780)).     

# Environment and software

- [Ilifu cloud](https://docs.ilifu.ac.za/#/): For now, the codes could only be run by submitting jobs to the ilifu cluster.  
- Python version > 3.6
- [CASA version > 6.0](https://casa.nrao.edu/casa_obtaining.shtml)
- [WSClean version > 1.6.3](https://wsclean.readthedocs.io/en/latest/)

# Running the scripts 
- Configure parameters in setup.py 
- For the present moment, the bright source position (image coordinates) needs to be specified manually in the make_mask.py and make_mask_inv.py
- Run process.py in python: this will create bash files (peel*.sh and mainbash.sh).
- Submit all peel*.sh (The number of peel*.sh depends on how many sub frequency channels you want to subtract the BS independently in setup.py) to ilifu cluster
- Submit mainbash.sh to complete the subtraction

# Contact details
If case of any bugs, more information request, or you would like to contribute in improving the scripts, feel free to email me (andrianjafyjuliocsar@yahoo.fr).
