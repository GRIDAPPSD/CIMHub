# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test13.py

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
cfg_json = 'cimhubconfig.json'

cases = [
  {'dssname':'IEEE13_Assets', 'root':'IEEE13_Assets', 'mRID':'DFBF372D-4291-49EF-ACCA-53DAFDE0338F',
    'substation':'sub1', 'region':'test_region', 'subregion':'test_subregion',
    'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 115000.0], 'export_options':' -l=1.0 -i=1.0 -e=carson',
    'check_branches':[{'dss_link': 'TRANSFORMER.XFM1', 'dss_bus': '633', 'gld_link': 'XF_XFM1', 'gld_bus': '633'},
                      {'dss_link': 'LINE.670671', 'dss_bus': '670', 'gld_link': 'LINE_670671', 'gld_bus': '670'}]},
  {'dssname':'IEEE13_CDPSM', 'root':'IEEE13_CDPSM', 'mRID':'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29',
    'substation':'sub2', 'region':'test_region', 'subregion':'test_subregion',
    'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 13200.0, 115000.0],
    'check_branches':[{'dss_link': 'TRANSFORMER.XFM1', 'dss_bus': '633', 'gld_link': 'XF_XFM1', 'gld_bus': '633'},
                      {'dss_link': 'LINE.670671', 'dss_bus': '670', 'gld_link': 'LINE_670671', 'gld_bus': '670'}]},
  {'dssname':'IEEE13_CDPSM_Z', 'root':'IEEE13_CDPSM_Z', 'mRID':'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29',
    'substation':'sub2', 'region':'test_region', 'subregion':'test_subregion',
    'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 13200.0, 115000.0], 'export_options':' -l=1.0 -z=1.0',
    'check_branches':[{'dss_link': 'TRANSFORMER.XFM1', 'dss_bus': '633', 'gld_link': 'XF_XFM1', 'gld_bus': '633'},
                      {'dss_link': 'LINE.670671', 'dss_bus': '670', 'gld_link': 'LINE_670671', 'gld_bus': '670'}]},
  {'dssname':'IEEE13_CDPSM_I', 'root':'IEEE13_CDPSM_I', 'mRID':'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29',
    'substation':'sub2', 'region':'test_region', 'subregion':'test_subregion',
    'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 13200.0, 115000.0], 'export_options':' -l=1.0 -i=1.0',
    'check_branches':[{'dss_link': 'TRANSFORMER.XFM1', 'dss_bus': '633', 'gld_link': 'XF_XFM1', 'gld_bus': '633'},
                      {'dss_link': 'LINE.670671', 'dss_bus': '670', 'gld_link': 'LINE_670671', 'gld_bus': '670'}]},
  {'dssname':'IEEE13_CDPSM_P', 'root':'IEEE13_CDPSM_P', 'mRID':'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29',
    'substation':'sub2', 'region':'test_region', 'subregion':'test_subregion',
    'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 13200.0, 115000.0], 'export_options':' -l=1.0 -p=1.0',
    'check_branches':[{'dss_link': 'TRANSFORMER.XFM1', 'dss_bus': '633', 'gld_link': 'XF_XFM1', 'gld_bus': '633'},
                      {'dss_link': 'LINE.670671', 'dss_bus': '670', 'gld_link': 'LINE_670671', 'gld_bus': '670'}]},
]

import json
for row in cases:
  row["inpath_dss"] = "../example"
  row["dssname"] = row["root"] + ".dss"
  row["path_xml"] = "./xml/"
  row["outpath_dss"] = "./dss/"
  row["outpath_glm"] = "./glm/"
  row["outpath_csv"] = ""
with open('cases.json', 'w') as fp:
  json.dump(cases, fp, indent=True)
quit()

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

fp = open ('cim_test.dss', 'w')
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

