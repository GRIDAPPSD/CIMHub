# Copyright (C) 2022 Battelle Memorial Institute
# file: batch_tests.py

import sys
import os
import subprocess

cwd = os.getcwd()

if sys.platform == 'win32':
  python_template = 'python {:s}.py > {:s}.log 2>&1'
  shell_template = '{:s}.bat {:s} > {:s}.log 2>&1'
else:
  python_template = 'python3 {:s}.py > {:s}.log'
  shell_template = './{:s}.sh {:s} > {:s}.log'

# do not use path separators in 'dir'
shell_tests = [
#  {'dir':'example', 'test':'example', 'args':'arg'},
#  {'dir':'tests', 'test':'test_combiner'},  # needs the example outputs
  ]
python_tests = [
#  {'dir':'tests', 'test':'test_cimhub'},
#  {'dir':'tests', 'test':'test_comparisons'},
#  {'dir':'tests', 'test':'test_drop'},
#  {'dir':'tests', 'test':'test_der'},
#  {'dir':'tests', 'test':'onestep'},
  {'dir':'tests', 'test':'naming'},
  ]

# do these first to create some working files
for test in shell_tests:
  testdir = os.path.join(cwd, test['dir'])
  root = test['test']
  os.chdir (testdir)
  args = ''
  if 'args' in test:
    if test['args'] is not None:
      args = test['args']
  cmd = shell_template.format (root, args, root)
  print ('** Testing "{:s}" in {:s}'.format (cmd, testdir))
  p1 = subprocess.call (cmd, shell=True)

for test in python_tests:
  testdir = os.path.join(cwd, test['dir'])
  root = test['test']
  os.chdir (testdir)
  cmd = python_template.format (root, root)
  print ('** Testing "{:s}" in {:s}'.format (cmd, testdir))
  p1 = subprocess.Popen (cmd, shell=True)
  p1.wait()

os.chdir (cwd)

