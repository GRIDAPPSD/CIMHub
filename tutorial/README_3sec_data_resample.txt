Data Imputation - '3sec_data_resample.py'
CIMHub/Tutorial/Impute Data with Houses and DER from cimhub.readthedocs.io

After completing the first 3 steps of the section (navigate to ./tutorial, invoke GRIDLAB-D two-day simulation
to create CSV files, and run 'combine recorders.py' loads the 3sec data into an HDF5 file), the next step is to 
plot the HDF5 data.  Running this script '3sec_data_resample.py' runs the script from step 4 'plot_hdf5.py' and
returns the plots, with the large DataFrame (df) containing 3sec data over a two-day period.  

The script is designed for user preference to resample the 3sec dataset at a designated number of minute intervals
using a moving avg.  Under 'main,' user may adjust the integer value from '15' to any number of 
minutes to produce a new df with the selected averages at each timestamp over the duration of the given 
sample period taken from the 3sec dataset. For example, running as is using a 15min sample time produces a new 
df 'df15' with DatetimeIndex containing 196 timestamps, each of which contains a moving avg from every column
of the 3sec dataset over that specific time interval.  The first measurement at t=00:00:00 in the new df is the first
average taken from the larger dataset spanning the interval t=00:00:00 - 00:14:57, and so forth.  

If the user prefers the windowed avg to fall at the end of the sample period as opposed to the beginning, simply 
call the 'dfShift' function using the newly formed df as input.  This method will add the first instantaneous 
measurement from the 3sec dataset at t=00:00:00 and place the first avg at t=00:15:00, etc. Running both allows 
for comparison.  There is also an option to resample with 30sec avgs (or any other timestamp in seconds by 
changing '30S').  Finally, the data may be plotted for comparison or written to CSV or HDF5 files if necessary.