""" CIMHub - Tutorial: Impute Data with Houses and DER
This script invokes ../tutorial/'plot_hdf5.py' and returns the pandas DF containing 3-sec Data for two days.
DF may be resampled at ANY desired time step in minutes for averaging all column data over a given interval.
dfShift modifies DF to include first measurement at time=0secs from 3 sec data """

import matplotlib.pyplot as plt
import pandas as pd
from tutorial.plot_hdf5 import df


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
def plotLoadPvPowers(df, title):
    df.plot(y=['pvP', 'primaryP', 'secondaryP'], title=title)
    plt.legend(loc='best')
    plt.grid()
    plt.show()


def dfToCSV(df, filename):
    df.to_csv(filename + '.csv')


def dfToHDF(df, filename):
    df.to_hdf(filename + '.hdf5', key=filename, mode='w')


if __name__ == '__main__':
    df_row1 = pd.DataFrame(df.iloc[[0]])  # get 0th measurement
    df15 = dfResampleMinsAvg(df, 15) # 15mins avgs, **change int for min selection**
    df30secs= dfResample30secsAvg(df) # resample at 30sec avgs
    df15shifted = dfShift(df15, df_row1) # avg at end of each timestamp

    plotLoadPvPowers(df15, '15-Minute Average Load and PV Power')
    plotLoadPvPowers(df15shifted, '15-Minute Shifted Average Load and PV Power')
    plotLoadPvPowers(df30secs, '30-second Average Load and PV Power')

    # write new df to csv or hdf5
    # dfToCSV(df15, '15min_avgs')
    # dfToHDF(df15, '15min_avgs')

print('data resample complete')
