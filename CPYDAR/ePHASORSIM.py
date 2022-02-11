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

  # DER
  for key, row in dict['DistSolar']['vals'].items():
    der_buses.add (row['bus'])
  for key, row in dict['DistStorage']['vals'].items():
    der_buses.add (row['bus'])

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

