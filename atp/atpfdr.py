# Copyright (C) 2021-2023 Battelle Memorial Institute
import cimhub.api as cimhub
import numpy as np
import math
import sys
import scipy.constants

cfg_file = 'cimhubconfig.json'
xml_file = 'q100.xml'

cases = [
  {'fname':'IEEE123_PV', 'fpath':'./', 'fid':'E407CBB6-8C8D-9BC9-589C-AB83FBF0826D',
      'load':0.9, 'pv':1.0, 'r1':0.01, 'x1':0.14, 'r0': 0.01, 'x0':0.14},
  {'fname':'LV_Network', 'fpath':'./LV_Network/', 'fid':'FF06502A-99DA-4AD9-A172-46CA60EDEF55',
      'load':1.0, 'pv':1.0, 'r1':0.06, 'x1':0.26, 'r0': 0.08, 'x0':0.25},
  {'fname':'IEEE13_PV', 'fpath':'./IEEE13/', 'fid':'8122F968-1805-4CDA-826D-E7006985C23B',
      'load':1.0, 'pv':1.0, 'r1':0.16, 'x1':0.64, 'r0': 0.18, 'x0':0.54},
  {'fname':'IEEE9500', 'fpath':'./IEEE9500/', 'fid':'EE71F6C9-56F0-4167-A14E-7F4C71F10EAA',
     'load':1.0, 'pv':1.0, 'r1':0.05, 'x1':1.00, 'r0': 0.20, 'x0':1.00},
  {'fname':'EPRI_J1', 'fpath':'./EPRI_J1/', 'fid':'67AB291F-DCCD-31B7-B499-338206B9828F',
     'load':1.0, 'pv':1.0, 'r1':0.02, 'x1':0.40, 'r0': 0.10, 'x0':0.40},
  {'fname':'SmartDS', 'fpath':'./SmartDS/', 'fid':'43790F23-2733-4F3F-9E57-09866A74F1E9',
     'load':1.0, 'pv':1.0, 'r1':0.01, 'x1':0.10, 'r0': 0.02, 'x0':0.10},
  {'fname':'CEF2', 'fpath':'./CEF2/', 'fid':'ABB82877-0960-4D84-BC17-B85CF7F194CB',
     'load':1.0, 'pv':1.0, 'r1':0.05, 'x1':1.00, 'r0': 0.20, 'x0':1.00},
  {'fname':'Nantucket', 'fpath':'./Nantucket/', 'fid':'CC0FC1EC-DE7F-46DD-9BEA-1D291D7D080E',
     'load':0.7, 'pv':1.0, 'r1':0.02, 'x1':0.40, 'r0': 0.10, 'x0':0.40, 'der_ang':-40.0},
  {'fname':'PNNL', 'fpath':'./PNNL/', 'fid':'0EAA27FD-4D5F-4F29-A928-939CF7D0EBA0',
     'load':0.6, 'pv':1.0, 'r1':0.05, 'x1':1.00, 'r0': 0.20, 'x0':1.00},

  {'fname':'IEEE13_Assets', 'fpath':'./Test/', 'fid':'5B816B93-7A5F-B64C-8460-47C17D6E4B0F',
    'load':1.0, 'pv':1.0, 'r1':0.001, 'x1':0.001, 'r0': 0.001, 'x0':0.001},

  {'fname':'IEEE8500', 'fpath':'./IEEE8500/', 'fid':'4F76A5F9-271D-9EB8-5E31-AA362D86F2C3',
    'load':1.0, 'pv':1.0, 'r1':0.05, 'x1':1.00, 'r0': 0.20, 'x0':1.00},
# {'fname':'AutoHLT', 'fpath':'./Test/', 'fid':'94BEE3C7-5EF1-465A-B872-FF43E62AA81B',
#     'load':1.0, 'pv':1.0, 'r1':0.001, 'x1':0.001, 'r0': 0.001, 'x0':0.001},
# {'fname':'AutoHLTCode', 'fpath':'./Test/', 'fid':'F57CC851-A475-40B8-8964-016013406E51',
#     'load':1.0, 'pv':1.0, 'r1':0.001, 'x1':0.001, 'r0': 0.001, 'x0':0.001},
  ]

PV_LIMIT = 319
DUM_NODES = 0
DUM_NODE_LIMIT = 9999
PV1_DUM_NODES = 31
PV2_DUM_NODES = 31
PV3_DUM_NODES = 49
DELIM = '&'
SQRT3 = math.sqrt(3.0)
SQRT2 = math.sqrt(2.0)
RAD_TO_DEG = 180.0 / math.pi
OMEGA = 2.0 * 60.0 * math.pi
RHO = 100.0
STRAND_RACDC = 1.02
MIN_IMAG = 0.00015
MIN_PNLL = 0.00010
TOPEN = 9990.0

DER_NPOLES = 4.0
DER_H = 1.0
DER_PF = 0.8
DER_ANG = 1.0
DER_J = 2.0e-6*DER_H*math.pow(0.5*DER_NPOLES/OMEGA, 2.0) # multiply by ratedS for Jmicro
# the following is based on a 562.5 kVA, 480 V, 1800 rpm diesel generator
# {rmva}, {rkv}, {vpk0}, {deg0}, {Jmicro} must be exactly 10 characters wide
# {bus} must be exactly 5 characters wide
type59_template = """C < n 1><>< Ampl.  >< Freq.  ><Phase/T0>
59{bus}A  {vpk0____}       60.{deg0____}
  {bus}B  
  {bus}C  
PARAMETER FITTING             2.
C    SI NP                    <    RMVA><     RKV><  AGLINE>
 1 1  1  4                    {rmva____}{rkv_____}        5.
BLANK
C <    RA><      XL><      XD><      XQ><     XDD><     XQQ><    XDDD><    XQQQ>
      .031      .019       3.7       2.2        .2        .2       .14       .19
C <  TDOP><    TQOP><   TDOPP><   TQOPP><      X0><      RN><      XN><    XCAN>
       1.9      .118      .013                 .02      1.E6      1.E6      .019
C MASS#   <   EXTRS><    HICO><     DSR><     DSM><     HSP><     DSD>
 1                1.{Jmicro__}                                     50.
BLANK
C OUT   ID    IQ
  1     1     2
C OUT MECH ANGLE
  2     1
BLANK
  FINISH"""

# these can be reset for each model conversion
LOAD_MULT = 1.0
PV_MULT = 1.0
LOAD_TOTAL = 0.0
PV_TOTAL = 0.0
SM_TOTAL = 0.0
ST_TOTAL = 0.0
PV_COUNT = 0
SM_COUNT = 0
ST_COUNT = 0
R0 = 0.001
X0 = 0.001
R1 = 0.001
X1 = 0.001

def reset_globals(case, pvMult, loadMult):
  global LOAD_TOTAL, PV_TOTAL, SM_TOTAL, ST_TOTAL, LOAD_MULT, PV_MULT, R0, R1, X0, X1, PV_COUNT, ST_COUNT, SM_COUNT
  global DUM_NODES, DER_ANG
  LOAD_TOTAL = 0.0
  PV_TOTAL = 0.0
  SM_TOTAL = 0.0
  ST_TOTAL = 0.0
  PV_COUNT = 0
  SM_COUNT = 0
  ST_COUNT = 0
  DER_ANG = 1.0
  LOAD_MULT = loadMult
  PV_MULT = pvMult
  R0 = 0.001
  X0 = 0.001
  R1 = 0.001
  X1 = 0.001
  DUM_NODES = 0
  if 'r0' in case:
    R0 = case['r0']
  if 'x0' in case:
    X0 = case['x0']
  if 'r1' in case:
    R1 = case['r1']
  if 'x1' in case:
    X1 = case['x1']
  if 'der_ang' in case:
    DER_ANG = case['der_ang']

def AtpNode(bus, phs):
  return '{:5s}{:1s}'.format(bus, phs)

# should preserve order
def GetAtpPhaseList(abc):
  if len(abc) < 1:
    return ['A', 'B', 'C']
  retval = []
  if '1' in abc:
    retval.append('1')
  if '2' in abc:
    retval.append('2')
  if 'A' in abc:
    retval.append('A')
  if 'B' in abc:
    retval.append('B')
  if 'C' in abc:
    retval.append('C')
  return retval

def GetAtpPhaseSequence (seqs):
  seqphs = sorted(seqs.split(':'))
  retval = []
  for e in seqphs:
    phs = e[1:]
    if phs == 's1':
      retval.append('1')
    elif phs == 's2':
      retval.append('2')
    elif phs != 'N':
      retval.append(phs)
  return retval

# look up the lower triangle, i.e., i >= j and both >= 0
# return ohms, ohms, uF
def PhaseMatrixElement (tbl, lname, i, j, llen):
  tok = '{:s}{:s}{:d}{:s}{:d}'.format (lname, DELIM, i, DELIM, j)
  row = tbl[tok]
  r = row['r'] * llen
  xl = row['x'] * llen
  uc = row['b'] * 1.0e6 * llen / OMEGA
  return r, xl, uc

def AtpLoadTo(bus, phs, bDelta):
  if bDelta == True:
    if phs == 'A':
      return AtpNode (bus, 'B')
    if phs == 'B':
      return AtpNode (bus, 'C')
    if phs == 'C':
      return AtpNode (bus, 'A')
  return '      '

def AtpDeltaLaggingNode(bus, phs):
  nd = 'B'
  if phs == 'B':
    nd = 'C'
  elif phs == 'C':
    nd = 'A'
  return AtpNode(bus, nd)

def AtpDeltaLeadingNode(bus, phs):
  nd = 'C'
  if phs == 'B':
    nd = 'A'
  elif phs == 'C':
    nd = 'B'
  return AtpNode(bus, nd)

def AtpXfmrNeutralNode(xfbus, wdgrow):
  if wdgrow['conn'] == 'Y':
    if wdgrow['grounded']:
      if wdgrow['rground'] > 0.0 or wdgrow['xground'] > 0.0:
        return AtpNode (xfbus, 'N')
      else:
        return '      '
  return ''

def PadBlanks(nb):
  retval = ''
  for i in range(nb):
    retval += ' '
  return retval

def AtpRXC(r, x, c):
  return '{:16e}{:16e}{:16e}'.format(r, x, c)

def AtpFit6(x):
  if x == 0.0:
    return '0.0000'
  elif x >= 10000:
    exp = 0
    while x >= 1000:
      x /= 10.0
      exp += 1
    xstr = '{:3d}.E{:d}'.format(int(round(x, 3)), exp)
  elif x >= 1000:
    xstr = '{:6.1f}'.format(x)
  elif x >= 100:
    xstr = '{:6.2f}'.format(x)
  elif x >= 10:
    xstr = '{:6.3f}'.format(x)
  elif x < 0.0:  #TODO: expand
    xstr = '{:6.1f}'.format(x)
  elif x <= 0.001:
    exp = 0
    while x < 10.0:
      x *= 10.0
      exp += 1
    xstr = '{:2d}.E-{:d}'.format(int(round(x)), exp)
  else:
    xstr = '{:6.4f}'.format(x)
  return xstr

def AtpXfmrNeutralNode(xfbus, enum, wdgrow):
  if wdgrow['conn'] == 'Y':
    if wdgrow['grounded']:
      if wdgrow['rground'] > 0.0 or wdgrow['xground'] > 0.0:
        return AtpNode (xfbus, chr(ord('M')+enum))
      else:
        return '      '
    else:
      return AtpNode (xfbus, chr(ord('M')+enum))
  return ''

def AtpXfmrNeutralImpedance(xfbus, enum, wdgrow):
  if wdgrow['conn'] == 'Y' and wdgrow['grounded']:
    if wdgrow['rground'] > 0.0 or wdgrow['xground'] > 0.0:
      return '  {:s}                  {:s}{:s}'.format (AtpNode (xfbus, chr(ord('M')+enum)), 
                                                        AtpFit6(wdgrow['rground']), 
                                                        AtpFit6(wdgrow['xground']))
  return ''

# this is for Transformer Tank
# ph can be A, B, C for Y or D; A, B, C, N, 1 or 2 for I
def AtpTankNodes(enum, end, code, xfbus, atp_buses=None):
  ordph = end['orderedPhases']
  bus = end['bus']
  if atp_buses:
    bus = atp_buses[bus]
  neutral = AtpNode (xfbus, chr(ord('M')+enum))
  if end['grounded']:
    if end['rground'] == 0.0 and end['xground'] == 0.0:
      neutral = '      '
  if ordph == 'Ns1':
    ph1 = 'N'
    ph2 = '1'
  elif ordph == 's1N':
    ph1 = '1'
    ph2 = 'N'
  elif ordph == 'Ns2':
    ph1 = 'N'
    ph2 = '2'
  elif ordph == 's2N':
    ph1 = '2'
    ph2 = 'N'
  elif 's12' in ordph:
    ph1 = '1'
    ph2 = '2'
  elif 's21' in ordph:
    ph1 = '2'
    ph2 = '1'
  else:
    ph1 = ordph[0]
    ph2 = ordph[1]
  if ph1 == 'N':
    return '{:2d}{:s}{:s}'.format(enum, neutral, AtpNode(bus, ph2))
  elif ph2 == 'N':
    return '{:2d}{:s}{:s}'.format(enum, AtpNode(bus, ph1), neutral)
  return '{:2d}{:s}{:s}'.format(enum, AtpNode(bus, ph1), AtpNode(bus, ph2))

# this is for balanced PowerTransformer; ph can be A, B, C for Y or D
def AtpXfmrNodes(xfbus, enum, wdgrow, bEnd1Delta, ph, atp_buses=None):
  bus = wdgrow['bus']
  if atp_buses:
    bus = atp_buses[bus]
  if wdgrow['conn'] == 'Y':
    return '{:2d}{:s}{:s}'.format(enum, AtpNode(bus, ph), AtpXfmrNeutralNode(xfbus, enum, wdgrow))
  else:
    if enum == 1 or bEnd1Delta: # leading Delta
      if ph == 'A':
        ph2 = 'C'
      elif ph == 'B':
        ph2 = 'A'
      elif ph == 'C':
        ph2 = 'B'
    else: # lagging Delta
      if ph == 'A':
        ph2 = 'B'
      elif ph == 'B':
        ph2 = 'C'
      elif ph == 'C':
        ph2 = 'A'
    return '{:2d}{:s}{:s}'.format(enum, AtpNode(bus, ph), AtpNode(bus, ph2))

def AtpXfmr(r, x, v, tap=1.0):
  return AtpFit6(r) + AtpFit6(x) + AtpFit6(v*tap)

def AtpStarEquivalent(wdgs, meshes, regs):
  nwdgs = len(wdgs)
  r = []
  x = []
  v = []
  for i in range(nwdgs):
    if wdgs[i]['conn'] == 'D':
      v.append(wdgs[i]['ratedU']*0.001)
    else:
      v.append(wdgs[i]['ratedU']*0.001/SQRT3)
    r.append(0.0001) # this should at least run for nwdgs > 3
    x.append(0.0001)
  if nwdgs == 2:
    # input impedances are wye equivalent on 3-phase base
    zbase1 = wdgs[0]['ratedU'] * wdgs[0]['ratedU'] / wdgs[0]['ratedS']
    zbase2 = wdgs[1]['ratedU'] * wdgs[1]['ratedU'] / wdgs[1]['ratedS']
    rpu = meshes[0]['r'] / zbase1
    xpu = meshes[0]['x'] / zbase1
    r[0] = 0.5 * rpu * zbase1
    r[1] = 0.5 * rpu * zbase2
    x[0] = 0.5 * xpu * zbase1
    x[1] = 0.5 * xpu * zbase2
  elif nwdgs == 3:
    zbase1 = wdgs[0]['ratedU'] * wdgs[0]['ratedU'] / wdgs[0]['ratedS'] # work on winding 1 Sbase
    zbase2 = wdgs[1]['ratedU'] * wdgs[1]['ratedU'] / wdgs[0]['ratedS']
    zbase3 = wdgs[2]['ratedU'] * wdgs[2]['ratedU'] / wdgs[0]['ratedS']
    r12pu = meshes[0]['r'] / zbase1
    x12pu = meshes[0]['x'] / zbase1
    r13pu = meshes[1]['r'] / zbase1
    x13pu = meshes[1]['x'] / zbase1
    r23pu = meshes[2]['r'] / zbase2
    x23pu = meshes[2]['x'] / zbase2
    r[0] = 0.5 * (r12pu + r13pu - r23pu) * zbase1
    r[1] = 0.5 * (r12pu + r23pu - r13pu) * zbase2
    r[2] = 0.5 * (r13pu + r23pu - r12pu) * zbase3
    x[0] = 0.5 * (x12pu + x13pu - x23pu) * zbase1
    x[1] = 0.5 * (x12pu + x23pu - x13pu) * zbase2
    x[2] = 0.5 * (x13pu + x23pu - x12pu) * zbase3
  # use incr (%) instead of neutralU; we don't know if exporters account for DY connections
  for reg in regs:
    i = reg['wnum'] - 1
    tap = 1.0 + 0.01 * reg['incr'] * (reg['step'] - reg['neutralStep'])
    v[i] *= tap
  # multiply any delta-connected impedances by 3
  for i in range(nwdgs):
    if wdgs[i]['conn'] == 'D':
      r[i] *= 3.0
      x[i] *= 3.0
  return r, x, v

def AtpXfmrCodeStar(wdgs, sctests):
  nwdgs = len(wdgs)
  r = []
  x = []
  v = []
  for i in range(nwdgs):
    if wdgs[i]['conn'] == 'D':
      v.append(wdgs[i]['ratedU']*0.001)
    elif wdgs[i]['conn'] == 'I':
      v.append(wdgs[i]['ratedU']*0.001)
    else:
      v.append(wdgs[i]['ratedU']*0.001/SQRT3)
    r.append(0.0001) # this should at least run for nwdgs > 3
    x.append(0.0001)
  if nwdgs == 2:
    zbase1 = wdgs[0]['ratedU'] * wdgs[0]['ratedU'] / wdgs[0]['ratedS']
    zbase2 = wdgs[1]['ratedU'] * wdgs[1]['ratedU'] / wdgs[1]['ratedS']
    rpu = 1000.0 * sctests[0]['ll'] / wdgs[0]['ratedS']
    zpu = sctests[0]['z'] / zbase1
    xpu = math.sqrt(zpu*zpu - rpu*rpu)
    r[0] = 0.5 * rpu * zbase1
    r[1] = 0.5 * rpu * zbase2
    x[0] = 0.5 * xpu * zbase1
    x[1] = 0.5 * xpu * zbase2
  elif nwdgs == 3:
    zbase1 = wdgs[0]['ratedU'] * wdgs[0]['ratedU'] / wdgs[0]['ratedS'] # work on winding 1 Sbase
    zbase2 = wdgs[1]['ratedU'] * wdgs[1]['ratedU'] / wdgs[0]['ratedS']
    zbase3 = wdgs[2]['ratedU'] * wdgs[2]['ratedU'] / wdgs[0]['ratedS']
    r12pu = 1000.0 * sctests[0]['ll'] / wdgs[0]['ratedS']
    z12pu = sctests[0]['z'] / zbase1
    r13pu = 1000.0 * sctests[1]['ll'] / wdgs[0]['ratedS']
    z13pu = sctests[1]['z'] / zbase1
    r23pu = 1000.0 * sctests[2]['ll'] / wdgs[0]['ratedS']
    z23pu = sctests[2]['z'] / zbase2
    x12pu = math.sqrt(z12pu*z12pu - r12pu*r12pu)
    x13pu = math.sqrt(z13pu*z13pu - r13pu*r13pu)
    x23pu = math.sqrt(z23pu*z23pu - r23pu*r23pu)
    r[0] = 0.5 * (r12pu + r13pu - r23pu) * zbase1
    r[1] = 0.5 * (r12pu + r23pu - r13pu) * zbase2
    r[2] = 0.5 * (r13pu + r23pu - r12pu) * zbase3
    x[0] = 0.5 * (x12pu + x13pu - x23pu) * zbase1
    x[1] = 0.5 * (x12pu + x23pu - x13pu) * zbase2
    x[2] = 0.5 * (x13pu + x23pu - x12pu) * zbase3
  for i in range(nwdgs): # multiply any delta-connected impedances by 3
    if wdgs[i]['conn'] == 'D':
      r[i] *= 3.0
      x[i] *= 3.0
  return r, x, v

def AtpXfmrCodeCore(wdgs, nltest):
  v = nltest['vbase']
  s = nltest['sbase'] 
  ppu = 1000.0 * nltest['nll'] / s
  if ppu < MIN_PNLL:
    ppu = MIN_PNLL
  Impu = 0.0
  Iexc = 0.01 * nltest['iexc']
  if Iexc > ppu:
    Impu = math.sqrt(Iexc*Iexc - ppu*ppu)
  if Impu < MIN_IMAG:
    Impu = MIN_IMAG
  Rmag = v * v / (ppu * s)
  Iss = SQRT2 * Impu * s / v
  Fss = SQRT2 * v / OMEGA
  if wdgs[0]['conn'] == 'Y':
    Fss /= SQRT3
    Iss /= SQRT3
  elif wdgs[0]['conn'] == 'D':
    Iss /= SQRT3
    Rmag *= 3.0
  return Iss, Fss, Rmag

def AtpStarCore(wdgs, core):
  core_b = core['b']
  core_g = core['g']
  core_e = core['enum'] - 1
  core_v = wdgs[core_e]['ratedU']
  core_s = wdgs[core_e]['ratedS']
  core_c = wdgs[core_e]['conn']
  core_s /= 3.0
  if core_c == 'Y':
    core_v /= SQRT3
  Fss = core_v / OMEGA * SQRT2
  if core_g > 0.0:
    Rmag = 1.0 / core_g
  else:
    Rmag = core_v * core_v / MIN_PNLL / core_s
  if core_b > 0.0:
    Iss = SQRT2 * core_b * core_v
  else:
    Iss = MIN_IMAG * SQRT2 * core_s / core_v
  return Iss, Fss, Rmag

def AtpLoadXfmr(zb, v):
  if zb < 0.001:
    return '{:6.5f}{:6.5f}{:6.2f}'.format(0.01*zb, 0.02*zb, v)
  elif zb < 0.1:
    return '{:6.4f}{:6.4f}{:6.2f}'.format(0.01*zb, 0.02*zb, v)
  elif zb < 1.0:
    return '{:6.3f}{:6.3f}{:6.2f}'.format(0.01*zb, 0.02*zb, v)
  elif zb < 1000.0:
    return '{:6.2f}{:6.2f}{:6.2f}'.format(0.01*zb, 0.02*zb, v)
  elif zb < 100000.0:
    return '{:6.1f}{:6.1f}{:6.2f}'.format(0.01*zb, 0.02*zb, v)
  else:
    return ' 1.0E5 2.0E5{:6.2f}'.format(v)

def short_phclass_name(s):
  if s == 'ConcentricNeutralCableInfo':
    return 'CN'
  if s == 'TapeShieldCableInfo':
    return 'TS'
  return 'OH'

def insulation_epsR(s):
  if s == 'asbestosAndVarnishedCambric':
    return 2.3
  elif s == 'butyl':
    return 2.3
  elif s == 'ethylenePropyleneRubber':
    return 2.3
  elif s == 'highMolecularWeightPolyethylene':
    return 2.3
  elif s == 'treeResistantHighMolecularWeightPolyethylene':
    return 2.3
  elif s == 'lowCapacitanceRubber':
    return 2.3
  elif s == 'oilPaper':
    return 2.3
  elif s == 'ozoneResistantRubber':
    return 2.3
  elif s == 'beltedPilc':
    return 2.3
  elif s == 'unbeltedPilc':
    return 2.3
  elif s == 'rubber':
    return 2.3
  elif s == 'siliconRubbber':
    return 2.3
  elif s == 'varnishedCambricCloth':
    return 2.3
  elif s == 'varnishedDacronGlass':
    return 2.3
  elif s == 'crosslinkedPolyethylene':
    return 2.3
  elif s == 'treeRetardantCrosslinkedPolyethylene':
    return 2.3
  elif s == 'highPressureFluidFilled':
    return 2.3
  elif s == 'other':
    return 2.3
  print ('** unrecognized WireInsulationKind', s)
  return 2.3

def conductor_temperature_M(s):
  if s == 'copper':
    return 241.5
  elif s == 'steel':
    return 100.0
  elif s == 'aluminum':
    return 228.1
  elif s == 'aluminumSteel':
    return 100.0
  elif s == 'acsr':
    return 100.0
  elif s == 'aluminumAlloy':
    return 100.0
  elif s == 'aluminumAlloySteel':
    return 100.0
  elif s == 'aaac':
    return 100.0
  elif s == 'other':
    return 100.0
  print ('** unrecognized WireMaterialKind', s)
  return 100.0

def OH_line_constants(row, spc, dict):
  nc = len(spc['y'])
  nphs = len(row['phases'])
  spd = {'y':spc['y'], 'x':spc['x'], 'nph': nphs, 'w': OMEGA, 'rho': RHO, 'len': row['len']}
  phname = row['names'][0]
  wire = dict['DistOverheadWire']['vals'][phname]
  phd = {'od':2.0*wire['rad'], 'id':2.0*wire['corerad'], 'rdc':wire['rdc'], 'rac':wire['r50'], 'gmr':wire['gmr'], 'nb':1, 'sb':0.0}
#  print (spd)
#  print ('Phase Wire', phname, phd)
  nd = None
  if nc > nphs:
    neutral = row['names'][nphs]
    wire = dict['DistOverheadWire']['vals'][neutral]
    nd = {'od':2.0*wire['rad'], 'id':2.0*wire['corerad'], 'rdc':wire['rdc'], 'rac':wire['r50'], 'gmr':wire['gmr'], 'nb':1, 'sb':0.0}
#    print ('  Neutral Wire', neutral, nd)
  zphs, yphs = cimhub.line_constants (spdata=spd, ohdata=phd, ndata=nd)
  cphs = np.imag(yphs) * 1.0e6 / OMEGA # uF

# print_scale = scipy.constants.mile / row['len']
# print ('\nOH Line {:s}-{:s}'.format (row['bus1'], row['bus2']))
# if nphs == 3:
#   zseq = cimhub.phs_to_seq(zphs)
#   cseq = cimhub.phs_to_seq(cphs)
#   z0 = zseq[0,0]*print_scale
#   z1 = zseq[1,1]*print_scale
#   print ('  Z1 = {:.4f} + j{:.4f} [Ohm/mile]'.format(z1.real, z1.imag))
#   print ('  Z0 = {:.4f} + j{:.4f} [Ohm/mile]'.format(z0.real, z0.imag))
#   print ('  C1 = {:.4f} [nF/mile]'.format (cseq[1,1].real*print_scale*1000.0))
#   print ('  C0 = {:.4f} [nF/mile]'.format (cseq[0,0].real*print_scale*1000.0))
# else:
#   cimhub.print_matrix ('Zphs [Ohm/mile]', zphs*print_scale)
#   cimhub.print_matrix ('Cphs [nF/mile]', cphs*print_scale*1000.0)

  return zphs, cphs

#DistConcentricNeutralCable: key,['id', 'rad', 'corerad', 'gmr', 'rdc', 'r25', 'r50', 'r75', 'amps', 'ins', 'insmat', 'insthick', 'diacore', 'diains', 'diascreen', 'diajacket', 'dianeut', 'sheathneutral', 'strand_cnt', 'strand_rad', 'strand_gmr', 'strand_rdc']
#cn_250,_5CF2A8A3-B30E-4907-8F88-5B3079AEE87E,0.0072009,0,0.00521208,0.00024976685,0.00025476219,0.00025476219,0.00025476219,260,true,crosslinkedPolyethylene,0.005588,0.015748,0.026924,0.02950972,0.032766,0.032766,false,13,0.00081407,0.000633984,0.0092411566

#cndata_250 = cimhub.convert_cndata_to_si ({'dia_ph': 0.567, 'gmr_ph':0.2052, 'rac_ph': 0.41, 'eps': 2.3,
#  'ins': 0.220, 'dia_ins': 1.06, 'dia_cable': 1.29,
#  'k': 13, 'dia_s': 0.0641, 'gmr_s': 0.02496, 'rac_s': 14.8722})
def CN_line_constants(row, spc, dict):
  nc = len(spc['y'])
  nphs = len(row['phases'])
  spd = {'y':spc['y'], 'x':spc['x'], 'nph': nphs, 'w': OMEGA, 'rho': RHO, 'len': row['len']}
  phname = row['names'][0]
  wire = dict['DistConcentricNeutralCable']['vals'][phname]
  phd = {'dia_ph':2.0*wire['rad'], 'eps': insulation_epsR(wire['insmat']), 'rac_ph':wire['r50'], 'gmr_ph':wire['gmr'],
    'ins':wire['insthick'], 'dia_ins':wire['diains'], 'dia_cable':wire['dianeut'], 'k':wire['strand_cnt'],
    'dia_s':2.0*wire['strand_rad'], 'gmr_s':wire['strand_gmr'], 'rac_s':wire['strand_rdc']*STRAND_RACDC}
#  print ('\nCN', spd)
#  print (phname, phd)
  nd = None
  if nc > nphs:
    neutral = row['names'][nphs]
    wire = dict['DistOverheadWire']['vals'][neutral]
    nd = {'od':2.0*wire['rad'], 'id':2.0*wire['corerad'], 'rdc':wire['rdc'], 'rac':wire['r50'], 'gmr':wire['gmr'], 'nb':1, 'sb':0.0}
#    print ('  Neutral Wire', neutral, nd)
  zphs, yphs = cimhub.line_constants (spdata=spd, cndata=phd, ndata=nd)
  cphs = np.imag(yphs) * 1.0e6 / OMEGA # uF
# print_scale = scipy.constants.mile / row['len']
# print ('\nCN Line {:s}-{:s}'.format (row['bus1'], row['bus2']))
# if nphs == 3:
#   zseq = cimhub.phs_to_seq(zphs)
#   cseq = cimhub.phs_to_seq(cphs)
#   z0 = zseq[0,0]*print_scale
#   z1 = zseq[1,1]*print_scale
#   print ('  Z1 = {:.4f} + j{:.4f} [Ohm/mile]'.format(z1.real, z1.imag))
#   print ('  Z0 = {:.4f} + j{:.4f} [Ohm/mile]'.format(z0.real, z0.imag))
#   print ('  C1 = {:.4f} [nF/mile]'.format (cseq[1,1].real*print_scale*1000.0))
#   print ('  C0 = {:.4f} [nF/mile]'.format (cseq[0,0].real*print_scale*1000.0))
# else:
#   cimhub.print_matrix ('Zphs [Ohm/mile]', zphs*print_scale)
#   cimhub.print_matrix ('Cphs [nF/mile]', cphs*print_scale*1000.0)
  return zphs, cphs

#DistTapeShieldCable: key,['rad', 'corerad', 'gmr', 'rdc', 'r25', 'r50', 'r75', 'amps', 'ins', 'insmat', 'insthick', 'diacore', 'diains', 'diascreen', 'diajacket', 'sheathneutral', 'tapelap', 'tapethickness']
#ts_1/0,0.0046736,0,0.00338328,0.00059091182,0.00060273006,0.00060273006,0.00060273006,165,true,crosslinkedPolyethylene,0.005588,0.009652,0.020828,0.022098,0.026924,true,20,0.000127

#tsdata_1oCu = cimhub.convert_tsdata_to_si ({'dia': 0.368, 'gmr': 0.13320, 'rac': 0.97, 'eps': 2.3,
#  'ins': 0.220, 'dia_ins': 0.82, 'dia_cable': 1.06, 'dia_shield': 0.88, 'tape': 0.005, 'lap_pct': 20.0})
def TS_line_constants(row, spc, dict):
  nc = len(spc['y'])
  nphs = len(row['phases'])
  spd = {'y':spc['y'], 'x':spc['x'], 'nph': nphs, 'w': OMEGA, 'rho': RHO, 'len': row['len']}
  phname = row['names'][0]
  wire = dict['DistTapeShieldCable']['vals'][phname]
  phd = {'dia':2.0*wire['rad'], 'eps': insulation_epsR(wire['insmat']), 'rac':wire['r50'], 'gmr':wire['gmr'],
    'ins':wire['insthick'], 'dia_ins':wire['diains'], 'dia_cable':wire['diajacket'], 'dia_shield':wire['diascreen'],
    'tape':wire['tapethickness'], 'lap_pct':wire['tapelap']}
#  print ('\nTS', spd)
#  print (phname, phd)
  nd = None
  if nc > nphs:
    neutral = row['names'][nphs]
    wire = dict['DistOverheadWire']['vals'][neutral]
    nd = {'od':2.0*wire['rad'], 'id':2.0*wire['corerad'], 'rdc':wire['rdc'], 'rac':wire['r50'], 'gmr':wire['gmr'], 'nb':1, 'sb':0.0}
#    print ('  Neutral Wire', neutral, nd)
  zphs, yphs = cimhub.line_constants (spdata=spd, tsdata=phd, ndata=nd)
  cphs = np.imag(yphs) * 1.0e6 / OMEGA # uF
# print_scale = scipy.constants.mile / row['len']
# print ('\nTS Line {:s}-{:s}'.format (row['bus1'], row['bus2']))
# if nphs == 3:
#   zseq = cimhub.phs_to_seq(zphs)
#   cseq = cimhub.phs_to_seq(cphs)
#   z0 = zseq[0,0]*print_scale
#   z1 = zseq[1,1]*print_scale
#   print ('  Z1 = {:.4f} + j{:.4f} [Ohm/mile]'.format(z1.real, z1.imag))
#   print ('  Z0 = {:.4f} + j{:.4f} [Ohm/mile]'.format(z0.real, z0.imag))
#   print ('  C1 = {:.4f} [nF/mile]'.format (cseq[1,1].real*print_scale*1000.0))
#   print ('  C0 = {:.4f} [nF/mile]'.format (cseq[0,0].real*print_scale*1000.0))
# else:
#   cimhub.print_matrix ('Zphs [Ohm/mile]', zphs*print_scale)
#   cimhub.print_matrix ('Cphs [nF/mile]', cphs*print_scale*1000.0)
  return zphs, cphs

def convert_one_atp_model (query_file, fid, fname, fpath, bSummaryAndMap=True):
  global LOAD_TOTAL, PV_TOTAL, SM_TOTAL, ST_TOTAL, LOAD_MULT, PV_MULT, R0, R1, X0, X1, SM_COUNT, PV_COUNT, ST_COUNT
  global DELIM, DUM_NODES

  dict = cimhub.load_feeder_dict (query_file, fid, bTime=False, keyDelimiter=DELIM, cfg_file=cfg_file)
  if bSummaryAndMap:
    cimhub.summarize_feeder_dict (dict)
#  cimhub.list_dict_table (dict, 'DistLinesCodeZ')
#  cimhub.list_dict_table (dict, 'DistSolar')
#  cimhub.list_dict_table (dict, 'DistPowerXfmrWinding')
#  cimhub.list_dict_table (dict, 'DistXfmrTank')
#  cimhub.list_dict_table (dict, 'DistPhaseMatrix')
#  cimhub.list_dict_table (dict, 'DistSequenceMatrix')
#  cimhub.list_dict_table (dict, 'DistStorage')
#  cimhub.list_dict_table (dict, 'DistSyncMachine')
#  cimhub.list_dict_table (dict, 'DistRegulatorBanked')

  atp_buses = {}  # find the ATP bus number from the CIM ConnectivityNode name
  cim_buses = {}  # find the CIM ConnectivityNode name from the ATP bus number
  bus_kv = {}     # nominal voltage (line-to-line kV) from the CIM ConnectivityNode name
  idx = 1
  for key, row in dict['DistBus']['vals'].items():
    bus = str(idx)
    atp_buses[key] = bus
    cim_buses[bus] = key
    bus_kv[key] = 0.001 * row['nomv']
    idx += 1
  if bSummaryAndMap:
    print ('Mapping {:d} buses to {:s}.atpmap'.format (idx-1, fname))
    fp = open (fpath + fname + '.atpmap', mode='w')
    print ('ATP Bus   CIM Bus               Bus kV', file=fp)
    for key in cim_buses:
      print ('{:6s}    {:20s} {:7.3f}'.format (key, cim_buses[key], bus_kv[cim_buses[key]]), file=fp)
    print ('\nCIM Bus              ATP Bus    Bus kV', file=fp)
    for key in atp_buses:
      print ('{:20s} {:6s}    {:7.3f}'.format (key, atp_buses[key], bus_kv[key]), file=fp)
    fp.close()

  ap = open (fpath + fname + '_net.atp', mode='w')
  print ('C file: {:s}, Load Mult={:.3f}, PV Mult={:.3f}'.format (fname, LOAD_MULT, PV_MULT), file=ap)
  print ('$VINTAGE,0', file=ap)
  for key, row in dict['DistSubstation']['vals'].items():
    bus = atp_buses[row['bus']]
    vmag = row['vmag'] * SQRT2 / SQRT3
    vang = row['vang'] * RAD_TO_DEG
    if not R0:
      R0 = row['r0']
    if not X0:
      X0 = row['x0']
    if not R0:
      R1 = row['r1']
    if not X1:
      X1 = row['x1']
    print ('C =============================================================================', file=ap)
    print ('C Substation {:s} at {:s}'.format (key, row['bus']), file=ap)
    print ('/SOURCE', file=ap)
    print ('C < n 1><>< Ampl.  >< Freq.  ><Phase/T0><   A1   ><   T1   >< TSTART >< TSTOP  >', file=ap)
    for ph in ['A', 'B', 'C']:
      print ('14{:s}  {:10.3f}{:10.3f}{:10.3f}{:s}{:10.3f}{:10.3f}'.format (AtpNode ('THEV', ph), 
                                                                            vmag, 60.0, vang, 
                                                                            PadBlanks(20), -1.0, 9999.0), file=ap)
      vang -= 120.0
    print ('/BRANCH', file=ap)
    print ('C < n1 >< n2 ><ref1><ref2>< R  >< X  >< C  >', file=ap)
    print ('51THEV ASBUS A            {:s}{:s}'.format (AtpFit6 (R0), AtpFit6 (X0)), file=ap)
    print ('52THEV BSBUS B            {:s}{:s}'.format (AtpFit6 (R1), AtpFit6 (X1)), file=ap)
    print ('53THEV CSBUS C', file=ap)
    print ('/SWITCH', file=ap)
    print ('C < n 1>< n 2>< Tclose ><Top/Tde ><   Ie   ><Vf/CLOP ><  type  >               1', file=ap)
    for ph in ['A', 'B', 'C']:
      print ('  {:6s}{:6s}{:10.3f}{:10.3f}                    MEASURING                1'.format (AtpNode ('SBUS', ph), 
        AtpNode (bus, ph), -1.0, TOPEN), file=ap)
  print ('/BRANCH', file=ap)

  # organize the balanced PowerTransformers and associated regulators
  PowerXfmrs = {}
  xfbusnum = 1
  for key in dict['DistPowerXfmrWinding']['vals']:
    pname = key.split(DELIM)[0]
    if pname in PowerXfmrs:
      PowerXfmrs[pname]['nwdg'] += 1
    else:
      PowerXfmrs[pname] = {'nwdg':1, 'regs': []}
  for key, row in dict['DistRegulatorBanked']['vals'].items():
    if row['pname'] in PowerXfmrs:
      PowerXfmrs[row['pname']]['regs'].append(row)
  for pname, row in PowerXfmrs.items():
    nwdg = row['nwdg']
    regs = row['regs']
    wdgs = []
    meshes = []
    for i in range(nwdg):
      wdgs.append (dict['DistPowerXfmrWinding']['vals']['{:s}{:s}{:d}'.format(pname, DELIM, i+1)])
      for j in range(i+1, nwdg):
        meshes.append (dict['DistPowerXfmrMesh']['vals']['{:s}{:s}{:d}{:s}{:d}'.format(pname, DELIM, i+1, DELIM, j+1)])
    print ('C =============================================================================', file=ap)
    print ('C transformer {:s}, {:d} windings from {:s}'.format (pname, nwdg, wdgs[0]['bus']), file=ap)
    if nwdg > 3:
      print ('C *** too many windings for saturable transformer component', file=ap)
      print ('*** Transformer {:s} has {:d} windings, but only 2 or 3 supported'.format(pname, nwdg))
      continue
    Iss, Fss, Rmag = AtpStarCore (wdgs, dict['DistPowerXfmrCore']['vals'][pname])
    xfbus = 'X' + str(xfbusnum)
    if wdgs[0]['conn'] == 'D':
      bEnd1Delta = True
    else:
      bEnd1Delta = False
    r, x, v = AtpStarEquivalent (wdgs, meshes, regs)
    for ph in ['A', 'B', 'C']:
      if ph == 'A':
        print ('C TRANSFORMER             < Iss>< Fss><BusT><Rmag>', file=ap)
        print ('  TRANSFORMER             {:s}{:s}{:s}{:s}'.format (AtpFit6 (Iss), AtpFit6 (Fss), 
                                                                    AtpNode (xfbus, 'X'),
                                                                    AtpFit6 (Rmag)), file=ap)
        print ('{:>16s}{:>16s}'.format (AtpFit6 (Iss), AtpFit6 (Fss)), file=ap)
        print ('            9999', file=ap)
        print ('C < n 1>< n 2><ref1><ref2><   R><   X><  KV>', file=ap)
        for i in range(nwdg):
          print ('{:s}{:s}{:s}'.format (AtpXfmrNodes(xfbus, i+1, wdgs[i], bEnd1Delta, ph, atp_buses), 
                                        PadBlanks(12), AtpXfmr (r[i], x[i], v[i])), file=ap)
      else:
        print ('  TRANSFORMER {:s}{:s}{:s}'.format (AtpNode (xfbus, 'X'), PadBlanks(18), 
                                                    AtpNode (xfbus, chr(ord(ph)+23))), file=ap)
        for i in range(nwdg):
          print ('{:s}'.format (AtpXfmrNodes(xfbus, i+1, wdgs[i], bEnd1Delta, ph, atp_buses)), file=ap)
    xfbusnum += 1

  # organize the transformer codes for tanks (there are no "banks" in ATP)
  xfcodes = {}
  for key, row in dict['DistXfmrCodeRating']['vals'].items():
    cname = key.split(DELIM)[0]
    if cname in xfcodes:
      xfcodes[cname]['nwdg'] += 1
    else:
      xfcodes[cname] = {'nwdg':1}
  for cname, row in xfcodes.items():
    nwdg = row['nwdg']
    nltest = dict['DistXfmrCodeNLTest']['vals'][cname]
    wdgs = []
    sctests = []
    for i in range(nwdg):
      wdgs.append (dict['DistXfmrCodeRating']['vals']['{:s}{:s}{:d}'.format(cname, DELIM, i+1)])
      for j in range(i+1, nwdg):
        sctests.append (dict['DistXfmrCodeSCTest']['vals']['{:s}{:s}{:d}{:s}{:d}'.format(cname, DELIM, i+1, DELIM, j+1)])
    row['r'], row['x'], row['v'] = AtpXfmrCodeStar (wdgs, sctests)
    row['Iss'], row['Fss'], row['Rmag'] = AtpXfmrCodeCore (wdgs, nltest)
    row['wdgs'] = wdgs

  # create one transformer per tank; they happen to be ordered by bank
  XfmrTanks = {}
  for key, row in dict['DistXfmrTank']['vals'].items():
    keys = key.split(DELIM)
    pname = keys[0]
    tname = keys[1]
    if tname not in XfmrTanks:
      XfmrTanks[tname] = {'pname': pname, 'nwdg': 0, 'regs':[]}
    XfmrTanks[tname]['nwdg'] += 1
  for key, row in dict['DistRegulatorTanked']['vals'].items():
    if row['tname'] in XfmrTanks:
      XfmrTanks[row['tname']]['regs'].append(row)
  for tname, row in XfmrTanks.items():
    pname = row['pname']
    nwdg = row['nwdg']
    regs = row['regs']
    taps = []
    ends = []
    for i in range(nwdg):
      ends.append (dict['DistXfmrTank']['vals']['{:s}{:s}{:s}{:s}{:d}'.format(pname, DELIM, tname, DELIM, i+1)])
      taps.append (1.0)
    for reg in regs:
      i = reg['wnum'] - 1
      taps[i] = 1.0 + 0.01 * reg['incr'] * (reg['step'] - reg['neutralStep'])
    xfcode = xfcodes[ends[0]['xfmrcode']]
    wdgs = xfcode['wdgs']
    r = xfcode['r']
    x = xfcode['x']
    v = xfcode['v']
    Iss = xfcode['Iss']
    Fss = xfcode['Fss']
    Rmag = xfcode['Rmag']
    xfbus = 'X' + str(xfbusnum)
    print ('C =============================================================================', file=ap)
    print ('C transformer tank {:s} from {:s}'.format (tname, ends[0]['bus']), file=ap)
    print ('C TRANSFORMER             < Iss>< Fss><BusT><Rmag>', file=ap)
    print ('  TRANSFORMER             {:s}{:s}{:s}{:s}'.format (AtpFit6 (Iss), 
                                                                AtpFit6 (Fss), 
                                                                AtpNode (xfbus, 'X'),
                                                                AtpFit6 (Rmag)), file=ap)
    print ('{:>16s}{:>16s}'.format (AtpFit6 (Iss), AtpFit6 (Fss)), file=ap)
    print ('            9999', file=ap)
    print ('C < n 1>< n 2><ref1><ref2><   R><   X><  KV>', file=ap)
    # decide whether to write this as a balanced tank, or I tanks. may not handle all use cases yet
    phases = ends[0]['orderedPhases']
    if (wdgs[0] != 'I') and ('A' in phases) and ('B' in phases) and ('C' in phases):
      bEnd1Delta = False
      if wdgs[0]['conn'] == 'D':
        bEnd1Delta = True
      for i in range(len(ends)):
        ends[i]['conn'] = wdgs[i]['conn']
      for ph in ['A', 'B', 'C']:
        if ph == 'A':
          for i in range(nwdg):
            print ('{:s}{:s}{:s}'.format (AtpXfmrNodes(xfbus, i+1, ends[i], bEnd1Delta, ph, atp_buses), 
                                          PadBlanks(12), AtpXfmr (r[i], x[i], v[i])), file=ap)
        else:
          print ('  TRANSFORMER {:s}{:s}{:s}'.format (AtpNode (xfbus, 'X'), PadBlanks(18), 
                                                      AtpNode (xfbus, chr(ord(ph)+23))), file=ap)
          for i in range(nwdg):
            print ('{:s}'.format (AtpXfmrNodes(xfbus, i+1, ends[i], bEnd1Delta, ph, atp_buses)), file=ap)
    else:
      for i in range(nwdg):
        print ('{:s}{:s}{:s}'.format (AtpTankNodes(i+1, ends[i], wdgs[i], xfbus, atp_buses), 
                                    PadBlanks(12), AtpXfmr (r[i], x[i], v[i], taps[i])), file=ap)
    xfbusnum += 1

  # assemble position arrays for line spacings
  Spacings = {}
  for key, row in dict['DistLineSpacing']['vals'].items():
    sname = key.split(DELIM)[0]
    if sname not in Spacings:
      Spacings[sname] = {'x':[], 'y': []}
    Spacings[sname]['x'].append(row['x'])
    Spacings[sname]['y'].append(row['y'])

#  for key, row in Spacings.items():
#    print (key, row)

  # count conductors and phases per spacing-defined line, collect the common attributes
  SpacingLines = {}
  for key, row in dict['DistLinesSpacingZ']['vals'].items():
    lname = key.split(DELIM)[0]
    if lname in SpacingLines:
      SpacingLines[lname]['nc'] += 1
    else:
      SpacingLines[lname] = {'nc':1, 'phases':[], 'bus1': row['bus1'], 'bus2': row['bus2'], 'len': row['len'], 
        'spacing': row['spacing'], 'types': [], 'names': []}
    SpacingLines[lname]['types'].append(short_phclass_name(row['phclass']))
    SpacingLines[lname]['names'].append(row['phname'])
    if 'N' not in row['phs']:
      SpacingLines[lname]['phases'].append(row['phs'])

  for key, row in SpacingLines.items():
    spc = Spacings[row['spacing']]
    line_type = 'OH'
    if 'TS' in row['types']:
      line_type = 'TS'
      zphs, cphs = TS_line_constants(row, spc, dict)
    elif 'CN' in row['types']:
      line_type = 'CN'
      zphs, cphs = CN_line_constants(row, spc, dict)
    else:
      zphs, cphs = OH_line_constants(row, spc, dict)
    aphs = row['phases'] # already in sequence order
    nphs = len(aphs)
    bus1 = atp_buses[row['bus1']]
    bus2 = atp_buses[row['bus2']]
    print ('C =============================================================================', file=ap)
    print ('C {:s} line {:s} from {:s} to {:s}'.format (line_type, key, row['bus1'], row['bus2']), file=ap)
    print ('C   {:.3f}m of {:s} on {:s}'.format (row['len'], row['names'][0], row['spacing']), file=ap)
    print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
    print ('$VINTAGE,1', file=ap)
    for i in range(nphs):
      for j in range(i+1):
        r = zphs[i,j].real
        xl = zphs[i,j].imag
        uc = cphs[i,j]
        if j == 0:
          print ('{:>2d}'.format(i+1) + AtpNode (bus1, aphs[i]) + AtpNode (bus2, aphs[i]) + PadBlanks (12) + AtpRXC (r, xl, uc), file=ap)
        else:
          print (PadBlanks (26) + AtpRXC (r, xl, uc), file=ap)
    print ('$VINTAGE,0', file=ap)

  PhaseMatrices = []
  for key, row in dict['DistPhaseMatrix']['vals'].items():
    sname = key.split(DELIM)[0]
    if sname not in PhaseMatrices:
      PhaseMatrices.append(sname)

  for key, row in dict['DistLinesCodeZ']['vals'].items():
    aphs = GetAtpPhaseSequence (row['seqs'])
    nphs = len(aphs)
    bus1 = atp_buses[row['bus1']]
    bus2 = atp_buses[row['bus2']]
    lname = row['lname']  # look for DistPhaseMatrix first, then DistSequenceMatrix
    llen = row['len']
    print ('C =============================================================================', file=ap)
    print ('C line {:s} from {:s} to {:s}'.format (key, row['bus1'], row['bus2']), file=ap)
    if lname in PhaseMatrices:
      print ('C   {:.3f}m of phase matrix {:s}'.format (llen, lname), file=ap)
      print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
  #    print ('C < n 1>< n 2><ref1><ref2><     R    ><    A     ><    B     ><  Length  ><><>0', file=ap)
      print ('$VINTAGE,1', file=ap)
      for i in range(nphs):
        for j in range(i+1):
          r, xl, uc = PhaseMatrixElement (dict['DistPhaseMatrix']['vals'], lname, i+1, j+1, llen)
          if j == 0:
            print ('{:>2d}'.format(i+1) + AtpNode (bus1, aphs[i]) + AtpNode (bus2, aphs[i]) + PadBlanks (12) + AtpRXC (r, xl, uc), file=ap)
          else:
            print (PadBlanks (26) + AtpRXC (r, xl, uc), file=ap)
      print ('$VINTAGE,0', file=ap)
    elif lname in dict['DistSequenceMatrix']['vals']:
      mat = dict['DistSequenceMatrix']['vals'][lname]
      rs = llen * (mat['r0']+2.0*mat['r1']) / 3.0
      rm = llen * (mat['r0']-mat['r1']) / 3.0
      xs = llen * (mat['x0']+2.0*mat['x1']) / 3.0
      xm = llen * (mat['x0']-mat['x1']) / 3.0
      cs = llen * 1.0e6 * (mat['b0']+2.0*mat['b1']) / 3.0 / OMEGA
      cm = llen * 1.0e6 * (mat['b0']-mat['b1']) / 3.0 / OMEGA
      print ('C   {:.3f}m of sequence matrix {:s}'.format (llen, lname), file=ap)
      print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
      print ('$VINTAGE,1', file=ap)
      print ('1 {:5s}A{:5s}A'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rs, xs, cs), file=ap)
      print ('2 {:5s}B{:5s}B'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rm, xm, cm), file=ap)
      print (PadBlanks(26) + AtpRXC(rs, xs, cs), file=ap)
      print ('3 {:5s}C{:5s}C'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rm, xm, cm), file=ap)
      print (PadBlanks(26) + AtpRXC(rm, xm, cm), file=ap)
      print (PadBlanks(26) + AtpRXC(rs, xs, cs), file=ap)
      print ('$VINTAGE,0', file=ap)
    else:
      print ('C could not find the PerLengthImpedance {:s}'.format(lname), file=ap)
      print ('** could not find PerLengthImpedance {:s} for line {:s}'.format (lname, key))

  for key, row in dict['DistLinesInstanceZ']['vals'].items():
    bus1 = atp_buses[row['bus1']]
    bus2 = atp_buses[row['bus2']]
    rs = (row['r0']+2.0*row['r']) / 3.0
    rm = (row['r0']-row['r']) / 3.0
    xs = (row['x0']+2.0*row['x']) / 3.0
    xm = (row['x0']-row['x']) / 3.0
    cs = 1.0e6 * (row['b0']+2.0*row['b']) / 3.0 / OMEGA
    cm = 1.0e6 * (row['b0']-row['b']) / 3.0 / OMEGA
    print ('C =============================================================================', file=ap)
    print ('C line {:s} from {:s} to {:s}'.format (key, row['bus1'], row['bus2']), file=ap)
    print ('C   per-instance sequence parameters for {:.3f}m'.format(row['len']), file=ap)
    print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
    print ('$VINTAGE,1', file=ap)
    print ('1 {:5s}A{:5s}A'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rs, xs, cs), file=ap)
    print ('2 {:5s}B{:5s}B'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rm, xm, cm), file=ap)
    print (PadBlanks(26) + AtpRXC(rs, xs, cs), file=ap)
    print ('3 {:5s}C{:5s}C'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rm, xm, cm), file=ap)
    print (PadBlanks(26) + AtpRXC(rm, xm, cm), file=ap)
    print (PadBlanks(26) + AtpRXC(rs, xs, cs), file=ap)
    print ('$VINTAGE,0', file=ap)

  for key, row in dict['DistSeriesCompensator']['vals'].items():
    bus1 = atp_buses[row['bus1']]
    bus2 = atp_buses[row['bus2']]
    print ('C =============================================================================', file=ap)
    print ('C series reactor {:s} from {:s} to {:s}'.format (key, row['bus1'], row['bus2']), file=ap)
    print ('C < n1 >< n2 ><ref1><ref2>< R  >< X  >< C  >', file=ap)
    print ('51{:5s}A{:5s}A            {:s}{:s}'.format (bus1, bus2, AtpFit6 (row['r0']), AtpFit6 (row['x0'])), file=ap)
    print ('52{:5s}B{:5s}B            {:s}{:s}'.format (bus1, bus2, AtpFit6 (row['r']), AtpFit6 (row['x'])), file=ap)
    print ('53{:5s}C{:5s}C'.format(bus1, bus2), file=ap)

  for key, row in dict['DistCapacitor']['vals'].items():
    kv = 0.001 * row['nomu']
    kvar = 1000.0 * row['bsection'] * kv * kv
    cuf = 1000.0 * kvar / kv / kv / OMEGA
    bus = atp_buses[row['bus']]
    print ('C =============================================================================', file=ap)
    print ('C capacitor {:s} at {:s} is {:.2f} kVAR'.format (key, row['bus'], kvar), file=ap)
    print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
    print ('$VINTAGE,1', file=ap)
    for ph in GetAtpPhaseList (row['phases']):
      print ('  ' + AtpNode (bus, ph) + PadBlanks(50) + '{:16e}'.format(cuf), file=ap)
    print ('$VINTAGE,0', file=ap)

  for key, row in dict['DistLoad']['vals'].items():
    bus = atp_buses[row['bus']]
    phases = GetAtpPhaseList (row['phases'])
    nph = len(phases)
    kv = 0.001 * row['basev']
    kw = 0.001 * row['p'] * LOAD_MULT
    kvar = 0.001 * row['q'] * LOAD_MULT
    LOAD_TOTAL += kw
    if row['conn'] == 'D':
      bDelta = True
      kvld = kv
    else:
      bDelta = False
      kvld = kv / SQRT3
    print ('C =============================================================================', file=ap)
    print ('C load {:s} at {:s} is {:.3f} + j{:.3f} kVA'.format (key, row['bus'], kw, kvar), file=ap)
    print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
    print ('$VINTAGE,1', file=ap)
    rload = nph * 1000.0 * kvld * kvld / kw
    if kvar > 0.0:
      xload = nph * 1000.0 * kvld * kvld / kvar
    else:
      xload = 0.0
    for ph in phases:
      bus_from = AtpNode (bus, ph)
      bus_to = AtpLoadTo (bus, ph, bDelta)
      print ('  ' + bus_from + bus_to + PadBlanks(12) + '{:16e}'.format(rload), file=ap)
      if xload > 0.0:
        print ('  ' + bus_from + bus_to + PadBlanks(28) + '{:16e}'.format(xload), file=ap)
    print ('$VINTAGE,0', file=ap)

  for key, row in dict['DistStorage']['vals'].items():
    bus = atp_buses[row['bus']]
    phases = GetAtpPhaseList (row['phases'])
    nph = len(phases)
    vbase = row['ratedU']
    sbase = row['ratedS']
    wtotal = row['maxP']  # regardless of the state
    ST_TOTAL += 0.001 * wtotal
    ST_COUNT += 1
    pfang = 0.0
    if row['q'] != 0.0:
      if wtotal != 0.0:
        pfang = math.atan2(row['q]'], wtotal) * RAD_TO_DEG
    vtrip = 0.5 * vbase / SQRT3
    if nph == 1:
      vbase /= SQRT3
      irmsmx = row['ipu'] * sbase / vbase
    elif nph == 2:
      irmsmx = row['ipu'] * sbase / vbase
      vtrip = 0.5 * vbase
    else:
      irmsmx = row['ipu'] * sbase / vbase / SQRT3
    sBus1 = AtpNode (bus, phases[0]).replace(' ', '#')
    sName = 'ST{:03d}'.format (ST_COUNT)
    sW = AtpFit6 (wtotal)
    sImax = AtpFit6 (irmsmx)
    sUV = AtpFit6 (vtrip)
    sUT = AtpFit6 (0.16)
    sPF = AtpFit6 (pfang)
    print ('C =============================================================================', file=ap)
    print ('C storage {:s} at {:s} is {:.3f} kVA discharging max {:.3f} kW'.format (key, row['bus'], sbase*0.001, wtotal*0.001), file=ap)
    if nph == 1:
      print ('$INCLUDE,TACSPV1.PCH,{:s},{:s},{:s},{:s},{:s},{:s},{:s}'.format(sBus, sName, sW, sImax, sUV, sUT, sPF), file=ap)
      DUM_NODES += PV1_DUM_NODES
    elif nph == 2:
      sBus2 = AtpNode (bus, phases[1]).replace(' ', '#')
      print ('$INCLUDE,TACSPV2.PCH,{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s}'.format(sBus1, sBus2, sName, sW, sImax, sUV, sUT, sPF), file=ap)
      DUM_NODES += PV2_DUM_NODES
    elif nph == 3:
      sBus = '{:5s}'.format(bus).replace(' ', '#')
      sV0 = AtpFit6 (vbase)
      sV02 = AtpFit6 (vbase*vbase)
      sVWc = AtpFit6 (vbase/376.9911)
      print ('$INCLUDE,TACSPV3.PCH,{:s},{:s},{:s},{:s},{:s},{:s},{:s} $$'.format(sBus, sName, sW, sImax, sUV, sUT, sPF), file=ap)
      print ('  ,{:s},{:s},{:s}'.format(sV0, sV02, sVWc), file=ap)
      DUM_NODES += PV3_DUM_NODES
    else:
      print ('C *** {:d}-phase call is not supported'.format(nph), file=ap)

  bCurtailed = False
  for key, row in dict['DistSolar']['vals'].items():
    bus = atp_buses[row['bus']]
    phases = GetAtpPhaseList (row['phases'])
    nph = len(phases)
    vbase = row['ratedU']
    sbase = row['ratedS']
    wtotal = row['p'] * PV_MULT
    if (nph < 3) and (PV_COUNT > PV_LIMIT):
      if not bCurtailed:
        print ('*** Curtailing PV installations, limit is about {:d}'.format(PV_LIMIT))
      bCurtailed = True
      continue
    PV_TOTAL += 0.001 * wtotal
    PV_COUNT += 1
    pfang = 0.0
    if row['q'] != 0.0:
      if wtotal != 0.0:
        pfang = math.atan2(row['q'], wtotal) * RAD_TO_DEG
    vtrip = 0.5 * vbase / SQRT3
    if nph == 1:
      vbase /= SQRT3
      irmsmx = row['ipu'] * sbase / vbase
    elif nph == 2:
      vtrip = 0.5 * vbase
      irmsmx = row['ipu'] * sbase / vbase
    else:
      irmsmx = row['ipu'] * sbase / vbase / SQRT3
    sBus1 = AtpNode (bus, phases[0]).replace(' ', '#')
    sName = 'PV{:03d}'.format (PV_COUNT)
    sW = AtpFit6 (wtotal)
    sImax = AtpFit6 (irmsmx)
    sUV = AtpFit6 (vtrip)
    sUT = AtpFit6 (0.16)
    if (abs(pfang) < 0.001) or (abs(pfang) > 100.0) or (pfang < 0.0):  # TODO: verify
      pfang = 0.0
    sPF = AtpFit6 (pfang)
    print ('C =============================================================================', file=ap)
    print ('C solar {:s} at {:s} is {:.3f} kVA producing {:.3f} kW'.format (key, row['bus'], sbase*0.001, wtotal*0.001), file=ap)
    if nph == 1:
      print ('$INCLUDE,TACSPV1.PCH,{:s},{:s},{:s},{:s},{:s},{:s},{:s}'.format(sBus1, sName, sW, sImax, sUV, sUT, sPF), file=ap)
      DUM_NODES += PV1_DUM_NODES
    elif nph == 2:
      sBus2 = AtpNode (bus, phases[1]).replace(' ', '#')
      print ('$INCLUDE,TACSPV2.PCH,{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s}'.format(sBus1, sBus2, sName, sW, sImax, sUV, sUT, sPF), file=ap)
      DUM_NODES += PV2_DUM_NODES
    elif nph == 3:
      sBus = '{:5s}'.format(bus).replace(' ', '#')
      sV0 = AtpFit6 (vbase)
      sV02 = AtpFit6 (vbase*vbase)
      sVWc = AtpFit6 (vbase/376.9911)
      print ('$INCLUDE,TACSPV3.PCH,{:s},{:s},{:s},{:s},{:s},{:s},{:s} $$'.format(sBus, sName, sW, sImax, sUV, sUT, sPF), file=ap)
      print ('  ,{:s},{:s},{:s}'.format(sV0, sV02, sVWc), file=ap)
      DUM_NODES += PV3_DUM_NODES
    else:
      print ('C *** {:d}-phase call is not supported'.format(nph), file=ap)

  if bCurtailed:
    uncurtailed = 0.0
    for key, row in dict['DistSolar']['vals'].items():
      uncurtailed += row['p'] * PV_MULT
    print ('*** Uncurtailed PV output would be {:.2f} kW'.format(uncurtailed*0.001))


  if len(dict['DistSyncMachine']['vals']) > 0: # ATP requires these come after all other sources
    print ('/SOURCE', file=ap)
    for key, row in dict['DistSyncMachine']['vals'].items():
      bus = atp_buses[row['bus']]
      phases = GetAtpPhaseList (row['phases'])
      nph = len(phases)
      vbase = row['ratedU']
      sbase = row['ratedS']
      rkva = 0.001 * sbase
      SM_TOTAL += rkva
      SM_COUNT += 1
      print ('C =============================================================================', file=ap)
      print ('C SyncMachine {:s} at {:s} is {:.3f} kVA'.format (key, row['bus'], rkva), file=ap)
      if nph == 3:
        sm_bus = '{:5s}'.format (bus)
        rmva = '{:10.4f}'.format (1.0e-6*sbase)
        rkv = '{:10.3f}'.format (1.0e-3*vbase)
        vpk0 = '{:10.3f}'.format (vbase*SQRT2/SQRT3)
        deg0 = '{:10.3f}'.format (DER_ANG)
        Jmicro = '{:10.8f}'.format (DER_J*sbase)
        type59 = type59_template.format(bus=sm_bus, rmva____=rmva, rkv_____=rkv, vpk0____=vpk0, deg0____=deg0, Jmicro__=Jmicro)
        print (type59, file=ap)
      else:
        print ('C  *** cannot represent {:d} phases in ATP Type 59 component'.format(nph), file=ap)
        print ('** unable to write Type 59 model for {:d}-phase generator {:s} rated {:.3f} kVA'.format (nph, key, rkva))
    print ('/BRANCH', file=ap)

  print ('/SWITCH', file=ap)
  print ('C < n 1>< n 2>< Tclose ><Top/Tde ><   Ie   ><Vf/CLOP ><  type  >               1', file=ap)
  for tag in ['DistBreaker', 'DistDisconnector', 'DistFuse', 'DistJumper', 'DistLoadBreakSwitch', 'DistRecloser', 'DistSectionaliser']:
    tbl = dict[tag]
    lbl = tag[4:]
    for key, row in tbl['vals'].items():
      phases = GetAtpPhaseList (row['phases'])
      bus1 = atp_buses[row['bus1']]
      bus2 = atp_buses[row['bus2']]
      topen = TOPEN
      if row['open'] == 'true':
        tclose = TOPEN - 1.0
      else:
        tclose = -1.0
      print ('C =============================================================================', file=ap)
      print ('C {:s} {:s} from {:s} to {:s}'.format (lbl, key, row['bus1'], row['bus2']), file=ap)
      for ph in phases:
        print ('  {:6s}{:6s}{:10.3f}{:10.3f}{:s}0'.format (AtpNode (bus1, ph), AtpNode (bus2, ph), tclose, topen, PadBlanks(45)), file=ap)

  ap.close()

  print ('Wrote {:s}_net.atp to {:s}'.format(fname, fpath))
  print ('  Total Load = {:.2f} kW, PV = {:.2f} kW, BESS = {:.2f} kW, SyncMach={:.2f} kVA'.format (LOAD_TOTAL, PV_TOTAL, ST_TOTAL, SM_TOTAL))
  print ('  Wrote {:d} transformers; limit of X bus numbers is 9999'.format(xfbusnum-1))
  print ('  Wrote {:d} PV, {:d} BESS, and {:d} SyncMach'.format (PV_COUNT, ST_COUNT, SM_COUNT))
  print ('  Estimated {:d} TACS dummy nodes, limit is {:d}'.format (DUM_NODES, DUM_NODE_LIMIT))

#  for tbl in ['DistSequenceMatrix']:
#    if len(dict[tbl]['vals']) > 0:
#      print ('**** {:s} used in the circuit; but not implemented'.format (tbl))

if __name__ == '__main__':
  idx = 0
  if len(sys.argv) > 1:
    idx = int(sys.argv[1])

  case = cases[idx]
  print ('case {:d} of {:d}; converting {:s} to {:s} from queries in {:s}'.format(idx, len(cases), case['fname'], case['fpath'], xml_file))

  reset_globals (case, loadMult=case['load'], pvMult=case['pv'])
  convert_one_atp_model (query_file=xml_file, fid=case['fid'], fname=case['fname'], fpath=case['fpath'])
  quit()

  # create min, shoulder, max loads (L1..3) and clear, cloudy days (C1..2)
  loadMult = case['load']
  pvMult = case['pv']
  conditions = [{'suffix':'L1C1', 'load':0.4, 'pv':0.2},
                {'suffix':'L2C1', 'load':0.7, 'pv':0.2},
                {'suffix':'L3C1', 'load':1.0, 'pv':0.2},
                {'suffix':'L1C2', 'load':0.4, 'pv':1.0},
                {'suffix':'L2C2', 'load':0.7, 'pv':1.0},
                {'suffix':'L3C2', 'load':1.0, 'pv':1.0}]
  for row in conditions:
    reset_globals (case, loadMult=row['load']*loadMult, pvMult=row['pv']*pvMult)
    convert_one_atp_model (query_file=xml_file, fid=case['fid'], fname='{:s}_{:s}'.format(case['fname'],row['suffix']), 
                           fpath=case['fpath'], bSummaryAndMap=False)

