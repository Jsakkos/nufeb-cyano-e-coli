import random
from scipy.stats import loguniform
import argparse
import numpy as np
from string import Template
import json
import os
import sys
from datetime import date
from math import log10, floor
import logging
from pathlib import Path
from glob import glob


__author__ = "Jonathan Sakkos"
__copyright__ = "Jonathan Sakkos"
__license__ = "MIT"

_logger = logging.getLogger(__name__)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def parse_args(args):
    """Parse command line parameters

    Args:
        args (List[str]): command line parameters as list of strings
            (for example  ``["--help"]``).

    Returns:
        :obj:`argparse.Namespace`: command line parameters namespace
    """
    # arguments to modify the conditions of the simulation seeding
    parser = argparse.ArgumentParser(description="Create atom definition files")
    parser.add_argument(
        "--n",
        dest="num",
        action="store",
        default=10,
        help="Create atom definition files for NUFEB with --n #files desired (default is 10)",
    )
    parser.add_argument(
        "--r", dest="reps", action="store", default=1, help="Number of replicates"
    )
    parser.add_argument(
        "--co2",
        dest="co2",
        action="store",
        default=6.8e-1,
        help="Set initial CO2 concentration (mM)",
    )
    parser.add_argument(
        "--d",
        dest="dims",
        action="store",
        type=str,
        default="1e-3,5e-5,5e-5",
        help="Set simulation box dimensions (m)",
    )
    parser.add_argument(
        "--t",
        dest="timesteps",
        action="store",
        default=35000,
        help="Number of timesteps to run",
    )
    parser.add_argument(
        "--suc",
        dest="sucrose",
        action="store",
        default=1e-19,
        help="Set initial sucrose concentration (mM)",
    )
    parser.add_argument(
        "--grid",
        dest="grid",
        action="store",
        default=10,
        help="Diffusion grid density (um/grid)",
    )
    parser.add_argument(
        "--mono",
        dest="monolayer",
        action="store",
        default=True,
        help="Set seed generation to monolayer of cells",
    )

    parser.add_argument(
        "--cells",
        dest="cells",
        action="store",
        default=None,
        help="Number of cyanobacteria and e.coli to initialize simulation with, `e.g., 100,100. ` Default is random number between 1 and 100.",
    )

    parser.add_argument(
        "--iptg",
        dest="iptg",
        action="store",
        default=None,
        type=float,
        help="Set IPTG induction for sucrose secretion (0 to 1). Default is random.",
    )
    parser.add_argument(
        "--muecw",
        dest="mu_ecw",
        action="store",
        default=6.71e-5,
        type=float,
        help="E. coli W maximum growth rate",
    )
    parser.add_argument(
        "--mucya",
        dest="mu_cya",
        action="store",
        default=1.89e-5,
        type=float,
        help="S. elongatus maximum growth rate",
    )
    parser.add_argument(
        "--rhoecw",
        dest="rho_ecw",
        action="store",
        default=230,
        type=float,
        help="E. coli W cell density",
    )
    parser.add_argument(
        "--rhocya",
        dest="rho_cya",
        action="store",
        default=370,
        type=float,
        help="S. elongatus cell density",
    )
    parser.add_argument(
        "--ksuc",
        dest="ksuc",
        action="store",
        default=3.6,
        type=float,
        help="E. coli W Ksuc",
    )
    parser.add_argument(
        "--maintecw",
        dest="maint_ecw",
        action="store",
        default=9.50e-7,
        type=float,
        help="E. coli W maintenance cost",
    )
    parser.add_argument(
        "--mass",
        dest="mass_max",
        action="store",
        default=None,
        type=float,
        help="Maximum biomass",
    )

    parser.add_argument(
        "--vtk",
        dest="vtk",
        action="store",
        default=False,
        type=bool,
        help="Output VTK files",
    )
    parser.add_argument(
        "--h5", dest="hdf5", action="store", default=True, help="Output HDF5 files"
    )
    parser.add_argument(
        "--lammps",
        dest="lammps",
        action="store",
        default=False,
        help="Output lammps files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "-e",
        "--extent",
        dest='extent',
        help='The maximum distance between the S. elongatus colony and the E. coli seed cell',
        action="store",
        default=1e-3,
        type=float,
    )
    parser.add_argument(
        "-s",
        "--scale",
        dest='scale',
        help='Distance scaling, linear or logarithmic',
        action="store",
        default='log',
        type=str,
    )
    parser.add_argument(
        "-c",
        "--closed",
        dest='closed',
        help='Closed system for sucrose',
        action="store",
        default=False,
        type=bool,
    )
    return parser.parse_args(args)

def find_exp(number:float) -> int:
    base10 = log10(abs(number))
    return floor(base10)

def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def clean():
    """Remove old NUFEB runs"""
    if os.path.isdir("runs"):
        import shutil

        try:
            shutil.rmtree("runs")
        except OSError as e:
            print("Error: %s : %s" % ("runs", e.strerror))



def main(args):
    """Wrapper function to generate new NUFEB simulation conditions

    Args:
      args (List[str]): command line parameters as list of strings

    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.info("Generating NUFEB simulation files")
    # maximum growth rates, mu
    # $mu_cyanos = round(0.06/3600,7)
    # mu_ecw = 2.7e-04 for 37C only
    # mu_ecw = 6.71e-5
    # molecular weights of co2 and sucrose for unit conversions
    CO2MW = 44.01
    SucMW = 342.3
    #TEMPLATES_DIR = (Path(__file__).parent) / "templates"
    # check for runs folder
    if not os.path.isdir('../runs'):
        os.mkdir('../runs')
    today = str(date.today())
    if args.mass_max is not None:
        max_mass = float(args.mass_max)
    else:
        max_mass = (
            1.5e-11
            * np.prod([float(x) for x in args.dims.split(",")])
            / (1e-4 * 1e-4 * 1e-5)
        )
    if args.scale =='linear' or args.scale =='Linear':
        spacing = np.linspace(6e-5,args.extent,args.num)  
    elif args.scale =='log' or args.scale =='logarithmic':
        spacing = np.logspace(-6,find_exp(args.extent)-.05,args.num)+6e-5
    for n in range(1, int(args.num) + 1):
        if args.iptg is not None:
            IPTG = float(args.iptg)
            SucRatio = IPTG
        else:
            IPTG = np.round(loguniform.rvs(1e-3, 1e0, size=1)[0], 5)
            SucRatio = IPTG
        # if args.SucRatio is not None:
        #    SucRatio = float(args.SucRatio)

        SucPct = int(SucRatio * 100)

        cell_types = ["cyano", "ecw"]
        if args.cells is not None:
            n_cyanos = int(args.cells.split(",")[0])
            n_ecw = int(args.cells.split(",")[1])
        else:
            n_cyanos = int(500)
            n_ecw = int(1)
        n_cells = n_cyanos + n_ecw
        cyGroup = "group CYANO type 1"
        ecwGroup = "group ECW type 2"
        cyDiv = (
            f"fix d1 CYANO divide 100 v_EPSdens v_divDia1 {random.randint(1,1e6)}"
        )
        ecwDiv = (
            f"fix d2 ECW divide 100 v_EPSdens v_divDia2 {random.randint(1,1e6)}"
        )
        masses = "c_myMass[1]+c_myMass[2]"

        RUN_DIR = Path(f'../runs/Run_{n_cyanos}_{n_ecw}_{SucPct}_{args.reps}_{today}_{random.randint(1,1e6)}')
        if not os.path.isdir(RUN_DIR):
            os.mkdir(RUN_DIR)

        InitialConditions = {
            "cyano": {
                "StartingCells": n_cyanos,
                "GrowthRate": args.mu_cya,
                "min_size": 1.37e-6,
                "max_size": 1.94e-6,
                "Density": args.rho_cya,
                "K_s": {"sub": 3.5e-4, "o2": 2e-4, "suc": 1e-2, "co2": 1.38e-4},
                "GrowthParams": {"Yield": 0.55, "Maintenance": 0, "Decay": 0},
            },
            "ecw": {
                "StartingCells": n_ecw,
                "GrowthRate": args.mu_ecw,
                "min_size": 8.8e-7,
                "max_size": 1.39e-6,
                "Density": args.rho_ecw,
                "K_s": {"sub": 0, "o2": 1e-3, "suc": args.ksuc, "co2": 5e-2},
                "GrowthParams": {
                    "Yield": 0.43,
                    "Maintenance": args.maint_ecw,
                    "Decay": 0,
                },
            },
            "Nutrients": {
                "Concentration": {
                    "sub": 1e-1,
                    "o2": 9e-3,
                    "suc": float(args.sucrose) * SucMW * 1e-3,
                    "co2": float(args.co2) * CO2MW * 1e-3,
                },
                "State": {"sub": "g", "o2": "l", "suc": "l", "co2": "l"},
                "xbc": {"sub": "nn", "o2": "nn", "suc": "nn", "co2": "nn"},
                "ybc": {"sub": "nn", "o2": "nn", "suc": "nn", "co2": "nn"},
                "zbc": {"sub": "nn", "o2": "nd", "suc": "nn", "co2": "nd"},
            },
            "Diff_c": {"sub": 0, "o2": 2.30e-9, "suc": 5.2e-10, "co2": 1.9e-09},
            "Dimensions": [float(x) for x in args.dims.split(",")],
            "SucRatio": SucRatio,
            "Replicates": int(args.reps),
            'Spacing': spacing[n-1],
        }
        if args.closed == False:
            InitialConditions["Nutrients"]["xbc"]["suc"] = "dd"
            print('system is open')
        else:
            print(args.closed)
        NutesNum = len(InitialConditions["Nutrients"]["Concentration"])

        L = [
            " NUFEB Simulation\r\n\n",
            f"     {n_cells} atoms \n",
            f"     {len(cell_types)} atom types \n",
            f"     {NutesNum} nutrients \n\n",
            f'  0.0e-4   {InitialConditions["Dimensions"][0] :.2e}  xlo xhi \n',
            f'  0.0e-4   {InitialConditions["Dimensions"][1] :.2e}  ylo yhi \n',
            f'  0.0e-4   {InitialConditions["Dimensions"][2] :.2e}  zlo zhi \n\n',
            " Atoms \n\n",
        ]
        # seed cyanobacteria
        j=1
        for cell in range(n_cyanos):
            x = random.uniform(5e-5+1.39e-06,6e-5-1.39e-06)
            y = random.uniform(1.39e-06,InitialConditions["Dimensions"][1]-1.39e-6)
            z = random.uniform(1.39e-06,InitialConditions["Dimensions"][2]-1.39e-6)
            L.append(f'     {j} 1 1.39e-06  370 {x:.2e} {y:.2e} {z:.2e} 1.39e-06 \n')
            j += 1
        
        # seed e. coli
        L.append(f'     {j} 2 1.00e-06  230 {spacing[n-1]-1e-6:.2e} {(InitialConditions["Dimensions"][1]+1e-6)/2:.2e} {(InitialConditions["Dimensions"][2]+1e-6)/2:.2e} 1.00e-06 \n')
        L.append("\n")
        L.append(" Nutrients \n\n")
        for i, nute in enumerate(
            InitialConditions["Nutrients"]["Concentration"].keys()
        ):
            L.append(
                f'     %d {nute} {InitialConditions["Nutrients"]["State"][nute]} {InitialConditions["Nutrients"]["xbc"][nute]} {InitialConditions["Nutrients"]["ybc"][nute]} {InitialConditions["Nutrients"]["zbc"][nute]} {InitialConditions["Nutrients"]["Concentration"][nute] :.2e} {InitialConditions["Nutrients"]["Concentration"][nute] :.2e} \n'
                % (i + 1)
            )

        L.append("\n")
        L.append(" Type Name \n\n")
        for c, CellType in enumerate(cell_types, start=1):
            L.append(f"     {c} {CellType}  \n")
        L.append("\n")
        L.append(" Diffusion Coeffs \n\n")
        for key in InitialConditions["Diff_c"].keys():
            L.append(f'     {key} {InitialConditions["Diff_c"][key]} \n')
        L.append("\n")
        L.append(" Growth Rate \n\n")
        for CellType in cell_types:
            L.append(
                f'     {CellType} {InitialConditions[CellType]["GrowthRate"]} \n'
            )
        L.append("\n")
        L.append(" Ks \n\n")
        for CellType in cell_types:
            k = f"     {CellType}"
            for key in InitialConditions[CellType]["K_s"].keys():
                k = k + " " + str(InitialConditions[CellType]["K_s"][key])
            k = k + f" \n"
            L.append(k)
        L.append("\n")
        for key in InitialConditions["cyano"]["GrowthParams"].keys():
            L.append(" " + key + f" \n\n")
            for CellType in cell_types:
                L.append(
                    f'     {CellType} {InitialConditions[CellType]["GrowthParams"][key]} \n'
                )
            L.append("\n")

        L.append("\n\n")

        # write atom definition file
        f = open(
            RUN_DIR / f"atom.in", "w+"
        )
        f.writelines(L)

        # write initial conditions json file
        dumpfile = open(RUN_DIR / "metadata.json", "w")
        json.dump(InitialConditions, dumpfile, indent=6)
        dumpfile.close()
        # write Inputscript
        # open the file

        if args.lammps == True:
            lammps = "dump    id all custom 100 output.lammmps id type diameter x y z"
        else:
            lammps = ""
        if args.hdf5 == True:
            hdf5 = (
                "dump    traj all bio/hdf5 100 trajectory.h5 id type radius x y z con"
            )
        else:
            hdf5 = ""
        if args.vtk == True:
            vtk = "dump    du1 all vtk 100 atom_*.vtu id type diameter x y z"
            grid = "dump    du2 all grid 100 grid_%_*.vti con"
            vtk_tarball = "true"
        else:
            vtk = ""
            grid = ""
            vtk_tarball = "false"
        #filein = open(TEMPLATES_DIR / "inputscript.txt")
        filein = open( r'../templates/inputscript_cell_spacing.txt' )
        # read it
        src = Template(filein.read())
        # do the substitution
        result = src.safe_substitute(
            {
                "n": n,
                "SucRatio": SucRatio,
                "SucPct": SucPct,
                "n_cyanos": n_cyanos,
                "n_ecw": n_ecw,
                "Replicates": args.reps,
                "IPTG": f"{IPTG:.0e}",
                "Timesteps": args.timesteps,
                "date": today,
                "CYANOGroup": cyGroup,
                "ECWGroup": ecwGroup,
                "Zheight": InitialConditions["Dimensions"][2],
                "CYANODiv": cyDiv,
                "ECWDiv": ecwDiv,
                "GridMesh": f'{int(InitialConditions["Dimensions"][0]*1e6/int(args.grid))} {int(InitialConditions["Dimensions"][1]*1e6/int(args.grid))} {int(InitialConditions["Dimensions"][2]*1e6/int(args.grid))}',
                "lammps": lammps,
                "hdf5": hdf5,
                "vtk": vtk,
                "grid": grid,
                "masses": masses,
                "mass_max": f"{max_mass:.2e}",
            }
        )
        f = open(
            RUN_DIR / f"Inputscript_{n_cyanos}_{n_ecw}_{IPTG:.0e}_{today}.lammps", "w+"
        )
        f.writelines(result)

        _logger.info("Script ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":

    run()
