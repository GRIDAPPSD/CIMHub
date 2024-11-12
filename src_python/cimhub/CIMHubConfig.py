# Copyright (C) 2018-2022 Battelle Memorial Institute
# file: CIMHubConfig.py
"""Set the CIM namespace and Blazegraph URL
"""
import json
import urllib.request

DB_URL = ''
CIMHUB_PATH = ''
CIMHUB_PROG = ''

#******************************************************************************
# Default URL for blazegraph

# URL from inside the docker container:
#blazegraph_url = "http://blazegraph:8080/bigdata/sparql"

# URL from outside the docker container, to insert measurements:
#blazegraph_url = "http://localhost:8889/bigdata/sparql"

# URL for the lyrasis Blazegraph container, i.e., not part of GridAPPS-D:
blazegraph_url = "http://localhost:8889/bigdata/namespace/kb/sparql"

#******************************************************************************
# Default prefix for blazegraph queries; canonical version is now CIM100

cim100 = '<http://iec.ch/TC57/CIM100#'
# Prefix for all queries.
prefix = """PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: {cimURL}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
""".format(cimURL=cim100)

# cim17 is used in InsertMeasurements.py prior to summer 2019. 
# Notice the lack of "greater than" at the end.
cim17 = '<http://iec.ch/TC57/2012/CIM-schema-cim17#'
# Prefix for all queries.
prefix17 = """PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: {cimURL}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
""".format(cimURL=cim17)
#******************************************************************************

# cim16 is used for some utility feeders and ListOverheadWires.py, ListCNCables.py
cim16 = '<http://iec.ch/TC57/2012/CIM-schema-cim16#'
# Prefix for all queries.
prefix16 = """PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: {cimURL}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
""".format(cimURL=cim16)
#******************************************************************************

# for testing configurability; the following choices no longer work
#cim_ns = cim16
#prefix = prefix16
#blazegraph_url = "http://blazegraph:8080/bigdata/sparql"

def ConfigFromJsonFile (fname):
  global blazegraph_url, prefix, cim_ns, DB_URL, CIMHUB_PATH, CIMHUB_PROG
  with open(fname) as fp: 
    cfg = json.load(fp)
    if 'blazegraph_url' in cfg:
      blazegraph_url = cfg['blazegraph_url']
      DB_URL = blazegraph_url
#      print ('Configured URL to', blazegraph_url)
    if 'cim_ns' in cfg:
      cim_ns = cfg['cim_ns']
      prefix = """PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c: {cimURL}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
""".format(cimURL=cim_ns)
#      print ('Configured CIM Namespace to', cim_ns)
    if 'use_proxy' in cfg:
      if cfg['use_proxy'] == True:
        proxy_support = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
    if 'CIMHUB_PATH' in cfg:
      CIMHUB_PATH = cfg['CIMHUB_PATH']
    if 'CIMHUB_PROG' in cfg:
      CIMHUB_PROG = cfg['CIMHUB_PROG']

