# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test9500.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os
import sys

cfg_json = '../queries/cimhubconfig.json'

if sys.platform == 'win32':
  sh_clean = 'clean.bat'
  sh_export = 'go.bat'
  sh_run = 'checkglm.bat'
else:
  sh_clean = './clean.sh'
  sh_export = './go.sh'
  sh_run = './checkglm.sh'

cwd = os.getcwd()

cases = []

for froot in ['ieee9500bal', 'ieee9500unbal']:
  cases.append ({
    'dssname':froot, 'root':froot, 'mRID':'EE71F6C9-56F0-4167-A14E-7F4C71F10EAA',
    'substation':'sub1', 'region':'geo1', 'subregion':'subgeo1',
    'glmvsrc': 69715.045, 'bases':[208.0, 480.0, 12470.0, 69000.0, 115000.0], 'export_options':' -p=1.0 -l=1.0 -e=carson -t=1',
    'check_branches':[{'dss_link': 'LINE.LN5815900-1', 'dss_bus': 'E192860',  'gld_link': 'LINE_LN5815900-1', 'gld_bus': 'E192860'},
                      {'dss_link': 'LINE.LN6380847-1', 'dss_bus': 'M1047303', 'gld_link': 'LINE_LN6380847-1', 'gld_bus': 'M1047303'},
                      {'dss_link': 'LINE.LN6044631-1', 'dss_bus': 'E203026',  'gld_link': 'LINE_LN6044631-1', 'gld_bus': 'E203026'},
                      {'dss_link': 'LINE.LN6381853-1', 'dss_bus': 'L2955077', 'gld_link': 'LINE_LN6381853-1', 'gld_bus': 'L2955077'},
                      {'dss_link': 'LINE.LN5486729-1', 'dss_bus': 'M1069310', 'gld_link': 'LINE_LN5486729-1', 'gld_bus': 'M1069310'},
                      {'dss_link': 'LINE.LN6350537-1', 'dss_bus': 'M1026907', 'gld_link': 'LINE_LN6350537-1', 'gld_bus': 'M1026907'},
                      ]})

import json
for row in cases:
  row["inpath_dss"] = "./base"
  row["dssname"] = row["root"] + ".dss"
  row["path_xml"] = "./xml/"
  row["outpath_dss"] = "./dss/"
  row["outpath_glm"] = "./glm/"
  row["outpath_csv"] = "./csv/"
with open('cases.json', 'w') as fp:
  json.dump(cases, fp, indent=True)
quit()


CIMHubConfig.ConfigFromJsonFile (cfg_json)
p1 = subprocess.call (sh_clean, shell=True)
cimhub.clear_db (cfg_json)

fp = open ('cim_test.dss', 'w')
for row in cases:
  root = row['root']
  mRID = row['mRID']
  sub = row['substation']
  geo = row['region']
  subgeo = row['subregion']
  print ('cd {:s}/original_dss'.format (cwd), file=fp)
  print ('redirect {:s}.dss'.format (root), file=fp)
  print ('uuids file={:s}/base/{:s}_uuids.dat'.format (cwd, root), file=fp)
  print ('set maxiterations=20', file=fp)
  print ('set tolerance=1e-5', file=fp)
  print ('solve', file=fp)
  print ('cd {:s}/base'.format (cwd), file=fp)
  print ('export cim100 fid={:s} substation={:s} geo={:s} subgeo={:s} file={:s}.xml'.format (mRID, sub, geo, subgeo, root), file=fp)
  print ('export summary   {:s}_s.csv'.format (root), file=fp)
  print ('export voltages  {:s}_v.csv'.format (root), file=fp)
  print ('export currents  {:s}_i.csv'.format (root), file=fp)
  print ('export taps      {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
  print ('export uuids {:s}_uuids.dat'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

# upload and convert each case one at a time
for row in cases:
  os.chdir(cwd)
#  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file base/' + row['root']+ '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
#  os.system (cmd)

  cimhub.make_blazegraph_script (casefiles=[row], xmlpath='base/', dsspath='dss/', glmpath='glm/', 
                                 scriptname=sh_export, csvpath='csv/', clean_dirs=False)
  st = os.stat (sh_export)
  os.chmod (sh_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
  p1 = subprocess.call (sh_export, shell=True)

  cimhub.make_dssrun_script (casefiles=[row], scriptname='./dss/check.dss', bControls=False, tol=1e-5)
  os.chdir('./dss')
  p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
  p1.wait()

  os.chdir(cwd)
  cimhub.make_glmrun_script (casefiles=[row], inpath='glm/', outpath='./', scriptname=sh_run)
  st = os.stat (sh_run)
  os.chmod (sh_run, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
  p1 = subprocess.call (sh_run)

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='base/', dsspath='dss/', glmpath='glm/')

