# Copyright (C) 2022 Battelle Memorial Institute
# file: augment123.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os
import sys
import json

cases = [
  {'dssname':'ieee123', 'root':'ieee123houses', 'mRID':'CBE09B55-091B-4BB0-95DA-392237B12640',
   'substation':'Fictitious', 'region':'Texas', 'subregion':'Austin', 'skip_gld': False,
   'glmvsrc': 2401.78, 'bases':[4160.0], 'export_options':' -l=1.0 -p=1.0 -h=1 -a=1 -e=carson',
   'check_branches':[{'dss_link': 'LINE.L115', 'dss_bus': '149', 'gld_link': 'LINE_L115', 'gld_bus': '149'}]},
]

cfg_json = '../queries/cimhubconfig.json'

if sys.platform == 'win32':
  shfile_export = '_export.bat'
  shfile_glm = '_checkglm.bat'
else:
  shfile_export = '_export.sh'
  shfile_glm = '_checkglm.sh'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()

  mRID = cases[0]['mRID']
  cases[0]['outpath_dss'] = ''

  cimhub.list_feeders ()
  cimhub.summarize_db ()

  # run insert houses, GridLAB-D power flow with houses
  cimhub.insert_houses (mRID=mRID, region=5, seed=0, uuidfile='ieee123_house_uuids.json', scale=0.4)

  cases[0]['root'] = 'ieee123houses'
  cases[0]['export_options'] = ' -l=1.0 -p=1.0 -h=1 -a=1 -e=carson'
  cimhub.make_export_script (cases=cases, scriptname=shfile_export, bClearOutput=False)
  p1 = subprocess.call (shfile_export, shell=True)

  shutil.copyfile('../support/appliance_schedules.glm', './glm/appliance_schedules.glm')
  cimhub.make_glmrun_script (cases=cases, scriptname=shfile_glm, bHouses=True, bProfiles=False)
  p1 = subprocess.call (shfile_glm)
  cimhub.write_glm_flows (glmpath='glm/', rootname=cases[0]['root'],
                          voltagebases=cases[0]['bases'],
                          check_branches=cases[0]['check_branches'])

  # insert aggregated residential rooftop PV, run GridLAB-D with houses and PV
  cimhub.insert_der ('ieee123_der.dat')
  cases[0]['root'] = 'ieee123houseder'

  cimhub.make_export_script (cases=cases, scriptname=shfile_export, bClearOutput=False)
  p1 = subprocess.call (shfile_export, shell=True)

  cimhub.make_glmrun_script (cases=cases, scriptname=shfile_glm, bHouses=True, bProfiles=False)
  p1 = subprocess.call (shfile_glm)
  cimhub.write_glm_flows (glmpath='glm/', rootname=cases[0]['root'], 
                          voltagebases=cases[0]['bases'], 
                          check_branches=cases[0]['check_branches'])

  #insert the player file references for spot loads, run GridLAB-D with houses, PV, variable spot loads
  cimhub.insert_profiles ('oedi_profiles.dat')
  cases[0]['root'] = 'ieee123ecp'

  cimhub.make_export_script (cases=cases, scriptname=shfile_export, bClearOutput=False)
  p1 = subprocess.call (shfile_export, shell=True)

  shutil.copyfile('../support/commercial_schedules.glm', './glm/commercial_schedules.glm')
  cimhub.make_glmrun_script (cases=cases, scriptname=shfile_glm, bHouses=True, bProfiles=True)
  p1 = subprocess.call (shfile_glm)
  cimhub.write_glm_flows (glmpath='glm/', rootname=cases[0]['root'], 
                          voltagebases=cases[0]['bases'], 
                          check_branches=cases[0]['check_branches'])

  # count the elements in the database; should have 287 Houses, 
  # 14 PhotovoltaicUnits, 14 PowerElectronicsConnections
  # 1 EnergyConnectionProfile
  cimhub.summarize_db (cfg_json)

