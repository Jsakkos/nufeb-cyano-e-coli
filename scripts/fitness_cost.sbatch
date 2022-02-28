#!/bin/bash -l
#SBATCH -J fitness
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1g
#SBATCH -t 4-0
#SBATCH --output=fitness-cost.out
#SBATCH --error=fitness-cost.err
#SBATCH --mail-type=END
#SBATCH --mail-user=sakkosjo@msu.edu
~/nufeb-cyano-e-coli/scripts/fitness_cost.sh