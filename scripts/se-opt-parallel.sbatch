#!/bin/bash -l
#SBATCH -J se-optimization
#SBATCH -A vermaaslab
#SBATCH --nodes 1
#SBATCH --ntasks=8
#SBATCH --mem=20g
#SBATCH -t 10:00:00
#SBATCH --output=nufeb.out
#SBATCH --error=nufeb.err
#SBATCH --mail-type=END
#SBATCH --mail-user=sakkosjo@msu.edu
set -x
python3 /mnt/home/sakkosjo/nufeb-cyano-e-coli/scripts/se-ODopt-ICER.py > nufeb.log
