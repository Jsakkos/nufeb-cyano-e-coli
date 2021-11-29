#!/bin/bash -l
#SBATCH -J se-data
#SBATCH -A cnms
#SBATCH -p batch
#SBATCH --nodes 3
#SBATCH --ntasks-per-node=32 
#SBATCH --mem=50g 
#SBATCH -t 1:00:00 
#SBATCH --output=test.out 
#SBATCH --error=test.err 

# script to generate validation simulations with axenic S. elongatus and run them on CADES
module purge
module load PE-gnu/3.0
module load parallel
export LAMMPS=~/NUFEB/lammps/src/lmp_png

cd /lustre/or-scratch/cades-cnms/12x

nufeb-clean

for i in 0 .005 .01 .02 .05 .1 .2 .5 1
do
nufeb-seed --n 5 --cells 100,0 --d 1e-4,1e-4,1e-4 --grid 20 --t 8700 --sucR ${i}
done
srun="srun -N1 -n32 --time 10:00"
parallel -j $SLURM_NTASKS "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/