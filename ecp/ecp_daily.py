#  Copyright (c) 2022, Battelle Memorial Institute
import os
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

plt.rcParams['savefig.directory'] = os.path.abspath ('..\docs\media') # os.getcwd()

vbase = 7621.0
tstep = 1.0
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

  d = np.loadtxt('./{:s}/ecp_daily_Mon_pv1_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  t = make_timebase (d, base=tbase)
  pv1 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/ecp_daily_Mon_pv2_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  pv2 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/ecp_daily_Mon_gen1_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  gen1 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/ecp_daily_Mon_gen2_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  gen2 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/ecp_daily_Mon_load1_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  load1 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/ecp_daily_Mon_load2_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  load2 = collect_columns (d, cols=[2,4,6])

  e1 = np.trapz (pv1, dx=tstep/tbase)
  e2 = np.trapz (pv2, dx=tstep/tbase)
  print ('Total Energy PV1={:.2f} PV2={:.2f} kwh'.format (e1, e2))
  e1 = np.trapz (gen1, dx=tstep/tbase)
  e2 = np.trapz (gen2, dx=tstep/tbase)
  print ('Total Energy Gen1={:.2f} Gen2={:.2f} kwh'.format (e1, e2))
  e1 = np.trapz (load1, dx=tstep/tbase)
  e2 = np.trapz (load2, dx=tstep/tbase)
  print ('Total Energy Load1={:.2f} Load2={:.2f} kwh'.format (e1, e2))

  ax[0].plot(t, pv1, label='PV 1 {:s}'.format(dsspath))
  ax[0].plot(t, pv2, label='PV 2 {:s}'.format(dsspath))
  ax[1].plot(t, gen1, label='Gen 1 {:s}'.format(dsspath))
  ax[1].plot(t, gen2, label='Gen 2 {:s}'.format(dsspath))
  ax[2].plot(t, load1, label='Load 1 {:s}'.format(dsspath))
  ax[2].plot(t, load2, label='Load 2 {:s}'.format(dsspath))

if __name__ == '__main__':

  fig, ax = plt.subplots(1, 3, figsize=(10,6))
  plt.suptitle ('Case ecp_daily')

  for dsspath in ['base', 'dssa']:
    add_case (ax, dsspath)

  ax[0].set_ylabel('Solar Power [kW]')
  ax[1].set_ylabel('Generator Power [kW]')
  ax[2].set_ylabel('Load Power [kW]')

  for i in range(3):
    ax[i].set_xlabel('Time [hr]')
    ax[i].legend()
    ax[i].grid()

  plt.show()
