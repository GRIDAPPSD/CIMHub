#  Copyright (c) 2022, Battelle Memorial Institute
import os
#import csv
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

plt.rcParams['savefig.directory'] = os.getcwd()

vbase = 7621.0
tstep = 3600.0
tbase = 3600.0

def collect_columns (d, cols, base=None):
  v = np.zeros(d.shape[0])
  for i in cols:
    v += d[:,i]
  if base is not None:
    v /= base
  return v

def make_timebase (d, base=1.0):
  n = d.shape[0]
  return np.linspace (0.0, tstep * float(n - 1) / base, n)

if __name__ == '__main__':
  fig, ax = plt.subplots(1, 1, figsize=(8,6))
  ax.set_ylabel('Load Power [kW]')
  t = None
  for idx in range(5):
    key = 'load{:d}'.format(idx+1)
    d = np.loadtxt('ecp_growthcvr_Mon_{:s}_1.csv'.format(key), skiprows=1, delimiter=',')
    if t is None:
      t = make_timebase (d, base=tbase)
    p = collect_columns (d, cols=[2,4,6])
    e = np.trapz (p, dx=tstep/tbase)
    print ('Total Energy {:s} = {:.2f} kwh'.format (key.upper(), e))
    ax.plot(t, p, label=key.upper())

  ax.set_xlabel('Time [hr]')
  ax.legend()
  ax.grid()

  plt.show()
