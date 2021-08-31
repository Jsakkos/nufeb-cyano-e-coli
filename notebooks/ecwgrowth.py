import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression

def func(x,K,r,N0):
    return K/(1  + ((K-N0)/N0)*np.exp(-r*x))

df = pd.read_excel('ecw growth.xlsx')

popt, pcov = curve_fit(func,df.Time,df.OD)
sns.lineplot(x='Time',y='OD',data=df)
plt.plot(df.Time,func(df.Time,*popt))
