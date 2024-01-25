# Copyright (C) 2022 Battelle Memorial Institute
# file: test_drop.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys

cfg_json = '../queries/cimhubconfig.json'

CIMHubConfig.ConfigFromJsonFile (cfg_json)

mRIDs = [
  '49AD8E07-3BF9-A4E2-CB8F-C3722F837B62', # 13-bus platform mRID
  '5B816B93-7A5F-B64C-8460-47C17D6E4B0F', # 13-bus assets platform mRID
  'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29', # 13-bus CIMHub mRID
  'DFBF372D-4291-49EF-ACCA-53DAFDE0338F'  # 13-bus assets CIMHub mRID
]

cimhub.summarize_db ()
for mRID in mRIDs:
  cimhub.drop_circuit (mRID)
cimhub.summarize_db ()


