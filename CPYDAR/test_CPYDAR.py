# Copyright (C) 2022 Battelle Memorial Institute
# file: test_CPYDAR.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import subprocess
import stat
import shutil
import glob 

cfg_json = 'cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)
cwd = os.getcwd()

# make some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
#
# 6114163B-E844-4DB9-9263-A2F2D5D0B596
# 


cases = [
  {'dssname':'ieee13pv', 'root':'ieee13x', 'mRID':'4BE6DD69-8FE9-4C9F-AD44-B327D5623974',
   'glmvsrc': 66395.28,'bases':[115000.0, 4160.0], 
   'export_options':'-s=_4BE6DD69-8FE9-4C9F-AD44-B327D5623974 -e=carson',
   'check_branches':[{'dss_link': 'LINE.650632', 'dss_bus': 'RG60', 'gld_link': 'LINE_650632', 'gld_bus': 'RG60'}]},
  {'dssname':'ieee123pv', 'root':'ieee123x', 'mRID':'4C4E3E2C-6332-4DCB-8425-26B628178374',
   'glmvsrc': 2401.78,'bases':[4160.0], 
   'export_options':'-s=_4C4E3E2C-6332-4DCB-8425-26B628178374 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.REG1A', 'dss_bus': '150', 'gld_link': 'REG_REG1A', 'gld_bus': '150'}]},
  {'dssname':'j1', 'root':'j1red', 'mRID':'1C9727D2-E4D2-4084-B612-90A44E1810FD',
   'glmvsrc': 39837.17,'bases':[69000.0, 12470.0, 416.0], 
   'export_options':'-s=_1C9727D2-E4D2-4084-B612-90A44E1810FD -e=carson -l=1.29',
   'check_branches':[{'dss_link': 'LINE.FEEDER', 'dss_bus': 'FDR_BUS', 'gld_link': 'SWT_FEEDER', 'gld_bus': 'FDR_BUS'}]},
  ]

## create the CIM XML and base case solutions from OpenDSS models
for row in cases:
  fp = open ('convert_CPYDAR.dss', 'w')
  root = row['root']
  mRID = row['mRID']
  print ('cd {:s}/{:s}'.format (cwd, root), file=fp)
  print ('redirect Master.dss'.format (root), file=fp)
  print ('solve', file=fp)
  print ('uuids {:s}_uuids.dat'.format (root.lower()), file=fp)
  print ('export cim100 fid={:s} substation=sub1 subgeo=subgeo1 geo=geo1 file={:s}.xml'.format (mRID, root), file=fp)
  print ('export uuids {:s}_uuids.dat'.format (root), file=fp)
  print ('export summary  {:s}_s.csv'.format (root), file=fp)
  print ('export voltages {:s}_v.csv'.format (root), file=fp)
  print ('export currents {:s}_i.csv'.format (root), file=fp)
  print ('export taps     {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
  fp.close ()
  p1 = subprocess.Popen ('opendsscmd convert_CPYDAR.dss', shell=True)
  p1.wait()

# upload the CIM XML files to Blazegraph
cimhub.clear_db (cfg_json)
for row in cases:
  root = row['root']
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file {:s}/{:s}.xml -X POST {:s}'.format (root, root, CIMHubConfig.blazegraph_url)
  os.system (cmd)
cimhub.list_feeders ()

#cimhub.list_measurables (cfg_json, 'j1red', '_1C9727D2-E4D2-4084-B612-90A44E1810FD')
#quit()

# create the OpenDSS, GridLAB-D and CSV versions
shfile = './go.sh'
cimhub.make_export_script (shfile, cases, dsspath='dss/', glmpath='glm/', csvpath='csv/')
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile, shell=True)

## run some load flow comparisons
for row in cases:
  os.chdir(cwd)
  cimhub.make_dssrun_script (casefiles=[row], scriptname='./dss/check.dss')
  os.chdir('./dss')
  p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
  p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname='./glm/checkglm.sh', movefiles=False)
shfile = './glm/checkglm.sh'
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call ('./checkglm.sh')

#quit()

# copy base DSS solutions to the same directory for compare_cases function to work
os.chdir(cwd)
os.makedirs(os.path.dirname('./base/'), exist_ok=True)
for row in cases:
  for f in glob.glob ('./{:s}/*.csv'.format(row['root'])):
    shutil.copy (f, './base/')
cimhub.compare_cases (casefiles=cases, basepath='./base/', dsspath='./dss/', glmpath='./glm/')

