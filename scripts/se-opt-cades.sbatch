#!/bin/bash -l
#SBATCH -J se-optimization
#SBATCH -A cnms
#SBATCH -p batch
#SBATCH --nodes 1
#SBATCH --ntasks=8
#SBATCH --mem=10g
#SBATCH -t 2-00:00:00
#SBATCH --output=nufeb.out
#SBATCH --error=nufeb.err
#SBATCH --mail-type=END
#SBATCH --mail-user=sakkosjo@msu.edu

set -x
python3 home/12x/nufeb-cyano-e-coli/scripts/se-ODopt-CADES.py > nufeb.log
