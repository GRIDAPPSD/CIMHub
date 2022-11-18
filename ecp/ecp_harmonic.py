#  Copyright (c) 2022, Battelle Memorial Institute
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['savefig.directory'] = os.getcwd()

classes = ['pv', 'load', 'gen', 'bess']

if __name__ == '__main__':
  fig, ax = plt.subplots(2, 4, figsize=(12,8))
  plt.suptitle ('Harmonic Current Distortion')
  t = None
  for col in range(4):
    for row in range(2):
      key = '{:s}{:d}'.format(classes[col], row+1)
      d = np.loadtxt('ecp_harmonic_Mon_{:s}_1.csv'.format(key), skiprows=1, delimiter=',')
      h = d[:,1]
      v = d[:,2] / d[0,2]
      i = d[:,3] / d[0,3]
      thdi = (np.sum(i**2) - 1.0) * 100.0
      print ('THDi {:6s} = {:6.2f} %'.format (key.upper(), thdi))
      ax[row,col].bar(h, i, label=key.upper())
      ax[row,col].set_ylabel('Magnitude [pu]')
      ax[row,col].set_xlabel('Harmonic')
      ax[row,col].legend()

  plt.show()
