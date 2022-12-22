# Copyright (C) 2022 Battelle Memorial Institute
# file: naming.py
#
# usage: python naming.py
#
# input: from name_cases.json
#

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import json
import sys
import subprocess

if sys.platform == 'win32':
  cfg_json = '../queries/cimhubconfig.json'
  shfile_upload = '_upload.bat'
  shfile_export = '_export.bat'
  dssfile_run = '_check.dss'
else:
  cfg_json = '../queries/cimhubdocker.json'
  shfile_upload = './_upload.sh'
  shfile_export = './_export.sh'
  dssfile_run = '_check.dss'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('name_cases.json')
  cases = json.load(fp)
  fp.close()
  for row in cases:
    row['export_options'] = row['export_options'] + ' -d=0'

  cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=True)
  p1 = subprocess.call (shfile_upload, shell=True)

  cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=True)
  p1 = subprocess.call (shfile_export, shell=True)

