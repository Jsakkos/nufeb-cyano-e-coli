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

test_data = pd.read_excel('/home/12x/nufeb-cyano-e-coli/experimental-data/sucrose-OD-IPTG-sweep.xls',sheet_name='data')
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
    os.chdir('/lustre/or-scratch/cades-cnms/12x/nufeb-test')
    filein = open( f'/home/12x/nufeb-cyano-e-coli/templates/fix_bio_kinetics_monod2.txt' )
    #read it
    src = Template( filein.read() )
    #do the substitution
    result = src.safe_substitute({'alpha' : alpha, 'tau' : tau, 'c' : c,'alpha2' : alpha2, 'tau2' : tau2, 'c2' : c2
                                        
                                        })
    with open("/lustre/or-scratch/cades-cnms/12x/nufeb-test/src/USER-NUFEB/fix_bio_kinetics_monod.cpp","w") as f:
       f.writelines(result)
    #Compile NUFEB
    nufeb_compile = subprocess.run('/home/12x/rapid-compile2.sh')

def func(x):
    #OD750 fitting
    alpha = x[0]
    tau = x[1]
    c = x[2]
    #Sucrose fitting
    alpha2 = x[3]
    tau2 = x[4]
    c2 = x[5]
    #growth rate
    mu = x[6]





    #Change input params
    
    os.chdir('/lustre/or-scratch/cades-cnms/12x/nufeb-test')
    recompile(alpha,tau,c,alpha2,tau2,c2)
    print(f'alpha: {alpha},tau: {tau},c: {c},alpha2: {alpha2},tau2: {tau2},c2: {c2}, mu: {mu}')

    #Clean old simulations
    os.system('nufeb-clean')
    #Run simulation
    for iptg in test_data.IPTG:
        text = f'nufeb-seed --cells 10,0 --d 1e-4,1e-4,1e-5 --t 8700 --mucya {mu} --sucR {iptg}'
        os.system(text)

    run_nufeb = subprocess.run('/home/12x/optim3.sh', stdout=subprocess.DEVNULL)
    BASE_DIR = Path(f'runs/')
    folders = [path for path in BASE_DIR.iterdir() if path.is_dir()]

    #Extract output

    data = [utils.get_data(directory=str(x)) for x in folders]
    Volume = 1e-4*1e-4*1e-4 #m^3
    CellNum2OD = Volume*1e6/0.3e-8
    SucroseMW = 342.3
    dfs = []
    for x in data:
        temp = pd.concat([x.ntypes.cyano/CellNum2OD,x.ntypes.step/60/60*x.timestep,x.avg_con.Sucrose.reset_index(drop=True)],axis=1)
        temp.columns=['OD750','Hours','Sucrose']
        temp['IPTG'] = x.metadata['SucRatio']
        dfs.append(temp)
    df = pd.concat(dfs,ignore_index=True)
    df = df.loc[(df.Hours > 23.8) & (df.Hours < 24)]
    df.sort_values(by='IPTG',inplace=True)
    df.reset_index(inplace=True)
    
    #Compare output with experimental data via RMSE
    
    return mean_squared_error(df.OD750,test_data.OD750, squared = False) + mean_squared_error(df.Sucrose,test_data.Sucrose, squared = False)

alpha_min = float('-2e-1')
alpha_max = float('0')
tau_min = float('1e-2')
tau_max = float('1e-1')
c_min = float('0')
c_max = float('5e-1')
alpha2_min = float('-1e1')
alpha2_max = float('0')
tau2_min = float('1e-2')
tau2_max = float('1e-1')
c2_min = float('0')
c2_max = float('1e1')

mu_min = float('1e-6')
mu_max = float('5e-5')

bounds = [(alpha_min,alpha_max),(tau_min,tau_max),(c_min,c_max),(alpha2_min,alpha2_max),(tau2_min,tau2_max),(c2_min,c2_max),(mu_min,mu_max)]#,



checkpoint_saver = CheckpointSaver('/home/12x/nufeb-cyano-e-coli/checkpoints/checkpoint-se2.pkl', compress=9)
n_calls = 15

res = gp_minimize(func, bounds, n_calls=n_calls,verbose=True,
                  callback=[checkpoint_saver])

# plot

alpha = res[0]
tau = res[1]
c = res[2]
#Sucrose fitting
alpha2 = res[3]
tau2 = res[4]
c2 = res[5]
#growth rate
mu = res[6]
os.chdir('/lustre/or-scratch/cades-cnms/12x/nufeb-test')
recompile(alpha,tau,c,alpha2,tau2,c2)
print(f'alpha: {alpha},tau: {tau},c: {c},alpha2: {alpha2},tau2: {tau2},c2: {c2}, mu: {mu}')

#Clean old simulations
os.system('nufeb-clean')
#Run simulation
for iptg in test_data.IPTG:
    text = f'nufeb-seed --cells 10,0 --d 1e-4,1e-4,1e-5 --t 8700 --mucya {mu} --sucR {iptg}'
    os.system(text)

run_nufeb = subprocess.run('/home/12x/optim3.sh', stdout=subprocess.DEVNULL)
BASE_DIR = Path(f'runs/')
folders = [path for path in BASE_DIR.iterdir() if path.is_dir()]

#Extract output

data = [utils.get_data(directory=str(x)) for x in folders]
Volume = 1e-4*1e-4*1e-4 #m^3
CellNum2OD = Volume*1e6/0.3e-8
SucroseMW = 342.3
dfs = []
for x in data:
    temp = pd.concat([x.ntypes.cyano/CellNum2OD,x.ntypes.step/60/60*x.timestep,x.avg_con.Sucrose.reset_index(drop=True)],axis=1)
    temp.columns=['OD750','Hours','Sucrose']
    temp['IPTG'] = x.metadata['SucRatio']
    dfs.append(temp)
df = pd.concat(dfs,ignore_index=True)
df = df.loc[(df.Hours > 23.8) & (df.Hours < 24)]
df.sort_values(by='IPTG',inplace=True)
df.reset_index(inplace=True)

f, ax = plt.subplots(ncols=2)
ax[0].set_title('Sucrose')
ax[0].plot(test_data.IPTG,test_data.Sucrose,marker='o')
ax[0].plot(df.IPTG,df.Sucrose)
ax[1].set_title('OD750')
ax[1].plot(test_data.IPTG,test_data.OD750,marker='o')
ax[1].plot(df.IPTG,df.OD750)
f.savefig(r'../figures/se-opt.png')


