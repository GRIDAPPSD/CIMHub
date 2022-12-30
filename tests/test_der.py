# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_der.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import sys

cfg_json = '../queries/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)

test_mRID = 'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29'  # 13-bus
test_froot = 'test13'

# empty the database, load the 13-bus test feeder
cimhub.clear_db ()
xml_path = '../model_output_tests/'  # copied from the example directory, different mRIDs than platform
for fname in ['IEEE13']:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_path + fname + '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders ()
cimhub.summarize_db ()

# der testing
der_fname = test_froot + '_new_der.dat'
der_uuids = test_froot + '_new_der_uuid.txt'
cimhub.insert_der (der_fname)
cimhub.summarize_db ()
cimhub.drop_der (der_uuids)
cimhub.summarize_db ()

# expected results from summarize_db
#               tuples  Battery Photovoltaic PEC   PECphase SynchMachine
# Base Feeder     3341        3            2   5          4            0
# Added DER       3825        5            4   9          8            1
# Dropped DER     3341        3            2   5          4            0
