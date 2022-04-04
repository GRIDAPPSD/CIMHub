# Copyright (C) 2021 Battelle Memorial Institute
# file: test9500.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os

cwd = os.getcwd()

cfg_json = 'cimhubconfig.json'
cases = [
  {
    'dssname':'ieee9500bal', 'root':'ieee9500bal', 'mRID':'EE71F6C9-56F0-4167-A14E-7F4C71F10EAA',
    'substation':'sub1', 'region':'geo1', 'subregion':'subgeo1',
    'glmvsrc': 69715.045, 'bases':[208.0, 480.0, 12470.0, 69000.0, 115000.0], 'export_options':' -p=1.0 -l=1.0 -e=carson -t=1',
    'check_branches':[{'dss_link': 'LINE.LN5815900-1', 'dss_bus': 'E192860',  'gld_link': 'LINE_LN5815900-1', 'gld_bus': 'E192860'},
                      {'dss_link': 'LINE.LN6380847-1', 'dss_bus': 'M1047303', 'gld_link': 'LINE_LN6380847-1', 'gld_bus': 'M1047303'},
                      {'dss_link': 'LINE.LN6044631-1', 'dss_bus': 'E203026',  'gld_link': 'LINE_LN6044631-1', 'gld_bus': 'E203026'},
                      {'dss_link': 'LINE.LN6381853-1', 'dss_bus': 'L2955077', 'gld_link': 'LINE_LN6381853-1', 'gld_bus': 'L2955077'},
                      {'dss_link': 'LINE.LN5486729-1', 'dss_bus': 'M1069310', 'gld_link': 'LINE_LN5486729-1', 'gld_bus': 'M1069310'},
                      {'dss_link': 'LINE.LN6350537-1', 'dss_bus': 'M1026907', 'gld_link': 'LINE_LN6350537-1', 'gld_bus': 'M1026907'},
                      ]},
]

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)
p1 = subprocess.call ('./clean.sh', shell=True)

fp = open ('cim_test.dss', 'w')
for row in cases:
  root = row['root']
  mRID = row['mRID']
  sub = row['substation']
  geo = row['region']
  subgeo = row['subregion']
  print ('cd original_dss', file=fp)
  print ('redirect {:s}.dss'.format (root), file=fp)
  # print ('uuids file=base/{:s}_uuids.dat'.format (root), file=fp)
  print ('set maxiterations=20', file=fp)
  print ('set tolerance=1e-5', file=fp)
  print ('solve', file=fp)
  print ('cd /home/ubuntu/CIMHub/ieee9500/base', file=fp)
  # print ('export cim100 fid={:s} substation={:s} geo={:s} subgeo={:s} file={:s}.xml'.format (mRID, sub, geo, subgeo, root), file=fp)
  print ('export summary   {:s}_s.csv'.format (root), file=fp)
  print ('export voltages  {:s}_v.csv'.format (root), file=fp)
  print ('export currents  {:s}_i.csv'.format (root), file=fp)
  print ('export taps      {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
  print ('export uuids {:s}_uuids.dat'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

for row in cases:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file base/' + row['root']+ '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders (cfg_json)

shfile = './go.sh'
cimhub.make_blazegraph_script (cases, 'base/', 'dss/', 'glm/', shfile, csvpath='csv/')
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile, shell=True)

cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss', bControls=False, tol=1e-5)
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
shfile = './checkglm.sh'
cimhub.make_glmrun_script (casefiles=cases, inpath='glm/', outpath='./', scriptname=shfile)
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile)

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='base/', dsspath='dss/', glmpath='glm/')

