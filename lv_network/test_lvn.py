# Copyright (C) 2021 Battelle Memorial Institute
# file: test_lvn.py
# for IEEE Low-Voltage Distribution test cases, European and North American

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os

cwd = os.getcwd()

# make some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
# 
cfg_json = 'cimhubconfig.json'
cases = [
  { 'dsspath':'/home/tom/src/OpenDSS/Distrib/IEEETestCases/LVTestCaseNorthAmerican', 'skip_gld':False,
    'dssname':'SecPar', 'root':'IEEE390par', 'mRID':'EE33AEC3-8835-45BC-85B1-0E019F5EE070',
    'substation':'sub1', 'region':'NorthAmerica', 'subregion':'test_subregion',
    'glmvsrc': 139430.09, 'bases':[480.0, 13800.0, 230000.0], 'export_options':' -e=carson',
    'check_branches':[
      {'dss_link': 'TRANSFORMER.1', 'dss_bus': 'P4', 'gld_link': 'XF_1', 'gld_bus': 'P4'},
      {'dss_link': 'TRANSFORMER.2', 'dss_bus': 'P8', 'gld_link': 'XF_2', 'gld_bus': 'P8'},
    ]
  },
  { 'dsspath':'/home/tom/src/OpenDSS/Distrib/IEEETestCases/LVTestCaseNorthAmerican', 'skip_gld':True,
    'dssname':'Master', 'root':'IEEE390', 'mRID':'F4127C61-BD06-47DF-9558-28785E0934D9',
    'substation':'sub1', 'region':'NorthAmerica', 'subregion':'test_subregion',
    'glmvsrc': 139430.09, 'bases':[480.0, 13800.0, 230000.0], 'export_options':' -e=carson',
    'check_branches':[
      {'dss_link': 'TRANSFORMER.1', 'dss_bus': 'P4', 'gld_link': 'XF_1', 'gld_bus': 'P4'},
      {'dss_link': 'TRANSFORMER.2', 'dss_bus': 'P8', 'gld_link': 'XF_2', 'gld_bus': 'P8'},
    ]
  },
  { 'dsspath':'/home/tom/src/OpenDSS/Distrib/IEEETestCases/LVTestCase', 'skip_gld':False,
    'dssname':'Master', 'root':'LVTest', 'mRID':'2DD6F13C-58B8-4D3A-8DE7-67FDA0560293',
    'substation':'sub1', 'region':'Europe', 'subregion':'test_subregion',
    'glmvsrc': 6668.3956, 'bases':[416.0, 11000.0], 'export_options':' -e=carson -f=50.0',
    'check_branches':[
      {'dss_link': 'LINE.LINE1', 'dss_bus': '1', 'gld_link': 'LINE_LINE1', 'gld_bus': '1'},
    ]
  },
]

#cimhub.compare_cases (casefiles=cases, basepath='./base/', dsspath='./dss/', glmpath='./glm/')
#quit()

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

fp = open ('cim_base.dss', 'w')
for row in cases:
  root = row['root']
  dssname = row['dssname']
  dsspath = row['dsspath']
  mRID = row['mRID']
  print ('cd {:s}'.format(dsspath), file=fp)
  print ('redirect {:s}.dss'.format (dssname), file=fp)
  print ('set maxiterations=20', file=fp)
  print ('set tolerance=1e-8', file=fp)
  print ('solve', file=fp)
  print ('cd {:s}/base'.format(cwd), file=fp)
  print ('uuids file={:s}_uuids.dat'.format (root.lower()), file=fp)
  print ('export cim100 fid={:s} substation=sub1 subgeo=subgeo1 geo=geo1 file={:s}.xml'.format (mRID, root), file=fp)
  print ('export uuids file={:s}_uuids.dat'.format (root), file=fp)
  print ('export summary   {:s}_s.csv'.format (root), file=fp)
  print ('export voltages  {:s}_v.csv'.format (root), file=fp)
  print ('export currents  {:s}_i.csv'.format (root), file=fp)
  print ('export taps      {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd cim_base.dss', shell=True)
p1.wait()

# This is helpful for checking the CIM upload, but make_blazegraph_script will repeat it
#for row in cases:
#  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file base/' + row['dssname']+ '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
#  os.system (cmd)
#cimhub.list_feeders (cfg_json)

shfile = './go.sh'
cimhub.make_blazegraph_script (cases, 'base/', 'dss/', 'glm/', shfile)
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile, shell=True)

cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss', bControls=False)
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname='./checkglm.sh')
shfile = './checkglm.sh'
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call ('./checkglm.sh')

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./base/', dsspath='./dss/', glmpath='./glm/')

