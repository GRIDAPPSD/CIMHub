# Copyright (C) 2022 Battelle Memorial Institute
# file: ConvertModels.py

import cimhub.api as cimhub
import subprocess
import stat
import shutil
import os
import sys
import json

def convert_and_check_models (cases, bClearDB, bClearOutput, glmScheduleDir=None, bDssControls=False, dssTol=1e-8):
  cwd = os.getcwd()
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

  if bClearDB:
    cimhub.clear_db()
  csv_dirs = set()
  dss_dirs = set()
  glm_dirs = set()
  xml_dirs = set()
  for row in cases:
    if ('path_xml' in row) and (len(row['path_xml']) > 0):
      xml_dirs.add(os.path.abspath(row['path_xml']))
    if ('outpath_csv' in row) and (len(row['outpath_csv']) > 0):
      csv_dirs.add(os.path.abspath(row['outpath_csv']))
    if ('outpath_dss' in row) and (len(row['outpath_dss']) > 0):
      dss_dirs.add(os.path.abspath(row['outpath_dss']))
    if ('outpath_glm' in row) and (len(row['outpath_glm']) > 0):
      glm_dirs.add(os.path.abspath(row['outpath_glm']))

  if bClearOutput:
    for outdir in csv_dirs.union(dss_dirs, glm_dirs):
      if os.path.exists(outdir):
        shutil.rmtree (outdir)

  for outdir in xml_dirs.union(csv_dirs, dss_dirs, glm_dirs):
    if not os.path.exists(outdir):
      os.mkdir(outdir)

  bProfiles=False
  bHouses=False
  if glmScheduleDir is not None:
    bProfiles=True
    bHouses=True
    fAppliances = os.path.join(glmScheduleDir, 'appliance_schedules.glm')
    fCommercial = os.path.join(glmScheduleDir, 'commercial_schedules.glm')
    for outdir in glm_dirs:
      shutil.copyfile(fAppliances, os.path.join(outdir, 'appliance_schedules.glm'))
      shutil.copyfile(fCommercial, os.path.join(outdir, 'commercial_schedules.glm'))

  cimhub.make_dss2xml_script (cases, outfile=dssfile_cim, bControls=bDssControls, tol=dssTol)
  p1 = subprocess.Popen ('opendsscmd {:s}'.format(dssfile_cim), shell=True)
  p1.wait()
 
  cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=False)
  p1 = subprocess.call (shfile_upload, shell=True)
 
  cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=False)
  p1 = subprocess.call (shfile_export, shell=True)

  cimhub.make_dssrun_script (cases, scriptname=dssfile_run, bControls=bDssControls, tol=dssTol)
  p1 = subprocess.Popen ('opendsscmd {:s}'.format(dssfile_run), shell=True)
  p1.wait()

  cimhub.make_glmrun_script (cases, scriptname=shfile_glm, bProfiles=bProfiles, bHouses=bHouses)
  p1 = subprocess.call (shfile_glm)

  cimhub.compare_cases (cases)

