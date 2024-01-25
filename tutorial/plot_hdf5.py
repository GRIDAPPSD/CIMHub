import sys
import matplotlib.pyplot as plt
import pandas as pd
import scipy.constants
import os

df = pd.read_hdf('./aug11.hdf5')
df.info()
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

# plot some of the 3-second data
plt.rcParams['savefig.directory'] = os.getcwd()
ax = df.plot (y=['pvP', 'primaryP', 'secondaryP'], title='Load and PV Total Real Power')
plt.savefig('components.png')
plt.show()

ax = df.plot (y=[xf_cols[0], xf_cols[10], xf_cols[20]], title='Sample Transformer Real Powers')
plt.savefig('transformers.png')
plt.show()

ax = df.plot (y=['fdrIa', 'fdrIb', 'fdrIc'], title='Feeder Current Magnitudes')
plt.savefig('feeder.png')
plt.show()

ax = df.plot (y=['sub_p', 'sub_q'], title='Substation Real and Reactive Power')
plt.savefig('substation.png')
plt.show()

ax = df.plot(y=['solar_flux', 'temperature', 'humidity', 'pressure'], subplots=True, title='Weather')
ax[0].set_ylabel('W/m2')
ax[1].set_ylabel('degF')
ax[2].set_ylabel('pu')
ax[3].set_ylabel('mbar')
plt.savefig('weather.png')
plt.show()

# downsample to 15 minutes, plot, and export to CSV
df2 = df[0::300]
df2.info()

ax = df2.plot (y=['pvP', 'primaryP', 'secondaryP'], title='15-minute Load and PV Total Real Power')
plt.savefig('components15min.png')
plt.show()

ax = df2.plot (y=[xf_cols[0], xf_cols[10], xf_cols[20]], title='15-minute Sample Transformer Real Powers')
plt.savefig('transformers15min.png')
plt.show()
df2.to_hdf('aug11slow.hdf5', key='Aug11slow', mode='w')
df2.to_csv('aug11slow.csv')

