import sys
import os
import stat
import shutil
import cimhub.CIMHubConfig as CIMHubConfig

def append_dss_case(cases, inpath, outpath, fp):
  for row in cases:
    c = row['file']
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

def append_xml_case (cases, xmlpath, outpath, fp):
  for row in cases:
    c = row['file']
    opts = row['opts']
    print('curl -D- -X POST $DB_URL --data-urlencode "update=drop all"', file=fp)
    print('curl -D- -H "Content-Type: application/xml" --upload-file', xmlpath + c + '.xml', '-X POST $DB_URL', file=fp)
    print('java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=both {:s}'.format (opts), outpath + c, file=fp)

def append_xml_case_windows (cases, xmlpath, outpath, fp):
  for row in cases:
    c = row['file']
    opts = row['opts']
    print('curl -D- -X POST %DB_URL% --data-urlencode "update=drop all"', file=fp)
    print('curl -D- -H "Content-Type: application/xml" --upload-file', xmlpath + c + '.xml', '-X POST %DB_URL%', file=fp)
    print('java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=both {:s}'.format (opts), outpath + c, file=fp)

def append_cimhub_envars (fp, bWindows):
  if bWindows:
    print ('echo off', file=fp)
    print ('set DB_URL="{:s}"'.format (CIMHubConfig.DB_URL), file=fp)
    print ('set CIMHUB_PATH="{:s}"'.format (CIMHubConfig.CIMHUB_PATH), file=fp)
    print ('set CIMHUB_PROG="{:s}"'.format (CIMHubConfig.CIMHUB_PROG), file=fp)
  else:
    print ('#!/bin/bash', file=fp)
    print ('declare -r DB_URL="{:s}"'.format (CIMHubConfig.DB_URL), file=fp)
    print ('declare -r CIMHUB_PATH="{:s}"'.format (CIMHubConfig.CIMHUB_PATH), file=fp)
    print ('declare -r CIMHUB_PROG="{:s}"'.format (CIMHubConfig.CIMHUB_PROG), file=fp)
    
def make_upload_script (cases, scriptname, bClearDB=True):
  fp = open (scriptname, 'w')
  bWindows = scriptname.endswith('.bat')
  if bWindows:
    db_string = '%DB_URL%'
  else:
    db_string = '$DB_URL'
  append_cimhub_envars (fp, bWindows)
  if bClearDB:
    print('curl -D- -X POST', db_string, '--data-urlencode "update=drop all"', file=fp)
  for row in cases:
    print('curl -D- -H "Content-Type: application/xml" --upload-file', 
          row['path_xml'] + row['root'] + '.xml', '-X POST', db_string, file=fp)
  fp.close()
  st = os.stat (scriptname)
  os.chmod (scriptname, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def get_actual_directory (row, key):
  if key in row:
    val = row[key]
    if val is not None:
      if len(val) > 0:
        return os.path.abspath(val)
  return None

def make_export_script (cases, scriptname, bClearOutput=True):
  fp = open (scriptname, 'w')
  bWindows = scriptname.endswith('.bat')
  if bWindows:
    cp_string = '%CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL%'
  else:
    cp_string = '$CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL'
  append_cimhub_envars (fp, bWindows)
  outdirs = []
  for row in cases:
    for key in ['outpath_glm', 'outpath_dss', 'outpath_csv']:
      if key in row:
        outdir = get_actual_directory (row, key)
        if outdir is not None:
          if outdir not in outdirs:
            outdirs.append(outdir)
  if bClearOutput:
    for outdir in outdirs:
      if os.path.exists(outdir):
        shutil.rmtree (outdir)
  for outdir in outdirs:
    if not os.path.exists(outdir):
      os.mkdir(outdir)
  for row in cases:
    dsspath = None
    glmpath = None
    csvpath = None
    opts = ''
    if ('mRID' in row) and (len(row['mRID']) > 0):
      opts += ' -s={:s}'.format(row['mRID'])
    if 'export_options' in row:
      opts += row['export_options']
    else:
      opts += ' -l=1.0 -i=1.0'
    dsspath = get_actual_directory (row, 'outpath_dss')
    glmpath = get_actual_directory (row, 'outpath_glm')
    csvpath = get_actual_directory (row, 'outpath_csv')
    if dsspath is not None:
      print('java -cp', cp_string, '-o=dss {:s}'.format (opts), os.path.join (dsspath, row['root']), file=fp)
    if csvpath is not None:
      print('java -cp', cp_string, '-o=csv {:s}'.format (opts), os.path.join (csvpath, row['root']), file=fp)
    if glmpath is not None:
      if 'skip_gld' in row:
        if row['skip_gld']:
          continue
      print('java -cp', cp_string, '-o=glm {:s}'.format (opts), os.path.join (glmpath, row['root']), file=fp)
  fp.close()
  st = os.stat (scriptname)
  os.chmod (scriptname, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def make_dssrun_script (cases, scriptname, bControls=False):
  fp = open (scriptname, 'w')
  for row in cases:
    bControls = False
    if 'dss_controls' in row:
      if row['dss_controls'] == True:
        bControls = True
    if 'dss_tolerance' in row:
      tol = float(row['dss_tolerance'])
    else:
      tol = 1e-8
    c = row['root']
    dsspath = os.path.abspath(row['outpath_dss'])
    print('//', file=fp)
    print('cd', dsspath, file=fp)
    print('clear', file=fp)
    print('redirect', c + '_base.dss', file=fp)
    print('set maxiterations=80', file=fp)
    print('set tolerance={:g}'.format(tol), file=fp)
    if bControls:
      print('set controlmode=static', file=fp)
      print('set maxcontroliter=200', file=fp)
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

  casefiles = [
    {'file':'ACEP_PSIL',      'opts':'-e=carson -p=1'},
    {'file':'EPRI_DPV_J1',    'opts':'-e=carson -i=1'}, # closest to CVR
    {'file':'IEEE123',        'opts':''},               # mixed loads, Deri
    {'file':'IEEE123_PV',     'opts':'-e=carson -p=1'},
    {'file':'IEEE13',         'opts':'-e=carson'},      # mixed loads
    {'file':'IEEE13_Assets',  'opts':'-e=carson'},      # mixed loads
    {'file':'IEEE13_OCHRE',   'opts':'-e=carson -p=1'},
    {'file':'IEEE37',         'opts':'-e=carson -p=1'},
    {'file':'IEEE8500',       'opts':'-e=carson -i=1'}, # needed to converge
    {'file':'IEEE9500bal',    'opts':'-e=carson -p=1'},
    {'file':'R2_12_47_2',     'opts':'-e=carson -p=1'},
    {'file':'Transactive',    'opts':'-e=carson -p=1'},
  ]

  if arg == '-b':
    if sys.platform == 'win32':
      dsspath = dsspath.replace ('/', '\\')
      glmpath = glmpath.replace ('/', '\\')
      bothpath = bothpath.replace ('/', '\\')
      xmlpath = xmlpath.replace ('/', '\\')
      fp = open ('convert_xml.bat', 'w')
      print ('call envars.bat', file=fp)
      print ('rd /s /q', dsspath, file=fp)
      print ('rd /s /q', glmpath, file=fp)
      print ('rd /s /q', bothpath, file=fp)
      print ('md', dsspath, file=fp)
      print ('md', glmpath, file=fp)
      print ('md', bothpath, file=fp)
      append_xml_case_windows (casefiles, xmlpath, bothpath, fp)
      print ('', file=fp)
      fp.close()
    else:
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

