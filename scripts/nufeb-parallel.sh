#!/bin/bash -l
module load parallel

export LAMMPS=~/NUFEB/lammps/src/lmp_png
cd ~/NUFEB
srun="srun -N1 -n8 --mpi=pmi2 --time 10:00"
parallel -j $SLURM_NTASKS --joblog logs/runtask.log --resume "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/