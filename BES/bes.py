#from SPARQLWrapper import SPARQLWrapper2, JSON
import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import math
import networkx as nx
import json
import matplotlib.pyplot as plt 
import matplotlib.lines as lines
import matplotlib.patches as patches

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 'name': 'IEEE118'},
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 'name': 'WECC240'},
]

nodeTypes = {
  'load':  {'color':'green', 'size':15},
  'gen':   {'color':'red',   'size':20},
  'solar': {'color':'gold',  'size':20},
  'wind':  {'color':'blue',  'size':20},
  'bus':   {'color':'black', 'size':10}
  }

# global constants
SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180.0 / math.pi
MVA_BASE = 100.0

def get_node_size(nclass):
  if nclass in nodeTypes:
    return nodeTypes[nclass]['size']
  return 3

def get_node_color(nclass):
  if nclass in nodeTypes:
    return nodeTypes[nclass]['color']
  return 'black'

def plot_system_graph (G, sys_name):
  # assign node colors
  plotNodes = []
  nodeColors = []
  nodeSizes = []
  for n in G.nodes():
    if 'nclass' in G.nodes()[n]:
      nclass = G.nodes()[n]['nclass']
    else:
      nclass = 'bus'
    plotNodes.append(n)
    nodeColors.append (get_node_color (nclass))
    nodeSizes.append (get_node_size (nclass))

  # assign edge colors

  # create the plot with autolayout
  fig, ax = plt.subplots()

  nx.draw(G)

  #nx.draw_networkx_nodes (G, xy, nodelist=plotNodes, node_color=nodeColors, node_size=nodeSizes, ax=ax)
  #nx.draw_networkx_edges (G, xy, edgelist=plotEdges, edge_color=edgeColors, width=edgeWidths, alpha=0.8, ax=ax)

  plt.title ('{:s} Network'.format(sys_name))
  plt.xlabel ('X coordinate')
  plt.ylabel ('Y coordinate')
  ax.grid(linestyle='dotted')
  plt.show()

def build_system_graph (dict):
  # accumulate loads and generation onto the buses
  buses = dict['BESBus']['vals']
  for key, data in dict['BESLoad']['vals'].items():
    buses[data['bus']]['has_load'] = True
  for key, data in dict['BESMachine']['vals'].items():
    buses[data['bus']]['has_gen'] = True
  G = nx.Graph()
  for key, data in buses.items():
    if 'has_gen' in data:
      nclass='gen'
    elif 'has_load' in data:
      nclass='load'
    else:
      nclass='bus'
    G.add_node (key, nclass=nclass, ndata={'kv':0.001*data['nomv']})
  # accumulate the transformer windings into transformers
  xfmrs = {}
  for key, data in dict['BESPowerXfmrWinding']['vals'].items():
    toks = key.split(':')
    pname = toks[0]
    busnum = 'bus{:s}'.format(toks[1])
    if pname not in xfmrs:
      xfmrs[pname] = {busnum:data['bus']}
    else:
      xfmrs[pname][busnum] = data['bus']

  # add line, transformer, series compensator branches
  for key, data in dict['BESLine']['vals'].items():
    G.add_edge(data['bus1'],data['bus2'],eclass='line',ename=key,
               edata={'km':round(0.001*data['len'],3), 'kv':0.001*data['basev']})
  for key, data in xfmrs.items():
    G.add_edge(data['bus1'],data['bus2'],eclass='transformer',ename=key,
               edata={'km':1.0})
  for key, data in dict['BESCompSeries']['vals'].items():
    G.add_edge(data['bus1'],data['bus2'],eclass='series',ename=key,
               edata={'km':1.0, 'kv':0.001*data['basev']})
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

  dict = cimhub.load_bes_dict ('qbes.xml', sys_id, bTime=False)
  cimhub.summarize_bes_dict (dict)
  cimhub.list_dict_table (dict, 'BESContainer')
  cimhub.list_dict_table (dict, 'BESBaseVoltage')

  G = build_system_graph (dict)
  save_system_graph (G, '{:s}_Network.json'.format(sys_name))
  plot_system_graph (G, sys_name)


