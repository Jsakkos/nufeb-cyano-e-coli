#!/bin/bash -l
#SBATCH -J loop
#SBATCH -A vermaaslab
#SBATCH --ntasks=72
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=5g
#SBATCH -t 10:00
#SBATCH --output=nufeb-parallel.out
#SBATCH --error=nufeb-parallel.err
#SBATCH -W

module load parallel

export LAMMPS=~/NUFEB/lammps/src/lmp_png
cd ~/NUFEB
srun="srun -N1 -n8 --mpi=pmi2 --time 10:00"
parallel -j $SLURM_NTASKS --joblog logs/runtask.log --resume "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/