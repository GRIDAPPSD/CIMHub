import sys
import os
import stat

def write_glm_case (c, v, fp):
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
  print('//  default_maximum_voltage_error 1e-6;', file=fp)
  print('};', file=fp)
  print('module generators;', file=fp)
  print('module tape;', file=fp)
  print('module reliability {', file=fp)
  print('  report_event_log false;', file=fp)
  print('};', file=fp)
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

def make_glmrun_script (casefiles, inpath, outpath, scriptname):
  bp = open (scriptname, 'w')
  print ('#!/bin/bash', file=bp)
  print('cd', inpath, file=bp)
  for row in casefiles:
    c = row['root']
    print('gridlabd -D WANT_VI_DUMP=1', c + '_run.glm >' + c + '.log', file=bp)
    print('mv {:s}*.csv {:s}'.format (c[0], outpath), file=bp)
    fp = open (inpath + c + '_run.glm', 'w')
    write_glm_case (c, row['glmvsrc'], fp)
    fp.close()
  bp.close()

# run the script this way for GridAPPS-D platform circuits
# python3 -m cimhub.MakeGlmTestScript $SRC_PATH
if __name__ == '__main__':
  srcpath = '/home/tom/src/Powergrid-Models/platform/'
  if len(sys.argv) > 1:
    srcpath = sys.argv[1]

  inpath = srcpath + 'both/'
  bpname = 'check_glm.sh'
  bp = open (bpname, 'w')
  print ('#!/bin/bash', file=bp)

  #casefiles = [['IEEE13',66395.3],
  #             ['IEEE13_Assets',66395.3],
  #             ['IEEE8500',66395.3],
  #             ['IEEE34',39837.2],
  #             ['IEEE37',132790.6],
  #             ['IEEE123',2401.8],
  #             ['DY-bal',7200.0],
  #             ['GYD-bal',7200.0],
  #             ['OYOD-bal',7200.0],
  #             ['OYOD-unbal',7200.0],
  #             ['YD-bal',7200.0],
  #             ['YY-bal',7200.0],
  #             ['IEEE8500u',66395.3],
  #             ['EPRI5',66395.3],
  #             ['EPRI7',66395.3],
  #             ['EPRI24',132790.6],
  #             ['GC_12_47_1',57735.0],
  #             ['R1_12_47_1',57735.0],
  #             ['R1_12_47_2',57735.0],
  #             ['R1_12_47_3',57735.0],
  #             ['R1_12_47_4',57735.0],
  #             ['R1_25_00_1',57735.0],
  #             ['R2_12_47_1',57735.0],
  #             ['R2_12_47_2',57735.0],
  #             ['R2_12_47_3',57735.0],
  #             ['R2_25_00_1',57735.0],
  #             ['R2_35_00_1',57735.0],
  #             ['R3_12_47_1',57735.0],
  #             ['R3_12_47_2',57735.0],
  #             ['R3_12_47_3',57735.0],
  #             ['R4_12_47_1',57735.0],
  #             ['R4_12_47_2',57735.0],
  #             ['R4_25_00_1',57735.0],
  #             ['R5_12_47_1',57735.0],
  #             ['R5_12_47_2',57735.0],
  #             ['R5_12_47_3',57735.0],
  #             ['R5_12_47_4',57735.0],
  #             ['R5_12_47_5',57735.0],
  #             ['R5_25_00_1',57735.0],
  #             ['R5_35_00_1',57735.0],
  #             ['EPRI_DPV_J1',39837.2],
  #             ['EPRI_DPV_K1',39837.2],
  #             ['EPRI_DPV_M1',38682.5]]

  #casefiles = [['IEEE13',66395.3],
  #             ['IEEE13_Assets',66395.3],
  #             ['IEEE8500',66395.3],
  #             ['IEEE123',2401.8],
  #             ['R2_12_47_2',57735.0],
  #             ['EPRI_DPV_J1',39837.2]]

  casefiles = [['R2_12_47_2',57735.0],
               ['EPRI_DPV_J1',39837.2],
               ['IEEE13',66395.3],
               ['IEEE13_Assets',66395.3],
               ['IEEE8500',66395.3],
               ['IEEE8500_3subs',66395.3],
               ['IEEE37',132790.6],
               ['IEEE123',2401.8],
               ['IEEE123_PV',2401.8],
               ['ACEP_PSIL',277.13],
               ['Transactive',2401.8]]

  #casefiles = [['IEEE8500_3subs',66395.3]]

  #casefiles = [['Transactive',2401.8]]

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

