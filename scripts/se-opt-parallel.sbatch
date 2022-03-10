#!/bin/bash -l
#SBATCH -J se-optimization
##SBATCH -A vermaaslab
#SBATCH --nodes 1
#SBATCH --ntasks=1
#SBATCH --mem=1g
#SBATCH -t 4-00:00:00
#SBATCH --output=nufeb.out
#SBATCH --error=nufeb.err
#SBATCH --mail-type=END
#SBATCH --mail-user=sakkosjo@msu.edu
#SBATCH -C '[intel14|intel16|intel18]'
set -x
python3 /mnt/home/sakkosjo/nufeb-cyano-e-coli/scripts/se-opt-ICER.py > nufeb_optimization.log
