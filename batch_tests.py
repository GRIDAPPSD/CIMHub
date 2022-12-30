# Copyright (C) 2022 Battelle Memorial Institute
# file: batch_tests.py

import sys
import os
import shutil
import subprocess

cwd = os.getcwd()

if sys.platform == 'win32':
  python_template = 'python {:s}.py {:s} > {:s}.log 2>&1'
  shell_template = '{:s}.bat {:s} > {:s}.log 2>&1'
  clean_cmd = 'clean.bat > nul 2>&1'
else:
  python_template = 'python3 {:s}.py {:s} > {:s}.log 2>&1'
  shell_template = './{:s}.sh {:s} > {:s}.log 2>&1'
  clean_cmd = './clean.sh > /dev/null 2>&1'

# do not use path separators in 'dir'
all_tests = [
  {'shell': True, 'dir':'example', 'test':'example',       'clean':True, 'args':'arg'}, # do this first
  {'shell': True, 'dir':'tests',   'test':'test_combiner', 'clean':True},
  {'dir':'tests',      'test':'test_cimhub'},
  {'dir':'tests',      'test':'test_comparisons'},
  {'dir':'tests',      'test':'test_drop'},
  {'dir':'tests',      'test':'test_der'},
  {'dir':'tests',      'test':'onestep'},
  {'dir':'tests',      'test':'naming'},
  {'dir':'ieee4',      'test':'onestep', 'clean':True},
  {'dir':'CPYDAR',     'test':'onestep', 'clean':True},
  {'dir':'der',        'test':'onestep', 'clean':True},
  {'dir':'OEDI',       'test':'onestep', 'clean':True},
  {'dir':'ieee9500',   'test':'onestep', 'clean':True},
  {'dir':'lv_network', 'test':'onestep', 'clean':True},
  {'dir':'ecp',        'test':'onestep', 'clean':True},
  {'dir':'ecp',        'test':'onestepa'},
  {'dir':'ecp',        'test':'ecp_daily',       'args':'noplot'},
  {'dir':'ecp',        'test':'ecp_duty',        'args':'noplot'},
  {'dir':'ecp',        'test':'ecp_growthcvr',   'args':'noplot'},
  {'dir':'ecp',        'test':'ecp_harmonic',    'args':'noplot'},
  {'dir':'ecp',        'test':'ecp_temperature', 'args':'noplot'},
  {'dir':'ecp',        'test':'ecp_yearly',      'args':'noplot'},
  {'dir':'ecp',        'test':'testgld'},
  {'dir':'ecp',        'test':'gld_daily',       'args':'noplot'},
  {'dir':'tutorial',   'test':'onestep',    'clean':True},
  {'dir':'gmdm',       'test':'adapt_gmdm', 'clean':True},
  ]

if len(sys.argv) > 1:
  if sys.argv[1] == 'clean':
    for test in all_tests:
      if 'clean' in test:
        if test['clean']:
          testdir = os.path.join(cwd, test['dir'])
          os.chdir (testdir)
          print ('** cleaning', testdir)
          p1 = subprocess.call (clean_cmd, shell=True)
    os.chdir(cwd)
    quit()

for test in all_tests:
  testdir = os.path.join(cwd, test['dir'])
  root = test['test']
  os.chdir (testdir)

  if 'clean' in test:
    if test['clean']:
      p1 = subprocess.call (clean_cmd, shell=True)

  args = ''
  if 'args' in test:
    if test['args'] is not None:
      args = test['args']

  bRunShell = False
  if 'shell' in test:
    if test['shell']:
      bRunShell = True

  if bRunShell:
    cmd = shell_template.format (root, args, root)
    print ('** Testing "{:s}" in {:s}'.format (cmd, testdir))
    p1 = subprocess.call (cmd, shell=True)
  else:
    cmd = python_template.format (root, args, root)
    print ('** Testing "{:s}" in {:s}'.format (cmd, testdir))
    p1 = subprocess.Popen (cmd, shell=True)
    p1.wait()

  if len(args) > 0:
    if args == 'noplot':
      shutil.copyfile('{:s}.log'.format(root), '{:s}.inc'.format(root))

os.chdir (cwd)

