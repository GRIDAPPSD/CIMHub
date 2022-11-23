from SPARQLWrapper import SPARQLWrapper2, JSON
import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import math
import pandas as pd

CASES = [
  {'fid': '4BE6DD69-8FE9-4C9F-AD44-B327D5623974', 'fname': 'ieee13x.xlsx'},
  {'fid': '4C4E3E2C-6332-4DCB-8425-26B628178374', 'fname': 'ieee123x.xlsx'},
  {'fid': '1C9727D2-E4D2-4084-B612-90A44E1810FD', 'fname': 'j1red.xlsx'},
  {'fid': '77966920-E1EC-EE8A-23EE-4EFD23B205BD', 'fname': 'acep_psil.xlsx'},
]

# prefixes for exported names; will not prefix buses
LOAD_PREFIX = 'LD_'
LINE_PREFIX = 'LN_'
SHUNT_PREFIX = 'SH_'
SRCE_PREFIX = 'VS_'
SWITCH_PREFIX = 'SW_'
XFMR_PREFIX = 'XF_'
MACH_PREFIX = 'SM_'

# global constants
SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180.0 / math.pi

# configurable parameters
LOAD_BANDWIDTH = 0.12  # per-unit range for using ZIP coefficients, change to constant Z outside this range
DER_K_z = 0.0
DER_K_i = 100.0  # representing DER as constant current negative loads
DER_K_p = 0.0
MVA_BASE = 100.0
XL_START_ROW = 10
XFBUSPREFIX = 'xfbus'
DFLT_TAP = 0
DFLT_LOW_TAP = 0
DFLT_HIGH_TAP = 0
DFLT_BOOST = 0
DFLT_BUCK = 0
DFLT_MACHINE_QF = 0.44  # for 0.9 power factor machine

def mark_all_device_phases (dict):
  for tbl in ['DistSubstation', 'DistSeriesCompensator', 'DistRegulatorBanked', 
              'DistLinesInstanceZ', 'DistPowerXfmrWinding']: # didn't query for phases, assume 3
    dict[tbl]['columns'].append('phases')
    for key, row in dict[tbl]['vals'].items():
      row['phases'] = 'ABC'
  for tbl in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser',
              'DistSolar', 'DistStorage', 'DistLoad', 'DistCapacitor', 'DistLinesCodeZ', 'DistLinesSpacingZ']: # queried for PhaseCodeKinde
    for key, row in dict[tbl]['vals'].items():
      if len(row['phases']) < 1:
        row['phases'] = 'ABC'
  for tbl in ['DistXfmrTank', 'DistRegulatorTanked']: # queried for OrderedPhaseCodeKind
    dict[tbl]['columns'].append('phases')
    for key, row in dict[tbl]['vals'].items():
      if len(row['orderedPhases']) < 1:
        row['phases'] = 'ABC'
      else:
        phs = ''
        for tok in ['A', 'B', 'C', 's1', 's2']:
          if tok in row['orderedPhases']:
            phs += tok
        row['phases'] = phs

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
    busvals[key]['nomv'] /= SQRT3
    busvals[key]['phases'] = set()
  for tbl in ['DistSolar', 'DistStorage', 'DistLoad', 'DistCapacitor', 'DistXfmrTank', 'DistSubstation', 'DistPowerXfmrWinding']:
    for key, row in dict[tbl]['vals'].items():
      mark_one_bus_phases (busvals[row['bus']], row['phases'])
  for tbl in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser',
              'DistLinesCodeZ', 'DistLinesSpacingZ', 'DistSeriesCompensator', 'DistLinesInstanceZ']:
    for key, row in dict[tbl]['vals'].items():
      mark_one_bus_phases (busvals[row['bus1']], row['phases'])
      mark_one_bus_phases (busvals[row['bus2']], row['phases'])

def add_comment_cell (xlw, sheet_name, startrow, txt, startcol=0, GotoCol=None):
  df = pd.DataFrame ([txt])
  df.to_excel (xlw, sheet_name = sheet_name, header=False, index=False, startrow=startrow, startcol=startcol)
  if GotoCol is not None:
    df = pd.DataFrame (['Go to Type List'])
    df.to_excel (xlw, sheet_name = sheet_name, header=False, index=False, startrow=startrow, startcol=GotoCol)

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
      tok = '{:s}:{:d}:{:d}'.format (str(key), i+1, j+1)
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

def make_transformer_star_bus (BusPhs, tname):
  StarPhs = []
  for elem in BusPhs:
    if len(elem) > 0:
      phs = elem[-1]
      if phs == '1':
        phs = 's1'
      elif phs == '2':
        phs = 's2'
      StarPhs.append ('{:s}_{:s}_{:s}'.format (XFBUSPREFIX, tname, phs))
  while len(StarPhs) < 3:
    StarPhs.append('')
  return StarPhs

def get_transformer_mesh (dict, base_key, end1, end2):
  BusPhs1 = []
  BusPhs2 = []
  r = 0.0
  x = 0.0
  key1 = '{:s}:{:d}'.format (base_key, end1)
  key2 = '{:s}:{:d}'.format (base_key, end2)

  wdg1 = dict['DistXfmrTank']['vals'][key1]
  wdg2 = dict['DistXfmrTank']['vals'][key2]
  aphs1 = phase_array (wdg1['phases'])
  aphs2 = phase_array (wdg2['phases'])
  nphs1 = len(aphs1)
  nphs2 = len(aphs2)
  for phs in aphs1:
    BusPhs1.append(wdg1['bus'] + phs)
  for phs in aphs2:
    BusPhs2.append(wdg2['bus'] + phs)
  while len(BusPhs1) < 3:
    BusPhs1.append('')
  while len(BusPhs2) < 3:
    BusPhs2.append('')

  code1 = dict['DistXfmrCodeRating']['vals']['{:s}:{:d}'.format(wdg1['xfmrcode'], end1)]
  v1 = 0.001 * code1['ratedU']
  s1 = 0.001 * code1['ratedS'] * nphs1
  zbase1 = 1000.0 * v1 * v1 / s1
  if code1['conn'] == 'I':
    v1 *= SQRT3
  conn1 = conn_string(code1['conn'])
  code2 = dict['DistXfmrCodeRating']['vals']['{:s}:{:d}'.format(wdg2['xfmrcode'], end2)]
  v2 = 0.001 * code2['ratedU']
  s2 = 0.001 * code2['ratedS'] * nphs2
  zbase2 = 1000.0 * v2 * v2 / s2
  if code2['conn'] == 'I':
    v2 *= SQRT3
  conn2 = conn_string(code2['conn'])

  sctest = dict['DistXfmrCodeSCTest']['vals']['{:s}:{:d}:{:d}'.format(wdg2['xfmrcode'], end1, end2)]
  zpu = sctest['z'] / zbase1
  # r = sctest['ll'] / s1
  r = code1['res'] / zbase1 + code2['res'] / zbase2
  x = zpu # math.sqrt(zpu*zpu - r*r)

# print ('Tank {:s}, {:d}-{:d}, bus1={:s},{:s},{:s}, bus2={:s},{:s},{:s}'.format(base_key, end1, end2,
#   BusPhs1[0], BusPhs1[1], BusPhs1[2], BusPhs2[0], BusPhs2[1], BusPhs2[2]))
# print ('  wdg 1: v={:.3f} s={:.2f} conn={:s}; wdg 2: v={:.3f} s={:.2f} conn={:s} rmesh={:.6f} xmesh={:.6f}'.format (v1, s1, conn1, v2, s2, conn2, r, x))

  return BusPhs1, BusPhs2, v1, v2, s1, s1, conn1, conn2, r, x

def append_transformer_branch_only (dxf, r, x):
  dxf['X (pu)'].append(x)
  if r < 0.0:
    r = 0.0
  dxf['RW1 (pu)'].append(0.5*r)
  dxf['RW2 (pu)'].append(0.5*r)

def append_transformer_branch_and_core (dxf, r, x, nll_kw):
  if r <= 0.0:
    r = 0.001 * x
  z = math.sqrt(r*r + x*x)
  xr = x/r
  dxf['Z1 leakage (pu)'].append(z)
  dxf['Z0 leakage (pu)'].append(z)
  dxf['X1/R1'].append(xr)
  dxf['X0/R0'].append(xr)
  dxf['No Load Loss (kW)'].append(nll_kw)

def append_transformer_tank (dxf, base_key, BusPhs1, BusPhs2, v1, v2, s1, s2, conn1, conn2,
                             tap1, tap2, tap3, lowtap, hightap, maxboost, maxbuck):
  dxf['ID'].append(XFMR_PREFIX + base_key)
  dxf['Status'].append(1)
  nph1 = 0
  for busphs in BusPhs1:
    if len(busphs) > 0:
      nph1 += 1
  nph2 = 0
  for busphs in BusPhs2:
    if len(busphs) > 0:
      nph2 += 1
  dxf['Number of phases'].append(min(nph1, nph2))
  dxf['Bus1_A'].append(BusPhs1[0])
  dxf['Bus1_B'].append(BusPhs1[1])
  dxf['Bus1_C'].append(BusPhs1[2])
  dxf['Bus2_A'].append(BusPhs2[0])
  dxf['Bus2_B'].append(BusPhs2[1])
  dxf['Bus2_C'].append(BusPhs2[2])
  dxf['V1 (kV)'].append(v1)
  dxf['S_base1 (kVA)'].append(s2)
  dxf['Conn. type1'].append(conn1)
  dxf['V2 (kV)'].append(v2)
  dxf['S_base2 (kVA)'].append(s2)
  dxf['Conn. type2'].append(conn2)
  dxf['Tap 1'].append(tap1)
  dxf['Tap 2'].append(tap2)
  dxf['Tap 3'].append(tap3)
  dxf['Lowest Tap'].append(lowtap)
  dxf['Highest Tap'].append(hightap)
  dxf['Min Range (%)'].append(maxbuck)
  dxf['Max Range (%)'].append(maxboost)

def add_template_block (xlw, sheetname, col0_labels = [], col1_labels = []):
  add_comment_cell (xlw, sheetname, 0, 'Type', 0)
  add_comment_cell (xlw, sheetname, 7, 'Important notes:', 0)
  add_comment_cell (xlw, sheetname, 8, 'Default order of blocks and columns after row 11 must not change', 0)
  add_comment_cell (xlw, sheetname, 9, 'One empty row between End of each block and the next block is mandatory; otherwise, empty rows are NOT allowed ', 0)
  row = 1
  for lbl in col0_labels:
    add_comment_cell (xlw, sheetname, row, lbl, 0)
    row += 1
  row = 1
  for lbl in col1_labels:
    add_comment_cell (xlw, sheetname, row, lbl, 1)
    row += 1

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
                      ['Power Base (MVA)', MVA_BASE]])
  df.to_excel (xlw, sheet_name='General', header=False, index=False)

  # voltage sources, identify slack buses
  add_template_block (xlw, 'Voltage Source', col0_labels = ['PositiveSeqVsource',
                                                            'SinglePhaseVsource',
                                                            'ThreePhaseShortCircuitVsource',
                                                            'ThreePhaseSequentialVsource'])
  xlrow = XL_START_ROW
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Positive Sequence Voltage Source', GotoCol=4)
  data = {'ID':[], 'Bus':[], 'Voltage (pu)':[], 'Angle (deg)':[], 'Rs (pu)':[], 'Xs (pu)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df.index) + 2
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'End of Positive Sequence Voltage Source')
  xlrow += 2

  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Single-Phase Voltage Source', GotoCol=4)
  data = {'ID':[], 'Bus1':[], 'Voltage (V)':[], 'Angle (deg)':[], 'Rs (Ohm)':[], 'Xs (Ohm)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df.index) + 2
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'End of Single-Phase Voltage Source')
  xlrow += 2

  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Three-Phase Voltage Source with Short-Circuit Level Data', GotoCol=4)
  data = {'ID':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 'kV (ph-ph RMS)':[], 'Angle_a (deg)':[], 'SC1ph (MVA)':[], 'SC3ph (MVA)':[]}
  df = pd.DataFrame (data)
  df.to_excel (xlw, sheet_name='Voltage Source', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df.index) + 2
  add_comment_cell (xlw, 'Voltage Source', xlrow, 'End of Three-Phase Voltage Source with Short-Circuit Level Data')
  xlrow += 2

  add_comment_cell (xlw, 'Voltage Source', xlrow, 'Three-Phase Voltage Source with Sequential Data', GotoCol=4)
  data = {'ID':[], 'Bus1':[], 'Bus2':[], 'Bus3':[], 'kV (ph-ph RMS)':[], 'Angle_a (deg)':[], 'R1 (Ohm)':[], 'X1 (Ohm)':[], 'R0 (Ohm)':[], 'X0 (Ohm)':[]}
  for key, row in dict['DistSubstation']['vals'].items():
    slack_buses.add (row['bus'])
    data['ID'].append(SRCE_PREFIX + key)
    data['Bus1'].append(row['bus'] + '_A')
    data['Bus2'].append(row['bus'] + '_B')
    data['Bus3'].append(row['bus'] + '_C')
    data['kV (ph-ph RMS)'].append(row['vmag'] * 0.001)
    data['Angle_a (deg)'].append(row['vang'] * RAD_TO_DEG)
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
    pz = row['pz']
    pi = row['pi']
    pp = row['pp']
    if (pz+pi+pp) <= 0.0:
      if row['pe'] >= 1.9:
        pz = 100.0
      elif row['pe'] >= 0.9:
        pi = 100.0
      else:
        pp = 100.0
    if len(aphs) == 1:
      data4['ID'].append(LOAD_PREFIX + key)
      data4['Status'].append(1)
      data4['V (kV)'].append(kv)
      data4['Bandwidth (pu)'].append(LOAD_BANDWIDTH)
      data4['Conn. type'].append(conn)
      data4['K_z'].append(pz)
      data4['K_i'].append(pi)
      data4['K_p'].append(pp)
      data4['Use initial voltage?'].append(0)
      data4['Bus1'].append(row['bus'] + aphs[0])
      data4['P1 (kW)'].append(kw)
      data4['Q1 (kVAr)'].append(kvar)
    elif len(aphs) == 2:
      kvar /= 2.0
      kw /= 2.0
      data5['ID'].append(LOAD_PREFIX + key)
      data5['Status'].append(1)
      data5['V (kV)'].append(kv)
      data5['Bandwidth (pu)'].append(LOAD_BANDWIDTH)
      data5['Conn. type'].append(conn)
      data5['K_z'].append(pz)
      data5['K_i'].append(pi)
      data5['K_p'].append(pp)
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
      data6['ID'].append(LOAD_PREFIX + key)
      data6['Status'].append(1)
      data6['V (kV)'].append(kv)
      data6['Bandwidth (pu)'].append(LOAD_BANDWIDTH)
      data6['Conn. type'].append(conn)
      data6['K_z'].append(pz)
      data6['K_i'].append(pi)
      data6['K_p'].append(pp)
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
        data4['ID'].append(LOAD_PREFIX + prefix + key)
        data4['Status'].append(1)
        data4['V (kV)'].append(kv)
        data4['Bandwidth (pu)'].append(LOAD_BANDWIDTH)
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
        data5['ID'].append(LOAD_PREFIX + prefix + key)
        data5['Status'].append(1)
        data5['V (kV)'].append(kv)
        data5['Bandwidth (pu)'].append(LOAD_BANDWIDTH)
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
        data6['ID'].append(LOAD_PREFIX + prefix + key)
        data6['Status'].append(1)
        data6['V (kV)'].append(kv)
        data6['Bandwidth (pu)'].append(LOAD_BANDWIDTH)
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
  print ('Writing', len(df1) + len(df2) + len(df3) + len(df4) + len(df5) + len(df6), 'loads and DER')
  add_template_block (xlw, 'Load', col0_labels = ['PositiveSeqZload',
                                                  'PositiveSeqPload',
                                                  'PositiveSeqIload',
                                                  'SinglePhaseZIPLoad',
                                                  'TwoPhaseZIPLoad'],
                      col1_labels = ['ThreePhaseZIPLoad'])
  xlrow = XL_START_ROW
  add_comment_cell (xlw, 'Load', xlrow, 'Positive-Sequence Constant Imepedance Load', GotoCol=2) # replicating typo on the Opal-RT template
  df1.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of Positive Sequence Constant Imepedance Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Positive-Sequence Constant Power Load', GotoCol=2)
  df2.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of Positive Sequence Constant Power Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Positive-Sequence Constant Current Load', GotoCol=2)
  df3.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of Positive Sequence Constant Current Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Single-Phase ZIP Load', GotoCol=2)
  df4.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of SinglePhase ZIP Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Two-Phase ZIP Load', GotoCol=2)
  df5.to_excel (xlw, sheet_name='Load', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df5.index) + 2
  add_comment_cell (xlw, 'Load', xlrow, 'End of TwoPhase ZIP Load')
  xlrow += 2
  add_comment_cell (xlw, 'Load', xlrow, 'Three-Phase ZIP Load', GotoCol=2)
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
      data2['ID'].append(SHUNT_PREFIX + key)
      data2['Status'].append(1)
      data2['kV (ph-gr RMS)'].append(kv)
      data2['Bus1'].append(row['bus'] + aphs[0])
      data2['P1 (kW)'].append(0.0)
      data2['Q1 (kVAr)'].append(kvar)
    elif len(aphs) == 2:
      kvar /= 2.0
      kv /= SQRT3
      data3['ID'].append(SHUNT_PREFIX + key)
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
      kv /= SQRT3
      data4['ID'].append(SHUNT_PREFIX + key)
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
  print ('Writing', len(df1) + len(df2) + len(df3) + len(df4), 'shunts')
  add_template_block (xlw, 'Shunt', col0_labels = ['PositiveSeqShunt',
                                                   'SinglePhaseShunt',
                                                   'TwoPhaseShunt',
                                                   'ThreePhaseShunt'])
  xlrow = XL_START_ROW
  add_comment_cell (xlw, 'Shunt', xlrow, 'Positive Sequence Shunt', GotoCol=2)
  df1.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Positive Sequence Shunt')
  xlrow += 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'Single-Phase Shunt', GotoCol=2)
  df2.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Single-Phase Shunt')
  xlrow += 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'Two-Phase Shunt', GotoCol=2)
  df3.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Two-Phase Shunt')
  xlrow += 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'Three-Phase Shunt', GotoCol=2)
  df4.to_excel (xlw, sheet_name='Shunt', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Shunt', xlrow, 'End of Three-Phase Shunt')

  # lines
  PhaseMatrices = []
  for key, row in dict['DistPhaseMatrix']['vals'].items():
    sname = key.split(':')[0]
    if sname not in PhaseMatrices:
      PhaseMatrices.append(sname)

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
    lname = row['lname']
    if lname in PhaseMatrices:
      aphs = sequenced_phase_array (row['seqs'])
      kv = 0.001 * row['basev']
      if len(aphs) == 1:
        data2['ID'].append(LINE_PREFIX + key)
        data2['Status'].append(1)
        data2['Length'].append(row['len'])
        data2['From1'].append(row['bus1'] + aphs[0])
        data2['To1'].append(row['bus2'] + aphs[0])
        append_phase_matrix (data2, lname, 1, dict['DistPhaseMatrix']['vals'])
      elif len(aphs) == 2:
        data3['ID'].append(LINE_PREFIX + key)
        data3['Status'].append(1)
        data3['Length'].append(row['len'])
        data3['From1'].append(row['bus1'] + aphs[0])
        data3['To1'].append(row['bus2'] + aphs[0])
        data3['From2'].append(row['bus1'] + aphs[1])
        data3['To2'].append(row['bus2'] + aphs[1])
        append_phase_matrix (data3, lname, 2, dict['DistPhaseMatrix']['vals'])
      elif len(aphs) == 3:
        data4['ID'].append(LINE_PREFIX + key)
        data4['Status'].append(1)
        data4['Length'].append(row['len'])
        data4['From1'].append(row['bus1'] + aphs[0])
        data4['To1'].append(row['bus2'] + aphs[0])
        data4['From2'].append(row['bus1'] + aphs[1])
        data4['To2'].append(row['bus2'] + aphs[1])
        data4['From3'].append(row['bus1'] + aphs[2])
        data4['To3'].append(row['bus2'] + aphs[2])
        append_phase_matrix (data4, lname, 3, dict['DistPhaseMatrix']['vals'])
    elif lname in dict['DistSequenceMatrix']['vals']:
      mat = dict['DistSequenceMatrix']['vals'][lname]
      data5['ID'].append(LINE_PREFIX + key)
      data5['Status'].append(1)
      data5['Length'].append(row['len'])
      data5['From1'].append(row['bus1'] + '_A')
      data5['To1'].append(row['bus2'] + '_A')
      data5['From2'].append(row['bus1'] + '_B')
      data5['To2'].append(row['bus2'] + '_B')
      data5['From3'].append(row['bus1'] + '_C')
      data5['To3'].append(row['bus2'] + '_C')
      data5['R0 (Ohm/length_unit)'].append(mat['r0'])
      data5['R1 (Ohm/length_unit)'].append(mat['r1'])
      data5['X0 (Ohm/length_unit)'].append(mat['x0'])
      data5['X1 (Ohm/length_unit)'].append(mat['x1'])
      data5['B0 (uS/length_unit)'].append(mat['b0'] * 1.0e6)
      data5['B1 (uS/length_unit)'].append(mat['b1'] * 1.0e6)

  for key, row in dict['DistLinesInstanceZ']['vals'].items():
    aphs = phase_array (row['phases'])
    if len(aphs) == 3:
      data5['ID'].append(LINE_PREFIX + key)
      data5['Status'].append(1)
      data5['Length'].append(row['len'])
      data5['From1'].append(row['bus1'] + aphs[0])
      data5['To1'].append(row['bus2'] + aphs[0])
      data5['From2'].append(row['bus1'] + aphs[1])
      data5['To2'].append(row['bus2'] + aphs[1])
      data5['From3'].append(row['bus1'] + aphs[2])
      data5['To3'].append(row['bus2'] + aphs[2])
      data5['R0 (Ohm/length_unit)'].append(row['r0'])
      data5['R1 (Ohm/length_unit)'].append(row['r'])
      data5['X0 (Ohm/length_unit)'].append(row['x0'])
      data5['X1 (Ohm/length_unit)'].append(row['x'])
      data5['B0 (uS/length_unit)'].append(row['b0'] * 1.0e6)
      data5['B1 (uS/length_unit)'].append(row['b'] * 1.0e6)
    else:
      print ('*** DistLinesInstanceZ {:s} has {:d} phases; it must have 3 phases'.format (key, len(aphs)))
    
  df1 = pd.DataFrame (data1)
  df2 = pd.DataFrame (data2)
  df3 = pd.DataFrame (data3)
  df4 = pd.DataFrame (data4)
  df5 = pd.DataFrame (data5)
  print ('Writing', len(df1) + len(df2) + len(df3) + len(df4) + len(df5), 'lines')
  add_template_block (xlw, 'Line', col0_labels = ['PositiveSeqLine',
                                                  'SinglePhaseLine',
                                                  'TwoPhaseLine',
                                                  'ThreePhaseLineFullData',
                                                  'ThreePhaseLineSequentialData'])
  xlrow = XL_START_ROW
  add_comment_cell (xlw, 'Line', xlrow, 'Positive-Sequence Line', GotoCol=2)
  df1.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Positive-Sequence Line')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Single-Phase Line', GotoCol=2)
  df2.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Single-Phase Line')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Two-Phase Line', GotoCol=2)
  df3.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Two-Phase Line')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Three-Phase Line with Full Data', GotoCol=2)
  df4.to_excel (xlw, sheet_name='Line', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Line', xlrow, 'End of Three-Phase Line with Full Data')
  xlrow += 2
  add_comment_cell (xlw, 'Line', xlrow, 'Three-Phase Line with Sequential Data', GotoCol=2)
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
  PowerXfmrs = {}
  for key in dict['DistPowerXfmrWinding']['vals']:
    pname = key.split(':')[0]
    if pname in PowerXfmrs:
      PowerXfmrs[pname]['nwdg'] += 1
    else:
      PowerXfmrs[pname] = {'nwdg':1, 'regulator': None}
  for key, row in dict['DistRegulatorBanked']['vals'].items():
    if row['pname'] in PowerXfmrs:
      PowerXfmrs[row['pname']]['regulator'] = key
#  print (PowerXfmrs)
  for pname, row in PowerXfmrs.items():
    nwdg = row['nwdg']
    if nwdg == 2:
      wdg1 = dict['DistPowerXfmrWinding']['vals']['{:s}:1'.format(pname)]
      wdg2 = dict['DistPowerXfmrWinding']['vals']['{:s}:2'.format(pname)]
      z12 = dict['DistPowerXfmrMesh']['vals']['{:s}:1:2'.format(pname)]
      ym = dict['DistPowerXfmrCore']['vals'][pname]
      zbase = wdg1['ratedU'] * wdg1['ratedU'] / wdg1['ratedS']
      tap1 = DFLT_TAP
      tap2 = DFLT_TAP
      tap3 = DFLT_TAP
      lowtap = DFLT_LOW_TAP
      hightap = DFLT_HIGH_TAP
      maxboost = DFLT_BOOST
      maxbuck = DFLT_BUCK
      if row['regulator'] is not None:
        reg = dict['DistRegulatorBanked']['vals'][row['regulator']]
        if reg['wnum'] == 1:  # reverse the order
          tap1 = reg['neutralStep'] - reg['step']
        else:
          tap1 = reg['step']
        tap2 = tap1
        tap3 = tap1
        lowtap = reg['lowStep']
        hightap = reg['highStep']
        maxboost = reg['incr']*abs(reg['highStep']-reg['neutralStep'])
        maxbuck = reg['incr']*abs(reg['neutralStep']-reg['lowStep'])
        print ('== taps for bank {:s}, wdg={:d}, phases={:s}, tap1={:d}, low={:d}, high={:d}, boost={:.2f}%, buck={:.2f}%'.format (pname,  
          reg['wnum'], reg['phases'], tap1, lowtap, hightap, maxboost, maxbuck))
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
      dxf['ID'].append(XFMR_PREFIX + pname)
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
      data2['ID'].append(XFMR_PREFIX + pname)
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
    if pname not in XfmrBanks:
      XfmrBanks[pname] = {'tanks': []}
    XfmrBanks[pname]['tanks'].append(tname)
  # also need the number of windings and back-pointer to the regulator (if present) on each tank
  XfmrTanks = {}
  for key, row in dict['DistXfmrTank']['vals'].items():
    keys = key.split(':')
    pname = keys[0]
    tname = keys[1]
    if tname not in XfmrTanks:
      XfmrTanks[tname] = {'nwdg': 0, 'regulator':None}
    XfmrTanks[tname]['nwdg'] += 1
  for key, row in dict['DistRegulatorTanked']['vals'].items():
    if row['tname'] in XfmrTanks:
      XfmrTanks[row['tname']]['regulator'] = key
# print ('XfmrBanks', XfmrBanks)
# print ('XfmrTanks', XfmrTanks)

  TooManyWindings = {}
  StarBuses = {}
  # now write the banked transformers as 2W multi-phase, one for each star branch
  for pname, row in XfmrBanks.items():
    ntank = len(row['tanks'])
    for itk in range(ntank):
      tname = row['tanks'][itk]
      base_key = pname + ':' + tname # will add :wdg
      nwdg = XfmrTanks[tname]['nwdg']
      nlcode = dict['DistXfmrTank']['vals'][base_key + ':1']['xfmrcode']
      nltest = dict['DistXfmrCodeNLTest']['vals'][nlcode]
      nll_kw = nltest['nll']
      iexc_pct = nltest['iexc']
      dxf = data3 # if NLL==0, else data4
      tap1 = DFLT_TAP
      tap2 = DFLT_TAP
      tap3 = DFLT_TAP
      lowtap = DFLT_LOW_TAP
      hightap = DFLT_HIGH_TAP
      maxboost = DFLT_BOOST
      maxbuck = DFLT_BUCK
      if  XfmrTanks[tname]['regulator'] is not None:
        reg = dict['DistRegulatorTanked']['vals'][XfmrTanks[tname]['regulator']]
        if reg['wnum'] == 1:  # reverse the order
          tap1 = reg['neutralStep'] - reg['step']
        else:
          tap1 = reg['step']
        if len(reg['phases']) > 1:
          tap2 = tap1
          if len(reg['phases']) > 2:
            tap3 = tap1
        lowtap = reg['lowStep']
        hightap = reg['highStep']
        maxboost = reg['incr']*abs(reg['highStep']-reg['neutralStep'])
        maxbuck = reg['incr']*abs(reg['neutralStep']-reg['lowStep'])
        print ('== taps for tank {:s}/{:s}, wdg={:d}, phases={:s}, tap1={:d}, low={:d}, high={:d}, boost={:.2f}%, buck={:.2f}%'.format (pname, tname, 
          reg['wnum'], reg['phases'], tap1, lowtap, hightap, maxboost, maxbuck))
      if nwdg == 2:
        BusPhs1, BusPhs2, v1, v2, s1, s2, conn1, conn2, r, x = get_transformer_mesh (dict, base_key, 1, 2)
        if nll_kw > 0.0:
          append_transformer_tank (data4, base_key, BusPhs1, BusPhs2, v1, v2, s1, s2, conn1, conn2,
                                   tap1, tap2, tap3, lowtap, hightap, maxboost, maxbuck)
          append_transformer_branch_and_core (data4, r, x, nll_kw)
        else:
          append_transformer_tank (data3, base_key, BusPhs1, BusPhs2, v1, v2, s1, s2, conn1, conn2,
                                   tap1, tap2, tap3, lowtap, hightap, maxboost, maxbuck)
          append_transformer_branch_only (data3, r, x)
      elif nwdg == 3:
        BusPhs12, BusPhs21, v12, v21, s12, s21, conn12, conn21, r12, x12 = get_transformer_mesh (dict, base_key, 1, 2)
        BusPhs13, BusPhs31, v13, v31, s13, s31, conn13, conn31, r13, x13 = get_transformer_mesh (dict, base_key, 1, 3)
        BusPhs23, BusPhs32, v23, v32, s23, s32, conn23, conn32, r23, x23 = get_transformer_mesh (dict, base_key, 2, 3)
        StarPhs = make_transformer_star_bus (BusPhs12, tname)
        for busphs in StarPhs:
          if len(busphs) > 0:
            StarBuses[busphs] = 1000.0 * v12/SQRT3
        if nll_kw > 0.0:
          append_transformer_tank (data4, base_key, BusPhs12, StarPhs, v12, v12, s12, s12, conn12, conn12,
                                   tap1, tap2, tap3, lowtap, hightap, maxboost, maxbuck)
          append_transformer_branch_and_core (data4, 0.5*(r12+r13-r23), 0.5*(x12+x13-x23), nll_kw)
        else:
          append_transformer_tank (data3, base_key, BusPhs12, StarPhs, v12, v12, s12, s12, conn12, conn12,
                                   tap1, tap2, tap3, lowtap, hightap, maxboost, maxbuck)
          append_transformer_branch_only (data3, 0.5*(r12+r13-r23), 0.5*(x12+x13-x23))
        append_transformer_tank (data3, base_key, StarPhs, BusPhs21, v12, v21, s12, s21, conn12, conn21, tap1, tap2, tap3, lowtap, hightap, maxboost, maxbuck)
        append_transformer_branch_only (data3, 0.5*(r12+r23-r13), 0.5*(x12+x23-x13))
        append_transformer_tank (data3, base_key, StarPhs, BusPhs32, v13, v32, s23, s32, conn12, conn32, tap1, tap2, tap3, lowtap, hightap, maxboost, maxbuck)
        append_transformer_branch_only (data3, 0.5*(r13+r23-r12), 0.5*(x13+x23-x12))
      else:
        TooManyWindings[base_key] = nwdg

  for tname, nwdg in TooManyWindings.items():
    print ('*** Transformer Tank {:s} has {:d} windings, which cannot be converted to star equivalent'.format (tname, nwdg))

  df1 = pd.DataFrame (data1)
  df2 = pd.DataFrame (data2)
  df3 = pd.DataFrame (data3)
  df4 = pd.DataFrame (data4)
  print ('Writing', len(df1) + len(df2) + len(df3) + len(df4), 'transformers')
  add_template_block (xlw, 'Transformer', col0_labels = ['PositiveSeq2wXF',
                                                   'PositiveSeq3wXF',
                                                   'Multiphase2wXF',
                                                   'Multiphase2wXFMutual'])
  xlrow = XL_START_ROW
  add_comment_cell (xlw, 'Transformer', xlrow, 'Positive-Sequence 2W Transformer', GotoCol=3)
  df1.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Positive-Sequence 2W Transformer')
  xlrow += 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'Positive-Sequence 3W Transformer', GotoCol=3)
  df2.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Positive-Sequence 3W Transformer')
  xlrow += 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'Multiphase 2W Transformer', GotoCol=3)
  df3.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Multiphase 2W Transformer')
  xlrow += 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'Multiphase 2W Transformer with Mutual Impedance', GotoCol=3)
  df4.to_excel (xlw, sheet_name='Transformer', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Transformer', xlrow, 'End of Multiphase 2W Transformer with Mutual Impedance')

  # synchronous machines; should probably use SyncGENCLS for all of them
  data1 = {'Bus':[], 'ID':[], 'Status':[], 'Pg (MW)':[], 'Qg (MVAr)':[], 'Qmin (MVAr)':[], 'Qmax (MVAr)':[], 'Sbase (MVA)':[],
          'H (s)':[], 'D':[], 'Ra (pu)':[], 'x\'_d (pu)':[]}
  data2 = {'Bus':[], 'ID':[], 'Status':[], 'Pg (MW)':[], 'Qg (MVAr)':[], 'Qmin (MVAr)':[], 'Qmax (MVAr)':[], 'Sbase (MVA)':[],
          'H (s)':[], 'D':[], 'Ra (pu)':[], 'x_d (pu)':[], 'x_q (pu)':[], 'x\'_d (pu)':[], 'x\'_q (pu)':[],
          'x\'\'_d (pu)':[], 'x_l (pu)':[], 'T\'_do (s)':[], 'T\'\'_do (s)':[],
          'T\'_qo (s)':[], 'T\'\'_qo (s)':[], 'S10':[], 'S12':[]}
  data3 = {'Bus':[], 'ID':[], 'Status':[], 'Pg (MW)':[], 'Qg (MVAr)':[], 'Qmin (MVAr)':[], 'Qmax (MVAr)':[], 'Sbase (MVA)':[],
          'H (s)':[], 'D':[], 'Ra (pu)':[], 'x_d (pu)':[], 'x_q (pu)':[], 'x\'_d (pu)':[], 'x\'_q (pu)':[],
          'x\'\'_d (pu)':[], 'x_l (pu)':[], 'T\'_do (s)':[], 'T\'\'_do (s)':[],
          'T\'_qo (s)':[], 'T\'\'_qo (s)':[], 'S10':[], 'S12':[]}
  data4 = {'Bus':[], 'ID':[], 'Status':[], 'Pg (MW)':[], 'Qg (MVAr)':[], 'Qmin (MVAr)':[], 'Qmax (MVAr)':[], 'Sbase (MVA)':[],
          'H (s)':[], 'D':[], 'Ra (pu)':[], 'x_d (pu)':[], 'x_q (pu)':[], 'x\'_d (pu)':[], 
          'x\'\'_d (pu)':[], 'x_l (pu)':[], 'T\'_do (s)':[], 'T\'\'_do (s)':[],
          'T\'\'_qo (s)':[], 'S10':[], 'S12':[]}
  data5 = {'Bus':[], 'ID':[], 'Status':[], 'Pg (MW)':[], 'Qg (MVAr)':[], 'Qmin (MVAr)':[], 'Qmax (MVAr)':[], 'Sbase (MVA)':[],
          'H (s)':[], 'D':[], 'Ra (pu)':[], 'x_d (pu)':[], 'x_q (pu)':[], 'x\'_d (pu)':[], 
          'x\'\'_d (pu)':[], 'x_l (pu)':[], 'T\'_do (s)':[], 'T\'\'_do (s)':[],
          'T\'\'_qo (s)':[], 'S10':[], 'S12':[]}
  data6 = {'Bus':[], 'ID':[], 'Status':[], 'Pg (MW)':[], 'Qg (MVAr)':[], 'Qmin (MVAr)':[], 'Qmax (MVAr)':[], 'Sbase (MVA)':[],
          'Pmech0 (pu)':[], 'H (s)':[], 'Ra (pu)':[], 'x (pu)':[], 'x\' (pu)':[],
          'x_l (pu)':[], 'T\' (s)':[], 'e1 (pu)':[], 'e2 (pu)':[], 'S(e1)':[], 'S(e2)':[]}
  data7 = {'Bus':[], 'ID':[], 'Status':[], 'Pg (MW)':[], 'Qg (MVAr)':[], 'Qmin (MVAr)':[], 'Qmax (MVAr)':[], 'Sbase (MVA)':[],
          'Pmech0 (pu)':[], 'H (s)':[], 'Ra (pu)':[], 'x (pu)':[], 'x\' (pu)':[], 'x\'\' (pu)':[],
          'x_l (pu)':[], 'T\' (s)':[], 'T\'\' (s)':[], 'e1 (pu)':[], 'e2 (pu)':[], 'S(e1)':[], 'S(e2)':[]}
  for key, row in dict['DistSyncMachine']['vals'].items():
    der_buses.add (row['bus'])
    ratedQ = max (DFLT_MACHINE_QF * row['ratedS'], math.fabs(row['q']))
    data1['Bus'].append(row['bus'])
    data1['ID'].append(MACH_PREFIX + key) 
    data1['Status'].append(1) 
    data1['Pg (MW)'].append(1.0e-6 * row['p'])
    data1['Qg (MVAr)'].append(1.0e-6 * row['q'])
    data1['Qmin (MVAr)'].append(-1.0e-6 * ratedQ)
    data1['Qmax (MVAr)'].append(1.0e-6 * ratedQ)
    data1['Sbase (MVA)'].append(1.0e-6 * row['ratedS'])
    data1['H (s)'].append(3.0)
    data1['D'].append(0.001)
    data1['Ra (pu)'].append(0.01)
    data1['x\'_d (pu)'].append(0.5)

  # push machine data into the spreadsheet
  df1 = pd.DataFrame (data1)
  df2 = pd.DataFrame (data2)
  df3 = pd.DataFrame (data3)
  df4 = pd.DataFrame (data4)
  df5 = pd.DataFrame (data5)
  df6 = pd.DataFrame (data6)
  df7 = pd.DataFrame (data7)
  print ('Writing', len(df1) + len(df2) + len(df3) + len(df4) + len(df5) + len(df6) + len(df7), 'machines')
  add_template_block (xlw, 'Machine', col0_labels = ['SyncGenGENCLS',
                                                     'SyncGenGENROE',
                                                     'SyncGenGENROU',
                                                     'SyncGenGENSAE',
                                                     'SyncGenGENSAL'],
                      col1_labels = ['AsyncGenSingleCage', 'AsyncGenDoubleCage'])
  xlrow = XL_START_ROW
  add_comment_cell (xlw, 'Machine', xlrow, 'SyncGenGENCLS', GotoCol=1)
  df1.to_excel (xlw, sheet_name='Machine', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df1.index) + 2
  add_comment_cell (xlw, 'Machine', xlrow, 'End of SyncGenGENCLS')
  xlrow += 2
  add_comment_cell (xlw, 'Machine', xlrow, 'SyncGenGENROE', GotoCol=1)
  df2.to_excel (xlw, sheet_name='Machine', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df2.index) + 2
  add_comment_cell (xlw, 'Machine', xlrow, 'End of SyncGenGENROE')
  xlrow += 2
  add_comment_cell (xlw, 'Machine', xlrow, 'SyncGenGENROU', GotoCol=1)
  df3.to_excel (xlw, sheet_name='Machine', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df3.index) + 2
  add_comment_cell (xlw, 'Machine', xlrow, 'End of SyncGenGENROU')
  xlrow += 2
  add_comment_cell (xlw, 'Machine', xlrow, 'SyncGenGENSAE', GotoCol=1)
  df4.to_excel (xlw, sheet_name='Machine', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df4.index) + 2
  add_comment_cell (xlw, 'Machine', xlrow, 'End of SyncGenGENSAE')
  xlrow += 2
  add_comment_cell (xlw, 'Machine', xlrow, 'SyncGenGENSAL', GotoCol=1)
  df5.to_excel (xlw, sheet_name='Machine', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df5.index) + 2
  add_comment_cell (xlw, 'Machine', xlrow, 'End of SyncGenGENSAL')
  xlrow += 2
  add_comment_cell (xlw, 'Machine', xlrow, 'AsyncGenSingleCage', GotoCol=1)
  df6.to_excel (xlw, sheet_name='Machine', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df6.index) + 2
  add_comment_cell (xlw, 'Machine', xlrow, 'End of AsyncGenSingleCage')
  xlrow += 2
  add_comment_cell (xlw, 'Machine', xlrow, 'AsyncGenDoubleCage', GotoCol=1)
  df7.to_excel (xlw, sheet_name='Machine', header=True, index=False, startrow=xlrow+1)
  xlrow += len(df7.index) + 2
  add_comment_cell (xlw, 'Machine', xlrow, 'End of AsyncGenDoubleCage')

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
  for busname, vnom in StarBuses.items():
    angle = 0.0
    phs = busname[-1]
    if phs == 'B':
      angle = -120.0
    elif phs == 'C':
      angle = 120.0
    elif phs == '2':
      angle = 180.0
    data['Bus'].append(busname)
    data['Base Voltage (V)'].append(vnom)
    data['Initial Vmag'].append(1.0)
    data['Unit (V, pu)'].append('pu')
    data['Angle (deg)'].append(angle)
    data['Type'].append('PQ')
  df = pd.DataFrame (data)
  print ('Writing', len(df), 'buses')
  df.to_excel (xlw, sheet_name='Bus', header=True, index=False)

  # switches
  data = {'From Bus':[], 'To Bus':[], 'ID':[], 'Status':[]}
  for tag in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser']:
    tbl = dict[tag]
    for key, row in tbl['vals'].items():
      for phs in row['phases']:
        ext = '_' + phs
        data['ID'].append (SWITCH_PREFIX + key + ext)
        data['From Bus'].append (row['bus1'] + ext)
        data['To Bus'].append (row['bus2'] + ext)
        if row['open'] == 'true':
          data['Status'].append(0)
        else:
          data['Status'].append(1)
  df = pd.DataFrame (data)
  print ('Writing', len(df), 'switches')
  df.to_excel (xlw, sheet_name='Switch', header=True, index=False)

  xlw.save()

  print ('DER at buses', der_buses)

if __name__ == '__main__':
  if sys.platform == 'win32':
    cfg_json = '../queries/cimhubconfig.json'
  else:
    cfg_json = '../queries/cimhubdocker.json'
  CIMHubConfig.ConfigFromJsonFile (cfg_json)
  xml_file = '../queries/q100.xml'
  case_id = 0
  if len(sys.argv) > 1:
    case_id = int(sys.argv[1])
  fid = CASES[case_id]['fid']
  fname = CASES[case_id]['fname']

  dict = cimhub.load_feeder_dict (xml_file, fid, bTime=False)
  cimhub.summarize_feeder_dict (dict)
#  cimhub.list_dict_table (dict, 'DistSequenceMatrix')

  write_ephasor_model (dict, fname)

  for tbl in ['DistLinesSpacingZ']:
    if len(dict[tbl]['vals']) > 0:
      print ('**** {:s} used in the circuit; but not implemented'.format (tbl))

