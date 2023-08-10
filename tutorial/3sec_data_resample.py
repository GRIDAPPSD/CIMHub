""" CIMHub - Tutorial: Impute Data with Houses and DER
This script invokes ../tutorial/'plot_hdf5.py' and returns the pandas DF containing 3-sec Data for two days.
DF may be resampled at ANY desired time step in minutes for averaging all column data over a given interval.
dfShift modifies DF to include first measurement at time=0secs from 3 sec data """

import matplotlib.pyplot as plt
import pandas as pd
import scipy.constants
import os

#from tutorial.plot_hdf5 import df
df = pd.read_hdf('./aug11.hdf5')
pv_cols = []
xf_cols = []
ld_cols = []
for col in df.columns.values.tolist():
  if col.startswith('xf_xfs') and 'power_in' in col:
    xf_cols.append(col)
  elif col.startswith('ld_s') and 'measured_power' in col:
    ld_cols.append(col)
  elif '_pvmtr:measured_power' in col:
    pv_cols.append(col)

print ('{:d} PV columns, {:d} primary load columns, {:d} transformer columns'.format(len(pv_cols),
                                           len(ld_cols),
                                           len(xf_cols)))

# make some convenience quantities and unit conversions
df['sub_p'] = df['distribution_load'].apply(lambda number: number.real)
df['sub_q'] = df['distribution_load'].apply(lambda number: number.imag)
SOLAR_FLUX_SCALE = 1.0 / scipy.constants.foot / scipy.constants.foot
df['solar_flux'] = df['solar_flux'] * SOLAR_FLUX_SCALE
df['fdrIa'] = df['current_in_A'].abs()
df['fdrIb'] = df['current_in_B'].abs()
df['fdrIc'] = df['current_in_C'].abs()
df['pvS'] = df[pv_cols].sum(axis=1)
df['primaryS'] = df[ld_cols].sum(axis=1)
df['secondaryS'] = df[xf_cols].sum(axis=1)
df['pvP'] = df['pvS'].apply(lambda number: number.real)
df['primaryP'] = df['primaryS'].apply(lambda number: number.real)
df['secondaryP'] = df['secondaryS'].apply(lambda number: number.real)
df.info()

# take measurement avgs from 3sec df data in minutes
def dfResampleMinsAvg(df, num_mins):
  number_mins = str(num_mins)
  df_resample = df.resample(number_mins + 'T').mean()
  return df_resample


# take measurement avgs from 3sec df data every 30 secs
def dfResample30secsAvg(df):
  df_resample = df.resample('30S').mean()
  return df_resample

# set averages at end of timestamp range each step
def dfShift(df, df_first_row):
  df_shift = df.shift(1)
  df_shifted = pd.concat([df_first_row, df_shift]) # add inst measurement for initial 0th timestamp
  df_shifted.drop_duplicates(keep='first')
  df_new = df_shifted.dropna()
  return df_new

# plot any given df quantities
def plotChannels(df, y, title, fname=None):
  df.plot(y=y, title=title)
  plt.legend(loc='best')
  plt.grid()
  if fname is not None:
    plt.savefig(fname)
  plt.show()

def dfToCSV(df, filename):
  df.to_csv(filename + '.csv')

def dfToHDF(df, key, filename):
  df.to_hdf(filename + '.hdf5', key=key, mode='w')

if __name__ == '__main__':
  outpath = './15min/'
  if not os.path.exists(outpath):
    os.makedirs(outpath)

  df_row1 = pd.DataFrame(df.iloc[[0]])  # get 0th measurement
  df15 = dfResampleMinsAvg(df, 15) # 15mins avgs, **change int for min selection**
  df30secs= dfResample30secsAvg(df) # resample at 30sec avgs
  df15shifted = dfShift(df15, df_row1) # avg at end of each timestamp

  dfout = df15shifted # select one for plotting and saving

  plotChannels(dfout, ['sub_p', 'sub_q'], 
         'Averaged Substation Real and Reactive Power', '{:s}substation.png'.format(outpath))
  plotChannels(dfout, ['fdrIa', 'fdrIb', 'fdrIc'], 
         'Averaged Feeder Current Magnitudes', '{:s}feeder.png'.format(outpath))
  plotChannels(dfout, ['pvP', 'primaryP', 'secondaryP'], 
         'Averaged Load and PV Total Real Power', '{:s}components.png'.format(outpath))
  plotChannels(dfout, ['xf_xfs49a:power_in', 'xf_xfs17c:power_in', 'xf_xfs1a:power_in'], 
         'Averaged Sample Transformer P', '{:s}transformers.png'.format(outpath))

  # write new df to csv or hdf5
  dfToCSV(dfout, '{:s}aug11avg'.format(outpath))
  dfToHDF(dfout, key='Aug11avg', filename='{:s}aug11avg'.format(outpath))

  print('data resample complete')
