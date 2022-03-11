#!/bin/bash -l
#SBATCH -J se-opt
##SBATCH -A vermaaslab
#SBATCH --ntasks=90
#SBATCH --ntasks-per-node=2
#SBATCH --mem-per-cpu=1g
#SBATCH -t 20:00
#SBATCH --output=nufeb-parallel.out
#SBATCH --error=nufeb-parallel.err
#SBATCH -W

module load parallel

export LAMMPS=~/NUFEB/lammps/src/lmp_png
cd /mnt/gs18/scratch/users/sakkosjo
srun="srun -N1 -n2 --mpi=pmi2 --time 20:00" #-N1 
parallel -j $SLURM_NTASKS "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/