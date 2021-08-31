#!/bin/bash

mpirun -np 8 lmp_png -in Inputscript_50_0_0.lammps > Inputscript_50_0_0.log
cd Run_50_0_0_1
tar -zcf VTK.tar.gz *.vtr *.vtu *.vti
python3 ../../nufeb-tools/Datafedcreate.py --id None --n VTK --m ../run_50_0_0.pkl --f ./VTK.tar.gz
python3 ../../nufeb-tools/Datafedcreate.py --id None --n Avg_con --m ../run_50_0_0.pkl --f ./Results/avg_concentration.csv
python3 ../../nufeb-tools/Datafedcreate.py --id None --n Biomass --m ../run_50_0_0.pkl --f ./Results/biomass.csv
python3 ../../nufeb-tools/Datafedcreate.py --id None --n Ntypes --m ../run_50_0_0.pkl --f ./Results/ntypes.csv
python3 ../../nufeb-tools/Datafedcreate.py --id None --n Trajectory --m ../run_50_0_0.pkl --f ./trajectory.h5
python3 ../../nufeb-tools/Datafedcreate.py --id None --n Log --m ../run_50_0_0.pkl --f ../Inputscript_50_0_0.log
cd ..
