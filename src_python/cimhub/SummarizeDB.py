from SPARQLWrapper import SPARQLWrapper2
import re
import cimhub.CIMHubConfig as CIMHubConfig

prefix_template = """PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: <{cimURL}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

count_classes = """SELECT ?class (COUNT(?class) as ?cnt)
WHERE {
  ?s a ?class .
} group by ?class order by ?class
"""

count_tuples = """SELECT (COUNT(?s) as ?cnt) where {
  ?s ?attr ?val.
}
"""

def run_query (sparql, prefix, lbl, qstr):
  print (lbl)
  sparql.setQuery (prefix + qstr)
  ret = sparql.query()
  for b in ret.bindings:
    if 'class' in b:
      print('  {:70s} {:5d}'.format(b['class'].value, int(b['cnt'].value)))
    else:
      print('  {:d} tuples'.format(int(b['cnt'].value)))

def summarize_db (cfg_file=None):
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2 (CIMHubConfig.blazegraph_url)
  sparql.method = 'GET'
  prefix = CIMHubConfig.prefix

  run_query (sparql, prefix, 'Class Summary', count_classes)
  run_query (sparql, prefix, 'Tuple Summary', count_tuples)

