from SPARQLWrapper import SPARQLWrapper2
import re

cim_ns = ''
blz_url = ''
sparql = None

prefix_template = """PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: <{cimURL}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

drop_all = """drop all
"""

def clear_db (db_cfg):
  fp = open (db_cfg, 'r')
  for ln in fp.readlines():
    toks = re.split('[,\s]+', ln)
    if toks[0] == 'blazegraph_url':
      blz_url = toks[1]
      sparql = SPARQLWrapper2 (blz_url)
      sparql.method = 'POST'
    elif toks[0] == 'cim_namespace':
      cim_ns = toks[1]
      prefix = prefix_template.format(cimURL=cim_ns)
  fp.close()

  sparql.setQuery (drop_all)
  ret = sparql.query()

