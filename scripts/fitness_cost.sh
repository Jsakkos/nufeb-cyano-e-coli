#!/bin/bash -l
module load libpng
export LAMMPS=/mnt/gs18/scratch/users/sakkosjo/fitness-cost/lammps/src/lmp_png
srun="srun -N1 -n1 --mpi=pmi2 --mem=1g --time 3:30:00"
cd /mnt/gs18/scratch/users/sakkosjo/fitness-cost
for i in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0; do
    for j in 0.5 1 2 3 4 5; do
        python ~/nufeb-cyano-e-coli/scripts/fitness_params.py -f $i -s $j
        ./install.sh --enable-hdf5
        nufeb seed --n 3
        for dir in runs/*/; do
            cd "$dir"
            $srun $LAMMPS -in *.lammps > nufeb.log &
            cd /mnt/gs18/scratch/users/sakkosjo/fitness-cost
        done
        wait
        mv runs runs_${i}_${j}
        echo "fitness $i, biomass $j done"
    done
done