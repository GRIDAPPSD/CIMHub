#  Copyright (c) 2022, Battelle Memorial Institute
import os
import sys
import numpy as np
from numpy import trapz
import pandas as pd

if not sys.warnoptions:
  import warnings
  warnings.simplefilter("ignore") # for the UnknownTimezoneWarning, to be fixed in GridLAB-D

try:
  import matplotlib.pyplot as plt
  plt.rcParams['savefig.directory'] = os.path.abspath ('..\docs\media') # os.getcwd()
  bShowPlot = True
except:
  bShowPlot = False

tstep_dss = 1.0
tbase = 3600.0
vbase = 7621.0
tticks = [0,4,8,12,16,20,24]

# CSV files from recorders have 9 comment lines
# CSV files from multirecorders have 8 comment lines; they have no single target
# the last of the comment lines is the column header
def read_csv_df(fname, complex_column_names=None):
  df = pd.read_csv (fname, skiprows=8, index_col=0, parse_dates=True)
  if complex_column_names is not None:
    for col in complex_column_names:
      df[col] = df[col].astype(complex)
#  print ('\n\n=== Read and converted', fname)
  return df

def read_multicsv_df(fname, complex_property_name=None):
  df = pd.read_csv (fname, skiprows=7, index_col=0, parse_dates=True)
  if complex_property_name is not None:
    for col in df.columns.values.tolist():
      if col.endswith(complex_property_name):
        df[col] = df[col].astype(complex)
#  print ('\n\n=== Read and converted', fname)
  return df

def collect_columns (d, cols, base=None):
  v = np.zeros(d.shape[0])
  for i in cols:
    v += d[:,i]
  if base is not None:
    v /= base
  return v

def make_timebase (d, base=1.0):
  n = d.shape[0]
  return np.linspace (0.0, tstep_dss * float(n - 1) / base, n)

def add_case (ax, dsspath):
  print ('Results from', dsspath)

  d = np.loadtxt('./{:s}/gld_daily_Mon_pv1_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  t = make_timebase (d, base=tbase)
  pv1 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/gld_daily_Mon_pv2_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  pv2 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/gld_daily_Mon_gen1_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  gen1 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/gld_daily_Mon_gen2_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  gen2 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/gld_daily_Mon_load1_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  load1 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/gld_daily_Mon_load2_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  load2 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/gld_daily_Mon_bess1_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  bess1 = collect_columns (d, cols=[2,4,6])
  d = np.loadtxt('./{:s}/gld_daily_Mon_bess2_1.csv'.format(dsspath), skiprows=1, delimiter=',')
  bess2 = collect_columns (d, cols=[2,4,6])

  e1 = np.trapz (pv1, dx=tstep_dss/tbase)
  e2 = np.trapz (pv2, dx=tstep_dss/tbase)
  print ('Total Energy PV1={:.2f} PV2={:.2f} kwh'.format (e1, e2))
  e1 = np.trapz (gen1, dx=tstep_dss/tbase)
  e2 = np.trapz (gen2, dx=tstep_dss/tbase)
  print ('Total Energy Gen1={:.2f} Gen2={:.2f} kwh'.format (e1, e2))
  e1 = np.trapz (load1, dx=tstep_dss/tbase)
  e2 = np.trapz (load2, dx=tstep/tbase)
  print ('Total Energy Load1={:.2f} Load2={:.2f} kwh'.format (e1, e2))
  e1 = np.trapz (bess1, dx=tstep_dss/tbase)
  e2 = np.trapz (bess2, dx=tstep_dss/tbase)
  print ('Total Energy BESS1={:.2f} BESS2={:.2f} kwh'.format (e1, e2))

  if ax is not None:
    ax[0,0].plot(t, pv1, label='PV 1 {:s}'.format(dsspath))
    ax[0,0].plot(t, pv2, label='PV 2 {:s}'.format(dsspath))
    ax[0,1].plot(t, gen1, label='Gen 1 {:s}'.format(dsspath))
    ax[0,1].plot(t, gen2, label='Gen 2 {:s}'.format(dsspath))
    ax[1,0].plot(t, load1, label='Load 1 {:s}'.format(dsspath))
    ax[1,0].plot(t, load2, label='Load 2 {:s}'.format(dsspath))
    ax[1,1].plot(t, bess1, label='BESS 1 {:s}'.format(dsspath))
    ax[1,1].plot(t, bess2, label='BESS 2 {:s}'.format(dsspath))

def plot_dss_case():

  fig, ax = plt.subplots(2, 2, figsize=(10,6))
  plt.suptitle ('Case gld_daily: OpenDSS Results')

  for dsspath in ['base', 'dssa']:
    add_case (ax, dsspath)

  if ax is None:
    return

  ax[0,0].set_ylabel('Solar Power [kW]')
  ax[0,1].set_ylabel('Generator Power [kW]')
  ax[1,0].set_ylabel('Load Power [kW]')
  ax[1,1].set_ylabel('BESS Power [kW]')

  for j in range(2):
    ax[1,j].set_xlabel('Time [hr]')
    for i in range(2):
      ax[i,j].legend()
      ax[i,j].grid()
      ax[i,j].set_xlim(tticks[0], tticks[-1])
      ax[i,j].set_xticks(tticks)
  plt.show()

def plot_gld_case(df, tstep, npts):

  fig, ax = plt.subplots(2, 2, figsize=(10,6))
  plt.suptitle ('Case gld_daily: GridLAB-D Results')

  t = np.linspace (0.0, tstep * float(npts - 1) / tbase, npts)

  ax[0,0].plot(t, df['pv1_pvmtr'].apply(lambda r: r.real), label='PV 1')
  ax[0,0].plot(t, df['pv2_pvmtr'].apply(lambda r: r.real), label='PV 2')
  ax[0,1].plot(t, df['gen1_dgmtr'].apply(lambda r: r.real), label='Gen 1')
  ax[0,1].plot(t, df['gen2_dgmtr'].apply(lambda r: r.real), label='Gen 2')
  ax[1,0].plot(t, df['ld_load1'].apply(lambda r: r.real), label='Load 1')
  ax[1,0].plot(t, df['ld_load2'].apply(lambda r: r.real), label='Load 2')
  ax[1,1].plot(t, df['bess1_stmtr'].apply(lambda r: r.real), label='BESS 1')
  ax[1,1].plot(t, df['bess2_stmtr'].apply(lambda r: r.real), label='BESS 2')

  ax[0,0].set_ylabel('Solar Power [kW]')
  ax[0,1].set_ylabel('Generator Power [kW]')
  ax[1,0].set_ylabel('Load Power [kW]')
  ax[1,1].set_ylabel('BESS Power [kW]')

  for j in range(2):
    ax[1,j].set_xlabel('Time [hr]')
    for i in range(2):
      ax[i,j].legend()
      ax[i,j].grid()
      ax[i,j].set_xlim(tticks[0], tticks[-1])
      ax[i,j].set_xticks(tticks)
  plt.show()

def plot_overlay(df, tstep, npts, bPlot=True):

  if bPlot:
    fig, ax = plt.subplots(2, 2, figsize=(10,6))
    plt.suptitle ('Case gld_daily: Overlaid Results')
  else:
    ax = None

  for dsspath in ['base', 'dssa']:
    add_case (ax, dsspath)

  if ax is None:
    return

  t = np.linspace (0.0, tstep * float(npts - 1) / tbase, npts)

  ax[0,0].plot(t, 0.001 * df['pv1_pvmtr'].apply(lambda r: r.real), label='PV 1 glma')
  ax[0,0].plot(t, 0.001 * df['pv2_pvmtr'].apply(lambda r: r.real), label='PV 2 glma')
  ax[0,1].plot(t, 0.001 * df['gen1_dgmtr'].apply(lambda r: r.real), label='Gen 1 glma')
  ax[0,1].plot(t, 0.001 * df['gen2_dgmtr'].apply(lambda r: r.real), label='Gen 2 glma')
  ax[1,0].plot(t, 0.001 * df['ld_load1'].apply(lambda r: r.real), label='Load 1 glma')
  ax[1,0].plot(t, 0.001 * df['ld_load2'].apply(lambda r: r.real), label='Load 2 glma')
  ax[1,1].plot(t, 0.001 * df['bess1_stmtr'].apply(lambda r: r.real), label='BESS 1 glma')
  ax[1,1].plot(t, 0.001 * df['bess2_stmtr'].apply(lambda r: r.real), label='BESS 2 glma')

  ax[0,0].set_ylabel('Solar Power [kW]')
  ax[0,1].set_ylabel('Generator Power [kW]')
  ax[1,0].set_ylabel('Load Power [kW]')
  ax[1,1].set_ylabel('BESS Power [kW]')

  for j in range(2):
    ax[1,j].set_xlabel('Time [hr]')
    for i in range(2):
      ax[i,j].legend()
      ax[i,j].grid()
      ax[i,j].set_xlim(tticks[0], tticks[-1])
      ax[i,j].set_xticks(tticks)
  plt.show()


if __name__ == '__main__':
  if len(sys.argv) > 1:
    if sys.argv[1] == 'noplot':
      bShowPlot = False

  df = read_multicsv_df ('glma/meters.csv', 'measured_power')
  column_map = {}
  ilen = len(':measured_power')
  for key in df.columns:
    column_map[key] = key[:-ilen]
  df.rename(columns=column_map, inplace=True)
  npts = len(df.index)
  dt = df.index[-1] - df.index[0]
  trange = 86400.0 * dt.days + dt.seconds
  tstep = trange / npts

  for key, data in df.iteritems():
    energy = np.trapz(data.apply(lambda r: r.real), dx=tstep/tbase) * 0.001
    print ('{:12s} {:10.3f} kwh'.format (key, energy))

  plot_overlay (df, tstep, npts, bShowPlot)
