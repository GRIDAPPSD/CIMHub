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

cfg_json = '../queries/cimhubconfig.json'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()

  cimhub.convert_and_check_models (cases, bClearDB=True, bClearOutput=True, rstFile='onestep.inc')

