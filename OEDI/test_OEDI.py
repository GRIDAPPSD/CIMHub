# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_OEDI.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import sys
import subprocess
import stat
import shutil 

ckt_mRID = '_E407CBB6-8C8D-9BC9-589C-AB83FBF0826D'
froot = 'IEEE123_PV'
cwd = os.getcwd()

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

CIMHubConfig.ConfigFromJsonFile (cfg_json)

cases = [
  {'root':'IEEE123_PV', 'mRID':'E407CBB6-8C8D-9BC9-589C-AB83FBF0826D','glmvsrc': 2400.00,'bases':[4160.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'inpath_dss':'../../Powergrid-Models/platform/dss/NREL',
   'dssname':'IEEE123Master_fixedVR.dss',
   'check_branches':[{'dss_link': 'LINE.L114', 'dss_bus': '135', 'gld_link': 'LINE_L114', 'gld_bus': '135'}]},

  {'root':'SmartDS', 'mRID':'43790F23-2733-4F3F-9E57-09866A74F1E9','glmvsrc': 7416.00,'bases':[12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'inpath_dss':'./SmartDS', 'dssname':'Master.dss',
   'substation':'p9udt12866-p9uhs16_1247x',
   'region':'OEDI',
   'subregion':'SmartDS',
   'substationID':'',
   'regionID':'',
   'subregionID':'',
   'check_branches':[{'dss_link': 'LINE.L(R:P9UDT12866-P9UHS16_1247)', 'dss_bus': 'P9UDT12866-P9UHS16_1247X', 
                      'gld_link': 'LINE_l(r:p9udt12866-p9uhs16_1247)', 'gld_bus': 'p9udt12866-p9uhs16_1247x'}]},

  {'root':'IEEE13_PV', 'mRID':'8122F968-1805-4CDA-826D-E7006985C23B','glmvsrc': 66395.28,'bases':[480.0, 4160.0, 115000.0],
   'inpath_dss':'./base/', 'substation':'IEEE13', 'region':'IEEE', 'subregion':'Medium'},

  {'root':'IEEE390_PV', 'mRID':'FF06502A-99DA-4AD9-A172-46CA60EDEF55', 'glmvsrc': 139430.09,'bases':[480.0,13800.0,230000.0],
   'inpath_dss':'./base/', 'substation':'IEEE390', 'region':'IEEE', 'subregion':'Medium'},
  ]

import json
for row in cases:
#  row["inpath_dss"] = os.path.join (dssroot, row["inpath_dss"])
  if "dssname" not in row:
    row["dssname"] = row["root"] + ".dss"
  row["path_xml"] = "./xml/"
  row["outpath_dss"] = "./dss/"
  row["outpath_glm"] = "./glm/"
  row["outpath_csv"] = ""
with open('cases.json', 'w') as fp:
  json.dump(cases, fp, indent=True)
quit()

# create the CIM XML and base case solution from GridAPPS-D's model
p1 = subprocess.Popen ('opendsscmd convert.dss', shell=True)
p1.wait()

# upload the CIM XML file to Blazegraph
cimhub.clear_db (cfg_json)
cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file {:s}.xml -X POST '.format (froot) + CIMHubConfig.blazegraph_url
os.system (cmd)
cimhub.list_feeders ()

# insert measurements
cimhub.list_measurables (cfg_json, froot, ckt_mRID)
for mtxt in ['node_v', 'xfmr_pq', 'lines_pq', 'switch_i', 'loads', 'machines', 'special']:
  mfile = '{:s}_{:s}.txt'.format (froot, mtxt)
  cimhub.insert_measurements (cfg_json, mfile, froot + '_msid.json')
cimhub.summarize_db (cfg_json)

# create the OpenDSS, GridLAB-D and CSV versions
cimhub.make_export_script (shfile_export, cases, dsspath='dss/', glmpath='glm/', csvpath='csv/')
st = os.stat (shfile_export)
os.chmod (shfile_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile_export, shell=True)

# run some load flow comparisons
cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss')
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname=shfile_glm, movefiles=False)
st = os.stat (shfile_glm)
os.chmod (shfile_glm, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call (shfile_run)

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')

