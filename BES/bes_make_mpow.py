# Copyright (C) 2023-2024 Battelle Memorial Institute
import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import os

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 'name': 'IEEE118', 'swingbus':'131'},
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 'name': 'WECC240', 'swingbus':'2438'},
]

FUELS = {
  'hydro':  {'c2':1.0e-5, 'c1': 1.29, 'c0': 0.0},
  'wind':   {'c2':1.0e-5, 'c1': 0.01, 'c0': 0.0},
  'solar':  {'c2':1.0e-5, 'c1': 0.01, 'c0': 0.0},
  'coal':   {'c2':0.0009, 'c1': 19.0, 'c0': 2128.0},
  'ng':     {'c2':0.0060, 'c1': 45.0, 'c0': 2230.0},
  'nuclear':{'c2':0.00019, 'c1': 8.0, 'c0': 1250.0}
}

# global constants
MVA_BASE = 100.0

def get_gencosts(fuel):
  c2 = 0.0
  c1 = 0.0
  c0 = 0.0
  if fuel in FUELS:
    c2 = FUELS[fuel]['c2']
    c1 = FUELS[fuel]['c1']
    c0 = FUELS[fuel]['c0']
  return c2, c1, c0

def add_mpc_generator (gens, data, bus_numbers, bus_generation, bus_headroom):
  busnum = int(data['bus'])
  Pg = data['p']/1.0e6
  Pmax = data['maxP']/1.0e6
  Pheadroom = Pmax - Pg
  if busnum in bus_generation:
    bus_generation[busnum] += Pg
  else:
    bus_generation[busnum] = Pg
  if busnum in bus_headroom:
    bus_headroom[busnum] += Pheadroom
  else:
    bus_headroom[busnum] = Pheadroom
  status = 1
  if Pg <= 0.0:
    status = 1
  gens.append ({'bus':bus_numbers[data['bus']],
                'Pg':Pg,
                'Qg':data['q']/1.0e6,
                'Qmax':data['maxQ']/1.0e6,
                'Qmin':data['minQ']/1.0e6,
                'Vg':1.0,
                'mBase':data['ratedS']/1.0e6,
                'status':status,
                'Pmax':Pmax,
                'Pmin':data['minP']/1.0e6,
                'Pc1':0.0, 'Pc2':0.0, 'Qc1min':0.0, 'Qc1max':0.0, 'Qc2min':0.0, 'Qc2max':0.0,
                'ramp_agc':0.0, 'ramp_10':0.0, 'ramp_30':0.0, 'ramp_q':0.0, 'apf':0.0})

def build_bus_lists (d):
  bNumeric = True
  for key in d['BESBus']['vals']:
    if not key.isdigit():
      bNumeric = False
      break
  if bNumeric:
    ordered_buses = dict(sorted(d['BESBus']['vals'].items(), key=lambda x:int(x[0])))
  else:
    ordered_buses = d['BESBus']['vals']
  bus_numbers = {}
  busnum = 1
  for key, data in ordered_buses.items():
    bus_numbers[key] = busnum
    busnum += 1
  return ordered_buses, bus_numbers

def build_matpower (d, sys_name, fp, swingbus):
  print ('function mpc = {:s}'.format(sys_name), file=fp)
  print ('mpc.version = "2";', file=fp)
  print ('mpc.baseMVA = {:.1f};'.format(MVA_BASE), file=fp)

  print ("""
%% bus data
%	bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
mpc.bus = [""", file=fp)
  mpc_buses = []
  mpc_bus_names = []
  # MATPOWER needs to number the buses as consecutive integers, and
  # we need to map the bus names (not necessarily integer) to MATPOWER bus numbers
  ordered_buses, bus_numbers = build_bus_lists(d)
  for key, data in ordered_buses.items():
    mpc_buses.append ({'bus_i':len(mpc_buses)+1,
                       'type':1,
                       'Pd':0.0,
                       'Qd':0.0,
                       'Gs':0.0,
                       'Bs':0.0,
                       'area':1,
                       'Vm':1.0,
                       'Va':0.0,
                       'baseKV':data['nomv'] * 0.001,
                       'zone':1,
                       'Vmax':1.1,
                       'Vmin':0.9})
    mpc_bus_names.append (key)
  # add loads and shunts to buses
  total_load = 0.0
  for key, data in d['BESLoad']['vals'].items():
    idx = bus_numbers[data['bus']]-1
    Pd = data['p'] / 1.0e6
    total_load += Pd
    mpc_buses[idx]['Pd'] += Pd
    mpc_buses[idx]['Qd'] += data['q'] / 1.0e6
  for key, data in d['BESCompShunt']['vals'].items():
    idx = bus_numbers[data['bus']]-1
    scale = data['sections']*data['nomu']*data['nomu']/1.0e6
    mpc_buses[idx]['Gs'] += data['gsection']*scale
    mpc_buses[idx]['Bs'] += data['bsection']*scale
  # any bus with a generator is type 2; bus with most total generation is type 3
  mpc_generators = []
  mpc_genfuels = []
  mpc_gentypes = []
  bus_generation = {}
  bus_headroom = {}
  for key, data in d['BESMachine']['vals'].items():
    idx = bus_numbers[data['bus']]-1
    mpc_buses[idx]['type'] = 2
    add_mpc_generator (mpc_generators, data, bus_numbers, bus_generation, bus_headroom)
    if data['type'] == 'Hydro':
      mpc_genfuels.append('hydro')
      mpc_gentypes.append('HY')
    elif data['type'] == 'Nuclear':
      mpc_genfuels.append('nuclear')
      mpc_gentypes.append('ST')
    else:
      mpc_genfuels.append('ng')
      mpc_gentypes.append('ST')
  for key, data in d['BESSolar']['vals'].items():
    idx = bus_numbers[data['bus']]-1
    mpc_buses[idx]['type'] = 2
    add_mpc_generator (mpc_generators, data, bus_numbers, bus_generation, bus_headroom)
    mpc_genfuels.append('solar')
    mpc_gentypes.append('PV')
  for key, data in d['BESWind']['vals'].items():
    idx = bus_numbers[data['bus']]-1
    mpc_buses[idx]['type'] = 2
    add_mpc_generator (mpc_generators, data, bus_numbers, bus_generation, bus_headroom)
    mpc_genfuels.append('wind')
    mpc_gentypes.append('WT')
  max_bus = max(bus_generation, key=bus_generation.get)
  print ('bus {:d} has maximum generation of {:.2f} MW and headroom of {:.2f} MW'.format (max_bus, 
                                                                                          bus_generation[max_bus], 
                                                                                          bus_headroom[max_bus]))
  head_bus = max(bus_headroom, key=bus_headroom.get)
  print ('bus {:d} has maximum headroom of {:.2f} MW and generation of {:.2f} MW'.format (head_bus, 
                                                                                          bus_headroom[head_bus], 
                                                                                          bus_generation[head_bus]))
  swingbus_num = bus_numbers[swingbus]
  mpc_buses[swingbus_num-1]['type'] = 3
  for data in mpc_buses:
    print (' {:5d} {:2d} {:9.3f} {:9.3f} {:9.3f} {:9.3f} {:3d} {:7.4f} {:7.4f} {:7.3f} {:3d} {:6.3f} {:6.3f};'.format(
      data['bus_i'], data['type'], data['Pd'], data['Qd'], data['Gs'], data['Bs'], data['area'], data['Vm'], data['Va'], 
      data['baseKV'], data['zone'], data['Vmax'], data['Vmin']), file=fp)
  print ('];', file=fp)

  print ("""
%% generator data - BESMachine+BESSolar+BESWind
%	bus Pg Qg Qmax Qmin Vg mBase status Pmax Pmin Pc1 Pc2 Qc1min Qc1max Qc2min Qc2max ramp_agc ramp_10 ramp_30 ramp_q apf
mpc.gen = [""", file=fp)
  total_gen = 0.0
  for data in mpc_generators:
    total_gen += data['Pg']
    print (' {:5d} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:6.4f} {:8.3f} {:1d} {:8.3f} {:8.3f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f};'.format(
      data['bus'], data['Pg'], data['Qg'], data['Qmax'], data['Qmin'], data['Vg'], data['mBase'], data['status'], data['Pmax'], 
      data['Pmin'], data['Pc1'], data['Pc2'], data['Qc1min'], data['Qc1max'], data['Qc2min'], data['Qc2max'],
      data['ramp_agc'], data['ramp_10'], data['ramp_30'], data['ramp_q'], data['apf']), file=fp)
  print ('];', file=fp)

  # accumulate the transformer windings into transformers
  xfmrs = {}
  for key, data in d['BESPowerXfmrWinding']['vals'].items():
    toks = key.split(':')
    pname = toks[0]
    bus = bus_numbers[data['bus']]
    if pname not in xfmrs:
      mva = data['ratedS'] / 1.0e6
      kv = data['ratedU'] / 1.0e3
      zbase = kv*kv / MVA_BASE # mva # on system MVA base, not on transformer MVA
      mesh = d['BESPowerXfmrMesh']['vals']['{:s}:1:2'.format(pname)]
      r = mesh['r'] / zbase
      x = mesh['x'] / zbase
      xfmrs[pname] = {'from':bus, 'mva':mva, 'r':r, 'x': x}
    else:
      xfmrs[pname]['to'] = bus

  print ("""
%% branch data - BESLine+BESCompSeries+collected transformers
%	fbus tbus r x b rateA rateB rateC ratio angle status angmin angmax
mpc.branch = [""", file=fp)
  for key, data in d['BESLine']['vals'].items():
    bus1 = bus_numbers[data['bus1']]
    bus2 = bus_numbers[data['bus2']]
    kvbase = data['basev']/1000.0
    zbase = kvbase*kvbase/MVA_BASE
    q = data['b']*kvbase*kvbase
    r = data['r']/zbase
    x = data['x']/zbase
    b = q/MVA_BASE
    print (' {:5d} {:5d} {:9.6f} {:9.6f} {:9.6f} 0.0 0.0 0.0 0.0 0.0 1 0.0 0.0;'.format (bus1, bus2, r, x, b), file=fp)
  for key, data in d['BESCompSeries']['vals'].items():
    bus1 = bus_numbers[data['bus1']]
    bus2 = bus_numbers[data['bus2']]
    kvbase = data['basev']/1000.0
    zbase = kvbase*kvbase/MVA_BASE
    r = data['r']/zbase
    x = data['x']/zbase
    print (' {:5d} {:5d} {:9.6f} {:9.6f} 0.0 0.0 0.0 0.0 0.0 0.0 1 0.0 0.0;'.format (bus1, bus2, r, x), file=fp)
  for key, data in xfmrs.items():
    rateA = data['mva']
    rateB = rateA * 4.0 / 3.0
    rateC = rateA * 5.0 / 3.0
    print (' {:5d} {:5d} {:9.6f} {:9.6f} 0.0 {:8.3f} {:8.3f} {:8.3f} 1.0 0.0 1 0.0 0.0;'.format (data['from'], 
      data['to'], data['r'], data['x'], rateA, rateB, rateC), file=fp)
  print ('];', file=fp)

  print ("""
%%-----  OPF Data  -----%%
%% generator cost data
%	1 startup shutdown n x1 y1 ... xn yn
%	2 startup shutdown n c(n-1) ... c0
mpc.gencost = [""", file=fp)
  for fuel in mpc_genfuels:
    c2, c1, c0 = get_gencosts(fuel)
    print ('  2 0 0 3 {:.7f} {:.3f} {:.3f};'.format (c2, c1, c0), file=fp)
  print ('];', file=fp)

  print ("""
%% generator unit type (see GENTYPES)
% use WT, PV, HY, ST, CT, ST for corresponding GENFUELS
% WT and PV will use WECC dynamics; the others will use Gov/Exc/PSS dynamics
mpc.gentype = {""", file=fp)
  for name in mpc_gentypes:
    print ("""  '{:s}';""".format(name), file=fp)
  print ('};', file=fp)

  print ("""
%% generator fuel type (see GENFUELS); use wind, solar, hydro, nuclear, ng, coal
mpc.genfuel = {""", file=fp)
  for name in mpc_genfuels:
    print ("""  '{:s}';""".format(name), file=fp)
  print ('};', file=fp)

  print ("""
%% bus names
mpc.bus_name = {""", file=fp)
  for name in mpc_bus_names:
    print ("""  '{:s}';""".format(name), file=fp)
  print ('};', file=fp)

#  print ("""
#%%-----  DC Line Data  -----%%
#%	fbus tbus status Pf Pt Qf Qt Vf Vt Pmin Pmax QminF QmaxF QminT QmaxT loss0 loss1 muPmin muPmax muQminF muQmaxF muQminT muQmaxT
#mpc.dcline = [""", file=fp)
#  print ('];', file=fp)

  print ('wrote {:d} generators totaling {:.2f} MW for loads totaling {:.2f} MW'.format(len(mpc_generators), total_gen, total_load))
  print ('suggest mpc = scale_load ({:.4f}, mpc)'.format(total_gen/total_load))

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile ('cimhubconfig.json')
  case_id = 0
  if len(sys.argv) > 1:
    case_id = int(sys.argv[1])
  sys_id = CASES[case_id]['id']
  sys_name = CASES[case_id]['name']
  fp = open (sys_name + '.m', 'w')

  d = cimhub.load_bes_dict ('qbes.xml', sys_id, bTime=False)
  cimhub.summarize_bes_dict (d)
#  cimhub.list_dict_table (d, 'BESContainer')
#  cimhub.list_dict_table (d, 'BESBaseVoltage')
#  cimhub.list_dict_table (d, 'BESWind')
#  cimhub.list_dict_table (d, 'BESSolar')
#  cimhub.list_dict_table (d, 'BESMachine')
#  cimhub.list_dict_table (d, 'BESPowerXfmrMesh')
#  cimhub.list_dict_table (d, 'BESBus')
#  cimhub.list_dict_table (d, 'BESCompShunt')

  build_matpower (d, sys_name, fp, CASES[case_id]['swingbus'])
  fp.close()

