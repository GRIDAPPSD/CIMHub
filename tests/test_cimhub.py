# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_cimhub.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import sys

cfg_json = '../queries/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)

test_mRID = 'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29'  # 13-bus
test_froot = 'test13'
second_mRID = 'DFBF372D-4291-49EF-ACCA-53DAFDE0338F'  # assets

# empty the database, load 2 test feeders, then delete one
cimhub.clear_db ()
#xml_path = '../../Powergrid-Models/platform/cimxml'
xml_path = '../model_output_tests/'  # copied from the example directory, different mRIDs than platform
for fname in ['IEEE13', 'IEEE13_Assets']:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_path + fname + '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders ()
cimhub.drop_circuit (second_mRID)

# measurement testing
cimhub.list_measurables (test_froot, test_mRID)
for mtxt in ['node_v', 'xfmr_pq', 'lines_pq', 'switch_i', 'loads', 'machines', 'special']:
  mfile = '{:s}_{:s}.txt'.format (test_froot, mtxt)
  cimhub.insert_measurements (mfile, test_froot + '_meas_uuid.txt')
cimhub.summarize_db ()
cimhub.drop_measurements (test_mRID)

# der testing
der_fname = test_froot + '_new_der.dat'
der_uuids = test_froot + '_new_der_uuid.txt'
cimhub.insert_der (der_fname)
cimhub.summarize_db ()
cimhub.drop_der (der_uuids)

# house testing
cimhub.insert_houses (test_mRID, 3, 0, 'test13_house_uuids.json', 1.0)
cimhub.summarize_db ()
cimhub.drop_houses (test_mRID)

# drop the test circuit, see if database is empty, (leaves two CIM version instances behind)
cimhub.drop_circuit (test_mRID)
cimhub.summarize_db ()

#cimhub.clear_db ()

# the following may take several minutes to run
#cimhub.count_platform_circuit_classes ('../model_output_tests/')


