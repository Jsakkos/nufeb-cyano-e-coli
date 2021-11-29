#!/bin/bash -l
#SBATCH -J fig4
#SBATCH -A vermaaslab
#SBATCH --ntasks=144
#SBATCH --ntasks-per-node=16
#SBATCH --mem-per-cpu=5g
#SBATCH -t 10:00:00 
#SBATCH --output=fig4.out 
#SBATCH --error=fig4.err 

export LAMMPS=~/NUFEB/lammps/src/lmp_png
cd /mnt/gs18/scratch/users/sakkosjo

#make NUFEB simulations for population stability runs
mkdir population-stability
cd population-stability
for i in 0.001 0.01 0.05 0.1 1.0
do
nufeb-seed --cells 5,50 --sucR ${i}
nufeb-seed --cells 1,100 --sucR ${i}
nufeb-seed --cells 50,50 --sucR ${i}
nufeb-seed --cells 50,5 --sucR ${i}
nufeb-seed --cells 100,1 --sucR ${i}
nufeb-seed --cells 75,25 --sucR ${i}
nufeb-seed --cells 25,75 --sucR ${i}

done
cd ..

mkdir sucrose
cd sucrose
#make NUFEB simulations for sucrose level sweep
for i in 0.001 0.00215443 0.00464159 0.01 0.02154435 0.04641589 0.1 0.21544347 0.46415888 1.0 #0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
do
nufeb-seed --n 5 --cells 50,50 --sucR ${i}
done
cd ..


mkdir mu-sweep
cd mu-sweep
#make NUFEB simulations for mu sweep
for i in 1.89e-06 3.15e-06 5.26e-06 8.77e-06 1.46e-05 2.44e-05 4.07e-05 6.79e-05 1.13e-04 1.89e-04
do
        for j in 0.001 0.01 0.05 0.1 1.0
        do
                nufeb-seed --n 5 --sucR ${j}  --muecw ${i}
        done
done
cd ..


srun="srun -N1 -n16 --mpi=pmi2 --time 20:00" #-N1 
parallel -j $SLURM_NTASKS "cd {1} && $srun $LAMMPS -in *.lammps > nufeb.log" ::: runs/*/

