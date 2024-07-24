import sys
import numpy as np
import h5py
import pandas as pd

timezones = {
  "EST": "EST5EDT",
  "EDT": "EST5EDT",
  "CST": "CST6CDT",
  "CDT": "CST6CDT",
  "MST": "MST7MDT",
  "MDT": "MST7MDT",
  "PST": "PST8PDT",
  "PDT": "PST8PDT",
}

fdr_csv = 'feeder_head.csv'
prim_csv = 'prim_loads.csv'
pv_csv = 'pv_meters.csv'
sub_csv = 'substation.csv'
weather_csv = 'weather.csv'

# CSV files from recorders have 9 comment lines
# CSV files from multirecorders have 8 comment lines; they have no single target
# the last of the comment lines is the column header
def read_csv_df(fname, complex_column_names=None):
  df = pd.read_csv (fname, skiprows=8, index_col=0, parse_dates=True)
  if complex_column_names is not None:
    for col in complex_column_names:
      df[col] = df[col].astype(complex)
  print ('\n\n=== Read and converted', fname)
#  df.info()
  return df

def read_multicsv_df(fname, complex_property_name=None):
  df = pd.read_csv (fname, skiprows=7, index_col=0, parse_dates=True)
  if complex_property_name is not None:
    for col in df.columns.values.tolist():
      if col.endswith(complex_property_name):
        df[col] = df[col].astype(complex)
  print ('\n\n=== Read and converted', fname)
#  df.info()
  return df

df_sub = read_csv_df(sub_csv, complex_column_names=['distribution_load', 'positive_sequence_voltage'])
df_fdr = read_csv_df(fdr_csv, complex_column_names=['power_in', 
                                                    'current_in_A',
                                                    'current_in_B',
                                                    'current_in_C'])
df_prim = read_multicsv_df (prim_csv, complex_property_name='measured_power')
df_pv = read_multicsv_df (pv_csv, complex_property_name='measured_power')
df_met = read_csv_df (weather_csv)
df = pd.concat([df_sub, df_fdr, df_prim, df_pv, df_met], axis=1)
print('\n\n=================')
print('before adding transformers')
df.info()

xfmrs = []
for ln in open ('load_xfmrs.dat', mode='r').readlines():
  xfmr = ln.strip()
  xfmrs.append (xfmr)

print ('Concatenating {:d} transformers'.format(len(xfmrs)))
for xf in xfmrs:
  xf_csv = xf + '.csv'
  df_xf = read_csv_df (xf_csv, complex_column_names=['power_in'])
  df_xf = df_xf.rename(columns={'power_in': xf+':power_in'})
  df = pd.concat([df, df_xf], axis=1)

print('\n\n=================')
print('processed for hdf5')
df.info()
df.to_hdf('aug11.hdf5', key='Aug11', mode='w')

