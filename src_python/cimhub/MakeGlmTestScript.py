import sys
import os
import stat

def write_glm_case (c, v, fp, bHouses=False, bProfiles=False):
  print('clock {', file=fp)
  print('  timezone EST+5EDT;', file=fp)
  print('  starttime \'2000-01-01 0:00:00\';', file=fp)
  print('  stoptime \'2000-01-01 0:00:00\';', file=fp)
  print('};', file=fp)
  print('#set relax_naming_rules=1', file=fp)
  print('#set profiler=1', file=fp)
  print('module powerflow {', file=fp)
  print('  solver_method NR;', file=fp)
  print('  line_capacitance TRUE;', file=fp)
  print('//  maximum_voltage_error 1e-6;', file=fp)
  print('//  default_maximum_voltage_error 1e-6;', file=fp)
  print('};', file=fp)
  print('module climate;', file=fp)
  print('module generators;', file=fp)
  print('module tape;', file=fp)
  print('module reliability {', file=fp)
  print('  report_event_log false;', file=fp)
  print('};', file=fp)
  print('object climate {', file=fp)
  print('  name climate;', file=fp)
  print('  latitude 45.0;', file=fp)
  print('  solar_direct 93.4458; // 92.902;', file=fp)
  print('}', file=fp)
  if bHouses:
    print('module residential;', file=fp)
    print('#include "appliance_schedules.glm";', file=fp)
  if bProfiles:
    print('#include "commercial_schedules.glm";', file=fp)
  print('#define VSOURCE=' + str (v), file=fp)
  print('#include \"' + c + '_base.glm\";', file=fp)
  print('#ifdef WANT_VI_DUMP', file=fp)
  print('object voltdump {', file=fp)
  print('  filename ' + c + '_volt.csv;', file=fp)
  print('  mode POLAR;', file=fp)
  print('};', file=fp)
  print('object currdump {', file=fp)
  print('  filename ' + c + '_curr.csv;', file=fp)
  print('  mode POLAR;', file=fp)
  print('};', file=fp)
  print('#endif', file=fp)

def make_glmrun_script (cases, scriptname, bHouses=False, bProfiles=False):
  bp = open (scriptname, 'w')
  bWindows = scriptname.endswith('.bat')
  if not bWindows:
    print ('#!/bin/bash', file=bp)
#  if movefiles:
#    print('cd', inpath, file=bp)
  for row in cases:
    # require outpath_glm not empty, and skip_gld not True
    if 'skip_gld' in row:
      if row['skip_gld']:
        continue
    if 'outpath_glm' not in row:
      continue
    if len(row['outpath_glm']) < 1:
      continue
    root = row['root']
    outpath_glm = os.path.abspath(row['outpath_glm'])
    print('cd', outpath_glm, file=bp)
    print('gridlabd -D WANT_VI_DUMP=1', root + '_run.glm >' + root + '.log', file=bp)
#    if movefiles:
#      print('mv {:s}*.csv {:s}'.format (c[0], outpath), file=bp)
    fp = open (os.path.join (outpath_glm, root + '_run.glm'), 'w')
    write_glm_case (root, row['glmvsrc'], fp, bHouses=bHouses, bProfiles=bProfiles)
    fp.close()
  bp.close()
  st = os.stat (scriptname)
  os.chmod (scriptname, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# run the script this way for GridAPPS-D platform circuits
# python3 -m cimhub.MakeGlmTestScript $SRC_PATH
if __name__ == '__main__':
  srcpath = '/home/tom/src/Powergrid-Models/platform/'
  if len(sys.argv) > 1:
    srcpath = sys.argv[1]
  inpath = srcpath + 'both/'

  casefiles = [['R2_12_47_2',57735.0],
               ['EPRI_DPV_J1',39837.2],
               ['IEEE13',66395.281],
               ['IEEE13_Assets',66395.281],
               ['IEEE13_OCHRE',66395.281],
               ['IEEE8500',69715.045],
               ['IEEE9500bal',69715.045],
#               ['IEEE37',132790.6],
               ['IEEE123',2401.8],
               ['IEEE123_PV',2401.8],
               ['ACEP_PSIL',277.13],
               ['Transactive',2401.8]]

  if sys.platform == 'win32':
    bp = open ('check_glm.bat', 'w')
    for c in casefiles:
      print('cd', inpath, file=bp)
      print('gridlabd -D WANT_VI_DUMP=1', c[0] + '_run.glm >../test/glm/' + c[0] + '.log', file=bp)
      print('mv {:s}*.csv ../test/glm'.format (c[0]), file=bp)

      fp = open (inpath + c[0] + '_run.glm', 'w')
      write_glm_case (c[0], c[1], fp)
      fp.close()
    bp.close()
  else:
    bpname = 'check_glm.sh'
    bp = open (bpname, 'w')
    print ('#!/bin/bash', file=bp)
    for c in casefiles:
      print('cd', inpath, file=bp)
      print('gridlabd -D WANT_VI_DUMP=1', c[0] + '_run.glm >../test/glm/' + c[0] + '.log', file=bp)
      print('mv {:s}*.csv ../test/glm'.format (c[0]), file=bp)

      fp = open (inpath + c[0] + '_run.glm', 'w')
      write_glm_case (c[0], c[1], fp)
      fp.close()
    bp.close()
    st = os.stat (bpname)
    os.chmod (bpname, st.st_mode | stat.S_IEXEC)

