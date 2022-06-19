import sys
import matplotlib.pyplot as plt
import numpy as np
import h5py
import pandas as pd

df = pd.read_csv ('summer.csv', skiprows=8, index_col=0, parse_dates=True)
print ('summer.csv\n', df)

df.plot(subplots=True)
plt.savefig('summer.png')
plt.show()

