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

cfg_json = '../queries/cimhubconfig.json'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()

  # Clear DB and load each case one-at-a-time, because some feeder mRIDs are duplicates
  #  in this directory, which violate assumption that mRIDs are unique between circuits.

  # It's also necessary to copy edit files to the dss and glm directories, to improve the
  #   validation results and satisfy the -m=2 export option.
  if not os.path.exists('dss'):
    os.mkdir('dss')
  if not os.path.exists('glm'):
    os.mkdir('glm')
  os.system ('cp *edits*.dss dss')
  os.system ('cp *edits*.glm glm')

  for row in cases:
    if 'unbal' in row['root']:
      rstFile = 'onestep_unbal.inc'
    else:
      rstFile = 'onestep_bal.inc'
    cimhub.convert_and_check_models ([row], bClearDB=True, bClearOutput=False, rstFile=rstFile)

