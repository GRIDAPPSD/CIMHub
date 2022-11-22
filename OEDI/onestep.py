# Copyright (C) 2022 Battelle Memorial Institute
# file: onestep.py
#
# usage: python onestep.py
#
# input: from cases.json
#
# To make random UUID values for cases.json:
#   import uuid
#   idNew=uuid.uuid4()
#   print(str(idNew).upper())
#

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import json
import sys
import os

if sys.platform == 'win32':
  cfg_json = '../queries/cimhubconfig.json'
  dssroot = os.path.abspath ('../../OpenDSS/Version8/Distrib/IEEETestCases/')
else:
  cfg_json = '../queries/cimhubdocker.json'
  dssroot = os.path.abspath ('../../OpenDSS/Distrib/IEEETestCases/')

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()

#  for row in cases:
#    row['inpath_dss'] = os.path.join (dssroot, row['inpath_dss'])

  cimhub.convert_and_check_models (cases, bClearDB=True, bClearOutput=True)

