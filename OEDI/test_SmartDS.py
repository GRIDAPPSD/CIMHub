# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_OEDI.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import sys
import subprocess
import stat
import shutil 

# make some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
# 

cwd = os.getcwd()
casepath = os.path.abspath('./SmartDS')

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
  {'root':'SmartDS', 'mRID':'43790F23-2733-4F3F-9E57-09866A74F1E9','glmvsrc': 7416.00,'bases':[12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LINE.L(R:P9UDT12866-P9UHS16_1247)', 'dss_bus': 'P9UDT12866-P9UHS16_1247X', 
                      'gld_link': 'LINE_l(r:p9udt12866-p9uhs16_1247)', 'gld_bus': 'p9udt12866-p9uhs16_1247x'}]},
  ]

froot = cases[0]['root']

# create the CIM XML and base case solution from GridAPPS-D's model
#os.chdir(casepath)
#p1 = subprocess.Popen ('opendsscmd convert_smartds.dss', shell=True)
#p1.wait()

# upload the CIM XML file to Blazegraph
#os.chdir(casepath)
#cimhub.clear_db ()
#cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file {:s}.xml -X POST '.format (froot) + CIMHubConfig.blazegraph_url
#os.system (cmd)
#cimhub.list_feeders ()

# create the OpenDSS, GridLAB-D and CSV versions
#os.chdir(casepath)
#cimhub.make_export_script (shfile_export, cases, dsspath='dss/', glmpath='glm/', csvpath='csv/')
#st = os.stat (shfile_export)
#os.chmod (shfile_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
#p1 = subprocess.call (shfile_export, shell=True)

# run some load flow comparisons
#os.chdir(casepath)
#cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss')
#os.chdir('./dss')
#p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
#p1.wait()

#os.chdir(casepath)
#cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname=shfile_glm, movefiles=False)
#st = os.stat (shfile_glm)
#os.chmod (shfile_glm, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
#os.chdir('./glm')
#p1 = subprocess.call (shfile_run)

os.chdir(casepath)
#cimhub.compare_cases (casefiles=cases, basepath=casepath+'/', dsspath='./dss/', glmpath='./glm/')
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')

os.chdir(cwd)
