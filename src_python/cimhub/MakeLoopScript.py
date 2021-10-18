import sys
import os
import stat

def append_dss_case(casefiles, inpath, outpath, fp):
  for c in casefiles:
    print('//', file=fp)
    print('clear', file=fp)
    print('cd', inpath, file=fp)
    print('redirect', c + '_base.dss', file=fp)
    print('set maxiterations=80', file=fp)
    print('set controlmode=off', file=fp)
    print('solve', file=fp)
    print('cd', outpath, file=fp)
    print('export summary ', c + '_s.csv', file=fp)
    print('export voltages', c + '_v.csv', file=fp)
    print('export currents', c + '_i.csv', file=fp)
    print('export taps    ', c + '_t.csv', file=fp)

def append_xml_case (casefiles, xmlpath, outpath, fp):
  for c in casefiles:
    print('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"', file=fp) # print('./drop_all.sh', file=fp)
    print('curl -D- -H "Content-Type: application/xml" --upload-file', xmlpath + c + '.xml', '-X POST $DB_URL', file=fp)
    print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=both -l=1.0 -i=1', outpath + c, file=fp)

def make_blazegraph_script (casefiles, xmlpath, dsspath, glmpath, scriptname):
  fp = open (scriptname, 'w')
  print ('#!/bin/bash', file=fp)
  print ('source envars.sh', file=fp)
  print ('mkdir', dsspath, file=fp)
  print ('mkdir', glmpath, file=fp)
  print ('rm', dsspath + '*.*', file=fp)
  print ('rm', glmpath + '*.*', file=fp)
  for row in casefiles:
    print('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"', file=fp) # print('./drop_all.sh arg', file=fp)
    print('curl -D- -H "Content-Type: application/xml" --upload-file', 
          xmlpath + row['root'] + '.xml', '-X POST $DB_URL', file=fp)
    print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=dss -l=1.0 -i=1', 
          dsspath + row['root'], file=fp)
    print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=glm -l=1.0 -i=1', 
          glmpath + row['root'], file=fp)
  fp.close()

def make_dssrun_script (casefiles, scriptname):
  fp = open (scriptname, 'w')
#  print('cd', dsspath, file=fp)
  for row in casefiles:
    c = row['root']
    print('//', file=fp)
    print('clear', file=fp)
    print('redirect', c + '_base.dss', file=fp)
    print('set maxiterations=80', file=fp)
    print('set controlmode=off', file=fp)
    print('solve', file=fp)
    print('export summary ', c + '_s.csv', file=fp)
    print('export voltages', c + '_v.csv', file=fp)
    print('export currents', c + '_i.csv', file=fp)
    print('export taps    ', c + '_t.csv', file=fp)
  fp.close()

# run the script this way for GridAPPS-D platform circuits
# python3 -m cimhub.MakeLoopScript -b $SRC_PATH
if __name__ == '__main__':
  srcpath = '/home/mcde601/src/Powergrid-Models/blazegraph/'
  arg = sys.argv[1]
  if len(sys.argv) > 2:
    srcpath = sys.argv[2]
  xmlpath = srcpath + 'cimxml/'
  dsspath = srcpath + 'test/dss/'
  glmpath = srcpath + 'test/glm/'
  bothpath = srcpath + 'both/'

  #casefiles = ['IEEE13',
  #             'IEEE13_Assets',
  #             'IEEE8500',
  #             'IEEE34',
  #             'IEEE37',
  #             'IEEE123',
  #             'DY-bal',
  #             'GYD-bal',
  #             'OYOD-bal',
  #             'OYOD-unbal',
  #             'YD-bal',
  #             'YY-bal',
  #             'IEEE8500u',
  #             'EPRI5',
  #             'EPRI7',
  #             'EPRI24',
  #             'GC_12_47_1',
  #             'R1_12_47_1',
  #             'R1_12_47_2',
  #             'R1_12_47_3',
  #             'R1_12_47_4',
  #             'R1_25_00_1',
  #             'R2_12_47_1',
  #             'R2_12_47_2',
  #             'R2_12_47_3',
  #             'R2_25_00_1',
  #             'R2_35_00_1',
  #             'R3_12_47_1',
  #             'R3_12_47_2',
  #             'R3_12_47_3',
  #             'R4_12_47_1',
  #             'R4_12_47_2',
  #             'R4_25_00_1',
  #             'R5_12_47_1',
  #             'R5_12_47_2',
  #             'R5_12_47_3',
  #             'R5_12_47_4',
  #             'R5_12_47_5',
  #             'R5_25_00_1',
  #             'R5_35_00_1',
  #             'EPRI_DPV_J1',
  #             'EPRI_DPV_K1',
  #             'EPRI_DPV_M1']

  #casefiles = ['IEEE13',
  #             'IEEE13_Assets',
  #             'IEEE8500',
  #             'IEEE123',
  #             'R2_12_47_2',
  #             'EPRI_DPV_J1']

  casefiles = ['ACEP_PSIL',
               'EPRI_DPV_J1',
               'IEEE123',
               'IEEE123_PV',
               'IEEE13',
               'IEEE13_Assets',
               'IEEE37',
               'IEEE8500',
               'IEEE8500_3subs',
               'R2_12_47_2',
               'Transactive']

  #casefiles = ['IEEE8500_3subs']

  #casefiles = ['IEEE123_PV']

  if arg == '-b':
    fp = open ('convert_xml.sh', 'w')
    print ('#!/bin/bash', file=fp)
    print ('source envars.sh', file=fp)
    print ('rm -rf', dsspath, file=fp)
    print ('rm -rf', glmpath, file=fp)
    print ('rm -rf', bothpath, file=fp)
    print ('mkdir', dsspath, file=fp)
    print ('mkdir', glmpath, file=fp)
    print ('mkdir', bothpath, file=fp)
    append_xml_case (casefiles, xmlpath, bothpath, fp)
    print ('', file=fp)
    fp.close()
    st = os.stat ('convert_xml.sh')
    os.chmod ('convert_xml.sh', st.st_mode | stat.S_IEXEC)

  if arg == '-d':
    fp = open ('check.dss', 'w')
    append_dss_case (casefiles, bothpath, dsspath, fp)
    fp.close()

