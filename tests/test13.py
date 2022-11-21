# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test13.py
import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import os
import sys
import json

if sys.platform == 'win32':
  shfile_export = 'go.bat'
  shfile_glm = './glm/checkglm.bat'
  shfile_run = 'checkglm.bat'
  cfg_json = '../queries/cimhubconfig.json'
else:
  shfile_export = './go.sh'
  shfile_glm = './glm/checkglm.sh'
  shfile_run = './checkglm.sh'
  cfg_json = '../queries/cimhubdocker.json'

cwd = os.getcwd()

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

fp = open('cases.json')
cases = json.load(fp)
fp.close()

fp = open ('_cim_test.dss', 'w')
for row in cases:
  root = row['root']
  mRID = row['mRID']
  print ('cd ../example', file=fp)
  print ('redirect {:s}.dss'.format (root), file=fp)
  print ('set maxiterations=20', file=fp)
  print ('set tolerance=1e-8', file=fp)
  print ('solve', file=fp)
  print ('cd ../tests', file=fp)
  print ('export cim100 fid={:s} substation=sub1 subgeo=subgeo1 geo=geo1 file={:s}.xml'.format (mRID, root), file=fp)
  print ('export summary   {:s}_s.csv'.format (root), file=fp)
  print ('export voltages  {:s}_v.csv'.format (root), file=fp)
  print ('export currents  {:s}_i.csv'.format (root), file=fp)
  print ('export taps      {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd _cim_test.dss', shell=True)
p1.wait()

for row in cases:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + row['root']+ '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders (cfg_json)

cimhub.make_export_script (cases, shfile_export, bClearOutput=False)
p1 = subprocess.call (shfile_export, shell=True)

cimhub.make_dssrun_script (cases, scriptname='./dss/check.dss', bControls=False)
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (cases, scriptname=shfile_glm)
os.chdir('./glm')
p1 = subprocess.call (shfile_run)

os.chdir(cwd)
cimhub.compare_cases (cases)

