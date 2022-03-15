import argparse
import sys
from pathlib import Path
import os
from string import Template
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
        "-f",
        dest="fitness",
        action="store",
        default=1,
        type=float,
    )
    parser.add_argument(
        "-s",
        dest="sucrose",
        action="store",
        default=4,
        type=float,
    )
    return parser.parse_args(args)
def main(args):
    """Wrapper function to generate new NUFEB simulation conditions

    Args:
      args (List[str]): command line parameters as list of strings

    """
    args = parse_args(args)
    filein = open( f'/mnt/home/sakkosjo/nufeb-cyano-e-coli/templates/fix_bio_kinetics_monod_fitness.txt' )
    src = Template( filein.read() )
    result = src.safe_substitute({'fitness' : args.fitness, 'biomass_flux' : args.sucrose})
    with open(f"/mnt/home/sakkosjo/fitness-cost/src/USER-NUFEB/fix_bio_kinetics_monod.cpp","w") as f:
        f.writelines(result)
def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":

    run()