from SPARQLWrapper import SPARQLWrapper2
import re
import cimhub.CIMHubConfig as CIMHubConfig

drop_all = """drop all
"""

def clear_db (cfg_file=None):
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2 (CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'
  sparql.setQuery (drop_all)
  ret = sparql.query()

