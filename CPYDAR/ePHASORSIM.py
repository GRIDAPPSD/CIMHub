from SPARQLWrapper import SPARQLWrapper2, JSON
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import time
import math
import xml.etree.ElementTree as ET
import pandas as pd

sparql = None
prefix = None

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
  print ('{:s}: key,{:s}'.format(tag, str(tbl['columns'])))
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
  sqrt3 = math.sqrt(3.0)
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

def write_ephasor_model (dict, filename):
  rad_to_deg = 180.0 / math.pi
  xlw = pd.ExcelWriter (filename)
  feeder_name = list(dict['DistFeeder']['vals'].keys())[0]
  mark_all_device_phases (dict)
  mark_all_bus_phases (dict)
  slack_buses = set()
  der_buses = set()

  df = pd.DataFrame ([['Excel file version', 'v2.0'], 
                      ['Name', feeder_name], 
                      ['Frequency (Hz)', 60], 
                      ['Power Base (MVA)', 100]])
  df.to_excel (xlw, sheet_name='General', header=False, index=False)

  # voltage sources, identify slack buses
  add_comment_cell (xlw, 'Voltage Source', 10, 'Positive Sequence Voltage Source')
  data = {'ID':[], 'Bus':[], 'Voltage (pu)':[], 'Angle (deg)':[], 'Rs (pu)':[], 'Xs (pu)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=11)
  add_comment_cell (xlw, 'Voltage Source', 12, 'End of Positive Sequence Voltage Source')

  add_comment_cell (xlw, 'Voltage Source', 14, 'Single-Phase Voltage Source')
  data = {'ID':[], 'Bus1':[], 'Voltage (V)':[], 'Angle (deg)':[], 'Rs (Ohm)':[], 'Xs (Ohm)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=15)
  add_comment_cell (xlw, 'Voltage Source', 16, 'End of Single-Phase Voltage Source')

  add_comment_cell (xlw, 'Voltage Source', 18, 'Three-Phase Voltage Source with Short-Circuit Level Data')
  data = {'ID':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 'kV (ph-ph RMS)':[], 'Angle_a (deg)':[], 'SC1ph (MVA)':[], 'SC3ph (MVA)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=19)
  add_comment_cell (xlw, 'Voltage Source', 20, 'End of Three-Phase Voltage Source with Short-Circuit Level Data')

  add_comment_cell (xlw, 'Voltage Source', 22, 'Three-Phase Voltage Source with Sequential Data')
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
#    zbase = row['nomv']*row['nomv'] / 100.0e6
#    data['Rs (pu)'].append(row['r1']/zbase)
#    data['Xs (pu)'].append(row['r1']/zbase)
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=23)
  add_comment_cell (xlw, 'Voltage Source', 24 + len(df.index), 'End of Three-Phase Voltage Source with Sequential Data')

  # Loads, plus DER as negative loads
  add_comment_cell (xlw, 'Load', 10, 'Positive-Sequence Constant Imepedance Load') # replicating typo on the Opal-RT template
  data = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=11)
  add_comment_cell (xlw, 'Load', 12, 'End of Positive Sequence Constant Imepedance Load')

  add_comment_cell (xlw, 'Load', 14, 'Positive-Sequence Constant Power Load')
  data = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=15)
  add_comment_cell (xlw, 'Load', 16, 'End of Positive Sequence Constant Power Load')

  add_comment_cell (xlw, 'Load', 18, 'Positive-Sequence Constant Current Load')
  data = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=19)
  add_comment_cell (xlw, 'Load', 20, 'End of Positive Sequence Constant Current Load')

  add_comment_cell (xlw, 'Load', 22, 'Single-Phase ZIP Load')
  data = {'ID':[], 'Status':[], 'V (kV)':[], 'Bandwidth (pu)':[], 'Conn. type':[], 'K_z':[], 'K_i':[], 'K_p':[], 'Use initial voltage?':[],
          'Bus1':[], 'P1 (kW)':[], 'Q1 (kVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=23)
  add_comment_cell (xlw, 'Load', 24, 'End of SinglePhase ZIP Load')

  add_comment_cell (xlw, 'Load', 26, 'Two-Phase ZIP Load')
  data = {'ID':[], 'Status':[], 'V (kV)':[], 'Bandwidth (pu)':[], 'Conn. type':[], 'K_z':[], 'K_i':[], 'K_p':[], 'Use initial voltage?':[],
          'Bus1':[], 'Bus2':[], 'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=27)
  add_comment_cell (xlw, 'Load', 28, 'End of TwoPhase ZIP Load')

  add_comment_cell (xlw, 'Load', 30, 'Three-Phase ZIP Load')
  data = {'ID':[], 'Status':[], 'V (kV)':[], 'Bandwidth (pu)':[], 'Conn. type':[], 'K_z':[], 'K_i':[], 'K_p':[], 'Use initial voltage?':[],
          'Bus1':[], 'Bus2':[], 'Bus3':[], 'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[], 'P3 (kW)':[], 'Q3 (kVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=31)
  add_comment_cell (xlw, 'Load', 32, 'End of ThreePhase ZIP Load')

  for key, row in dict['DistSolar']['vals'].items():
    der_buses.add (row['bus'])
  for key, row in dict['DistStorage']['vals'].items():
    der_buses.add (row['bus'])

  # shunts
  add_comment_cell (xlw, 'Shunt', 10, 'Positive Sequence Shunt')
  data = {'ID':[], 'Status':[], 'Bus':[], 'P (MW)':[], 'Q (MVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=11)
  add_comment_cell (xlw, 'Shunt', 12, 'End of Positive Sequence Shunt')

  add_comment_cell (xlw, 'Shunt', 14, 'Single-Phase Shunt')
  data = {'ID':[], 'Status':[], 'kV (ph-gr RMS)':[], 'Bus1':[], 'P1 (kW)':[], 'Q1 (kVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=15)
  add_comment_cell (xlw, 'Shunt', 16, 'End of Single-Phase Shunt')

  add_comment_cell (xlw, 'Shunt', 18, 'Two-Phase Shunt')
  data = {'ID':[], 'Status1':[], 'Status2':[], 'kV (ph-gr RMS)':[], 'Bus1':[], 'Bus2':[], 'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=19)
  add_comment_cell (xlw, 'Shunt', 20, 'End of Two-Phase Shunt')

  add_comment_cell (xlw, 'Shunt', 22, 'Three-Phase Shunt')
  data = {'ID':[], 'Status1':[], 'Status2':[], 'Status3':[], 'kV (ph-gr RMS)':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 
          'P1 (kW)':[], 'Q1 (kVAr)':[], 'P2 (kW)':[], 'Q2 (kVAr)':[], 'P3 (kW)':[], 'Q3 (kVAr)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=23)
  add_comment_cell (xlw, 'Shunt', 24, 'End of Three-Phase Shunt')

  # lines
  add_comment_cell (xlw, 'Line', 10, 'Positive-Sequence Line')
  data = {'ID':[], 'Status':[], 'From bus':[], 'To bus':[], 'R (pu)':[], 'X (pu)':[], 'B (pu)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=11)
  add_comment_cell (xlw, 'Line', 12, 'End of Positive-Sequence Line')

  add_comment_cell (xlw, 'Line', 14, 'Single-Phase Line')
  data = {'ID':[], 'Status':[], 'Length':[], 
          'From1':[], 'To1':[], 
          'r11 (Ohm/length_unit)':[], 'x11 (Ohm/length_unit)':[], 'b11 (uS/length_unit)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=15)
  add_comment_cell (xlw, 'Line', 16, 'End of Single-Phase Line')

  add_comment_cell (xlw, 'Line', 18, 'Two-Phase Line')
  data = {'ID':[], 'Status':[], 'Length':[], 
          'From1':[], 'From2':[], 'To1':[], 'To2':[], 
          'r11 (Ohm/length_unit)':[], 'x11 (Ohm/length_unit)':[], 
          'r21 (Ohm/length_unit)':[], 'x21 (Ohm/length_unit)':[], 
          'r22 (Ohm/length_unit)':[], 'x22 (Ohm/length_unit)':[], 
          'b11 (uS/length_unit)':[], 'b21 (uS/length_unit)':[], 'b22 (uS/length_unit)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=19)
  add_comment_cell (xlw, 'Line', 20, 'End of Two-Phase Line')

  add_comment_cell (xlw, 'Line', 22, 'Three-Phase Line with Full Data')
  data = {'ID':[], 'Status':[], 'Length':[], 
          'From1':[], 'From2':[], 'From3':[], 'To1':[], 'To2':[], 'To3':[], 
          'r11 (Ohm/length_unit)':[], 'x11 (Ohm/length_unit)':[], 
          'r21 (Ohm/length_unit)':[], 'x21 (Ohm/length_unit)':[], 
          'r22 (Ohm/length_unit)':[], 'x22 (Ohm/length_unit)':[], 
          'r31 (Ohm/length_unit)':[], 'x31 (Ohm/length_unit)':[], 
          'r32 (Ohm/length_unit)':[], 'x32 (Ohm/length_unit)':[], 
          'r33 (Ohm/length_unit)':[], 'x33 (Ohm/length_unit)':[], 
          'b11 (uS/length_unit)':[], 'b21 (uS/length_unit)':[], 'b22 (uS/length_unit)':[],
          'b31 (uS/length_unit)':[], 'b32 (uS/length_unit)':[], 'b33 (uS/length_unit)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=23)
  add_comment_cell (xlw, 'Line', 24, 'End of Three-Phase Line with Full Data')

  add_comment_cell (xlw, 'Line', 26, 'Three-Phase Line with Sequential Data')
  data = {'ID':[], 'Status':[], 'Length':[], 
          'From1':[], 'From2':[], 'From3':[], 'To1':[], 'To2':[], 'To3':[], 
          'R0 (Ohm/length_unit)':[], 'X0 (Ohm/length_unit)':[], 
          'R1 (Ohm/length_unit)':[], 'X1 (Ohm/length_unit)':[], 
          'B0 (uS/length_unit)':[], 'B1 (uS/length_unit)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=27)
  add_comment_cell (xlw, 'Line', 28, 'End of Three-Phase Line with Sequential Data')

  # transformers
  add_comment_cell (xlw, 'Transformer', 10, 'Positive-Sequence 2W Transformer')
  data = {'ID':[], 'Status':[], 'From bus':[], 'To bus':[], 'R (pu)':[], 'Xl (pu)':[], 'Gmag (pu)':[], 'Bmag (pu)':[],
          'Ratio W1 (pu)':[], 'Ratio W2 (pu)':[], 'Phase Shift (deg)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=11)
  add_comment_cell (xlw, 'Transformer', 12, 'End of Positive-Sequence 2W Transformer')

  add_comment_cell (xlw, 'Transformer', 14, 'Positive-Sequence 3W Transformer')
  data = {'ID':[], 'Status':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 
          'R_12 (pu)':[], 'Xl_12 (pu)':[], 'R_23 (pu)':[], 'Xl_23 (pu)':[], 'R_31 (pu)':[], 'Xl_31 (pu)':[], 'Gmag (pu)':[], 'Bmag (pu)':[],
          'Ratio W1 (pu)':[], 'Ratio W2 (pu)':[], 'Ratio W3 (pu)':[], 
          'Phase Shift W1 (deg)':[], 'Phase Shift W2 (deg)':[], 'Phase Shift W3 (deg)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=15)
  add_comment_cell (xlw, 'Transformer', 16, 'End of Positive-Sequence 3W Transformer')

  add_comment_cell (xlw, 'Transformer', 18, 'Multiphase 2W Transformer')
  data = {'ID':[], 'Status':[], 'Number of phases':[], 
          'Bus1_A':[], 'Bus1_B':[], 'Bus1_C':[], 'V1 (kV)':[], 'S_base1 (kVA)':[], 'Conn. type1':[],
          'Bus2_A':[], 'Bus2_B':[], 'Bus2_C':[], 'V2 (kV)':[], 'S_base2 (kVA)':[], 'Conn. type2':[],
          'Tap 1':[], 'Tap 2':[], 'Tap 3':[], 'Lowest Tap':[], 'Highest Tap':[], 'Min Range (%)':[], 'Max Range (%)':[], 
          'X (pu)':[], 'RW1 (pu)':[], 'RW2':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=19)
  add_comment_cell (xlw, 'Transformer', 20, 'End of Multiphase 2W Transformer')

  add_comment_cell (xlw, 'Transformer', 22, 'Multiphase 2W Transformer with Mutual Impedance')
  data = {'ID':[], 'Status':[], 'Number of phases':[], 
          'Bus1_A':[], 'Bus1_B':[], 'Bus1_C':[], 'V1 (kV)':[], 'S_base1 (kVA)':[], 'Conn. type1':[],
          'Bus2_A':[], 'Bus2_B':[], 'Bus2_C':[], 'V2 (kV)':[], 'S_base2 (kVA)':[], 'Conn. type2':[],
          'Tap 1':[], 'Tap 2':[], 'Tap 3':[], 'Lowest Tap':[], 'Highest Tap':[], 'Min Range (%)':[], 'Max Range (%)':[], 
          'Z0 leakage (pu)':[], 'Z1 leakage (pu)':[], 'X0/R0':[], 'X1/R1':[], 'No Load Loss (kW)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=23)
  add_comment_cell (xlw, 'Transformer', 24, 'End of Multiphase 2W Transformer with Mutual Impedance')

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

if __name__ == '__main__':
  cfg_file = 'cimhubconfig.json'
  if len(sys.argv) > 1:
    cfg_file = sys.argv[1]
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

  fid = '4BE6DD69-8FE9-4C9F-AD44-B327D5623974'  # ieee13x
#  fid = '4C4E3E2C-6332-4DCB-8425-26B628178374'  # ieee123x
#  fid = '1C9727D2-E4D2-4084-B612-90A44E1810FD'  # j1red
#  list_feeders (dict)
  load_feeder (dict, fid, bTime=False)
  summarize_dict (dict)

  write_ephasor_model (dict, 'ieee13x.xlsx')

  list_table (dict, 'DistSubstation')

