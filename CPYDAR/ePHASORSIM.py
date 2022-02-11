from SPARQLWrapper import SPARQLWrapper2, JSON
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import time
import xml.etree.ElementTree as ET
import pandas as pd

sparql = None
prefix = None

# ieee13x  4BE6DD69-8FE9-4C9F-AD44-B327D5623974
# ieee123x 4C4E3E2C-6332-4DCB-8425-26B628178374
# j1red    1C9727D2-E4D2-4084-B612-90A44E1810FD

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
              'DistBus']:

    start_time = time.time()
    query_for_values (dict[key], fid)
    if bTime:
      print ('Running {:30s} took {:6.3f} s'.format (key, time.time() - start_time))
  # remove all but fid from the list of feeders
  match_fid = '_' + fid
  delete = [key for key in dict['DistFeeder']['vals'] if dict['DistFeeder']['vals'][key]['fid'] != match_fid]
  for key in delete: 
    del dict['DistFeeder']['vals'][key]

def write_ephasor_model (dict, filename):
  xlw = pd.ExcelWriter (filename)
  feeder_name = list(dict['DistFeeder']['vals'].keys())[0]
  slack_buses = set()
  pv_buses = set()

  df = pd.DataFrame ([['Excel file version', 'v2.0'], 
                      ['Name', feeder_name], 
                      ['Frequency (Hz)', 60], 
                      ['Power Base (MVA)', 100]])
  df.to_excel (xlw, sheet_name='General', header=False, index=False)

  # voltage sources, identify slack buses
  data = {'ID':[], 'Bus':[], 'Voltage (pu)':[], 'Angle (deg)':[], 'Rs (pu)':[], 'Xs (pu)':[]}
  for key, row in dict['DistSubstation']['vals'].items():
    slack_buses.add (row['bus'])
    zbase = row['nomv']*row['nomv'] / 100.0e6
    data['ID'].append(key)
    data['Bus'].append(row['bus'])
    data['Voltage (pu)'].append(row['vmag'])
    data['Angle (deg)'].append(key)
    data['Rs (pu)'].append(row['r1']/zbase)
    data['Xs (pu)'].append(row['r1']/zbase)
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=12)

  # DER
  for key, row in dict['DistSolar']['vals'].items():
    pv_buses.add (row['bus'])
  for key, row in dict['DistStorage']['vals'].items():
    pv_buses.add (row['bus'])

  # buses
  data = {'Bus':[], 'Base Voltage (V)':[], 'Initial Vmag':[], 'Unit (V, pu)':[], 'Angle (deg)':[], 'Type':[]}
  for key, row in dict['DistBus']['vals'].items():
    data['Bus'].append(key)
    data['Base Voltage (V)'].append(row['nomv'])
    data['Initial Vmag'].append(1.0)
    data['Unit (V, pu)'].append('pu')
    data['Angle (deg)'].append(0.0)
    if key in slack_buses:
      data['Type'].append('SLACK')
    elif key in pv_buses:
      data['Type'].append('PV')
    else:
      data['Type'].append('PQ')
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Bus', header=True, index=False)

  # switches
  data = {'From Bus':[], 'To Bus':[], 'ID':[], 'Status':[]}
  for tag in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser']:
    tbl = dict[tag]
    for key, row in tbl['vals'].items():
      data['ID'].append (key)
      data['From Bus'].append (row['bus1'])
      data['To Bus'].append (row['bus2'])
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

  fid = '4BE6DD69-8FE9-4C9F-AD44-B327D5623974'
#  fid = '4C4E3E2C-6332-4DCB-8425-26B628178374'
#  fid = '1C9727D2-E4D2-4084-B612-90A44E1810FD'
#  list_feeders (dict)
  load_feeder (dict, fid, bTime=False)
  summarize_dict (dict)
  list_table (dict, 'DistLoad')
#  list_table (dict, 'DistBreaker')
#  list_table (dict, 'DistPowerXfmrMesh')
#  list_table (dict, 'DistCoordinates')
#  list_table (dict, 'DistPhaseMatrix')
#  list_table (dict, 'DistXfmrTank')
#  list_table (dict, 'DistXfmrCodeSCTest')
#  list_table (dict, 'DistXfmrCodeNLTest')
#  list_table (dict, 'DistXfmrCodeRating')

  write_ephasor_model (dict, 'ieee13x.xlsx')
