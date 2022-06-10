# Copyright (C) 2022 Battelle Memorial Institute
# file: base123.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os
import sys

if sys.platform == 'win32':
  shfile_export = 'go.bat'
  shfile_glm = './glm/checkglm.bat'
  shfile_run = 'checkglm.bat'
else:
  shfile_export = './go.sh'
  shfile_glm = './glm/checkglm.sh'
  shfile_run = './checkglm.sh'

cwd = os.getcwd()

cfg_json = '../queries/cimhubconfig.json'

# make some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
# CA7CB1B6-BD68-44BF-8C6C-66BB4FA0081D
# 

cases = [
  {'dssname':'ieee123', 'root':'ieee123', 'mRID':'CBE09B55-091B-4BB0-95DA-392237B12640',
   'substation':'Fictitious', 'region':'Texas', 'subregion':'Austin',
   'glmvsrc': 2401.78, 'bases':[208.0, 480.0, 4160.0], 'export_options':' -l=1.0 -p=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.REG4A', 'dss_bus': '160'},
                     {'dss_link': 'TRANSFORMER.REG4B', 'dss_bus': '160'},
                     {'dss_link': 'TRANSFORMER.REG4C', 'dss_bus': '160'}, 
                     {'gld_link': 'REG_REG4', 'gld_bus': '160'},
                     {'dss_link': 'LINE.L115', 'dss_bus': '149', 'gld_link': 'LINE_L115', 'gld_bus': '149'}]},
]

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

fp = open ('cim_test.dss', 'w')
for row in cases:
  root = row['root']
  mRID = row['mRID']
  print ('redirect {:s}.dss'.format (root), file=fp)
  print ('uuids {:s}_uuids.dat'.format (root.lower()), file=fp)
  print ('export cim100 fid={:s} substation=sub1 subgeo=subgeo1 geo=geo1 file={:s}.xml'.format (mRID, root), file=fp)
  print ('export uuids {:s}_uuids.dat'.format (root), file=fp)
  print ('export summary   {:s}_s.csv'.format (root), file=fp)
  print ('export voltages  {:s}_v.csv'.format (root), file=fp)
  print ('export currents  {:s}_i.csv'.format (root), file=fp)
  print ('export taps      {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

for row in cases:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + row['root']+ '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders (cfg_json)

cimhub.make_blazegraph_script (cases, './', 'dss/', 'glm/', shfile_export)
st = os.stat (shfile_export)
os.chmod (shfile_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile_export, shell=True)

cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss', bControls=False)
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname=shfile_glm)
st = os.stat (shfile_glm)
os.chmod (shfile_glm, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call (shfile_run)

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')

