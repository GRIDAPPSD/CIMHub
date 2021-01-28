from SPARQLWrapper import SPARQLWrapper2
import sys
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

if len(sys.argv) < 2:
  print ('usage: python3 ClearDB.py db.cfg')
  print (' Blazegraph server must already be started')
  exit()

fp = open (sys.argv[1], 'r')
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

