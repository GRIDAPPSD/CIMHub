# Copyright (C) 2022 Battelle Memorial Institute
# file: test_ecp.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os
import sys
import json

cwd = os.getcwd()

if sys.platform == 'win32':
  shfile_upload = 'upload.bat'
  shfile_export = 'export.bat'
  shfile_glm = './glm/checkglm.bat'
  shfile_run = 'checkglm.bat'
  cfg_json = '../queries/cimhubconfig.json'
else:
  shfile_upload = './upload.sh'
  shfile_export = './export.sh'
  shfile_glm = './glm/checkglm.sh'
  shfile_run = './checkglm.sh'
  cfg_json = '../queries/cimhubdocker.json'

# make some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
#

CIMHubConfig.ConfigFromJsonFile (cfg_json)

fp = open('cases.json')
cases = json.load(fp)
fp.close()

cimhub.make_dss2xml_script (cases, outfile='cim_test.dss')
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=True)
p1 = subprocess.call (shfile_upload, shell=True)
cimhub.list_feeders()

cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=True)
p1 = subprocess.call (shfile_export, shell=True)

cimhub.make_dssrun_script (cases, scriptname='./dss/check.dss')
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (cases, scriptname=shfile_glm, bProfiles=True, bHouses=True)
shutil.copyfile('../support/appliance_schedules.glm', './glm/appliance_schedules.glm')
shutil.copyfile('../support/commercial_schedules.glm', './glm/commercial_schedules.glm')
os.chdir('./glm')
p1 = subprocess.call (shfile_run)

os.chdir(cwd)
cimhub.compare_cases (cases)

