# Copyright (C) 2021-2023 Battelle Memorial Institute
import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import numpy as np
import math
import cmath
import sys
import os
import scipy.constants

basepath = 'c:/src/cimhub/bes/'

cfg_file = basepath + 'cimhubconfig.json'
xml_file = basepath + 'qbes.xml'

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 
   'name': 'IEEE118', 
   'bus_ic': 'c:/src/cimhub/bes/ieee118mb.txt',
   'gen_ic': 'c:/src/cimhub/bes/ieee118mg.txt',
   'swingbus':'131', 
   'load': 0.6748},
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 
   'name': 'WECC240', 
   'bus_ic': 'c:/src/cimhub/bes/wecc240mb.txt',
   'gen_ic': 'c:/src/cimhub/bes/wecc240mg.txt',
   'swingbus':'2438', 
   'load': 1.0425}
]

BUS_VMAG_IDX = 0
BUS_VDEG_IDX = 1
GEN_BUS_IDX = 0
GEN_P_IDX = 1
GEN_Q_IDX = 2
GEN_TYPE_IDX = 3
GEN_TYPE_ST = 0
GEN_TYPE_PV = 1
GEN_TYPE_WT = 2

USE_TYPE_14_MACHINES = False
USE_FIELD_SATURATION = False
USE_TYPE_14_WIND = True
USE_TYPE_14_SOLAR = True
MIN_BERGERON_TAU = 200.0e-6

DUM_NODES = 0
PV3_DUM_NODES = 49
MACHINE_DUM_NODES = 31
SOLAR_DUM_NODES = 0
WIND_DUM_NODES = 0
DUM_NODE_LIMIT = 9999

DELIM = ':'
SQRT3 = math.sqrt(3.0)
SQRT2 = math.sqrt(2.0)
RAD_TO_DEG = 180.0 / math.pi
OMEGA = 2.0 * 60.0 * math.pi
MIN_IMAG = 0.00015
MIN_PNLL = 0.00010
TOPEN = 9990.0
GEN_SHIFT = -30.0

MACHINE_NPOLES = 2.0
MACHINE_H = 3.0
MACHINE_J = 2.0*MACHINE_H*math.pow(0.5*MACHINE_NPOLES/OMEGA, 2.0) # multiply by RMVA for HICO in million kg-m2
MACHINE_DSD = 1e-5 * 1e6 * 0.5 * MACHINE_NPOLES / OMEGA # multiply by RMVA for DSD in N-m

# these can be reset for each model conversion
LOAD_MULT = 1.0
LOAD_TOTAL = 0.0
DR_COUNT = 0
DR_TOTAL = 0.0
PV_COUNT = 0
PV_TOTAL = 0.0
SM_COUNT = 0
SM_TOTAL = 0.0
WND_COUNT = 0
WND_TOTAL = 0.0
NEXT_BUSNUM = 0

def reset_globals(case):
  global LOAD_MULT, DUM_NODES, LOAD_TOTAL, PV_COUNT, PV_TOTAL, SM_COUNT, SM_TOTAL, WND_COUNT, WND_TOTAL
  global NEXT_BUSNUM, DR_COUNT, DR_TOTAL
  LOAD_MULT = case['load']
  LOAD_TOTAL = 0.0
  DUM_NODES = 0
  DR_COUNT = 0
  DR_TOTAL = 0.0
  PV_COUNT = 0
  PV_TOTAL = 0.0
  SM_COUNT = 0
  SM_TOTAL = 0.0
  WND_COUNT = 0
  WND_TOTAL = 0.0
  NEXT_BUSNUM = 0

def AtpNode(bus, phs):
  if bus[0].isdigit():
    return 'B{:4s}{:1s}'.format(bus, phs).replace(' ', '_')
  return '{:5s}{:1s}'.format(bus, phs).replace(' ', '_')

def AtpBus(bus):
  if bus[0].isdigit():
    return 'B{:4s}'.format(bus).replace(' ', '_')
  return '{:5s}'.format(bus).replace(' ', '_')

def GetNextScratchBus ():
  global NEXT_BUSNUM
  NEXT_BUSNUM += 1
  return '_{:4s}'.format(str(NEXT_BUSNUM)).replace(' ', '_')

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

def AtpRZTL(r, z, t, l):
  return '{:12e}{:12e}{:12e}{:12e}'.format(r, z, t, l)

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
  elif x <= -100.0:
    xstr = '{:6.1f}'.format(x)
  elif x <= -10.0:
    xstr = '{:6.2f}'.format(x)
  elif x <= -1.0:
    xstr = '{:6.3f}'.format(x)
  elif x < 0.0:
    xstr = '{:6.3f}'.format(x)
  elif x <= 0.001:
    exp = 0
    while x < 10.0:
      x *= 10.0
      exp += 1
    xstr = '{:2d}.E-{:d}'.format(int(round(x)), exp)
  else:
    xstr = '{:6.4f}'.format(x)
  return xstr

def AtpFit10(x):
  if x == 0.0:
    return '0.0'
  elif x < 0.0:
    return '{:9.3e}'.format(x)
  return '{:10.4e}'.format(x)

def AtpXfmrNeutralNode(xfbus, enum, wdgrow):
  if wdgrow['conn'] == 'Y':
    if wdgrow['grounded']:
      if (len(wdgrow['rground']) < 1) or (len(wdgrow['xground']) < 1):
        return '      '
      elif wdgrow['rground'] > 0.0 or wdgrow['xground'] > 0.0:
        return AtpNode (xfbus, chr(ord('M')+enum))
      else:
        return '      '
    else:
      return AtpNode (xfbus, chr(ord('M')+enum))
  return ''

def AtpXfmrNeutralImpedance(xfbus, enum, wdgrow):
  if wdgrow['conn'] == 'Y' and wdgrow['grounded'] and (len(wdgrow['rground']) > 0) and (len(wdgrow['rground']) > 0):
    if wdgrow['rground'] > 0.0 or wdgrow['xground'] > 0.0:
      return '  {:s}                  {:s}{:s}'.format (AtpNode (xfbus, chr(ord('M')+enum)), 
                                                        AtpFit6(wdgrow['rground']), 
                                                        AtpFit6(wdgrow['xground']))
  return ''

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

def AtpStarCore(wdgs, core):
  core_b = core['b']
  core_g = core['g']
  core_e = core['enum'] - 1
  core_e = 0 # TODO: verify CIM places core admittance on highest voltage winding
  core_v = wdgs[core_e]['ratedU']
  core_s = wdgs[core_e]['ratedS']
  core_c = wdgs[core_e]['conn']
  core_s /= 3.0
#  print (core_b, core_g, core_e, core_v, core_s, core_c)
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

def TheveninVoltage (vpu, deg, rpu, xpu, p_mw, q_mvar, mva_base):
  p = p_mw / mva_base
  q = q_mvar / mva_base
  s = complex(p, q)
  z = complex(rpu, xpu)
  rad = deg / RAD_TO_DEG
  vt = complex(vpu*math.cos(rad), vpu*math.sin(rad))
  i = (s/vt).conjugate()
  vs = vt + z*i
  return abs(vs), cmath.phase(vs) * RAD_TO_DEG

def AppendType14Generator (bus, vbase, rmva, Xdp, Ra, bus_ic, mw, mvar, ap):
  vpu = 1.0
  vdeg = 0.0
  if bus_ic is not None:
    idx = int(bus) - 1
    vpu = bus_ic[idx,BUS_VMAG_IDX]
    deg = bus_ic[idx,BUS_VDEG_IDX]
  vpu, deg = TheveninVoltage (vpu, deg, Xdp, Ra, mw, mvar, rmva)
  kv = vbase * 0.001
  zbase = kv * kv / rmva
  X1 = Xdp * zbase
  R1 = Ra * zbase
  X0 = X1
  R0 = R1
  vmag = vpu * kv * 1000.0 * SQRT2 / SQRT3
  vang = deg + GEN_SHIFT

  genbus = GetNextScratchBus()
  bus = AtpBus(bus)

  print ('/SOURCE', file=ap)
  print ('C < n 1><>< Ampl.  >< Freq.  ><Phase/T0><   A1   ><   T1   >< TSTART >< TSTOP  >', file=ap)
  for ph in ['A', 'B', 'C']:
    print ('14{:s}  {:10.3f}{:10.3f}{:10.3f}{:s}{:10.3f}{:10.3f}'.format (AtpNode (genbus, ph), 
                                                                          vmag, 60.0, vang, 
                                                                          PadBlanks(20), -1.0, 9999.0), file=ap)
    vang -= 120.0
  print ('/BRANCH', file=ap)
  print ('C < n1 >< n2 ><ref1><ref2>< R  >< X  >< C  >', file=ap)
  print ('51{:5s}A{:5s}A            {:s}{:s}'.format (bus, genbus, AtpFit6 (R0), AtpFit6 (X0)), file=ap)
  print ('52{:5s}B{:5s}B            {:s}{:s}'.format (bus, genbus, AtpFit6 (R1), AtpFit6 (X1)), file=ap)
  print ('53{:5s}C{:5s}C'.format (bus, genbus), file=ap)

def GetMachineDynamic (d, mach_id):
  for key, row in d.items():
    if mach_id == row['machid']:
      return row
  return None

machine_dynamic_template = """$INCLUDE,SYNCMACH.PCH,{sbus},{sname} $$
  ,{rmva},{rkv},{agline},{s1d},{s2d},{vpk} $$
  ,{ang0},{ra},{xl},{xd},{xq},{xdp} $$
  ,{xqp},{xdpp},{xqpp},{tdop},{tqop},{tdopp} $$
  ,{tqopp},{x0},{rn},{xn},{xcan},{hico} $$
  ,{dsd} $$
  ,{ikv0},{kvini},{ifini},{ifnom} $$
  ,{kgov},{t2},{t1t3},{t1pt3},{pmax} $$
  ,{kc},{ilr},{klr},{vrmin},{vrmax} $$
  ,{v0pu},{ka},{ta},{tb},{tc},{tled} $$
  ,{tlag},{kfbk},{tfbk} $$
  ,{psk5},{psa1},{psa2},{pst3},{pst4},{pst5} $$
  ,{pst6},{vstmn},{vstmx}"""

def AppendMachineDynamics (bus, vpu, deg, mach, gov, exc, pss, ap):
  global SM_COUNT
  sbus = AtpBus (bus)
  sname = 'SM{:03d}'.format (SM_COUNT)
  rmva = 1e-6 * mach['ratedS']
  rkv = 1e-3 * mach['ratedU']
  if USE_FIELD_SATURATION:
    agline = -1000.0
  else:
    agline = 1000.0
  ifini = 1.76 # 1.44673 # 1.76 # 0.0
  ifnom = abs(agline)
  s1d = 1.073 * abs(agline)
  s2d = 1.760 * abs(agline)
  vpk = 1000.0 * vpu * rkv * SQRT2 / SQRT3
  ang0 = deg + GEN_SHIFT
  ra = mach['Ra']
  xl = mach['Xl']
  xd = mach['Xd']
  xq = mach['Xq']
  xdp = mach['Xdp']
  xqp = mach['Xqp']
  xdpp = mach['Xdpp']
  xqpp = mach['Xqpp']
  tdop = mach['Tdop']
  tqop = mach['Tqop']
  tdopp = mach['Tdopp']
  tqopp = mach['Tqopp']
  x0 = mach['X0']
  rn = 900.0 # 0.0
  xn = 65.0 # 0.0
  xcan = xl
  hico = rmva * MACHINE_J
  dsd = rmva * MACHINE_DSD
  ikv0 = 1.0 / vpu / rkv
  kvini = vpu * rkv
  kgov = gov['k1']
  t2 = gov['t2']
  t1t3 = gov['t1'] * gov['t3']
  t1pt3 = gov['t1'] + gov['t3']
  pmax = max (1.2, gov['pmax']) # pmin not used from CIM?
  kc = exc['kc'] # not using CIM kf, tb1, tc1, tf, vamax, vamin, vimax, vimin
  ilr = exc['ilr']
  klr = exc['klr']
  vrmin = abs(exc['vrmin'])
  vrmax = exc['vrmax']
  ka = exc['ka']
  v0pu = vpu + 1.0 / ka
  ta = max(exc['ta'],1e-9)
  tb = exc['tb']
  tc = exc['tc']
  tled = max(0.0,0.4)
  tlag = max(0.0,0.025)
  kfbk = 0.0
  tfbk = max(0.0,1.0)
  psk5 = pss['ks'] # t1 and t2 from CIM not used?
  psa1 = max(pss['a1'],2e-9)
  psa2 = max(pss['a2'],1e-18)
  pst3 = pss['t3']
  pst4 = pss['t4']
  pst5 = pss['t5']
  pst6 = max(pss['t6'],1e-9)
  vstmn = pss['vstmin']
  vstmx = pss['vstmax']
#  print ('58 at {:s}, V={:.2f} at {:.2f}, gov={:s}, exc={:s}, pss={:s}'.format(bus, vpu, deg+GEN_SHIFT, gov['id'], exc['id'], pss['id']), file=ap)
  print (machine_dynamic_template.format(sbus=sbus,
                                         sname=sname,
                                         rmva = AtpFit10 (rmva),
                                         rkv = AtpFit10(rkv),
                                         agline = AtpFit10(agline),
                                         s1d = AtpFit10(s1d),
                                         s2d = AtpFit10(s2d),
                                         vpk = AtpFit10(vpk),
                                         ang0 = AtpFit10(ang0),
                                         ra = AtpFit10(ra),
                                         xl = AtpFit10(xl),
                                         xd = AtpFit10(xd),
                                         xq = AtpFit10(xq),
                                         xdp = AtpFit10(xdp),
                                         xqp = AtpFit10(xqp),
                                         xdpp = AtpFit10(xdpp),
                                         xqpp = AtpFit10(xqpp),
                                         tdop = AtpFit10(tdop),
                                         tqop = AtpFit10(tqop),
                                         tdopp = AtpFit10(tdopp),
                                         tqopp = AtpFit10(tqopp),
                                         x0 = AtpFit10(x0),
                                         rn = AtpFit10(rn),
                                         xn = AtpFit10(xn),
                                         xcan = AtpFit10(xcan),
                                         hico = AtpFit10(hico),
                                         dsd = AtpFit10(dsd),
                                         ikv0 = AtpFit6(ikv0),
                                         kvini = AtpFit10(kvini),
                                         ifini = AtpFit10(ifini),
                                         ifnom = AtpFit10(ifnom),
                                         kgov = AtpFit6(kgov),
                                         t2 = AtpFit10(t2),
                                         t1t3 = AtpFit10(t1t3),
                                         t1pt3 = AtpFit10(t1pt3),
                                         pmax = AtpFit6(pmax),
                                         kc = AtpFit6(kc),
                                         ilr = AtpFit10(ilr),
                                         klr = AtpFit10(klr),
                                         vrmin = AtpFit6(vrmin),
                                         vrmax = AtpFit6(vrmax),
                                         v0pu = AtpFit10(v0pu),
                                         ka = AtpFit6(ka),
                                         ta = AtpFit10(ta),
                                         tb = AtpFit10(tb),
                                         tc = AtpFit10(tc),
                                         tled = AtpFit10(tled),
                                         tlag = AtpFit10(tlag),
                                         kfbk = AtpFit10(kfbk),
                                         tfbk = AtpFit10(tfbk),
                                         psk5 = AtpFit6(psk5),
                                         psa1 = AtpFit10(psa1),
                                         psa2 = AtpFit10(psa2),
                                         pst3 = AtpFit10(pst3),
                                         pst4 = AtpFit10(pst4),
                                         pst5 = AtpFit10(pst5),
                                         pst6 = AtpFit10(pst6),
                                         vstmn = AtpFit6(vstmn),
                                         vstmx = AtpFit6(vstmx)), file=ap)

# parallel all machines at a bus, since they have identical controls and electrical parameters
# (this avoids need for FINISH and FINISH PART input of the individual machines in parallel)
# at the same time, assign initial conditions of P, Q, and voltage
def ParallelMachines (d, gen_ic, bus_ic, atp_buses):
  par = {}
  bus_generators = {}
  gen_ic_idx = 0
  for key, row in d.items():
    bus = row['bus']
    row['p'] = 1e6 * gen_ic[gen_ic_idx][GEN_P_IDX]
    row['q'] = 1e6 * gen_ic[gen_ic_idx][GEN_Q_IDX]
    gen_ic_idx += 1
    idx = int(atp_buses[bus]) - 1
    row['vpu'] = bus_ic[idx, BUS_VMAG_IDX]
    row['deg'] = bus_ic[idx, BUS_VDEG_IDX]
    if bus not in bus_generators:
      bus_generators[bus] = [key]
    else:
      bus_generators[bus].append(key)
  for bus, machines in bus_generators.items():
    if len(machines) < 2:
      key = machines[0]
      par[key] = d[key]
    else:
      parkey = '{:s}_{:d}EQG'.format(bus, len(machines))
      par[parkey] = d[machines[0]]
      for i in range(1, len(machines)):
        key = machines[i]
        row = d[key]
        for tag in ['ratedS', 'p', 'q', 'minP', 'maxP', 'minQ', 'maxQ']:
          par[parkey][tag] += row[tag]
  print ('Generator  Bus           MVA          P      Vpu     Vdeg')
  for key, row in par.items():
    print ('{:10s} {:6s} {:10.2f} {:10.2f} {:8.4f} {:8.4f}'.format (key, 
                                                                    row['bus'], 
                                                                    row['ratedS']*1e-6, 
                                                                    row['p']*1e-6,
                                                                    row['vpu'], row['deg']))
  return par

def convert_one_atp_model (query_file, fpath, case):
  global LOAD_MULT, DUM_NODES, LOAD_TOTAL, PV_COUNT, PV_TOTAL, SM_COUNT, SM_TOTAL, WND_COUNT, WND_TOTAL
  global DELIM, DR_COUNT, DR_TOTAL

  sys_id=case['id']
  fname=case['name']
  swingbus=case['swingbus']
  bus_ic = None
  if os.path.exists(case['bus_ic']):
    print ('Initial bus voltages and angles from', case['bus_ic'])
    bus_ic = np.loadtxt (case['bus_ic'], delimiter=',')
  gen_ic = None
  if os.path.exists(case['gen_ic']):
    print ('Generator bus, p, q, and types [0=ST,1=PV,2=WT] from', case['gen_ic'])
    gen_ic = np.loadtxt (case['gen_ic'], delimiter=',')
    print (gen_ic.shape, gen_ic[9,GEN_BUS_IDX], gen_ic[9,GEN_P_IDX], gen_ic[9,GEN_Q_IDX], gen_ic[9,GEN_TYPE_IDX])

  d = cimhub.load_bes_dict (query_file, sys_id, bTime=False)
  cimhub.summarize_bes_dict (d)
#  cimhub.list_dict_table (d, 'BESPowerXfmrCore')
#  cimhub.list_dict_table (d, 'BESBus')
#  cimhub.list_dict_table (d, 'BESMachine')
#  cimhub.list_dict_table (d, 'BESSolar')
#  cimhub.list_dict_table (d, 'BESWind')

  atp_buses = {}  # find the ATP bus number from the CIM ConnectivityNode name
  cim_buses = {}  # find the CIM ConnectivityNode name from the ATP bus number
  bus_kv = {}     # nominal voltage (line-to-line kV) from the CIM ConnectivityNode name
  bNumeric = True
  for key in d['BESBus']['vals']:
    if not key.isdigit():
      bNumeric = False
      break
  if bNumeric:
    ordered_buses = dict(sorted(d['BESBus']['vals'].items(), key=lambda x:int(x[0])))
  else:
    ordered_buses = d['BESBus']['vals']
  idx = 1
  for key, data in ordered_buses.items():
    bus = str(idx)
    atp_buses[key] = bus
    cim_buses[bus] = key
    bus_kv[key] = 0.001 * data['nomv']
    idx += 1
  print ('Mapping {:d} buses to {:s}.atpmap'.format (idx-1, fname))
  fp = open (fpath + fname + '.atpmap', mode='w')
  print ('ATP Bus   CIM Bus               Bus kV', file=fp)
  for key in cim_buses:
    print ('{:6s}    {:20s} {:7.3f}'.format (key, cim_buses[key], bus_kv[cim_buses[key]]), file=fp)
  print ('\nCIM Bus              ATP Bus    Bus kV', file=fp)
  for key in atp_buses:
    print ('{:20s} {:6s}    {:7.3f}'.format (key, atp_buses[key], bus_kv[key]), file=fp)
  fp.close()

  machines = ParallelMachines (d['BESMachine']['vals'], gen_ic, bus_ic, atp_buses)

  ap = open (fpath + fname + '_net.atp', mode='w')
  print ('C file: {:s}, Load Mult={:.3f}'.format (fname, LOAD_MULT), file=ap)
  print ('$VINTAGE,0', file=ap)

  bus = atp_buses[swingbus]
  kv = bus_kv[swingbus]
  x1pu_swing = 0.050
  r1pu_swing = 0.005
  mva_swing = 1000.0
  p_swing = 0.0
  q_swing = 0.0
  vmag = 1.0
  vang = 0.0
  if len(machines) > 0: # find the swing bus
    for key, row in machines.items():
      if bus == atp_buses[row['bus']]:
        mva_swing = 1.0e-6 * row['ratedS']
        x1pu_swing = row['Xdp']
        r1pu_swing = row['Ra']
        vmag = row['vpu']
        vang = row['deg']
        p_swing = 1.0e-6*row['p']
        q_swing = 1.0e-6*row['q']
        print ('Swing Generator {:.2f} MVA, {:.2f} MW, {:.2f} MVAR, X1={:.6f} pu, R1={:.6f} pu'.format(mva_swing, 
                                                                                                       p_swing, 
                                                                                                       q_swing, 
                                                                                                       x1pu_swing, 
                                                                                                       r1pu_swing))
        print ('   Swing bus V={:.4f} pu @ {:.3f} deg'.format (vmag, vang))
        break

  zbase = kv * kv / mva_swing
  X1 = x1pu_swing * zbase
  R1 = r1pu_swing * zbase
  X0 = X1
  R0 = R1
  vmag, vang = TheveninVoltage (vmag, vang, R1, X1, p_swing, q_swing, mva_swing)
  vmag = vmag * kv * 1000.0 * SQRT2 / SQRT3
  vang = vang + GEN_SHIFT
  print ('C =============================================================================', file=ap)
  print ('C Swing Bus {:s} at {:s}'.format (swingbus, bus), file=ap)
  print ('/SOURCE', file=ap)
  print ('C < n 1><>< Ampl.  >< Freq.  ><Phase/T0><   A1   ><   T1   >< TSTART >< TSTOP  >', file=ap)
  for ph in ['A', 'B', 'C']:
    print ('14{:s}  {:10.3f}{:10.3f}{:10.3f}{:s}{:10.3f}{:10.3f}'.format (AtpNode ('THEV', ph), 
                                                                          vmag, 60.0, vang, 
                                                                          PadBlanks(20), -1.0, 9999.0), file=ap)
    vang -= 120.0
  print ('/BRANCH', file=ap)
  print ('C < n1 >< n2 ><ref1><ref2>< R  >< X  >< C  >', file=ap)
  print ('51THEV_ASBUS_A            {:s}{:s}'.format (AtpFit6 (R0), AtpFit6 (X0)), file=ap)
  print ('52THEV_BSBUS_B            {:s}{:s}'.format (AtpFit6 (R1), AtpFit6 (X1)), file=ap)
  print ('53THEV_CSBUS_C', file=ap)
  print ('/SWITCH', file=ap)
  print ('C < n 1>< n 2>< Tclose ><Top/Tde ><   Ie   ><Vf/CLOP ><  type  >               1', file=ap)
  for ph in ['A', 'B', 'C']:
    print ('  {:6s}{:6s}{:10.3f}{:10.3f}                    MEASURING                1'.format (AtpNode ('SBUS', ph), 
      AtpNode (bus, ph), -1.0, TOPEN), file=ap)
  print ('/BRANCH', file=ap)

  # organize the balanced PowerTransformers (no regulators are supported yet)
  PowerXfmrs = {}
  xfbusnum = 1
  for key in d['BESPowerXfmrWinding']['vals']:
    pname = key.split(DELIM)[0]
    if pname in PowerXfmrs:
      PowerXfmrs[pname]['nwdg'] += 1
    else:
      PowerXfmrs[pname] = {'nwdg':1, 'regs': []}
  for pname, row in PowerXfmrs.items():
    nwdg = row['nwdg']
    regs = row['regs']
    wdgs = []
    meshes = []
    for i in range(nwdg):
      wdgs.append (d['BESPowerXfmrWinding']['vals']['{:s}{:s}{:d}'.format(pname, DELIM, i+1)])
      for j in range(i+1, nwdg):
        meshes.append (d['BESPowerXfmrMesh']['vals']['{:s}{:s}{:d}{:s}{:d}'.format(pname, DELIM, i+1, DELIM, j+1)])
    print ('C =============================================================================', file=ap)
    print ('C transformer {:s}, {:d} windings from {:s}'.format (pname, nwdg, wdgs[0]['bus']), file=ap)
    if nwdg > 3:
      print ('C *** too many windings for saturable transformer component', file=ap)
      print ('*** Transformer {:s} has {:d} windings, but only 2 or 3 supported'.format(pname, nwdg))
      continue
    Iss, Fss, Rmag = AtpStarCore (wdgs, d['BESPowerXfmrCore']['vals'][pname])
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
    for i in range(nwdg):
      if wdgs[i]['conn'] == 'D':
        for ph in ['A', 'B', 'C']:
          print ('  {:s}                  1000.0         1.0'.format (AtpNode (atp_buses[wdgs[i]['bus']], ph)), file=ap)

    xfbusnum += 1

  for key, row in d['BESLine']['vals'].items():
    bus1 = AtpBus(atp_buses[row['bus1']])
    bus2 = AtpBus(atp_buses[row['bus2']])
    rs = (row['r0']+2.0*row['r']) / 3.0
    rm = (row['r0']-row['r']) / 3.0
    xs = (row['x0']+2.0*row['x']) / 3.0
    xm = (row['x0']-row['x']) / 3.0
    cs = 1.0e6 * (row['b0']+2.0*row['b']) / 3.0 / OMEGA
    cm = 1.0e6 * (row['b0']-row['b']) / 3.0 / OMEGA
    if rs < 0.0 or rm < 0.0:
      print ('** Line', key, 'has negative resistance')
    # calculate the positive and negative Bergeron parameters
    bergeron = False
    km = 0.001*row['len']
    if cs > 0.0:
      r0p = (rs + 2*rm) / km
      l0 = (xs + 2*xm) / OMEGA
      c0 = 1.0e-6 * (cs + 2*cm)
      r1p = (rs - rm) / km
      l1 = (xs - xm) / OMEGA
      c1 = 1.0e-6 * (cs - cm)
      tau1 = math.sqrt(l1 * c1)
      tau0 = math.sqrt(l0 * c0)
      z1 = math.sqrt(l1/c1)
      z0 = math.sqrt(l0/c0)
      if min(tau0, tau1) >= MIN_BERGERON_TAU:
        bergeron = True
    print ('C =============================================================================', file=ap)
    print ('C line {:s} from {:s} to {:s}'.format (key, row['bus1'], row['bus2']), file=ap)
    print ('C   per-instance sequence parameters for {:.2f}km'.format(km), file=ap)
    if bergeron:
      print ('$VINTAGE,1', file=ap)
      print ('C < n 1>< n 2>            <   R/LEN  ><     Z    ><   TAU    ><   LEN    > 2 0 0', file=ap)
      print ('-1{:5s}A{:5s}A            {:s} 2 0 0'.format (bus1, bus2, AtpRZTL(r0p, z0, tau0, km)), file=ap)
      print ('-2{:5s}B{:5s}B            {:s} 2 0 0'.format (bus1, bus2, AtpRZTL(r1p, z1, tau1, km)), file=ap)
      print ('-3{:5s}C{:5s}C'.format (bus1, bus2), file=ap)
      print ('$VINTAGE,0', file=ap)
    else:
      print ('$VINTAGE,1', file=ap)
      print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
      print ('1 {:5s}A{:5s}A'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rs, xs, cs), file=ap)
      print ('2 {:5s}B{:5s}B'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rm, xm, cm), file=ap)
      print (PadBlanks(26) + AtpRXC(rs, xs, cs), file=ap)
      print ('3 {:5s}C{:5s}C'.format (bus1, bus2) + PadBlanks(12) + AtpRXC(rm, xm, cm), file=ap)
      print (PadBlanks(26) + AtpRXC(rm, xm, cm), file=ap)
      print (PadBlanks(26) + AtpRXC(rs, xs, cs), file=ap)
      print ('$VINTAGE,0', file=ap)

  for key, row in d['BESCompSeries']['vals'].items():
    bus1 = AtpBus(atp_buses[row['bus1']])
    bus2 = AtpBus(atp_buses[row['bus2']])
    if row['x'] > 0.0:
      print ('C =============================================================================', file=ap)
      print ('C series reactor {:s} from {:s} to {:s}'.format (key, row['bus1'], row['bus2']), file=ap)
      print ('C < n1 >< n2 ><ref1><ref2>< R  >< X  >< C  >', file=ap)
      print ('51{:5s}A{:5s}A            {:s}{:s}'.format (bus1, bus2, AtpFit6 (row['r0']), AtpFit6 (row['x0'])), file=ap)
      print ('52{:5s}B{:5s}B            {:s}{:s}'.format (bus1, bus2, AtpFit6 (row['r']), AtpFit6 (row['x'])), file=ap)
      print ('53{:5s}C{:5s}C'.format(bus1, bus2), file=ap)
    else:
      cuf = -1.0e6 / row['x'] / OMEGA
      print ('C =============================================================================', file=ap)
      print ('C series capacitor {:s} from {:s} to {:s}'.format (key, row['bus1'], row['bus2']), file=ap)
      print ('C < n1 >< n2 ><ref1><ref2>< R  >< X  >< C  >', file=ap)
      print ('  {:5s}A{:5s}A                        {:s}'.format (bus1, bus2, AtpFit6 (cuf)), file=ap)
      print ('  {:5s}B{:5s}B                        {:s}'.format (bus1, bus2, AtpFit6 (cuf)), file=ap)
      print ('  {:5s}C{:5s}C                        {:s}'.format (bus1, bus2, AtpFit6 (cuf)), file=ap)

  for key, row in d['BESCompShunt']['vals'].items():
    kv = 0.001 * row['nomu']
    kvar = 1000.0 * row['bsection'] * row['sections'] * kv * kv
    if kvar > 0.0:
      cuf = 1000.0 * kvar / kv / kv / OMEGA
      bus = atp_buses[row['bus']]
      print ('C =============================================================================', file=ap)
      print ('C capacitor {:s} at {:s} is {:.2f} kVAR'.format (key, row['bus'], kvar), file=ap)
      print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
      print ('$VINTAGE,1', file=ap)
      for ph in GetAtpPhaseList ('ABC'):
        print ('  ' + AtpNode (bus, ph) + PadBlanks(50) + '{:16e}'.format(cuf), file=ap)
      print ('$VINTAGE,0', file=ap)
    elif kvar < 0.0:
      xshunt = -1000.0 * kv * kv / kvar
      bus = atp_buses[row['bus']]
      print ('C =============================================================================', file=ap)
      print ('C reactor {:s} at {:s} is {:.2f} kVAR'.format (key, row['bus'], -kvar), file=ap)
      print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
      print ('$VINTAGE,1', file=ap)
      for ph in GetAtpPhaseList ('ABC'):
        print ('  ' + AtpNode (bus, ph) + PadBlanks(34) + '{:16e}'.format(xshunt), file=ap)
      print ('$VINTAGE,0', file=ap)


  for key, row in d['BESLoad']['vals'].items():
    bus = atp_buses[row['bus']]
    phases = GetAtpPhaseList ('ABC')
    nph = len(phases)
    kv = 0.001 * row['basev']
    kw = 0.001 * row['p'] * LOAD_MULT
    kvar = 0.001 * row['q'] * LOAD_MULT
    LOAD_TOTAL += 0.001 * kw
    if False: # row['conn'] == 'D':
      bDelta = True
      kvld = kv
    else:
      bDelta = False
      kvld = kv / SQRT3
    rload = nph * 1000.0 * kvld * kvld / kw
    if kvar > 0.0:
      xload = nph * 1000.0 * kvld * kvld / kvar
    else:
      xload = 0.0
    if rload < 0.0:
      print ('** Load', key, 'has negative resistance, write as DER')
      DR_COUNT += 1
      DUM_NODES += PV3_DUM_NODES
      vbase = row['basev']
      sbase = abs(row['p'])
      wtotal = sbase
      DR_TOTAL += 1e-6 * wtotal
      irmsmx = 1.1 * sbase / vbase / SQRT3
      vtrip = 0.5 * vbase / SQRT3
      pfang = 0.0
      sBus = AtpBus(bus) # '{:5s}'.format(bus).replace(' ', '#')
      sName = 'DR{:03d}'.format (DR_COUNT)
      sW = AtpFit6 (wtotal)
      sImax = AtpFit6 (irmsmx)
      sUV = AtpFit6 (vtrip)
      sUT = AtpFit6 (0.16)
      sV0 = AtpFit6 (vbase)
      sV02 = AtpFit6 (vbase*vbase)
      sVWc = AtpFit6 (vbase/376.9911)
      sPF = AtpFit6 (pfang)
      print ('C =============================================================================', file=ap)
      print ('C DER {:s} at {:s} is {:.2f} MVA producing {:.2f} MW'.format (key, row['bus'], 1e-6*sbase, 1e-6*wtotal), file=ap)
      print ('$INCLUDE,TACSPV3.PCH,{:s},{:s},{:s},{:s},{:s},{:s},{:s} $$'.format(sBus, sName, sW, sImax, sUV, sUT, sPF), file=ap)
      print ('  ,{:s},{:s},{:s}'.format(sV0, sV02, sVWc), file=ap)
      print ('/BRANCH', file=ap)
    else:
      print ('C =============================================================================', file=ap)
      print ('C load {:s} at {:s} is {:.3f} + j{:.3f} kVA'.format (key, row['bus'], kw, kvar), file=ap)
      print ('C < n 1>< n 2><ref1><ref2><       R      ><      X       ><      C       ><   >', file=ap)
      print ('$VINTAGE,1', file=ap)
      for ph in phases:
        bus_from = AtpNode (bus, ph)
        bus_to = AtpLoadTo (bus, ph, bDelta)
        print ('  ' + bus_from + bus_to + PadBlanks(12) + '{:16e}'.format(rload), file=ap)
        if xload > 0.0:
          print ('  ' + bus_from + bus_to + PadBlanks(28) + '{:16e}'.format(xload), file=ap)
      print ('$VINTAGE,0', file=ap)

  for key, row in d['BESSolar']['vals'].items():
    bus = atp_buses[row['bus']]
    phases = GetAtpPhaseList ('ABC')
    nph = len(phases)
    vbase = row['ratedU']
    sbase = row['ratedS']
    wtotal = row['p'] * 1.0 # PV_MULT
    PV_TOTAL += 1e-6 * wtotal
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
    print ('C solar {:s} at {:s} is {:.3f} MVA producing {:.3f} MW'.format (key, row['bus'], sbase*1e-6, wtotal*1e-6), file=ap)

  for key, row in d['BESWind']['vals'].items():
    bus = atp_buses[row['bus']]
    phases = GetAtpPhaseList ('ABC')
    nph = len(phases)
    vbase = row['ratedU']
    sbase = row['ratedS']
    wtotal = row['p'] * 1.0 # PV_MULT
    WND_TOTAL += 1e-6 * wtotal
    WND_COUNT += 1
    print ('C =============================================================================', file=ap)
    print ('C wind {:s} at {:s} is {:.3f} MVA producing {:.3f} MW'.format (key, row['bus'], sbase*1e-6, wtotal*1e-6), file=ap)

  ic_idx = 0
  if len(machines) > 0: # ATP requires these come after all other sources
    lastKey = list(machines.keys())[-1]
    for key, row in machines.items():
      bus = atp_buses[row['bus']]
      phases = GetAtpPhaseList ('ABC')
      nph = len(phases)
      vbase = row['ratedU']
      sbase = row['ratedS']
      rmva = 1e-6 * sbase
      mw = 1.0e-6 * row['p']
      mvar = 1.0e-6 * row['q']
      SM_TOTAL += mw
      SM_COUNT += 1
      if row['Ra'] < 0.0:
        print ('** Machine', key, 'has negative resistance')
      if row['bus'] == swingbus:
        print ('C =============================================================================', file=ap)
        print ('C SyncMachine {:s} at {:s} is {:.2f} MVA, part of Swing Bus'.format (key, row['bus'], rmva), file=ap)
      else:
        print ('C =============================================================================', file=ap)
        print ('C SyncMachine {:s} at {:s} is {:.2f} MVA, {:.2f} MW, {:.2f} MVAR'.format (key, row['bus'], rmva, mw, mvar), file=ap)
        if USE_TYPE_14_MACHINES: #  or (key != lastKey):
          AppendType14Generator (bus, vbase, rmva, row['Xdp'], row['Ra'], bus_ic, mw, mvar, ap)
        else:
          gov = GetMachineDynamic (d['BESGovernor']['vals'], row['id'])
          exc = GetMachineDynamic (d['BESExciter']['vals'], row['id'])
          pss = GetMachineDynamic (d['BESStabilizer']['vals'], row['id'])
          AppendMachineDynamics (bus=bus, vpu=row['vpu'], deg=row['deg'], mach=row, gov=gov, exc=exc, pss=pss, ap=ap)
          DUM_NODES += MACHINE_DUM_NODES
    print ('/BRANCH', file=ap)

#  no CIM breakers in the BES queries
#  print ('/SWITCH', file=ap)
#  print ('C < n 1>< n 2>< Tclose ><Top/Tde ><   Ie   ><Vf/CLOP ><  type  >               1', file=ap)

  ap.close()

  print ('Wrote {:s}_net.atp to {:s}'.format(fname, fpath))
  print ('  Total Load = {:.2f} MW, PV = {:.2f} MW, Wind = {:.2f} MW, SyncMach={:.2f} MVA, DER={:.2f} MW'.format (LOAD_TOTAL, PV_TOTAL, WND_TOTAL, SM_TOTAL, DR_TOTAL))
  print ('  Wrote {:d} transformers; limit of X bus numbers is 9999'.format(xfbusnum-1))
  print ('  Wrote {:d} PV, {:d} Wind, {:d} Equiv SyncMach, {:d} DER'.format (PV_COUNT, WND_COUNT, SM_COUNT, DR_COUNT))
  print ('  Estimated {:d} TACS dummy nodes, limit is {:d}'.format (DUM_NODES, DUM_NODE_LIMIT))

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_file)
  idx = 0
  if len(sys.argv) > 1:
    idx = int(sys.argv[1])

  case = CASES[idx]
  print ('case {:d} of {:d}; exporting {:s} from queries in {:s}'.format(idx, len(CASES), case['name'], xml_file))

  reset_globals (case)
  convert_one_atp_model (query_file=xml_file, fpath = './', case=case)

