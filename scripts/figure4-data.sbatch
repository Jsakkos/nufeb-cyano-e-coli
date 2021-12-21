#!/bin/bash -l
#SBATCH -J fig4
#SBATCH --ntasks=100
#SBATCH --mem-per-cpu=1g
#SBATCH -t 10:00:00 
#SBATCH --output=fig4.out 
#SBATCH --error=fig4.err
#SBATCH --mail-type=END
#SBATCH --mail-user=sakkosjo@msu.edu 

module load parallel
export LAMMPS=~/NUFEB/lammps/src/lmp_png
srun="srun -N1 -n2 --mpi=pmi2 --mem=1g --time 2:00:00"

cd /mnt/gs18/scratch/users/sakkosjo

#make NUFEB simulations for population stability runs
mkdir population-stability
cd population-stability
nufeb-clean
for i in 0.00206914 0.00428133 0.01274275 0.0379269 1.0
do
nufeb-seed --n 3 --cells 5,50 --iptg ${i}
nufeb-seed --n 3 --cells 1,100 --iptg ${i}
nufeb-seed --n 3 --cells 50,50 --iptg ${i}
nufeb-seed --n 3 --cells 50,5 --iptg ${i}
nufeb-seed --n 3 --cells 100,1 --iptg ${i}
nufeb-seed --n 3 --cells 75,25 --iptg ${i}
nufeb-seed --n 3 --cells 25,75 --iptg ${i}

done
parallel -j $SLURM_NTASKS "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/
cd /mnt/gs18/scratch/users/sakkosjo

mkdir sucrose
cd sucrose
nufeb-clean
#make NUFEB simulations for sucrose level sweep
for i in 0.001 0.00143845 0.00206914 0.00297635 0.00428133 0.00615848 0.00885867 0.01274275 0.01832981 0.02636651 0.0379269 0.05455595 0.078476 0.11288379 0.16237767 0.23357215 0.33598183 0.48329302 0.6951928 1. #0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
do
nufeb-seed --n 3 --cells 50,50 --iptg ${i}
done
parallel -j $SLURM_NTASKS "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/
cd /mnt/gs18/scratch/users/sakkosjo


mkdir mu-sweep
cd mu-sweep
nufeb-clean
#make NUFEB simulations for mu sweep
for i in 1.89e-06 3.15e-06 5.26e-06 8.77e-06 1.46e-05 2.44e-05 4.07e-05 6.79e-05 1.13e-04 1.89e-04
do
        for j in 0.00206914 0.00428133 0.01274275 0.0379269 1.0
        do
                nufeb-seed --n 3 --iptg ${j}  --muecw ${i}
        done
done
parallel -j $SLURM_NTASKS "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/
cd /mnt/gs18/scratch/users/sakkosjo




