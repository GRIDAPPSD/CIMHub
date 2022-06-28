# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_cimhub.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import sys

if sys.platform == 'win32':
#  shfile_export = 'go.bat'
#  shfile_glm = './glm/checkglm.bat'
#  shfile_run = 'checkglm.bat'
  cfg_json = '../queries/cimhubjar.json'
else:
#  shfile_export = './go.sh'
#  shfile_glm = './glm/checkglm.sh'
#  shfile_run = './checkglm.sh'
  cfg_json = '../queries/cimhubdocker.json'

test_mRID = 'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29'  # 13-bus
test_froot = 'test13'
second_mRID = 'DFBF372D-4291-49EF-ACCA-53DAFDE0338F'  # assets

# empty the database, load 2 test feeders, then delete one
cimhub.clear_db (cfg_json)
#xml_path = '../../Powergrid-Models/platform/cimxml'
xml_path = '../model_output_tests/'  # copied from the example directory, different mRIDs than platform
CIMHubConfig.ConfigFromJsonFile (cfg_json)
for fname in ['IEEE13', 'IEEE13_Assets']:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_path + fname + '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders ()
cimhub.drop_circuit (cfg_json, second_mRID)

# measurement testing
cimhub.list_measurables (cfg_json, test_froot, test_mRID)
for mtxt in ['node_v', 'xfmr_pq', 'lines_pq', 'switch_i', 'loads', 'machines', 'special']:
  mfile = '{:s}_{:s}.txt'.format (test_froot, mtxt)
  cimhub.insert_measurements (cfg_json, mfile, test_froot + '_meas_uuid.txt')
cimhub.summarize_db (cfg_json)
cimhub.drop_measurements (cfg_json, test_mRID)

# der testing
der_fname = test_froot + '_new_der.dat'
der_uuids = test_froot + '_new_der_uuid.txt'
cimhub.insert_der (cfg_json, der_fname)
cimhub.summarize_db (cfg_json)
cimhub.drop_der (cfg_json, der_uuids)

# house testing
cimhub.insert_houses (cfg_json, test_mRID, 3, 0, 'test13_house_uuids.json', 1.0)
cimhub.summarize_db (cfg_json)
cimhub.drop_houses (cfg_json, test_mRID)

# drop the test circuit, see if database is empty, (leaves two CIM version instances behind)
cimhub.drop_circuit (cfg_json, test_mRID)
cimhub.summarize_db (cfg_json)

#cimhub.clear_db (cfg_json)

# the following may take several minutes to run
#cimhub.count_platform_circuit_classes (cfg_json, '../model_output_tests/')


