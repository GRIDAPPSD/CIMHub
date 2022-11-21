#  Copyright (c) 2022, Battelle Memorial Institute
import os
#import csv
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

plt.rcParams['savefig.directory'] = os.getcwd()

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

if __name__ == '__main__':
  d1 = np.loadtxt('ecp_duty_Mon_pv1_1.csv', skiprows=1, delimiter=',')
  d2 = np.loadtxt('ecp_duty_Mon_pv2_1.csv', skiprows=1, delimiter=',')
  d3 = np.loadtxt('ecp_duty_Mon_bess1_1.csv', skiprows=1, delimiter=',')
  d4 = np.loadtxt('ecp_duty_Mon_bess2_1.csv', skiprows=1, delimiter=',')
  pv1 = collect_columns (d1, cols=[2,4,6])
  pv2 = collect_columns (d2, cols=[2,4,6])
  bess1 = collect_columns (d3, cols=[2,4,6])
  bess2 = collect_columns (d4, cols=[2,4,6])
  t = make_timebase (d1, base=tbase)

  e1 = np.trapz (pv1, dx=tstep/tbase)
  e2 = np.trapz (pv2, dx=tstep/tbase)
  print ('Total Energy PV1={:.2f} PV2={:.2f} kwh'.format (e1, e2))
  b1 = np.trapz (bess1, dx=tstep/tbase)
  b2 = np.trapz (bess2, dx=tstep/tbase)
  print ('Total Energy BESS1={:.2f} BESS2={:.2f} kwh'.format (b1, b2))

  fig, ax = plt.subplots(1, 2, figsize=(10,6))
  ax[0].set_ylabel('Solar Power [kW]')
  ax[0].plot(t, pv1, color='red', label='PV 1 orig')
  ax[0].plot(t, pv2, color='blue', label='PV 2 orig')
  ax[0].set_xlabel('Time [hr]')
  ax[0].legend()
  ax[0].grid()

  ax[1].set_ylabel('Battery Power [kW]')
  ax[1].plot(t, bess1, color='red', label='BESS 1 orig')
  ax[1].plot(t, bess2, color='blue', label='BESS 2 orig')
  ax[1].set_xlabel('Time [hr]')
  ax[1].legend()
  ax[1].grid()

  plt.show()