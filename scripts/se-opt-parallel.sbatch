#!/bin/bash -l
#SBATCH -J loop
#SBATCH -A vermaaslab
#SBATCH --ntasks=72
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=5g
#SBATCH -t 1:00:00
#SBATCH --output=nufeb-parallel.out
#SBATCH --error=nufeb-parallel.err

python3 /mnt/home/sakkosjo/nufeb-cyano-e-coli/scripts/se-opt-ICER.py
