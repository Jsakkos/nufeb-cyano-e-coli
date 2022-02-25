import os
import subprocess
from pathlib import Path
from string import Template
import numpy as np

    #os.chdir('/mnt/home/sakkosjo/NUFEB/')




    #Change input params
fitness = np.linspace(0.1,1,10)
biomass_flux = np.linspace(0.5,5,10)
#os.chdir('/mnt/gs18/scratch/users/sakkosjo/nufeb-fitness')

#os.mkdir('finished')
#os.system('nufeb-clean')
for fit in fitness:
    for flux in biomass_flux:
        os.chdir('/mnt/gs18/scratch/users/sakkosjo/fitness-cost')
        text = 'nufeb-seed --n 3 --cells 50,50 --iptg 1'
        os.system(text)
        os.system(f'mv runs runs_{fit}_{flux}')
        #print(f'fitness: {fit},flux: {flux}')
        #Seed new simulations

        #print('Running simulations')
        #os.system('/mnt/home/sakkosjo/pyrun.sh')
        #print('Moving simulations')
        #srun_text = 'srun -N1 -n1 --mpi=pmi2 --mem=1g --time 3:30:00 /mnt/gs18/scratch/users/sakkosjo/nufeb-fitness/src/lmp_png -in *.lammps > nufeb.log &'
        #folders = [path for path in BASE_DIR.iterdir() if path.is_dir()]
        #for i, folder in enumerate(folders):
        #    os.system(f'mv {folder} ../finished/{folder}_{fit}_{flux}_{i}')
        #for folder in folders:
        #    os.system(f'cd {folder} && {srun_text}')
        #         os.system('base=$PWD; for dir in runs/*/;do;cd "$dir";srun -N1 -n1 --mpi=pmi2 --mem=1g --time 3:30:00 /mnt/gs18/scratch/users/sakkosjo/nufeb-fitness/src/lmp_png -in *.lammps > nufeb.log &;cd "$base";done;wait')
        #
        #print(f'Done with fitness: {fit},flux: {flux}')





