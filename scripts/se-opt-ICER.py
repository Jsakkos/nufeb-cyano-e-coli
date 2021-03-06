import os
from random import uniform
import subprocess
from pathlib import Path
from nufeb_tools import utils,plot
import pandas as pd
from string import Template
import numpy as np
from functools import partial
import time
from skopt import gp_minimize, forest_minimize, dummy_minimize, gbrt_minimize
from skopt.plots import plot_convergence, plot_objective
import matplotlib.pyplot as plt
from scipy import interpolate
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error 
from skopt import dump, load
from skopt.callbacks import CheckpointSaver
import seaborn as sns
test_data = pd.read_excel('/mnt/home/sakkosjo/nufeb-cyano-e-coli/experimental-data/sucrose-OD-IPTG-sweep.xls',sheet_name='data')
from scipy.optimize import curve_fit

def od_func(x):
    """Exponential fit to IPTG vs OD750 experimental data

    Args:
        x (float): IPTG concentration (mM)

    Returns:
        float: Smoothed OD750
    """
    return 0.25482 * np.exp(-x/.06811) + 1.12893

# Smooth OD750 data for fitting
test_data.loc[:,'OD750'] = od_func(test_data.IPTG)

def recompile(alpha,tau,c,alpha2,tau2,c2):
    """Recompile NUFEB with new fitting parameters

    Args:
        alpha ([type]): [description]
        tau ([type]): [description]
        c ([type]): [description]
        alpha2 ([type]): [description]
        tau2 ([type]): [description]
        c2 ([type]): [description]
    """
    #
    filein = open( f'/mnt/home/sakkosjo/nufeb-cyano-e-coli/templates/fix_bio_kinetics_monod2.txt' )
    #read it
    src = Template( filein.read() )
    #do the substitution
    result = src.safe_substitute({'alpha' : alpha, 'tau' : tau, 'c' : c,'alpha2' : alpha2, 'tau2' : tau2, 'c2' : c2
                                        
                                        })
    with open("/mnt/home/sakkosjo/NUFEB/src/USER-NUFEB/fix_bio_kinetics_monod.cpp","w") as f:
       f.writelines(result)
    #Compile NUFEB
    os.chdir('/mnt/home/sakkosjo/NUFEB/')
    os.system('module load libpng; ./install.sh --enable-hdf5')

def func(x):
    """Optimization function

    Args:
        x ([type]): [description]

    Returns:
        [type]: RMSE
    """
    global Nfeval
    #OD750 fitting
    alpha = x[0]
    tau = x[1]
    c = x[2]
    #Sucrose fitting
    alpha2 = x[3]
    tau2 = x[4]
    c2 = x[5]
    #growth rate
  

    #Change input params
    
    recompile(alpha,tau,c,alpha2,tau2,c2)
    print(f'alpha: {alpha},tau: {tau},c: {c},alpha2: {alpha2},tau2: {tau2},c2: {c2}')

    #Clean old simulations
    os.chdir('/mnt/gs18/scratch/users/sakkosjo')
    os.system('nufeb-clean')
    #Seed new simulations
    for iptg in test_data.IPTG:
        text = f'nufeb-seed --n 5 --cells 10,0 --t 8700 --mucya 1.89e-5 --iptg {iptg}'
        os.system(text)
    #Run new simulations
    os.system('sbatch /mnt/home/sakkosjo/nufeb-cyano-e-coli/scripts/nufeb-parallel.sbatch')
    BASE_DIR = Path(f'runs/')
    folders = [path for path in BASE_DIR.iterdir() if path.is_dir()]

    #Extract output

    data = [utils.get_data(directory=str(x)) for x in folders]
    Volume = np.prod(data[0].metadata['Dimensions'])
    CellNum2OD = Volume*1e6/0.3e-8
    SucroseMW = 342.3
    dfs = []
    for x in data:
        temp = pd.concat([x.ntypes.cyano/CellNum2OD,x.ntypes.step/60/60*x.timestep,x.avg_con.Sucrose.reset_index(drop=True)],axis=1)
        temp.columns=['OD750','Hours','Sucrose']
        temp['IPTG'] = x.metadata['IPTG']
        dfs.append(temp)
    df = pd.concat(dfs,ignore_index=True)
    df = df.loc[(df.Hours > 23.8) & (df.Hours < 24)]
    df.sort_values(by='IPTG',inplace=True)
    df.reset_index(inplace=True)
    #save in progress plot
    f, ax = plt.subplots(ncols=2)
    ax[0].set_title('Sucrose')
    ax[0].plot(test_data.IPTG,test_data.Sucrose,marker='o')

    sns.lineplot(x='IPTG',y='Sucrose',ax=ax[0],data=df)
    ax[1].set_title('OD750')
    ax[1].plot(test_data.IPTG,test_data.OD750,marker='o')
    sns.lineplot(x='IPTG',y='OD750',ax=ax[1],data=df)
    f.tight_layout()
    f.savefig(f'/mnt/home/sakkosjo/nufeb-cyano-e-coli/simulation-data/se-opt-{Nfeval}.png')
    plt.close()
    #Compare output with experimental data via RMSE

    Nfeval += 1
    ODerr=0
    SUCerr=0
    temp = df.groupby('IPTG').mean().reset_index()
    if len(temp.OD750)==len(test_data.OD750):
        ODerr = np.average((test_data.OD750 - temp.OD750) ** 2, axis=0, weights=test_data.OD750)+ODerr
    else:
        ODerr = (((temp.OD750-test_data.OD750)/test_data.OD750)**2).mean()+ODerr

    if len(temp.Sucrose)==len(test_data.Sucrose):
        SUCerr = np.average((test_data.Sucrose - temp.Sucrose) ** 2, axis=0, weights=test_data.Sucrose)+SUCerr
    else:
        SUCerr = (((temp.Sucrose-test_data.Sucrose)/test_data.Sucrose)**2).mean()+SUCerr
    return ODerr + SUCerr
#return  + (((df.Sucrose-test_data.Sucrose)/(test_data.Sucrose))**2).mean()
#return mean_squared_error(df.OD750,test_data.OD750,sample_weight=test_data.OD750) + mean_squared_error(df.Sucrose,test_data.Sucrose, sample_weight=test_data.Sucrose)


alpha_min = float('-5e-1')
alpha_max = float('-1e-2')
tau_min = float('1e-3')
tau_max = float('1e-1')
c_min = float('1e-3')
c_max = float('5e-1')

alpha2_min = float('-1e1')
alpha2_max = float('-1e-3')
tau2_min = float('1e-3')
tau2_max = float('1e-1')
c2_min = float('1e-3')
c2_max = float('1e1')


bounds = [(alpha_min,alpha_max),(tau_min,tau_max),(c_min,c_max),(alpha2_min,alpha2_max),(tau2_min,tau2_max),(c2_min,c2_max)]#,


if Path('/mnt/home/sakkosjo/nufeb-cyano-e-coli/checkpoints/checkpoint-se-icer.pkl').exists():
    res = load('/mnt/home/sakkosjo/nufeb-cyano-e-coli/checkpoints/checkpoint-se-icer.pkl')
    checkpoint_saver = CheckpointSaver('/mnt/home/sakkosjo/nufeb-cyano-e-coli/checkpoints/checkpoint-se-icer.pkl', compress=9)
    n_calls = 500

    Nfeval = len(res.x_iters)+1
    x0 = res.x_iters
    y0 = res.func_vals
    #base_estimator = res.specs['args']['base_estimator']
    random_state = res.random_state
    res = gp_minimize(func, bounds, x0=x0,y0=y0,
            n_calls=n_calls,n_initial_points=20,
            verbose=True,random_state=random_state,
                    callback=[checkpoint_saver])
else:
    checkpoint_saver = CheckpointSaver('/mnt/home/sakkosjo/nufeb-cyano-e-coli/checkpoints/checkpoint-se-icer.pkl', compress=9)
    n_calls = 500

    Nfeval = 1

    res = gp_minimize(func, bounds,
            n_calls=n_calls,n_initial_points=20,
            verbose=True, callback=[checkpoint_saver])


