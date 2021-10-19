# Copyright (C) 2021 Battelle Memorial Institute
# file: test_xfmr.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os

cwd = os.getcwd()

cfg_json = 'cimhubconfig.json'
cases = [
  {'root':'YYBal',    'mRID':'161B1872-2B5C-4CBF-9ED0-7193495CBE79','glmvsrc': 7200.00,'bases':[12.47,4.16]}, 
  {'root':'YDBal',    'mRID':'D09B6037-6236-42CA-AA11-811FE941AF5B','glmvsrc': 7200.00,'bases':[12.47,4.16]}, 
  {'root':'GYDBal',   'mRID':'0EC1B5A1-1EF7-4BDE-BA05-7391020BCE47','glmvsrc': 7200.00,'bases':[12.47,4.16]}, 
#         {'root':'DYBal',    'mRID':'D9A6F0E3-DD90-46AD-9CB1-7EDF15C41F9F','glmvsrc': 7200.00,'bases':[12.47,4.16]}, 
#         {'root':'YYD',      'mRID':'7319BD48-9C66-4038-B0AC-30DBD289A4A6','glmvsrc':39837.17,'bases':[69.0,13.2,2.4]}, 
#         {'root':'OYODBal',  'mRID':'AA782F4B-C424-4D54-AE39-9E6B108A7E0A','glmvsrc': 7200.00,'bases':[12.47,4.16]}, 
#         {'root':'OYODUnbal','mRID':'088F22EA-893E-4ED5-BB7B-E74585EB3DA1','glmvsrc': 7200.00,'bases':[12.47,4.16]}
]

#cases = [{'root':'YDBal',    'mRID':'D09B6037-6236-42CA-AA11-811FE941AF5B','glmvsrc': 7200.00,'bases':[12.47,4.16]}]

# exluding cases with IndMotor: 4wire_lagging.dss, 4wire_leading.dss, 4wire_motor.dss

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

