#  Copyright (c) 2022, Battelle Memorial Institute
import os
import sys
import numpy as np

try:
  import matplotlib.pyplot as plt
  plt.rcParams['savefig.directory'] = os.path.abspath ('..\docs\media') # os.getcwd()
  bShowPlot = True
except:
  bShowPlot = False

classes = ['pv', 'load', 'gen', 'bess']

def add_case (ax, dsspath, offset):
  print ('Results from', dsspath)
  t = None
  for col in range(4):
    for row in range(2):
      key = '{:s}{:d}'.format(classes[col], row+1)
      d = np.loadtxt('./{:s}/ecp_harmonic_Mon_{:s}_1.csv'.format(dsspath, key), skiprows=1, delimiter=',')
      h = d[:,1]
      v = d[:,2] / d[0,2]
      i = d[:,3] / d[0,3]
      thdi = (np.sum(i**2) - 1.0) * 100.0
      print ('THDi {:6s} = {:6.2f} %'.format (key.upper(), thdi))
      if ax is not None:
        ax[row,col].bar(h + offset, i, width=0.45, label='{:s} {:s}'.format (key.upper(), dsspath))
        ax[row,col].set_ylabel('Magnitude [pu]')
        ax[row,col].set_xlabel('Harmonic')
        ax[row,col].legend()

if __name__ == '__main__':
  if len(sys.argv) > 1:
    if sys.argv[1] == 'noplot':
      bShowPlot = False

  if bShowPlot:
    fig, ax = plt.subplots(2, 4, figsize=(12,8))
    plt.suptitle ('Harmonic Current Distortion')
  else:
    ax = None

  offset = -0.25
  for dsspath in ['base', 'dssa']:
    add_case (ax, dsspath, offset)
    offset += 0.5

  if bShowPlot:
    plt.show()

