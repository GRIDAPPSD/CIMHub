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
    print('export summary  ', c + '_s.csv', file=fp)
    print('export voltages ', c + '_v.csv', file=fp)
    print('export currents ', c + '_i.csv', file=fp)
    print('export taps     ', c + '_t.csv', file=fp)
    print('export nodeorder', c + '_n.csv', file=fp)

def append_xml_case (casefiles, xmlpath, outpath, fp):
  for c in casefiles:
    print('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"', file=fp) # print('./drop_all.sh', file=fp)
    print('curl -D- -H "Content-Type: application/xml" --upload-file', xmlpath + c + '.xml', '-X POST $DB_URL', file=fp)
    print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=both -l=1.0 -i=1', outpath + c, file=fp)

def make_blazegraph_script (casefiles, xmlpath, dsspath, glmpath, scriptname, csvpath=None):
  fp = open (scriptname, 'w')
  print ('#!/bin/bash', file=fp)
  print ('source envars.sh', file=fp)
  print ('mkdir', dsspath, file=fp)
  print ('mkdir', glmpath, file=fp)
  print ('rm', dsspath + '*.*', file=fp)
  print ('rm', glmpath + '*.*', file=fp)
  if csvpath is not None:
    print ('mkdir', csvpath, file=fp)
    print ('rm', csvpath + '*.*', file=fp)
  for row in casefiles:
    if 'export_options' in row:
      opts = row['export_options']
    else:
      opts = ' -l=1.0 -i=1.0'
    print('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"', file=fp) # print('./drop_all.sh arg', file=fp)
    print('curl -D- -H "Content-Type: application/xml" --upload-file', 
          xmlpath + row['root'] + '.xml', '-X POST $DB_URL', file=fp)
    print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=dss {:s}'.format (opts), dsspath + row['root'], file=fp)
    if csvpath is not None:
      print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=csv {:s}'.format (opts), csvpath + row['root'], file=fp)
    if 'skip_gld' in row:
      if row['skip_gld']:
        continue
    print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=glm {:s}'.format (opts), glmpath + row['root'], file=fp)
  fp.close()

def make_dssrun_script (casefiles, scriptname, bControls=False, tol=1e-8):
  fp = open (scriptname, 'w')
#  print('cd', dsspath, file=fp)
  for row in casefiles:
    c = row['root']
    print('//', file=fp)
    print('clear', file=fp)
    print('redirect', c + '_base.dss', file=fp)
    print('set maxiterations=80', file=fp)
    print('set tolerance={:g}'.format(tol), file=fp)
    if bControls:
      print('set controlmode=static', file=fp)
      print('set maxcontroliter=50', file=fp)
    else:
      print('set controlmode=off', file=fp)
    print('solve', file=fp)
    print('export summary  ', c + '_s.csv', file=fp)
    print('export voltages ', c + '_v.csv', file=fp)
    print('export currents ', c + '_i.csv', file=fp)
    print('export taps     ', c + '_t.csv', file=fp)
    print('export nodeorder', c + '_n.csv', file=fp)
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

  casefiles = ['ACEP_PSIL',
               'EPRI_DPV_J1',
               'IEEE123',
               'IEEE123_PV',
               'IEEE13',
               'IEEE13_Assets',
               'IEEE13_OCHRE',
               'IEEE37',
               'IEEE8500',
               'IEEE8500_3subs',
               'R2_12_47_2',
               'Transactive']

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

