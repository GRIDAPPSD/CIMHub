# Copyright (C) 2022 Battelle Memorial Institute
# file: onestep.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import json
import sys

if sys.platform == 'win32':
  cfg_json = '../queries/cimhubconfig.json'
else:
  cfg_json = '../queries/cimhubdocker.json'

CIMHubConfig.ConfigFromJsonFile (cfg_json)

fp = open('ecp_cases.json')
cases = json.load(fp)
fp.close()

cimhub.convert_and_check_models (cases, bClearDB=True, bClearOutput=True, glmScheduleDir='../support/')

