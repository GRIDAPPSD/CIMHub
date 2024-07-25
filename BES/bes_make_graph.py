import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import math
import networkx as nx
import json
import os

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 'name': 'IEEE118'},
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 'name': 'WECC240'},
]

# global constants
SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180.0 / math.pi
MVA_BASE = 100.0

def km_distance (G, n1, n2):
#  seq = nx.dijkstra_path(G, n1, n2)
  seq = nx.shortest_path(G, n1, n2)
#  print (seq)
  edges = zip(seq[0:], seq[1:])
  km = 0.0
  for u, v in edges:
#    print(G[u][v])
    km += G[u][v]['edata']['km']
  return km

def build_system_graph (d):
  # accumulate loads and generation onto the buses
  buses = d['BESBus']['vals']
  for key, data in d['BESLoad']['vals'].items():
    buses[data['bus']]['has_load'] = True
  for key, data in d['BESMachine']['vals'].items():
    buses[data['bus']]['has_gen'] = True
  for key, data in d['BESSolar']['vals'].items():
    buses[data['bus']]['has_solar'] = True
  for key, data in d['BESWind']['vals'].items():
    buses[data['bus']]['has_wind'] = True
  G = nx.Graph()
  for key, data in buses.items():
    if 'has_solar' in data:
      nclass='solar'
    elif 'has_wind' in data:
      nclass='wind'
    elif 'has_gen' in data:
      nclass='gen'
    elif 'has_load' in data:
      nclass='load'
    else:
      nclass='bus'
    G.add_node (key, nclass=nclass, ndata={'kv':0.001*data['nomv']})
  # accumulate the transformer windings into transformers
  xfmrs = {}
  for key, data in d['BESPowerXfmrWinding']['vals'].items():
    toks = key.split(':')
    pname = toks[0]
    busnum = 'bus{:s}'.format(toks[1])
    if pname not in xfmrs:
      xfmrs[pname] = {busnum:data['bus']}
    else:
      xfmrs[pname][busnum] = data['bus']

  # add line, transformer, series compensator branches
  for key, data in d['BESLine']['vals'].items():
    km = round(0.001*data['len'],3)
    G.add_edge(data['bus1'],data['bus2'],eclass='line',ename=key,
               edata={'km':km, 'kv':0.001*data['basev']}, weight=km)
  for key, data in xfmrs.items():
    G.add_edge(data['bus1'],data['bus2'],eclass='transformer',ename=key,
               edata={'km':1.0}, weight=1.0)
  for key, data in d['BESCompSeries']['vals'].items():
    G.add_edge(data['bus1'],data['bus2'],eclass='series',ename=key,
               edata={'km':1.0, 'kv':0.001*data['basev']}, weight=1.0)

  # create XY coordinates for the buses
  dist = {}
  for n1 in G.nodes():
    if n1 not in dist:
      dist[n1] = {}
    for n2 in G.nodes():
      dist[n1][n2] = km_distance(G, n1, n2)
#  dist = dict(nx.shortest_path_length(G))
#  print (dist['99']['119'], dist['99']['99'], km_distance (G, '99', '119'))

  xy = nx.kamada_kawai_layout (G, dist=dist)
  for bus, row in xy.items():
    G.nodes()[bus]['ndata']['x'] = row[0]
    G.nodes()[bus]['ndata']['y'] = row[1]

  return G

def save_system_graph (G, fname):
  fp = open (fname, 'w')
  data = nx.readwrite.json_graph.node_link_data(G)
  json.dump (data, fp, indent=2)
  fp.close()

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile ('cimhubconfig.json')
  case_id = 0
  if len(sys.argv) > 1:
    case_id = int(sys.argv[1])
  sys_id = CASES[case_id]['id']
  sys_name = CASES[case_id]['name']

  d = cimhub.load_bes_dict ('qbes.xml', sys_id, bTime=False)
#  cimhub.summarize_bes_dict (d)
#  cimhub.list_dict_table (d, 'BESContainer')
#  cimhub.list_dict_table (d, 'BESBaseVoltage')

  G = build_system_graph (d)
  save_system_graph (G, '{:s}_Network.json'.format(sys_name))


