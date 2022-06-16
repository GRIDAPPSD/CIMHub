import sys
import matplotlib.pyplot as plt
import numpy as np
import h5py
import pandas as pd
from dateutil.parser import parse

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

xfmrs = []
fdr_csv = 'feeder_head.csv'
prim_csv = 'prim_loads.csv'
sec_csv = 'sec_loads.csv'
pv_csv = 'pv_meters.csv'
sub_csv = 'substation.csv'
weather_csv = 'weather.csv'

# CSV files from recorders have 9 comment lines
# CSV files from multirecorders have 8 comment lines; they have no single target
# the last of the comment lines is the column header
def n_comments (filename):
  if filename in [prim_csv, sec_csv, pv_csv]:
    return 8
  return 9

for ln in open ('load_xfmrs.dat', mode='r').readlines():
  xfmr = ln.strip()
  xfmrs.append (xfmr)

#print ('{:d} transformers'.format(len(xfmrs)))

df_sub = pd.read_csv (sub_csv, skiprows=n_comments(sub_csv)-1, index_col=0,
                      parse_dates=True, date_parser=lambda col: pd.to_datetime(col, tzinfos=timezones))# date_parser=lambda col: pd.to_datetime(col, utc=True))# , date_parser=lambda *x: parse(*x, tzinfos=timezones))

print (df_sub)
print (df_sub.describe())
print (df_sub.dtypes)
