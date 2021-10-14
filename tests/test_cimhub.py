# Copyright (C) 2021 Battelle Memorial Institute
# file: test_cimhub.py

import cimhub.api as cimhub

db_cfg = 'db.cfg'
cfg_json = 'cimhubconfig.json'
test_mRID = '_F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29'
test_froot = 'test13'

#cimhub.list_feeders ()
#cimhub.summarize_db (db_cfg)
#cimhub.drop_circuit (db_cfg, '_DFBF372D-4291-49EF-ACCA-53DAFDE0338F')
#cimhub.list_measurables (cfg_json, test_froot, test_mRID)
#cimhub.drop_measurements (cfg_json, test_mRID)
#for mtxt in ['node_v', 'xfmr_pq', 'lines_pq', 'switch_i', 'loads', 'machines', 'special']:
#  mfile = '{:s}_{:s}.txt'.format (test_froot, mtxt)
#  cimhub.insert_measurements (cfg_json, mfile, test_froot + '_meas_uuid.txt')

#der_fname = test_froot + '_new_der.dat'
#der_uuids = test_froot + '_new_der_uuid.txt'
#cimhub.drop_der (cfg_json, der_uuids)
#cimhub.insert_der (cfg_json, der_fname)

#cimhub.drop_houses (cfg_json, test_mRID)
#cimhub.insert_houses (cfg_json, test_mRID, 3, 0, 'test13_house_uuids.json', 1.0)

cimhub.clear_db (db_cfg)

#cimhub.count_platform_circuit_classes (cfg_json, '../model_output_tests/')

cimhub.summarize_db (db_cfg)

