import sys
import matplotlib.pyplot as plt
import numpy as np
import h5py
import pandas as pd
import os

df = pd.read_csv ('summer.csv', skiprows=8, index_col=0, parse_dates=True)
print ('summer.csv\n', df)

df.plot(subplots=True)
plt.rcParams['savefig.directory'] = os.getcwd()
plt.savefig('summer.png')
plt.show()

