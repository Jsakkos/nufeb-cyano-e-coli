#!/bin/bash -l
#SBATCH -J se-optimization
#SBATCH -A vermaaslab
#SBATCH --nodes 1
#SBATCH --ntasks=8
#SBATCH --mem=20g
#SBATCH -t 10:00:00
#SBATCH --output=nufeb-parallel.out
#SBATCH --error=nufeb-parallel.err
#SBATCH --mail-type=END
#SBATCH --mail-user=sakkosjo@msu.edu

python3 /mnt/home/sakkosjo/nufeb-cyano-e-coli/scripts/se-ODopt-ICER.py
