# Copyright (C) 2022 Battelle Memorial Institute
# file: onestepa.py
#
# usage: python onestepa.py
#
# input: from cases.json
#
# exports dss and glm with profiles
# pre-conditions:
#    onestep.py has created the xml files
#    blazegraph engine is running

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import json
import sys
import shutil
#import stat
#import os
import subprocess

if sys.platform == 'win32':
  cfg_json = '../queries/cimhubconfig.json'
  shfile_upload = '_upload.bat'
  shfile_export = '_export.bat'
  shfile_glm = '_checkglm.bat'
  dssfile_run = '_check.dss'
else:
  cfg_json = '../queries/cimhubdocker.json'
  shfile_upload = './_upload.sh'
  shfile_export = './_export.sh'
  shfile_glm = './_checkglm.sh'
  dssfile_run = '_check.dss'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()

  dssout = './dssa/'
  glmout = './glma/'
  for row in cases:
    row['outpath_csv'] = ''
    row['outpath_dss'] = dssout
    row['outpath_glm'] = '' # glmout
    row['export_options'] = ' -l=1.0 -a=1 -e=carson'

  cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=True)
  p1 = subprocess.call (shfile_upload, shell=True)

  cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=True)
  p1 = subprocess.call (shfile_export, shell=True)

  cimhub.make_dssrun_script (cases, scriptname=dssfile_run) # , bControls=bDssControls, tol=dssTol)
  p1 = subprocess.Popen ('opendsscmd {:s}'.format(dssfile_run), shell=True)
  p1.wait()

# cimhub.make_glmrun_script (cases, scriptname=shfile_glm, bProfiles=True, bHouses=False)
# shutil.copyfile('../support/commercial_schedules.glm', './glma/commercial_schedules.glm')
# p1 = subprocess.call (shfile_glm)

  cimhub.compare_cases (cases)

