#  Copyright (c) 2022, Battelle Memorial Institute
import os
import sys
import numpy as np
from numpy import trapz

try:
  import matplotlib.pyplot as plt
  plt.rcParams['savefig.directory'] = os.path.abspath ('..\docs\media') # os.getcwd()
  bShowPlot = True
except:
  bShowPlot = False

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

def add_case (ax, dsspath):
  print ('Results from', dsspath)
  t = None
  for idx in range(5):
    key = 'load{:d}'.format(idx+1)
    d = np.loadtxt('./{:s}/ecp_growthcvr_Mon_{:s}_1.csv'.format(dsspath, key), skiprows=1, delimiter=',')
    if t is None:
      t = make_timebase (d, base=tbase)
    p = collect_columns (d, cols=[2,4,6])
    e = np.trapz (p, dx=tstep/tbase)
    print ('Total Energy {:s} = {:.2f} kwh'.format (key.upper(), e))
    if ax is not None:
      ax.plot(t, p, label='{:s} {:s}'.format(key.upper(), dsspath))

if __name__ == '__main__':
  if len(sys.argv) > 1:
    if sys.argv[1] == 'noplot':
      bShowPlot = False

  if bShowPlot:
    fig, ax = plt.subplots(1, 1, figsize=(8,6))
    plt.suptitle ('Case ecp_growthcvr')
  else:
    ax = None

  for dsspath in ['base', 'dssa']:
    add_case (ax, dsspath)

  if bShowPlot:
    ax.set_ylabel('Load Power [kW]')
    ax.set_xlabel('Time [hr]')
    ax.legend()
    ax.grid()
    plt.show()
