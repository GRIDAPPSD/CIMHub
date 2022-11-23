# Copyright (C) 2022 Battelle Memorial Institute
# file: list_db.py; for listing the structure and contents of the Blazegraph DB

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
from SPARQLWrapper import SPARQLWrapper2

cfg_json = '../queries/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)

cimhub.summarize_db()

sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'

q1 = """# discover the attributes of each class
SELECT DISTINCT ?class ?attr 
WHERE {
  ?s a ?class .
  ?s ?attr ?val
} ORDER BY ?class ?attr
"""

# [namespace][classname] points to [attributes from the namespace]
#   precondition: all namespaces of interest have been merged to one
dict = {} 
sparql.setQuery(q1)
ret = sparql.query()
for b in ret.bindings:
  cls = b['class'].value
  idx = cls.find('#')
  ns = cls[:idx+1]
  classname = cls[idx+1:]
  attr = b['attr'].value
  if ns not in dict:
    dict[ns] = {}
  if classname not in dict[ns]:
    dict[ns][classname] = []
  if attr.startswith(ns):
    idx = attr.find('#')
    dict[ns][classname].append(attr[idx+1:])
  else:
    pass
#    dict[ns][classname].append(attr)

for ns in dict:
  for cls in dict[ns]:
    dict[ns][cls].sort()

print ('Data Structure in Blazegraph:')
for ns in dict:
  print ('  Namespace:', ns)
  for cls in dict[ns]:
    print ('    Class:', cls, '(attributes follow)') # , ",".join(dict[ns][cls]))
    for attr in dict[ns][cls]:
      print ('      ', attr)

#input('Press a key for database content listing...')

ns = 'http://iec.ch/TC57/CIM100#'
for cls in dict[ns].keys():
  tbl=dict[ns][cls]
  fields = []
  if 'IdentifiedObject.name' in tbl:
    fields.append('IdentifiedObject.name')
  for fld in tbl:
    if fld not in fields:
      fields.append(fld)
  q2select = CIMHubConfig.prefix + '\nSELECT '
  q2where = ' ?s r:type c:{:s}.\n'.format(cls)
  i = 0
  for fld in fields:
    q2select = q2select + ' ?v{:d}'.format(i)
    q2where = q2where + ' ?s c:{:s} ?v{:d}.\n'.format(fld, i)
    i += 1

  q2 = q2select + ' WHERE {\n' + q2where + '\n} ORDER by ?v0'
  print(cls, fields)
  sparql.setQuery(q2)
  ret = sparql.query()
  for b in ret.bindings:
    print ('  ', ','.join([str(x.value) for x in b.values()]))

