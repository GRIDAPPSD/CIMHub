# Copyright (C) 2021 Battelle Memorial Institute
# file: test_xfmr.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os

cwd = os.getcwd()

# some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
# EF222C39-6F6C-44BC-9A11-26EAE5AA4EF0
# CCB9EF29-23DF-429E-B609-B06EFB4945BA
# 13A48073-FBD8-42B6-8957-746E3F4FECC9
# 5F0B3FFA-C2D4-47D6-AB25-54231CEEA4B6
# 2921AE75-39A1-40D1-98DE-8E7BE5DC3A66

cfg_json = 'cimhubconfig.json'
cases = [
  {'dssname':'YYBal',    'root':'YYBal',    'mRID':'161B1872-2B5C-4CBF-9ED0-7193495CBE79','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'TRANSFORMER.T1', 'check_dss_bus': 'N2', 'check_gld_link': 'XF_T1', 'check_gld_bus': 'N2'},
  {'dssname':'YDBal',    'root':'YDBal',    'mRID':'D09B6037-6236-42CA-AA11-811FE941AF5B','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'LINE.LINE2', 'check_dss_bus': 'N3', 'check_gld_link': 'LINE_LINE2', 'check_gld_bus': 'N3'},
  {'dssname':'GYDBal',   'root':'GYDBal',   'mRID':'0EC1B5A1-1EF7-4BDE-BA05-7391020BCE47','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'LINE.LINE2', 'check_dss_bus': 'N3', 'check_gld_link': 'XF_T1', 'check_gld_bus': 'N3'},
  {'dssname':'DDBal',    'root':'DDBal',    'mRID':'D9A6F0E3-DD90-46AD-9CB1-7EDF15C41F9F','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'TRANSFORMER.T1', 'check_dss_bus': 'N2', 'check_gld_link': 'XF_T1', 'check_gld_bus': 'N2'},
  {'dssname':'DYBal',    'root':'DYBal',    'mRID':'7319BD48-9C66-4038-B0AC-30DBD289A4A6','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'TRANSFORMER.T1', 'check_dss_bus': 'N2', 'check_gld_link': 'XF_T1', 'check_gld_bus': 'N2'},
  {'dssname':'SCTUnBal', 'root':'SCTUnBal', 'mRID':'AA782F4B-C424-4D54-AE39-9E6B108A7E0A','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'TRANSFORMER.T1', 'check_dss_bus': 'N2', 'check_gld_link': 'XF_T1', 'check_gld_bus': 'N2'},
  {'dssname':'OnePh',    'root':'OnePh',    'mRID':'088F22EA-893E-4ED5-BB7B-E74585EB3DA1','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'TRANSFORMER.T1', 'check_dss_bus': 'N2', 'check_gld_link': 'XF_T1', 'check_gld_bus': 'N2'},
  {'dssname':'OYODBal',  'root':'OYODBal',  'mRID':'FE17C848-D906-499B-8EAD-F0ECF1F8A2AB','glmvsrc': 7200.00,'bases':[4160.0, 12470.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'LINE.LINE2', 'check_dss_bus': 'N3', 'skip_gld': True},
  {'dssname':'YYD',  'root':'YYD',  'mRID':'8C63A72C-9B64-42E7-B021-3FD00B4EBCEE','glmvsrc': 39837.17,'bases':[4160.0, 13200.0, 69000.0], 'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_dss_link': 'LINE.DLINE3-4', 'check_dss_bus': 'B4', 'skip_gld': True},
]

# exluding cases with IndMotor: 4wire_lagging.dss, 4wire_leading.dss, 4wire_motor.dss, the three-winding cases and the open wye/delta cases
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')
quit()

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

fp = open ('cim_test.dss', 'w')
for row in cases:
  root = row['root']
  mRID = row['mRID']
  print ('redirect {:s}.dss'.format (root), file=fp)
  print ('export cim100 fid={:s} substation=sub1 subgeo=subgeo1 geo=geo1 file={:s}.xml'.format (mRID, root), file=fp)
  print ('export summary  {:s}_s.csv'.format (root), file=fp)
  print ('export voltages {:s}_v.csv'.format (root), file=fp)
  print ('export currents {:s}_i.csv'.format (root), file=fp)
  print ('export taps     {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

for row in cases:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + row['root']+ '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders (cfg_json)

shfile = './go.sh'
cimhub.make_blazegraph_script (cases, './', 'dss/', 'glm/', shfile)
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile, shell=True)

cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss')
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname='./glm/checkglm.sh')
shfile = './glm/checkglm.sh'
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call ('./checkglm.sh')

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')

