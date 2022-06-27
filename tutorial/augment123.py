# Copyright (C) 2022 Battelle Memorial Institute
# file: augment123.py

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
  {'dssname':'ieee123', 'root':'ieee123houses', 'mRID':'CBE09B55-091B-4BB0-95DA-392237B12640',
   'substation':'Fictitious', 'region':'Texas', 'subregion':'Austin',
   'glmvsrc': 2401.78, 'bases':[4160.0], 'export_options':' -l=1.0 -p=1.0 -h=1 -e=carson',
   'check_branches':[{'dss_link': 'LINE.L115', 'dss_bus': '149', 'gld_link': 'LINE_L115', 'gld_bus': '149'}]},
]

mRID = cases[0]['mRID']

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.list_feeders (cfg_json)
cimhub.summarize_db (cfg_json)

# run insert houses, GridLAB-D power flow with houses
cimhub.insert_houses (cfg_json, mRID, 5, 0, 'ieee123_house_uuids.json', scale=0.4)

cimhub.make_export_script (cases=cases, glmpath='glm/', scriptname=shfile_export, clean_dirs=False)
st = os.stat (shfile_export)
os.chmod (shfile_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile_export, shell=True)

os.chdir(cwd)
shutil.copyfile('../support/appliance_schedules.glm', './glm/appliance_schedules.glm')
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/',
                           scriptname=shfile_glm, bHouses=True, movefiles=False)
st = os.stat (shfile_glm)
os.chmod (shfile_glm, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call (shfile_run)
cimhub.write_glm_flows (glmpath='./', rootname=cases[0]['root'],
                        voltagebases=cases[0]['bases'],
                        check_branches=cases[0]['check_branches'])

# insert aggregated residential rooftop PV, run GridLAB-D with houses and PV
os.chdir(cwd)
cimhub.insert_der (cfg_json, 'ieee123_der.dat')
cases[0]['root'] = 'ieee123houseder'

cimhub.make_export_script (cases=cases, glmpath='glm/', scriptname=shfile_export, clean_dirs=False)
st = os.stat (shfile_export)
os.chmod (shfile_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile_export, shell=True)

os.chdir(cwd)
shutil.copyfile('../support/appliance_schedules.glm', './glm/appliance_schedules.glm')
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', 
                           scriptname=shfile_glm, bHouses=True, movefiles=False)
st = os.stat (shfile_glm)
os.chmod (shfile_glm, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call (shfile_run)
cimhub.write_glm_flows (glmpath='./', rootname=cases[0]['root'], 
                        voltagebases=cases[0]['bases'], 
                        check_branches=cases[0]['check_branches'])

# count the elements in the database; should have 287 Houses, 14 PhotovoltaicUnits, 14 PowerElectronicsConnections
os.chdir(cwd)
cimhub.summarize_db (cfg_json)

