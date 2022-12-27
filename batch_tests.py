# Copyright (C) 2022 Battelle Memorial Institute
# file: batch_tests.py

import sys
import os
import subprocess

cwd = os.getcwd()

if sys.platform == 'win32':
  template = 'python {:s}.py > {:s}.log 2>&1'
else:
  template = 'python3 {:s}.py > {:s}.log'

# do not use path separators in 'dir'
tests = [
  {'dir':'tests', 'test':'onestep'},
  ]

for test in tests:
  testdir = os.path.join(cwd, test['dir'])
  root = test['test']
  os.chdir (testdir)
  print ('** Testing {:s} in {:s}'.format (root, testdir))
  cmd = template.format (root, root)
  p1 = subprocess.Popen (cmd, shell=True)
  p1.wait()


os.chdir (cwd)

