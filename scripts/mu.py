import os
import nufeb_tools
import numpy as np
from pathlib import Path
space = np.logspace(-6,-3,2)
os.chdir('/mnt/gs18/scratch/users/sakkosjo/mu-sweep')
os.system('nufeb-clean')
    
for mu in space:
    text = f'nufeb-seed --n 5  --muecw ${mu}'
    os.system(text)

DIR = Path('/mnt/gs18/scratch/users/sakkosjo/mu-sweep/runs')
folders = [path for path in DIR.iterdir() if path.is_dir()]
for folder in folders:
    text = f'srun -N1 -n2 --mpi=pmi2 --mem=1g --time 2:00:00 ~/NUFEB/lammps/src/lmp_png -in {folder}/*.lammps > nufeb.log'
    os.system(text)
