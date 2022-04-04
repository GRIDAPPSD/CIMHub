# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_dercat.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os

cfg_json = 'cimhubconfig.json'
test_mRID = '_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62'
test_froot = 'test13'

# empty the database, load 2 test feeders, then delete one
cimhub.clear_db (cfg_json)
#xml_path = '~/src/Powergrid-Models/platform/cimxml/'
xml_path = '../model_output_tests/'
CIMHubConfig.ConfigFromJsonFile (cfg_json)
for fname in ['IEEE13']:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_path + fname + '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
#cimhub.list_feeders ()

# der testing
der_fname = test_froot + '_new_der.dat'
der_uuids = test_froot + '_new_der_uuid.txt'
cimhub.insert_der (cfg_json, der_fname)
#cimhub.summarize_db (cfg_json)
#cimhub.drop_der (cfg_json, der_uuids)

