# Copyright (C) 2021-22 Battelle Memorial Institute
# file: test_comparisons.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import subprocess

cfg_json = '../queries/cimhubconfig.json'
if sys.platform == 'win32':
  shfile_upload = '_upload_xml.bat'
  shfile_export = '_convert_xml.bat'
  shfile_glm = '_checkglm.bat'
else:
  shfile_upload = './_upload_xml.sh'
  shfile_export = './_convert_xml.sh'
  shfile_glm = './_checkglm.sh'

CIMHubConfig.ConfigFromJsonFile (cfg_json)

cases = [{'dssname':'IEEE13_Assets.dss', 'root':'IEEE13_Assets', 'mRID': 'DFBF372D-4291-49EF-ACCA-53DAFDE0338F',
          'inpath_dss': '../example', 'path_xml': './xml/', 'outpath_dss': './dss/', 'outpath_glm': './glm/',
          'substation':'sub1', 'region':'test_region', 'subregion':'test_subregion', 
          'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 115000.0]},
         {'dssname':'IEEE13_CDPSM.dss', 'root':'IEEE13_CDPSM', 'mRID': 'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29',
          'inpath_dss': '../example', 'path_xml': './xml/', 'outpath_dss': './dss/', 'outpath_glm': './glm/',
          'substation':'sub2', 'region':'test_region', 'subregion':'test_subregion', 
          'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 13200.0, 115000.0]}]

cimhub.make_dss2xml_script (cases=cases, outfile='_cim_test.dss')
p1 = subprocess.Popen ('opendsscmd _cim_test.dss', shell=True)
p1.wait()

cimhub.make_upload_script (cases=cases, scriptname=shfile_upload, bClearDB=True)
p1 = subprocess.call (shfile_upload, shell=True)

cimhub.make_export_script (cases=cases, scriptname=shfile_export)
p1 = subprocess.call (shfile_export, shell=True)

cimhub.make_dssrun_script (cases=cases, scriptname='_check.dss')
p1 = subprocess.Popen ('opendsscmd _check.dss', shell=True)
p1.wait()

cimhub.make_glmrun_script (cases=cases, scriptname=shfile_glm)
p1 = subprocess.call (shfile_glm)

cimhub.compare_cases (cases=cases)
