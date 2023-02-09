#from SPARQLWrapper import SPARQLWrapper2, JSON
import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import math
#import pandas as pd

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 'name': 'IEEE118'},
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 'name': 'WECC240'},
]

# global constants
SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180.0 / math.pi
MVA_BASE = 100.0

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile ('cimhubconfig.json')
  case_id = 0
  if len(sys.argv) > 1:
    case_id = int(sys.argv[1])
  sys_id = CASES[case_id]['id']
  sys_name = CASES[case_id]['name']

  dict = cimhub.load_feeder_dict ('qbes.xml', sys_id, bTime=False)
  cimhub.summarize_feeder_dict (dict)
#  cimhub.list_dict_table (dict, 'DistSequenceMatrix')


