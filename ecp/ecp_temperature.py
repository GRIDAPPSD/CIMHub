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
tstep = 60.0
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
  d1 = np.loadtxt('./{:s}/ecp_temperature_Mon_pv1_pq_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  d2 = np.loadtxt('./{:s}/ecp_temperature_Mon_pv1_vi_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  d3 = np.loadtxt('./{:s}/ecp_temperature_Mon_pv2_pq_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  d4 = np.loadtxt('./{:s}/ecp_temperature_Mon_pv2_vi_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  p1 = collect_columns (d1, cols=[2,4,6])
  v1 = collect_columns (d2, cols=[2,4,6], base=3.0*vbase)
  p2 = collect_columns (d3, cols=[2,4,6])
  v2 = collect_columns (d4, cols=[2,4,6], base=3.0*vbase)
  t = make_timebase (d1, base=tbase)

  e1 = np.trapz (p1, dx=tstep/tbase)
  e2 = np.trapz (p2, dx=tstep/tbase)
  print ('Total Energy PV1={:.2f} PV2={:.2f} kWh'.format (e1, e2))

  if ax is not None:
    ax[0].plot(t, p1, label='PV1 {:s}'.format(dsspath))
    ax[0].plot(t, p2, label='PV2 {:s}'.format(dsspath))
    ax[1].plot(t, v1, label='PV1 {:s}'.format(dsspath))
    ax[1].plot(t, v2, label='PV2 {:s}'.format(dsspath))

if __name__ == '__main__':
  if len(sys.argv) > 1:
    if sys.argv[1] == 'noplot':
      bShowPlot = False

  if bShowPlot:
    fig, ax = plt.subplots(1, 2, figsize=(10,6))
    plt.suptitle ('Case ecp_temperature')
  else:
    ax = None

  for dsspath in ['base', 'dssa']:
    add_case (ax, dsspath)

  if bShowPlot:
    ax[0].set_ylabel('Power [kW]')
    ax[0].set_xlabel('Time [hr]')
    ax[0].legend()
    ax[0].grid()
    ax[1].set_ylabel('Voltage [pu]')
    ax[1].set_xlabel('Time [hr]')
    ax[1].legend()
    ax[1].grid()
    plt.show()
