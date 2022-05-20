# Copyright (C) 2022 Battelle Memorial Institute
# file: test_drop.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig

cfg_json = '../queries/cimhubconfig.json'
test_mRID = '49AD8E07-3BF9-A4E2-CB8F-C3722F837B62'   # 13-bus platform mRID
second_mRID = '5B816B93-7A5F-B64C-8460-47C17D6E4B0F' # 13-bus assets platform mRID

cimhub.summarize_db (cfg_json)
cimhub.drop_circuit (cfg_json, test_mRID)
cimhub.drop_circuit (cfg_json, second_mRID)
cimhub.summarize_db (cfg_json)


