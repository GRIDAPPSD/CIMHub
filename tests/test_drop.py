# Copyright (C) 2022 Battelle Memorial Institute
# file: test_drop.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig

cfg_json = 'cimhubconfig.json'
test_mRID = '_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62'
second_mRID = '_5B816B93-7A5F-B64C-8460-47C17D6E4B0F'

cimhub.summarize_db (cfg_json)
cimhub.drop_circuit (cfg_json, test_mRID)
cimhub.drop_circuit (cfg_json, second_mRID)
cimhub.summarize_db (cfg_json)


