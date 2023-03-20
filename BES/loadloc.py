import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 'name': 'IEEE118', 'xml': 'IEEE118_CIM_Loc.xml'},
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 'name': 'WECC240', 'xml': 'WECC240_CIM_Loc.xml'}
]

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile ('cimhubconfig.json')
#  cimhub.clear_db ()

  for row in CASES:
    xmlpath = row['xml']
    cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xmlpath + ' -X POST ' + CIMHubConfig.blazegraph_url
#    print (cmd)
    os.system (cmd)

  cimhub.list_bes ()

