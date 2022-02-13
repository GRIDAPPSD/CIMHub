from SPARQLWrapper import SPARQLWrapper2, JSON
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import time
import math
import xml.etree.ElementTree as ET
import pandas as pd

cases = [
  {'fid': '4BE6DD69-8FE9-4C9F-AD44-B327D5623974', 'fname': 'ieee13x.xlsx'},
  {'fid': '4C4E3E2C-6332-4DCB-8425-26B628178374', 'fname': 'ieee123x.xlsx'},
  {'fid': '1C9727D2-E4D2-4084-B612-90A44E1810FD', 'fname': 'j1red.xlsx'},
]

sparql = None
prefix = None
sqrt3 = math.sqrt(3.0)
rad_to_deg = 180.0 / math.pi
load_bandwidth = 0.12  # per-unit range for using ZIP coefficients, change to constant Z outside this range
DER_K_z = 0.0
DER_K_i = 100.0  # representing DER as constant current negative loads
DER_K_p = 0.0
mva_base = 100.0
xl_start_row = 10

def initialize_sparql (cfg_file=None):
  global sparql
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)

  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
  sparql.setReturnFormat(JSON)

def build_query (prefix, base, fid):
  idx = base.find('WHERE {') + 8
  retq = prefix + '\n' + base[:idx] + """ VALUES ?fdrid {{"_{:s}"}}\n""".format (fid) + base[idx:]
  return retq

def build_dict (ret):
  dict = {}
  vars = ret.variables
  keyfld = 'id'
  vars.remove(keyfld)
  for b in ret.bindings:
    key = b[keyfld].value
    row = {}
    for fld in vars:
      row[fld] = b[fld].value
    dict[key] = row
  return dict

def query_for_values (tbl, fid):
  keyflds = tbl['keyfld'].split(':')
  query = build_query (prefix, tbl['sparql'], fid)
  sparql.setQuery (query)
  ret = sparql.query()
  vars = ret.variables
  for akey in keyflds:
    vars.remove (akey)
  tbl['columns'] = vars
  for b in ret.bindings:
    row = {}
    key = b[keyflds[0]].value
    for i in range(1, len(keyflds)):
      key = key + ':' + b[keyflds[i]].value
    for fld in vars:
      if fld not in b:
        row[fld] = ''
      else:
        if fld in ['name', 'phases', 'bus', 'state', 'conn', 'fdrid', 'bus1', 'bus2']:
          row[fld] = b[fld].value
        else:
          try:
            row[fld] = int(b[fld].value)
          except ValueError:
            try:
              row[fld] = float(b[fld].value)
            except ValueError:
              row[fld] = b[fld].value

    tbl['vals'][key] = row

def summarize_dict (dict):
  print ('Query ID                       Key Field              Nrows Columns')
  lst = sorted(dict.keys())
  for key in lst:
    q = dict[key]
    print ('{:30s} {:21s} {:6d} {:s}'.format(key, str(q['keyfld']), len(q['vals']), str(q['columns'])))

def list_feeders (dict):
  print ('Feeder Name          FID')
  sparql.setQuery (prefix + dict['DistFeeder']['sparql'])
  ret = sparql.query()
  for b in ret.bindings:
    print ('{:20s} {:s}'.format (b['feeder'].value, b['fid'].value))

def list_table(dict, tag):
  tbl = dict[tag]
  print ('\n{:s}: key,{:s}'.format(tag, str(tbl['columns'])))
  for key, row in tbl['vals'].items():
    print ('{:s},{:s}'.format (key, ','.join(str(row[c]) for c in tbl['columns'])))

def load_feeder (dict, fid, bTime=True):
  for key in ['DistSolar', 'DistStorage', 'DistLoad', 'DistCapacitor', 'DistLinesSpacingZ', 'DistSubstation', 'DistBaseVoltage', 'DistFeeder',
              'DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser',
              'DistOverheadWire', 'DistConcentricNeutralCable', 'DistLineSpacing',
              'DistXfmrTank', 'DistXfmrBank', 'DistXfmrCodeRating', 'DistXfmrCodeNLTest', 'DistXfmrCodeSCTest',
              'DistCoordinates', 'DistRegulatorBanked', 'DistRegulatorTanked',
              'DistPowerXfmrCore', 'DistPowerXfmrMesh', 'DistSeriesCompensator',
              'DistPhaseMatrix', 'DistSequenceMatrix', 'DistLinesCodeZ', 'DistLinesInstanceZ', 'DistTapeShieldCable',
              'DistBus', 'DistPowerXfmrWinding']:

    start_time = time.time()
    query_for_values (dict[key], fid)
    if bTime:
      print ('Running {:30s} took {:6.3f} s'.format (key, time.time() - start_time))
  # remove all but fid from the list of feeders
  match_fid = '_' + fid
  delete = [key for key in dict['DistFeeder']['vals'] if dict['DistFeeder']['vals'][key]['fid'] != match_fid]
  for key in delete: 
    del dict['DistFeeder']['vals'][key]

def mark_all_device_phases (dict):
  for tbl in ['DistSubstation', 'DistSeriesCompensator', 'DistRegulatorBanked', 
              'DistLinesInstanceZ', 'DistPowerXfmrWinding']: # didn't query for phases, assume 3
    dict[tbl]['columns'].append('phases')
    for key, row in dict[tbl]['vals'].items():
      row['phases'] = 'ABC'
  for tbl in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser',
              'DistSolar', 'DistStorage', 'DistLoad', 'DistCapacitor', 'DistXfmrTank', 'DistRegulatorTanked',
              'DistLinesCodeZ', 'DistLinesSpacingZ']:
    for key, row in dict[tbl]['vals'].items():
      if len(row['phases']) < 1:
        row['phases'] = 'ABC'

def mark_one_bus_phases (busrow, phases):
  if 's1' in phases:
    busrow['phases'].add('s1')
  if 's2' in phases or 's12' in phases:
    busrow['phases'].add('s2')
  if 'A' in phases:
    busrow['phases'].add('A')
  if 'B' in phases:
    busrow['phases'].add('B')
  if 'C' in phases:
    busrow['phases'].add('C')

def mark_all_bus_phases (dict):
  busvals = dict['DistBus']['vals']
  dict['DistBus']['columns'].append('phases')
  for key in busvals:
    busvals[key]['nomv'] /= sqrt3
    busvals[key]['phases'] = set()
  for tbl in ['DistSolar', 'DistStorage', 'DistLoad', 'DistCapacitor', 'DistXfmrTank', 'DistSubstation', 'DistPowerXfmrWinding']:
    for key, row in dict[tbl]['vals'].items():
      mark_one_bus_phases (busvals[row['bus']], row['phases'])
  for tbl in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser',
              'DistLinesCodeZ', 'DistLinesSpacingZ', 'DistSeriesCompensator', 'DistLinesInstanceZ']:
    for key, row in dict[tbl]['vals'].items():
      mark_one_bus_phases (busvals[row['bus1']], row['phases'])
      mark_one_bus_phases (busvals[row['bus2']], row['phases'])

def add_comment_cell (xlw, sheet_name, startrow, txt):
  df = pd.DataFrame ([txt])
  df.to_excel (xlw, sheet_name = sheet_name, header=False, index=False, startrow=startrow)

def sequenced_phase_array (seqs):
  seqphs = sorted(seqs.split(':'))
  retval = []
  for e in seqphs:
    retval.append ('_' + e[1:])
  return retval

def phase_array (phases):
  retval = []
  for phs in ['A', 'B', 'C', 's1', 's2']:
    if phs in phases:
      retval.append ('_' + phs)
  return retval

def conn_string (cim_conn):
  if cim_conn == 'D':
    return 'delta'
  return 'wye'

def name_prefix (query_id):
  if query_id == 'DistSolar':
    return 'pv_'
  if query_id == 'DistStorage':
    return 'bat_'
  return ''

def append_phase_matrix (data, key, nphs, tbl):
  for i in range(nphs):
    for j in range(i+1):
      tok = '{:s}:{:d}:{:d}'.format (key, i+1, j+1)
      row = tbl[tok]
      data['r{:d}{:d} (Ohm/length_unit)'.format(i+1, j+1)].append (row['r'])
      data['x{:d}{:d} (Ohm/length_unit)'.format(i+1, j+1)].append (row['x'])
      data['b{:d}{:d} (uS/length_unit)'.format(i+1, j+1)].append (row['b']*1.0e6)

def winding_shift (clock_angle):
  if clock_angle == 0:
    return 0.0
  elif clock_angle == 1:
    return -30.0
  elif clock_angle == 11:
    return 30.0
  elif clock_angle == 10:
    return 60.0
  elif clock_angle == 9:
    return 90.0
  elif clock_angle == 8:
    return 120.0
  elif clock_angle == 7:
    return 150.0
  elif clock_angle == 6:
    return 180.0
  elif clock_angle == 5:
    return -150.0
  elif clock_angle == 4:
    return -120.0
  elif clock_angle == 3:
    return -90.0
  return -60.0 # 2

def write_ephasor_model (dict, filename):
  xlw = pd.ExcelWriter (filename)
  feeder_name = list(dict['DistFeeder']['vals'].keys())[0]
  mark_all_device_phases (dict)
  mark_all_bus_phases (dict)
  slack_buses = set()
  der_buses = set()

  df = pd.DataFrame ([['Excel file version', 'v2.0'], 
                      ['Name', feeder_name], 
                      ['Frequency (Hz)', 60], 
                      ['Power Base (MVA)', mva_base]])
  df.to_excel (xlw, sheet_name='General', header=False, index=False)

  # voltage sources, identify slack buses
  xlrow = xl_start_row
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Positive Sequence Voltage Source')
  data = {'ID':[], 'Bus':[], 'Voltage (pu)':[], 'Angle (deg)':[], 'Rs (pu)':[], 'Xs (pu)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df.index) + 2
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'End of Positive Sequence Voltage Source')
  xlrow += 2

  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Single-Phase Voltage Source')
  data = {'ID':[], 'Bus1':[], 'Voltage (V)':[], 'Angle (deg)':[], 'Rs (Ohm)':[], 'Xs (Ohm)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df.index) + 2
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'End of Single-Phase Voltage Source')
  xlrow += 2

  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Three-Phase Voltage Source with Short-Circuit Level Data')
  data = {'ID':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 'kV (ph-ph RMS)':[], 'Angle_a (deg)':[], 'SC1ph (MVA)':[], 'SC3ph (MVA)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df.index) + 2
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'End of Three-Phase Voltage Source with Short-Circuit Level Data')
  xlrow += 2

  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Three-Phase Voltage Source with Sequential Data')
  data = {'ID':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 'kV (ph-ph RMS)':[], 'Angle_a (deg)':[], 'R1 (Ohm)':[], 'X1 (Ohm)':[], 'R0 (Ohm)':[], 'X0 (Ohm)':[]}
  for key, row in dict['DistSubstation']['vals'].items():
    slack_buses.add (row['bus'])
    data['ID'].append(key)
    data['Bus1'].append(row['bus'] + '_A')
    data['Bus2'].append(row['bus'] + '_B')
    data['Bus3'].append(row['bus'] + '_C')
    data['kV (ph-ph RMS)'].append(row['vmag'] * 0.001)
    data['Angle_a (deg)'].append(row['vang'] * rad_to_deg)
    data['R1 (Ohm)'].append(row['r1'])
    data['X1 (Ohm)'].append(row['x1'])
    data['R0 (Ohm)'].append(row['r0'])
    data['X0 (Ohm)'].append(row['x0'])
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df.index) + 2
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'End of Three-Phase Voltage Source with Sequential Data')

  # Loads, plus DER as negative loads
  data1 = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  data2 = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  data3 = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  data4 = {'ID':[], 'Status':[], 'V (kV)':[], 'Bandwidth (pu)':[], 'Conn. type':[], 'K_z':[], 'K_i':[], 'K_p':[], 'Use initial voltage?':[],
           'Bus1':[], 'P1 (kW)':[], 'Q1 (kVAr)':[]}
  data5 = {'ID':[], 'Status':[], 'V (kV)':[], 'Bandwidth (pu)':[], 'Conn. type':[], 'K_z':[], 'K_i':[], 'K_p':[], 'Use initial voltage?':[],
           'Bus1':[], 'Bus2':[], 'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[]}
  data6 = {'ID':[], 'Status':[], 'V (kV)':[], 'Bandwidth (pu)':[], 'Conn. type':[], 'K_z':[], 'K_i':[], 'K_p':[], 'Use initial voltage?':[],
           'Bus1':[], 'Bus2':[], 'Bus3':[], 'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[], 'P3 (kW)':[], 'Q3 (kVAr)':[]}

  for key, row in dict['DistLoad']['vals'].items():
    aphs = phase_array (row['phases'])
    kv = 0.001 * row['basev']
    kw = 0.001 * row['p']
    kvar = 0.001 * row['q']
    conn = conn_string(row['conn'])
    if len(aphs) == 1:
      data4['ID'].append(key)
      data4['Status'].append(1)
      data4['V (kV)'].append(kv)
      data4['Bandwidth (pu)'].append(load_bandwidth)
      data4['Conn. type'].append(conn)
      data4['K_z'].append(row['pz'])
      data4['K_i'].append(row['pi'])
      data4['K_p'].append(row['pp'])
      data4['Use initial voltage?'].append(0)
      data4['Bus1'].append(row['bus'] + aphs[0])
      data4['P1 (kW)'].append(kw)
      data4['Q1 (kVAr)'].append(kvar)
    elif len(aphs) == 2:
      kvar /= 2.0
      kw /= 2.0
      data5['ID'].append(key)
      data5['Status'].append(1)
      data5['V (kV)'].append(kv)
      data5['Bandwidth (pu)'].append(load_bandwidth)
      data5['Conn. type'].append(conn)
      data5['K_z'].append(row['pz'])
      data5['K_i'].append(row['pi'])
      data5['K_p'].append(row['pp'])
      data5['Use initial voltage?'].append(0)
      data5['Bus1'].append(row['bus'] + aphs[0])
      data5['Bus2'].append(row['bus'] + aphs[1])
      data5['P1 (kW)'].append(kw)
      data5['Q1 (kVAr)'].append(kvar)
      data5['P2 (kW)'].append(kw)
      data5['Q2 (kVAr)'].append(kvar)
    elif len(aphs) == 3:
      kvar /= 3.0
      kw /= 3.0
      data6['ID'].append(key)
      data6['Status'].append(1)
      data6['V (kV)'].append(kv)
      data6['Bandwidth (pu)'].append(load_bandwidth)
      data6['Conn. type'].append(conn)
      data6['K_z'].append(row['pz'])
      data6['K_i'].append(row['pi'])
      data6['K_p'].append(row['pp'])
      data6['Use initial voltage?'].append(0)
      data6['Bus1'].append(row['bus'] + aphs[0])
      data6['Bus2'].append(row['bus'] + aphs[1])
      data6['Bus3'].append(row['bus'] + aphs[2])
      data6['P1 (kW)'].append(kw)
      data6['Q1 (kVAr)'].append(kvar)
      data6['P2 (kW)'].append(kw)
      data6['Q2 (kVAr)'].append(kvar)
      data6['P3 (kW)'].append(kw)
      data6['Q3 (kVAr)'].append(kvar)
  for der_tbl in ['DistSolar', 'DistStorage']:
    prefix = name_prefix (der_tbl)
    for key, row in dict[der_tbl]['vals'].items():
      der_buses.add (row['bus'])
      aphs = phase_array (row['phases'])
      kv = 0.001 * row['ratedU']
      kw = -0.001 * row['p']
      kvar = -0.001 * row['q']
      conn = 'wye'  # TODO - should be available from CIM?
      if len(aphs) == 1:
        data4['ID'].append(prefix + key)
        data4['Status'].append(1)
        data4['V (kV)'].append(kv)
        data4['Bandwidth (pu)'].append(load_bandwidth)
        data4['Conn. type'].append(conn)
        data4['K_z'].append(DER_K_z)
        data4['K_i'].append(DER_K_i)
        data4['K_p'].append(DER_K_p)
        data4['Use initial voltage?'].append(0)
        data4['Bus1'].append(row['bus'] + aphs[0])
        data4['P1 (kW)'].append(kw)
        data4['Q1 (kVAr)'].append(kvar)
      elif len(aphs) == 2:
        kvar /= 2.0
        kw /= 2.0
        data5['ID'].append(prefix + key)
        data5['Status'].append(1)
        data5['V (kV)'].append(kv)
        data5['Bandwidth (pu)'].append(load_bandwidth)
        data5['Conn. type'].append(conn)
        data5['K_z'].append(DER_K_z)
        data5['K_i'].append(DER_K_i)
        data5['K_p'].append(DER_K_p)
        data5['Use initial voltage?'].append(0)
        data5['Bus1'].append(row['bus'] + aphs[0])
        data5['Bus2'].append(row['bus'] + aphs[1])
        data5['P1 (kW)'].append(kw)
        data5['Q1 (kVAr)'].append(kvar)
        data5['P2 (kW)'].append(kw)
        data5['Q2 (kVAr)'].append(kvar)
      elif len(aphs) == 3:
        kvar /= 3.0
        kw /= 3.0
        data6['ID'].append(prefix + key)
        data6['Status'].append(1)
        data6['V (kV)'].append(kv)
        data6['Bandwidth (pu)'].append(load_bandwidth)
        data6['Conn. type'].append(conn)
        data6['K_z'].append(DER_K_z)
        data6['K_i'].append(DER_K_i)
        data6['K_p'].append(DER_K_p)
        data6['Use initial voltage?'].append(0)
        data6['Bus1'].append(row['bus'] + aphs[0])
        data6['Bus2'].append(row['bus'] + aphs[1])
        data6['Bus3'].append(row['bus'] + aphs[2])
        data6['P1 (kW)'].append(kw)
        data6['Q1 (kVAr)'].append(kvar)
        data6['P2 (kW)'].append(kw)
        data6['Q2 (kVAr)'].append(kvar)
        data6['P3 (kW)'].append(kw)
        data6['Q3 (kVAr)'].append(kvar)

  df1 = pd.DataFrame (data1)
  df2 = pd.DataFrame (data2)
  df3 = pd.DataFrame (data3)
  df4 = pd.DataFrame (data4)
  df5 = pd.DataFrame (data5)
  df6 = pd.DataFrame (data6)
  xlrow = xl_start_row
  add_comment_cell (xlw, 'Load', xlrow, 'Positive-Sequence Constant Imepedance Load') # replicating typo on the Opal-RT template
  df1.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of Positive Sequence Constant Imepedance Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Positive-Sequence Constant Power Load')
  df2.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of Positive Sequence Constant Power Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Positive-Sequence Constant Current Load')
  df3.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of Positive Sequence Constant Current Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Single-Phase ZIP Load')
  df4.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of SinglePhase ZIP Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Two-Phase ZIP Load')
  df5.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df5.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of TwoPhase ZIP Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Three-Phase ZIP Load')
  df6.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df6.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of ThreePhase ZIP Load')

  # shunts
  data1 = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  data2 = {'ID':[], 'Status':[], 'kV (ph-gr RMS)':[], 'Bus1':[], 'P1 (kW)':[], 'Q1 (kVAr)':[]}
  data3 = {'ID':[], 'Status1':[], 'Status2':[], 'kV (ph-gr RMS)':[], 'Bus1':[], 'Bus2':[], 'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[]}
  data4 = {'ID':[], 'Status1':[], 'Status2':[], 'Status3':[], 'kV (ph-gr RMS)':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 
          'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[], 'P3 (kW)':[], 'Q3 (kVAr)':[]}
  for key, row in dict['DistCapacitor']['vals'].items():
    aphs = phase_array (row['phases'])
    kv = 0.001 * row['nomu']
    kvar = 1000.0 * row['bsection'] * kv * kv
    if len(aphs) == 1:
      data2['ID'].append(key)
      data2['Status'].append(1)
      data2['kV (ph-gr RMS)'].append(kv)
      data2['Bus1'].append(row['bus'] + aphs[0])
      data2['P1 (kW)'].append(0.0)
      data2['Q1 (kVAr)'].append(kvar)
    elif len(aphs) == 2:
      kvar /= 2.0
      kv /= sqrt3
      data3['ID'].append(key)
      data3['Status1'].append(1)
      data3['Status2'].append(1)
      data3['kV (ph-gr RMS)'].append(kv)
      data3['Bus1'].append(row['bus'] + aphs[0])
      data3['Bus2'].append(row['bus'] + aphs[1])
      data3['P1 (kW)'].append(0.0)
      data3['Q1 (kVAr)'].append(kvar)
      data3['P2 (kW)'].append(0.0)
      data3['Q2 (kVAr)'].append(kvar)
    elif len(aphs) == 3:
      kvar /= 3.0
      kv /= sqrt3
      data4['ID'].append(key)
      data4['Status1'].append(1)
      data4['Status2'].append(1)
      data4['Status3'].append(1)
      data4['kV (ph-gr RMS)'].append(kv)
      data4['Bus1'].append(row['bus'] + aphs[0])
      data4['Bus2'].append(row['bus'] + aphs[1])
      data4['Bus3'].append(row['bus'] + aphs[2])
      data4['P1 (kW)'].append(0.0)
      data4['Q1 (kVAr)'].append(kvar)
      data4['P2 (kW)'].append(0.0)
      data4['Q2 (kVAr)'].append(kvar)
      data4['P3 (kW)'].append(0.0)
      data4['Q3 (kVAr)'].append(kvar)

  df1 = pd.DataFrame (data1)
  df2 = pd.DataFrame (data2)
  df3 = pd.DataFrame (data3)
  df4 = pd.DataFrame (data4)
  xlrow = xl_start_row
  add_comment_cell (xlw, 'Shunt', xlrow, 'Positive Sequence Shunt')
  df1.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Positive Sequence Shunt')
  xlrow += 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'Single-Phase Shunt')
  df2.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Single-Phase Shunt')
  xlrow += 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'Two-Phase Shunt')
  df3.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Two-Phase Shunt')
  xlrow += 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'Three-Phase Shunt')
  df4.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Three-Phase Shunt')

  # lines
  data1 = {'ID':[], 'Status':[], 'From bus':[], 'To bus':[], 'R (pu)':[], 'X (pu)':[], 'B (pu)':[]}
  data2 = {'ID':[], 'Status':[], 'Length':[], 
           'From1':[], 'To1':[], 
           'r11 (Ohm/length_unit)':[], 'x11 (Ohm/length_unit)':[], 'b11 (uS/length_unit)':[]}
  data3 = {'ID':[], 'Status':[], 'Length':[], 
           'From1':[], 'From2':[], 'To1':[], 'To2':[], 
           'r11 (Ohm/length_unit)':[], 'x11 (Ohm/length_unit)':[], 
           'r21 (Ohm/length_unit)':[], 'x21 (Ohm/length_unit)':[], 
           'r22 (Ohm/length_unit)':[], 'x22 (Ohm/length_unit)':[], 
           'b11 (uS/length_unit)':[], 'b21 (uS/length_unit)':[], 'b22 (uS/length_unit)':[]}
  data4 = {'ID':[], 'Status':[], 'Length':[], 
           'From1':[], 'From2':[], 'From3':[], 'To1':[], 'To2':[], 'To3':[], 
           'r11 (Ohm/length_unit)':[], 'x11 (Ohm/length_unit)':[], 
           'r21 (Ohm/length_unit)':[], 'x21 (Ohm/length_unit)':[], 
           'r22 (Ohm/length_unit)':[], 'x22 (Ohm/length_unit)':[], 
           'r31 (Ohm/length_unit)':[], 'x31 (Ohm/length_unit)':[], 
           'r32 (Ohm/length_unit)':[], 'x32 (Ohm/length_unit)':[], 
           'r33 (Ohm/length_unit)':[], 'x33 (Ohm/length_unit)':[], 
           'b11 (uS/length_unit)':[], 'b21 (uS/length_unit)':[], 'b22 (uS/length_unit)':[],
           'b31 (uS/length_unit)':[], 'b32 (uS/length_unit)':[], 'b33 (uS/length_unit)':[]}
  data5 = {'ID':[], 'Status':[], 'Length':[], 
           'From1':[], 'From2':[], 'From3':[], 'To1':[], 'To2':[], 'To3':[], 
           'R0 (Ohm/length_unit)':[], 'X0 (Ohm/length_unit)':[], 
           'R1 (Ohm/length_unit)':[], 'X1 (Ohm/length_unit)':[], 
           'B0 (uS/length_unit)':[], 'B1 (uS/length_unit)':[]}
  for key, row in dict['DistLinesCodeZ']['vals'].items():
    aphs = sequenced_phase_array (row['seqs'])
    kv = 0.001 * row['basev']
    if len(aphs) == 1:
      data2['ID'].append(key)
      data2['Status'].append(1)
      data2['Length'].append(row['len'])
      data2['From1'].append(row['bus1'] + aphs[0])
      data2['To1'].append(row['bus2'] + aphs[0])
      append_phase_matrix (data2, row['lname'], 1, dict['DistPhaseMatrix']['vals'])
    elif len(aphs) == 2:
      data3['ID'].append(key)
      data3['Status'].append(1)
      data3['Length'].append(row['len'])
      data3['From1'].append(row['bus1'] + aphs[0])
      data3['To1'].append(row['bus2'] + aphs[0])
      data3['From2'].append(row['bus1'] + aphs[1])
      data3['To2'].append(row['bus2'] + aphs[1])
      append_phase_matrix (data3, row['lname'], 2, dict['DistPhaseMatrix']['vals'])
    elif len(aphs) == 3:
      data4['ID'].append(key)
      data4['Status'].append(1)
      data4['Length'].append(row['len'])
      data4['From1'].append(row['bus1'] + aphs[0])
      data4['To1'].append(row['bus2'] + aphs[0])
      data4['From2'].append(row['bus1'] + aphs[1])
      data4['To2'].append(row['bus2'] + aphs[1])
      data4['From3'].append(row['bus1'] + aphs[2])
      data4['To3'].append(row['bus2'] + aphs[2])
      append_phase_matrix (data4, row['lname'], 3, dict['DistPhaseMatrix']['vals'])

  df1 = pd.DataFrame (data1)
  df2 = pd.DataFrame (data2)
  df3 = pd.DataFrame (data3)
  df4 = pd.DataFrame (data4)
  df5 = pd.DataFrame (data5)
  xlrow = xl_start_row
  add_comment_cell (xlw, 'Line', xlrow, 'Positive-Sequence Line')
  df1.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Positive-Sequence Line')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Single-Phase Line')
  df2.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Single-Phase Line')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Two-Phase Line')
  df3.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Two-Phase Line')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Three-Phase Line with Full Data')
  df4.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Three-Phase Line with Full Data')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Three-Phase Line with Sequential Data')
  df5.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df5.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Three-Phase Line with Sequential Data')

  # transformers
  data1 = {'ID':[], 'Status':[], 'From bus':[], 'To bus':[], 'R (pu)':[], 'Xl (pu)':[], 'Gmag (pu)':[], 'Bmag (pu)':[],
           'Ratio W1 (pu)':[], 'Ratio W2 (pu)':[], 'Phase Shift (deg)':[]}
  data2 = {'ID':[], 'Status':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 
           'R_12 (pu)':[], 'Xl_12 (pu)':[], 'R_23 (pu)':[], 'Xl_23 (pu)':[], 'R_31 (pu)':[], 'Xl_31 (pu)':[], 'Gmag (pu)':[], 'Bmag (pu)':[],
           'Ratio W1 (pu)':[], 'Ratio W2 (pu)':[], 'Ratio W3 (pu)':[], 
           'Phase Shift W1 (deg)':[], 'Phase Shift W2 (deg)':[], 'Phase Shift W3 (deg)':[]}
  data3 = {'ID':[], 'Status':[], 'Number of phases':[], 
           'Bus1_A':[], 'Bus1_B':[], 'Bus1_C':[], 'V1 (kV)':[], 'S_base1 (kVA)':[], 'Conn. type1':[],
           'Bus2_A':[], 'Bus2_B':[], 'Bus2_C':[], 'V2 (kV)':[], 'S_base2 (kVA)':[], 'Conn. type2':[],
           'Tap 1':[], 'Tap 2':[], 'Tap 3':[], 'Lowest Tap':[], 'Highest Tap':[], 'Min Range (%)':[], 'Max Range (%)':[], 
           'X (pu)':[], 'RW1 (pu)':[], 'RW2 (pu)':[]}
  data4 = {'ID':[], 'Status':[], 'Number of phases':[], 
           'Bus1_A':[], 'Bus1_B':[], 'Bus1_C':[], 'V1 (kV)':[], 'S_base1 (kVA)':[], 'Conn. type1':[],
           'Bus2_A':[], 'Bus2_B':[], 'Bus2_C':[], 'V2 (kV)':[], 'S_base2 (kVA)':[], 'Conn. type2':[],
           'Tap 1':[], 'Tap 2':[], 'Tap 3':[], 'Lowest Tap':[], 'Highest Tap':[], 'Min Range (%)':[], 'Max Range (%)':[], 
           'Z0 leakage (pu)':[], 'Z1 leakage (pu)':[], 'X0/R0':[], 'X1/R1':[], 'No Load Loss (kW)':[]}

  # balanced PowerTransformer instances can be represented as positive-sequence 2W or 3W
  XfmrWindingCount = {}
  for key in dict['DistPowerXfmrWinding']['vals']:
    pname = key.split(':')[0]
    if pname in XfmrWindingCount:
      XfmrWindingCount[pname] += 1
    else:
      XfmrWindingCount[pname] = 1
  for pname, nwdg in XfmrWindingCount.items():
    if nwdg == 2:
      wdg1 = dict['DistPowerXfmrWinding']['vals']['{:s}:1'.format(pname)]
      wdg2 = dict['DistPowerXfmrWinding']['vals']['{:s}:2'.format(pname)]
      z12 = dict['DistPowerXfmrMesh']['vals']['{:s}:1:2'.format(pname)]
      ym = dict['DistPowerXfmrCore']['vals'][pname]
      zbase = wdg1['ratedU'] * wdg1['ratedU'] / wdg1['ratedS']
      tap1 = 0
      tap2 = 0
      tap3 = 0
      lowtap = -16
      hightap = -16
      maxboost = 10.0
      maxbuck = 10.0
      # this balanced 2W version cannot be mixed with multi-phase models in ePHASORSIM
#     data1['ID'].append(pname)
#     data1['Status'].append(1)
#     data1['From bus'].append(wdg1['bus'])
#     data1['To bus'].append(wdg2['bus'])
#     data1['R (pu)'].append(z12['r']/zbase)
#     data1['Xl (pu)'].append(z12['x']/zbase)
#     if ym['enum'] == 2:
#       zbase = wdg2['ratedU'] * wdg2['ratedU'] / wdg2['ratedS']
#     data1['Gmag (pu)'].append(ym['g']*zbase)
#     data1['Bmag (pu)'].append(ym['b']*zbase)
#     data1['Ratio W1 (pu)'].append(1.0)
#     data1['Ratio W2 (pu)'].append(1.0)
#     data1['Phase Shift (deg)'].append(winding_shift (wdg2['ang']))
      # 2W multi-phase; no place for the core admittance
      aphs = phase_array ('ABC')
      if ym['g'] <= 0.0:
        dxf = data3
        xpu = z12['x']/zbase
        rpu = 0.5 * z12['r']/zbase
        data3['X (pu)'].append(xpu)
        data3['RW1 (pu)'].append(rpu)
        data3['RW2 (pu)'].append(rpu)
      else:
        dxf = data4
        xpu = z12['x']/zbase
        rpu = z12['r']/zbase
        if rpu <= 0.0:
          rpu = 0.001 * xpu
        zpu = math.sqrt(rpu*rpu + xpu*xpu)
        xr = xpu/rpu
        if ym['enum'] == 1:
          kw = 0.001 * ym['g'] * wdg1['ratedU'] * wdg1['ratedU']
        else:
          kw = 0.001 * ym['g'] * wdg2['ratedU'] * wdg2['ratedU']
        data4['Z1 leakage (pu)'].append(zpu)
        data4['Z0 leakage (pu)'].append(zpu)
        data4['X1/R1'].append(xr)
        data4['X0/R0'].append(xr)
        data4['No Load Loss (kW)'].append(kw)
      dxf['ID'].append(pname)
      dxf['Status'].append(1)
      dxf['Number of phases'].append(len(aphs))
      dxf['Bus1_A'].append(wdg1['bus'] + aphs[0])
      dxf['Bus1_B'].append(wdg1['bus'] + aphs[1])
      dxf['Bus1_C'].append(wdg1['bus'] + aphs[2])
      dxf['Bus2_A'].append(wdg2['bus'] + aphs[0])
      dxf['Bus2_B'].append(wdg2['bus'] + aphs[1])
      dxf['Bus2_C'].append(wdg2['bus'] + aphs[2])
      dxf['V1 (kV)'].append(wdg1['ratedU'] * 0.001)
      dxf['S_base1 (kVA)'].append(wdg1['ratedS'] * 0.001)
      dxf['Conn. type1'].append(conn_string(wdg1['conn']))
      dxf['V2 (kV)'].append(wdg2['ratedU'] * 0.001)
      dxf['S_base2 (kVA)'].append(wdg2['ratedS'] * 0.001)
      dxf['Conn. type2'].append(conn_string(wdg2['conn']))
      dxf['Tap 1'].append(tap1)
      dxf['Tap 2'].append(tap2)
      dxf['Tap 3'].append(tap3)
      dxf['Lowest Tap'].append(lowtap)
      dxf['Highest Tap'].append(hightap)
      dxf['Min Range (%)'].append(maxbuck)
      dxf['Max Range (%)'].append(maxboost)
    elif nwdg == 3:
      wdg1 = dict['DistPowerXfmrWinding']['vals']['{:s}:1'.format(pname)]
      wdg2 = dict['DistPowerXfmrWinding']['vals']['{:s}:2'.format(pname)]
      wdg3 = dict['DistPowerXfmrWinding']['vals']['{:s}:3'.format(pname)]
      z12 = dict['DistPowerXfmrMesh']['vals']['{:s}:1:2'.format(pname)]
      z13 = dict['DistPowerXfmrMesh']['vals']['{:s}:1:3'.format(pname)]
      z23 = dict['DistPowerXfmrMesh']['vals']['{:s}:2:3'.format(pname)]
      z12base = wdg1['ratedU'] * wdg1['ratedU'] / wdg1['ratedS'] # TODO - check these against the Java code
      z13base = wdg1['ratedU'] * wdg1['ratedU'] / wdg1['ratedS']
      z23base = wdg2['ratedU'] * wdg2['ratedU'] / wdg2['ratedS']
      ym = dict['DistPowerXfmrCore']['vals'][pname]
      data2['ID'].append(pname)
      data2['Status'].append(1)
      data2['Bus1'].append(wdg1['bus'])
      data2['Bus2'].append(wdg2['bus'])
      data2['Bus3'].append(wdg3['bus'])
      data2['R_12 (pu)'].append(z12['r']/z12base)
      data2['Xl_12 (pu)'].append(z12['x']/z12base)
      data2['R_23 (pu)'].append(z23['r']/z23base)
      data2['Xl_23 (pu)'].append(z23['x']/z23base)
      data2['R_31 (pu)'].append(z13['r']/z13base)
      data2['Xl_31 (pu)'].append(z13['x']/z13base)
      zybase = z12base
      if ym['enum'] == 2:
        zybase = wdg2['ratedU'] * wdg2['ratedU'] / wdg2['ratedS']
      elif ym['enum'] == 3:
        zybase = wdg3['ratedU'] * wdg3['ratedU'] / wdg3['ratedS']
      data2['Gmag (pu)'].append(ym['g']*zybase)
      data2['Bmag (pu)'].append(ym['b']*zybase)
      data2['Ratio W1 (pu)'].append(1.0)
      data2['Ratio W2 (pu)'].append(1.0)
      data2['Ratio W3 (pu)'].append(1.0)
      data2['Phase Shift W1 (deg)'].append(winding_shift (wdg1['ang']))
      data2['Phase Shift W2 (deg)'].append(winding_shift (wdg2['ang']))
      data2['Phase Shift W3 (deg)'].append(winding_shift (wdg3['ang']))
      print ('*** PowerTransformer {:s} has 3 windings, exported as 3W positive sequence, which cannot be mixed with multi-phase models.\n'.format (pname),
             '   Suggest editing the original model to use 2W transformer(s) here.')
    else:
      print ('*** PowerTransformer {:s} has {:d} windings, which is not supported in this conversion'.format (pname, nwdg))

  # each transformer bank is an unbalanced transformer; need to list its tanks and count its phases
  XfmrBanks = {}
  for key, row in dict['DistXfmrBank']['vals'].items():
    keys = key.split(':')
    pname = keys[0]
    tname = keys[1]
    vgrp = row['vgrp'].upper()
    if pname not in XfmrBanks:
      XfmrBanks[pname] = {'tanks': [], 'nphs': 1}
    XfmrBanks[pname]['tanks'].append(tname)
    if 'Y' in vgrp or 'D' in vgrp:
      XfmrBanks[pname]['nphs'] = 3
  # also need the number of windings and list of phases on each XfmrTank, for ePHASORSIM, s1 and s2 are supplanted by the primary phase
  XfmrTanks = {}
  for key, row in dict['DistXfmrTank']['vals'].items():
    keys = key.split(':')
    pname = keys[0]
    tname = keys[1]
    enum = int(keys[2])
    phases = row['phases']
    if tname not in XfmrTanks:
      XfmrTanks[tname] = {'nwdg': 0, 'phases': set()}
    XfmrTanks[tname]['nwdg'] += 1
    if 'A' in phases:
      XfmrTanks[tname]['phases'].add('A')
    if 'B' in phases:
      XfmrTanks[tname]['phases'].add('B')
    if 'C' in phases:
      XfmrTanks[tname]['phases'].add('C')

  # now write the banked transformers as 2W multi-phase
  for pname, row in XfmrBanks.items():
    if len(row['tanks']) > 1:
      print ('*** PowerTransformer {:s} has {:d} tanks; only using impedances and ratings from the first'.format (pname, len(row['tanks'])))
    dxf = data3

#    dxf['ID'].append(pname)
#    dxf['Status'].append(1)
#    dxf['Number of phases'].append(row['nphs'])
#   dxf['Bus1_A'].append(wdg1['bus'] + aphs[0])
#   dxf['Bus1_B'].append(wdg1['bus'] + aphs[1])
#   dxf['Bus1_C'].append(wdg1['bus'] + aphs[2])
#   dxf['Bus2_A'].append(wdg2['bus'] + aphs[0])
#   dxf['Bus2_B'].append(wdg2['bus'] + aphs[1])
#   dxf['Bus2_C'].append(wdg2['bus'] + aphs[2])

  df1 = pd.DataFrame (data1)
  df2 = pd.DataFrame (data2)
  df3 = pd.DataFrame (data3)
  df4 = pd.DataFrame (data4)
  xlrow = xl_start_row
  add_comment_cell (xlw, 'Transformer', xlrow, 'Positive-Sequence 2W Transformer')
  df1.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Positive-Sequence 2W Transformer')
  xlrow += 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'Positive-Sequence 3W Transformer')
  df2.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Positive-Sequence 3W Transformer')
  xlrow += 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'Multiphase 2W Transformer')
  df3.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Multiphase 2W Transformer')
  xlrow += 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'Multiphase 2W Transformer with Mutual Impedance')
  df4.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Multiphase 2W Transformer with Mutual Impedance')

  # buses
  data = {'Bus':[], 'Base Voltage (V)':[], 'Initial Vmag':[], 'Unit (V, pu)':[], 'Angle (deg)':[], 'Type':[]}
  for key, row in dict['DistBus']['vals'].items():
    if key in slack_buses:
      bustype = 'SLACK'
    elif key in der_buses:
      bustype = 'PQ' # not 'PV'
    else:
      bustype = 'PQ'
    for phs in row['phases']:
      angle = 0.0
      busname = '{:s}_{:s}'.format (key, phs)
      if phs == 'B':
        angle = -120.0
      elif phs == 'C':
        angle = 120.0
      elif phs == 's2':
        angle = 180.0
      data['Bus'].append(busname)
      data['Base Voltage (V)'].append(row['nomv'])
      data['Initial Vmag'].append(1.0)
      data['Unit (V, pu)'].append('pu')
      data['Angle (deg)'].append(angle)
      data['Type'].append(bustype)
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Bus', header=True, index=False)

  # switches
  data = {'From Bus':[], 'To Bus':[], 'ID':[], 'Status':[]}
  for tag in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser']:
    tbl = dict[tag]
    for key, row in tbl['vals'].items():
      for phs in row['phases']:
        ext = '_' + phs
        data['ID'].append (key + ext)
        data['From Bus'].append (row['bus1'] + ext)
        data['To Bus'].append (row['bus2'] + ext)
        if row['open'] == 'true':
          data['Status'].append(0)
        else:
          data['Status'].append(1)
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Switch', header=True, index=False)

  xlw.save()

  print ('DER at buses', der_buses)

if __name__ == '__main__':
  cfg_file = 'cimhubconfig.json'
  case_id = 0
#  if len(sys.argv) > 1:
#    cfg_file = sys.argv[1]
  if len(sys.argv) > 1:
    case_id = int(sys.argv[1])
  fid = cases[case_id]['fid']
  fname = cases[case_id]['fname']

  initialize_sparql (cfg_file)

  # read the queries into dict
  tree = ET.parse('../q100.xml')
  root = tree.getroot()
  nsCIM = root.find('nsCIM').text.strip()
  nsRDF = root.find('nsRDF').text.strip()
  prefix = """PREFIX r: <{:s}>\nPREFIX c: <{:s}>""".format (nsRDF, nsCIM)
  dict = {}
  for query in root.findall('query'):
    qid = query.find('id').text.strip()
    dict[qid] = {}
    dict[qid]['keyfld'] = query.find('keyfld').text
    dict[qid]['sparql'] = query.find('value').text.strip()
    dict[qid]['columns'] = []
    dict[qid]['vals'] = {}

  load_feeder (dict, fid, bTime=False)
  summarize_dict (dict)

  write_ephasor_model (dict, fname)

#  list_table (dict, 'DistPowerXfmrWinding')
#  list_table (dict, 'DistRegulatorBanked')
  list_table (dict, 'DistXfmrBank')
  list_table (dict, 'DistXfmrTank')
  list_table (dict, 'DistXfmrCodeRating')
  list_table (dict, 'DistXfmrCodeSCTest')
  list_table (dict, 'DistXfmrCodeNLTest')
  list_table (dict, 'DistRegulatorTanked')
  for tbl in ['DistLinesInstanceZ', 'DistLinesSpacingZ', 'DistSequenceMatrix', 'DistRegulatorBanked', 'DistRegulatorTanked',
              'DistXfmrBank', 'DistSyncMachine']:
    if len(dict[tbl]['vals']) > 0:
      print ('**** {:s} used in the circuit; but not implemented'.format (tbl))

