#!/bin/bash -l
#SBATCH -J loop
#SBATCH -A cnms
#SBATCH -p burst
#SBATCH --nodes 3
#SBATCH --ntasks-per-node=32
#SBATCH --mem=50g
#SBATCH -t 1:00:00
#SBATCH --output=test.out
#SBATCH --error=test.err
#SBATCH -W
module purge
module load PE-gnu/3.0
module load parallel
export LAMMPS=~/NUFEB/lammps/src/lmp_png

cd /lustre/or-scratch/cades-cnms/12x
srun="srun -N1 -n32 --time 10:00"
parallel -j $SLURM_NTASKS "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/
