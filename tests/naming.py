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

cfg_json = '../queries/cimhubconfig.json'
if sys.platform == 'win32':
  shfile_upload = '_upload.bat'
  shfile_export = '_export.bat'
  shfile_glm = '_checkglm.bat'
  dssfile_cim = '_conv_cim.dss'
  dssfile_run = '_check.dss'
else:
  shfile_upload = './_upload.sh'
  shfile_export = './_export.sh'
  shfile_glm = './_checkglm.sh'
  dssfile_cim = '_conv_cim.dss'
  dssfile_run = '_check.dss'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  # if running inside a container without GridLAB-D, provide an option to skip GridLAB-D
  skip_gld = False
  if len(sys.argv) > 1:
    if sys.argv[1] == 'nogld':
      skip_gld = True

  fp = open('name_cases.json')
  cases = json.load(fp)
  fp.close()
  for row in cases:
    row['export_options'] = row['export_options'] + ' -d=2'
    if skip_gld:
      row['outpath_glm'] = ''
      row['skip_gld'] = True

  cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=True)
  p1 = subprocess.call (shfile_upload, shell=True)

  cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=True)
  p1 = subprocess.call (shfile_export, shell=True)

  cimhub.make_dssrun_script (cases, scriptname=dssfile_run)
  p1 = subprocess.Popen ('opendsscmd {:s}'.format(dssfile_run), shell=True)
  p1.wait()

  cimhub.make_glmrun_script (cases, scriptname=shfile_glm)
  p1 = subprocess.call (shfile_glm, shell=True)

  cimhub.compare_cases (cases, 'naming.inc')

