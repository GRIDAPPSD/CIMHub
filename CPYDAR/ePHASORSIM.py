from SPARQLWrapper import SPARQLWrapper2
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import xml.etree.ElementTree as ET

sparql = None

# ieee13x  4BE6DD69-8FE9-4C9F-AD44-B327D5623974
# ieee123x 4C4E3E2C-6332-4DCB-8425-26B628178374
# j1red    1C9727D2-E4D2-4084-B612-90A44E1810FD

def initialize_sparql (cfg_file=None):
  global sparql
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)

  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)

def build_query (prefix, base, fid):
  idx = base.find('WHERE {') + 8
  retq = prefix + '\n' + base[:idx] + """ VALUES ?fdrid {{"_{:s}"}}\n""".format (fid) + base[idx:]
  return retq

if __name__ == '__main__':
  cfg_file = 'cimhubconfig.json'
  if len(sys.argv) > 1:
    cfg_file = sys.argv[1]
  initialize_sparql (cfg_file)

  # read the queries
  tree = ET.parse('../q100.xml')
  root = tree.getroot()
  nsCIM = root.find('nsCIM').text.strip()
  nsRDF = root.find('nsRDF').text.strip()
  prefix = """PREFIX r: <{:s}>\nPREFIX c: <{:s}>""".format (nsRDF, nsCIM)
  queries = {}
  for query in root.findall('query'):
    queries[query.find('id').text.strip()] = query.find('value').text.strip()

  # test a query
  print ('ListFeeders from XML file of queries')
  sparql.setQuery (prefix + queries['DistFeeder'])
  ret = sparql.query()
  for b in ret.bindings:
    print (' ', b['feeder'].value,b['fid'].value)

  fid = '4BE6DD69-8FE9-4C9F-AD44-B327D5623974'
  #  VALUES ?fdrid {"_4C4E3E2C-6332-4DCB-8425-26B628178374"}
  print ('Photovoltaics')
  query = build_query (prefix, queries['DistSolar'], fid)
  print (query)
  sparql.setQuery (query)
  ret = sparql.query()
  for b in ret.bindings:
    print (' ', b['name'].value,b['bus'].value,b['ratedS'].value,b['ratedU'].value)

