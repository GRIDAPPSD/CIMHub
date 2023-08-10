import csv
import operator
import math
import sys
import os
import json

DEG_TO_RAD = math.pi / 180.0

# Do all of the name-matching in upper case!!

# 208/120 is always used as a candidate base voltage
casefiles = [{'root':'ACEP_PSIL',      'do_gld':True,  'bases':[318.0,480.0], 'check_branches':[{'dss_link': 'LINE.SEG4', 'dss_bus': 'BATT', 'gld_link': 'LINE_SEG4', 'gld_bus': 'BATT'}]},
             {'root':'EPRI_DPV_J1',    'do_gld':True,  'bases':[416.0,12470.0,69000.0], 'check_branches':[]},
             {'root':'IEEE123',        'do_gld':True,  'bases':[480.0,4160.0], 'check_branches':[]},
             {'root':'IEEE123_PV',     'do_gld':True,  'bases':[4160.0], 'check_branches':[]},
             {'root':'Transactive',    'do_gld':True,  'bases':[4160.0], 'check_branches':[]},
             {'root':'IEEE13',         'do_gld':True,  'bases':[480.0,4160.0,13200.0,115000.0], 'check_branches':[]},
             {'root':'IEEE13_Assets',  'do_gld':True,  'bases':[480.0,4160.0,115000.0], 'check_branches':[]},
             {'root':'IEEE13_OCHRE',   'do_gld':True,  'bases':[480.0,4160.0,115000.0], 'check_branches':[]},
             {'root':'IEEE37',         'do_gld':False, 'bases':[480.0,4800.0,230000.0], 'check_branches':[{'dss_link': 'LOAD.S728', 'dss_bus': '728'}]},
             {'root':'IEEE8500',       'do_gld':True,  'bases':[12470.0,115000.0], 'check_branches':[]},
             {'root':'IEEE9500bal',    'do_gld':True,  'bases':[12480.0,69000.0,115000.0], 'check_branches':[]},
             {'root':'R2_12_47_2',     'do_gld':True,  'bases':[480.0,12470.0,100000.0], 'check_branches':[]}]

dir1 = './test/'     # baseline dss outputs
dir2 = './test/dss/'   # converted dss output files
dir3 = './test/glm/'   # converted gridlab-d output files

def dss_phase(col):
  if col==1:
    return '_A'
  elif col==2:
    return '_B'
  else:
    return '_C'

# heuristically estimate a base voltage from a set of common values, assuming
#  that a normal per-unit voltage should be 0.9 to 1.1, and 120.0 is the default base

def glmVpu(v, bases):
  vpu = v / 120.0
  if vpu < 1.15:
    return vpu
  for vbase in bases:
    vpu = v / vbase
    if vpu < 1.15:
      return vpu
  return 0.0 # indicates a problem

def load_glm_voltages(fname, voltagebases, dictNames=None):
  vpu = {}
  vmag = {}
  vrad = {}
  buses = []
  if not os.path.isfile (fname):
    return buses, vpu, vmag, vrad
  fd = open (fname, 'r')
  rd = csv.reader (fd, delimiter=',')
  next (rd)
  next (rd)
  for row in rd:
    bus = row[0].upper()
    if dictNames is not None:
      if bus in dictNames:
        bus = dictNames[bus].upper()
    buses.append (bus)
    maga = float(row[1])
    if maga > 0.0:
      vmag[bus+'_A'] = maga
      vrad[bus+'_A'] = float(row[2])
      vpu[bus+'_A'] = glmVpu (maga, voltagebases)
    magb = float(row[3])
    if magb > 0.0:
      vmag[bus+'_B'] = magb
      vrad[bus+'_B'] = float(row[4])
      vpu[bus+'_B'] = glmVpu (magb, voltagebases)
    magc = float(row[5])
    if magc > 0.0:
      vmag[bus+'_C'] = magc
      vrad[bus+'_C'] = float(row[6])
      vpu[bus+'_C'] = glmVpu (magc, voltagebases)
  fd.close()
  return buses, vpu, vmag, vrad
    
def load_glm_currents(fname, dictNames=None, dictClasses=None):
  iglm = {}
  irad = {}
  links = []
  if not os.path.isfile (fname):
    return links, iglm
  fd = open (fname, 'r')
  rd = csv.reader (fd, delimiter=',')
  next (rd)
  next (rd)
  itol = 0.0 # 0.001
  #link_name,currA_mag,currA_angle,currB_mag,currB_angle,currC_mag,currC_angle
  for row in rd:
    link = row[0].upper()
    if (dictNames is not None) and (dictClasses is not None):
      mRID = link
      if (mRID in dictNames) and (mRID in dictClasses):
        link = '{:s}_{:s}'.format (dictClasses[mRID].upper(), dictNames[mRID].upper())
    if link.startswith ('LINE_') or link.startswith ('REG_') or link.startswith ('SWT_') or link.startswith ('XF_') or link.startswith ('REAC_'):
      links.append(link)
      maga = float(row[1])
      if maga >= itol:
        iglm[link+'_A'] = maga
        irad[link+'_A'] = float(row[2])
      magb = float(row[3])
      if magb >= itol:
        iglm[link+'_B'] = magb
        irad[link+'_B'] = float(row[4])
      magc = float(row[5])
      if magc >= itol:
        iglm[link+'_C'] = magc
        irad[link+'_C'] = float(row[6])
  fd.close()
  return links, iglm, irad

def load_currents(fname, ordname, dictNames=None):
  idss = {}
  irad = {}
  if not os.path.isfile (fname):
    return idss
  if not os.path.isfile (ordname):
    return idss

  phases = {}
  fd = open (ordname, 'r')
  rd = csv.reader (fd, delimiter=',', skipinitialspace=True)
  next (rd)
  #Element, Nterminals, Nconductors, N1, N2, N3, ...
  for row in rd:
    link = row[0].strip('\"').upper()
    if dictNames is not None:
      toks = link.split('.')
      if toks[1] in dictNames:
        link = '{:s}.{:s}'.format (toks[0], dictNames[toks[1]].upper())
    nt = int(row[1])
    nc = int(row[2])
    phases[link] = []
    for i in range(nc):
      phases[link].append(int(row[3+i]))
  fd.close()
#  print ('Phase Map', phases)

  fd = open (fname, 'r')
  rd = csv.reader (fd, delimiter=',', skipinitialspace=True)
  next (rd)
  itol = 0.0 # 1.0e-8  # if this is too high, the comparison may think a conductive branch is missing
  #Element, I1_1, Ang1_1, I1_2, Ang1_2, I1_3, Ang1_3, I1_4, Ang1_4, Iresid1, AngResid1, I2_1, Ang2_1, I2_2, Ang2_2, I2_3, Ang2_3, I2_4, Ang2_4, Iresid2, AngResid2
  for row in rd:
    link = row[0].strip('\"').upper()
    if dictNames is not None:
      toks = link.split('.')
      if toks[1] in dictNames:
        link = '{:s}.{:s}'.format (toks[0], dictNames[toks[1]].upper())
    phs = phases[link]
    for i in range(len(phs)):
      idx = phs[i]
      if idx > 0:
        amps = float(row[1 + 2*i])
        if amps >= itol:
          idss[link+'.'+str(idx)] = amps
          irad[link+'.'+str(idx)] = float(row[2 + 2*i]) * DEG_TO_RAD
  fd.close()
  return idss, irad

def load_voltages(fname, dictNames=None):
#  print ('load_voltages from:', fname)
  vpu = {}
  vmag = {}
  vrad = {}
  if not os.path.isfile (fname):
    return vpu
  fd = open (fname, 'r')
  rd = csv.reader (fd, delimiter=',', skipinitialspace=True)
  next (rd)
  #Bus, BasekV, Node1, Magnitude1, Angle1, pu1, Node2, Magnitude2, Angle2, pu2, Node3, Magnitude3, Angle3, pu3
  for row in rd:
    if dictNames is not None:
      bus = dictNames[row[0].strip('\"').upper()].upper()
    else:
      bus = row[0].strip('\"').upper()
    if len(bus) > 0:
      vpu1 = float(row[5])
      vpu2 = float(row[9])
      vpu3 = float(row[13])
      if float(vpu1) > 0:
        phs = dss_phase (int(row[2]))
        vpu[bus+phs] = vpu1
        vmag[bus+phs] = float(row[3])
        vrad[bus+phs] = float(row[4])*DEG_TO_RAD
      if float(vpu2) > 0:
        phs = dss_phase (int(row[6]))
        vpu[bus+phs] = vpu2
        vmag[bus+phs] = float(row[7])
        vrad[bus+phs] = float(row[8])*DEG_TO_RAD
      if float(vpu3) > 0:
        phs = dss_phase (int(row[10]))
        vpu[bus+phs] = vpu3
        vmag[bus+phs] = float(row[11])
        vrad[bus+phs] = float(row[12])*DEG_TO_RAD
  fd.close()
  return vpu, vmag, vrad

def print_dss_flow (vtag, itag, volts, vang, amps, iang, label=None, fps=[sys.stdout]):
#  print (vtag, (vtag+'_A') in volts)
#  print (itag, (itag+'.1') in amps)
  if vtag is None or itag is None:
    return
  ptot = 0.0
  qtot = 0.0
  iline_mag = {}
  vln_mag = {}
  iline_ang = {}
  vln_ang = {}
  pkw = {}
  qkvar = {}
  for fp in fps:
    if label is None:
      print ('  OpenDSS branch flow in {:s} from {:s}'.format (itag, vtag), file=fp)
    else:
      print ('  OpenDSS branch flow in {:s} from {:s}, {:s} case'.format (itag, vtag, label), file=fp)
    print ('  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad', file=fp)
  for num, phs in zip(['1', '2', '3'], ['A', 'B', 'C']):
    vtarget = vtag + '_' + phs
    itarget = itag + '.' + num
    if itarget in amps and vtarget in volts:
      iline_mag[phs] = amps[itarget]
      iline_ang[phs] = iang[itarget]
      vln_mag[phs] = volts[vtarget]
      vln_ang[phs] = vang[vtarget]
      skva = amps[itarget] * volts[vtarget] * 0.001
      pkw[phs] = skva * math.cos (vang[vtarget]-iang[itarget])
      qkvar[phs] = skva * math.sin (vang[vtarget]-iang[itarget])
      ptot += pkw[phs]
      qtot += qkvar[phs]
  for phs, llp in zip(['A', 'B', 'C'], ['B', 'C', 'A']):
    vll_mag = 0.0
    vll_ang = 0.0
    if phs in vln_mag and llp in vln_mag:
      realpart = vln_mag[phs] * math.cos(vln_ang[phs]) - vln_mag[llp] * math.cos(vln_ang[llp])
      imagpart = vln_mag[phs] * math.sin(vln_ang[phs]) - vln_mag[llp] * math.sin(vln_ang[llp])
      vll_mag = math.sqrt (realpart*realpart + imagpart*imagpart)
      vll_ang = math.atan2 (imagpart, realpart)
    if phs in vln_mag:
      for fp in fps:
        print ('    {:s} {:9.2f} {:7.4f} {:9.2f} {:7.4f}  {:9.3f} + j {:9.3f}     {:s}{:s}   {:9.2f} {:7.4f}'.format (phs, vln_mag[phs], 
          vln_ang[phs], iline_mag[phs], iline_ang[phs], pkw[phs], qkvar[phs], phs, llp, vll_mag, vll_ang), file=fp)
  for fp in fps:
    print ('    Total S = {:9.3f} + j {:9.3f}'.format (ptot, qtot), file=fp)
  return ptot, qtot

def print_glm_flow (vtag, itag, volts, vang, amps, iang, fps=[sys.stdout]):
  if vtag is None or itag is None:
    return
  ptot = 0.0
  qtot = 0.0
  iline_mag = {}
  vln_mag = {}
  iline_ang = {}
  vln_ang = {}
  pkw = {}
  qkvar = {}
  for fp in fps:
    print ('  GridLAB-D branch flow in {:s} from {:s}'.format (itag, vtag), file=fp)
    print ('  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad', file=fp)
  for phs in ['A', 'B', 'C']:
    vtarget = vtag + '_' + phs
    itarget = itag + '_' + phs
    if itarget in amps and vtarget in volts:
      iline_mag[phs] = amps[itarget]
      iline_ang[phs] = iang[itarget]
      vln_mag[phs] = volts[vtarget]
      vln_ang[phs] = vang[vtarget]
      skva = amps[itarget] * volts[vtarget] * 0.001
      pkw[phs] = skva * math.cos (vang[vtarget]-iang[itarget])
      qkvar[phs] = skva * math.sin (vang[vtarget]-iang[itarget])
      ptot += pkw[phs]
      qtot += qkvar[phs]
  for phs, llp in zip(['A', 'B', 'C'], ['B', 'C', 'A']):
    vll_mag = 0.0
    vll_ang = 0.0
    if phs in vln_mag and llp in vln_mag:
      realpart = vln_mag[phs] * math.cos(vln_ang[phs]) - vln_mag[llp] * math.cos(vln_ang[llp])
      imagpart = vln_mag[phs] * math.sin(vln_ang[phs]) - vln_mag[llp] * math.sin(vln_ang[llp])
      vll_mag = math.sqrt (realpart*realpart + imagpart*imagpart)
      vll_ang = math.atan2 (imagpart, realpart)
    for fp in fps:
      print ('    {:s} {:9.2f} {:7.4f} {:9.2f} {:7.4f}  {:9.3f} + j {:9.3f}     {:s}{:s}   {:9.2f} {:7.4f}'.format (phs, vln_mag[phs], 
        vln_ang[phs], iline_mag[phs], iline_ang[phs], pkw[phs], qkvar[phs], phs, llp, vll_mag, vll_ang), file=fp)
  for fp in fps:
    print ('    Total S = {:9.3f} + j {:9.3f}'.format (ptot, qtot), file=fp)

def load_taps(fname, dictNames=None):
  vtap = {}
  if not os.path.isfile (fname):
    return vtap
  fd = open (fname, 'r')
  rd = csv.reader (fd, delimiter=',', skipinitialspace=True)
  next (rd)
  # Name, Tap, Min, Max, Step, Position
  for row in rd:
    bus = row[0].strip('\"').upper()
    if dictNames is not None:
      if bus in dictNames:
        bus = dictNames[bus].upper()
    if len(bus) > 0:
      vtap[bus] = int (row[6])
  fd.close()
  return vtap

# Summary information - we want the last row
# DateTime, CaseName, Status, Mode, Number, 
# LoadMult, NumDevices, NumBuses, NumNodes, Iterations, 
# ControlMode, ControlIterations, MostIterationsDone, Year, Hour, 
# MaxPuVoltage, MinPuVoltage, TotalMW, TotalMvar, MWLosses, 
# pctLosses, MvarLosses, Frequency
def load_summary(fname):
  summ = {}
  if not os.path.isfile (fname):
    return summ
  fd = open (fname, 'r')
  rd = csv.reader (fd, delimiter=',', skipinitialspace=True)
  next (rd)
  for row in rd:
    if row[2].upper() == 'UNSOLVED':
      continue
    summ['Status'] = row[2]
    summ['Mode'] = row[3]
    summ['Number'] = row[4]
    summ['LoadMult'] = row[5]
    summ['NumDevices'] = row[6]
    summ['NumBuses'] = row[7]
    summ['NumNodes'] = row[8]
    summ['Iterations'] = row[9]
    summ['ControlMode'] = row[10]
    summ['ControlIterations'] = row[11]
    summ['MaxPuVoltage'] = row[15]
    summ['MinPuVoltage'] = row[16]
    summ['TotalMW'] = row[17]
    summ['TotalMvar'] = row[18]
    summ['MWLosses'] = row[19]
    summ['pctLosses'] = row[20]
    summ['MvarLosses'] = row[21]
    summ['Frequency'] = row[22]
  fd.close()
  return summ

def error_norm (diffs, limit=None):
  cnt = 0
  sum = 0.0
  for row in diffs:
    v = row[1]
    if limit is None:
      sum += v
      cnt += 1
    elif v <= limit:
      sum += v
      cnt += 1
  if cnt < 1:
    return 0.0
  return sum/cnt

def error_norm_tuple (diffs):
  cnt = len(diffs)
  if cnt < 1:
    return 0.0
  sum = 0.0
  for row in diffs:
    v = row[1][0]
    sum += v
  return sum/cnt

def write_glm_flows(glmpath, rootname, voltagebases, check_branches, fps=[sys.stdout]):
  gldbus, gldv, gldmagv, gldangv = load_glm_voltages (glmpath + rootname + '_volt.csv', voltagebases)
  gldlink, gldi, gldangi = load_glm_currents (glmpath + rootname + '_curr.csv')
  for row in check_branches:
    if (('gld_link' in row) and ('gld_bus' in row)):
      print_glm_flow (row['gld_bus'], row['gld_link'], gldmagv, gldangv, gldi, gldangi, fps)

def write_dss_flows(dsspath, rootname, check_branches, fps=[sys.stdout]):
  dssroot = rootname.lower()
  v1, magv1, angv1 = load_voltages (dsspath + dssroot + '_v.csv')
  t1 = load_taps (dsspath + dssroot + '_t.csv')
  i1, angi1 = load_currents (dsspath + dssroot + '_i.csv', dsspath + dssroot + '_n.csv')
  s1 = load_summary (dsspath + dssroot + '_s.csv')
  print ('OpenDSS solution from: {:s} {:s} in {:s} iterations'.format(dsspath, s1['Status'], s1['Iterations']))
  print ('  Number of Devices={:s} Buses={:s} Nodes={:s}'.format(s1['NumDevices'], s1['NumBuses'], s1['NumNodes']))
  print ('  Line-Neutral Voltage min={:.4f}    max={:.4f} pu'.format(float(s1['MinPuVoltage']), float(s1['MaxPuVoltage'])))
  print ('  Source P={:.2f} kW    Q={:.2f} kVAR'.format(1000*float(s1['TotalMW']), 1000*float(s1['TotalMvar'])))
  print ('  Loss   P={:.2f} kW    Q={:.2f} kVAR'.format(1000*float(s1['MWLosses']), 1000*float(s1['MvarLosses'])))
  print ('Tap Changer     Position')
  for key, val in t1.items():
    print ('  {:14s} {:3d}'.format(key, val))
  classes = ['LINE', 'VSOURCE', 'PVSYSTEM', 'STORAGE', 'TRANSFORMER', 'CAPACITOR', 'GENERATOR', 'REACTOR', 'AUTOTRANS',
             'GICTRANSFORMER', 'GENERIC5', 'GICLINE', 'LOAD', 'INDMACH012', 'UPFC', 'VCCS', 'VSCONVERTER', 'WINDGEN']
  class_instances = {}
  for cls in classes:
    class_instances[cls] = []
  for key in i1:
    for cls in classes:
      if key.startswith(cls):
        idx1 = key.find('.') + 1
        idx2 = key.find('.', idx1)
        tok = key[idx1:idx2]
        if tok not in class_instances[cls]:
          class_instances[cls].append(tok)
          break
  print ('Object counts (with non-zero current flow):')
  for key, toks in class_instances.items():
    if len(toks) > 0:
      print ('  {:15s} {:5d}'.format(key, len(toks)))
  branch_p = 0.0
  branch_q = 0.0
  for row in check_branches:
    if (('dss_link' in row) and ('dss_bus' in row)):
      p, q = print_dss_flow (row['dss_bus'], row['dss_link'], magv1, angv1, i1, angi1, label=None, fps=fps)
      if 'bLoad' in row:
        if row['bLoad']:
          branch_p += p
          branch_q += q
  print ('Accumulated Load P={:.2f} kW   Q={:.2f} kVAR'.format(branch_p, branch_q))

def get_glm_class (cimClass):
  if cimClass == 'ACLineSegment':
    return 'LINE'
  if cimClass in ['PowerTransformer', 'PowerTransformerEnds']:
    return 'XF'
  if cimClass == 'SeriesCompensator':
    return 'REAC'
  if cimClass == 'RatioTapChangers':
    return 'REG'
  if cimClass in ['Breaker', 'Fuse', 'LoadBreakSwitch', 'Recloser', 'Sectionaliser']:
    return 'SWT'
  return ''

def read_mrid_dictionary (dictpath, rootname):
  dictNames = None
  dictClasses = None
  dictFile = os.path.join (dictpath, rootname + '_dict.json')
  if os.path.exists(dictFile):
    dict = json.load (open(dictFile))
    if 'exportNameMode' in dict:
      if dict['exportNameMode'] == 'MRID':
        dictNames = {}
        dictClasses = {}
        for fdr in dict['feeders']:
          for bus in fdr['busnames']:
            dictNames[bus['mRID']] = bus['name']
          for eq in fdr['equipmentnames']:
            dictNames[eq['mRID']] = eq['name']
            dictClasses[eq['mRID']] = get_glm_class (eq['class'])
  return dictNames, dictClasses

def write_comparisons(basepath, dsspath, glmpath, rootname, voltagebases, check_branches=[], do_gld=True, fps=[sys.stdout]):
  dssroot = rootname.lower()

  v1, magv1, angv1 = load_voltages (os.path.join (basepath, dssroot + '_v.csv'))
  t1 = load_taps (os.path.join (basepath, dssroot + '_t.csv'))
  i1, angi1 = load_currents (os.path.join (basepath, dssroot + '_i.csv'),
                             os.path.join (basepath, dssroot + '_n.csv'))
  s1 = load_summary (os.path.join (basepath, dssroot + '_s.csv'))

  if dsspath:
    dictNames, dictClasses = read_mrid_dictionary (dsspath, dssroot)
    v2, magv2, angv2 = load_voltages (os.path.join (dsspath, dssroot + '_v.csv'), dictNames)
    t2 = load_taps (os.path.join (dsspath, dssroot + '_t.csv'), dictNames)
    i2, angi2 = load_currents (os.path.join (dsspath, dssroot + '_i.csv'), 
                               os.path.join (dsspath, dssroot + '_n.csv'), dictNames)
    s2 = load_summary (os.path.join (dsspath, dssroot + '_s.csv'))

  if do_gld:
    dictNames, dictClasses = read_mrid_dictionary (glmpath, rootname)
    gldbus, gldv, gldmagv, gldangv = load_glm_voltages (os.path.join (glmpath, rootname + '_volt.csv'), voltagebases, dictNames)
    gldlink, gldi, gldangi = load_glm_currents (os.path.join (glmpath, rootname + '_curr.csv'), dictNames, dictClasses)
  else:
    gldv = []
    gldi = []

# print (gldbus)
# print ('**GLM  V**', gldv)
# print ('**MAG V**', gldmagv)
# print ('**ANG V**', gldangv)
# print (gldlink)
# print ('**GLM  I**', gldi)
# print ('**ANG I**', gldangi)

  for row in check_branches:
    if (('dss_link' in row) and ('dss_bus' in row)):
      print_dss_flow (row['dss_bus'], row['dss_link'], magv1, angv1, i1, angi1, 'Base', fps)
      if dsspath:
        print_dss_flow (row['dss_bus'], row['dss_link'], magv2, angv2, i2, angi2, 'Converted', fps)
    if (do_gld and ('gld_link' in row) and ('gld_bus' in row)):
      print_glm_flow (row['gld_bus'], row['gld_link'], gldmagv, gldangv, gldi, gldangi, fps)

#  print (basepath+dssroot+'_s.csv', s1)
#  print (dsspath+dssroot+'_s.csv', s2)
#  print ('\n** BASE I**')
#  for key, val in i1.items():
#    print ('{:24s} {:10.4f}'.format (key, val))
#  print ('\n** BASE V**')
#  for key, val in v1.items():
#    print ('{:24s} {:10.4f}'.format (key, val))
# print ('\n** GLM I**')
# for key, val in gldi.items():
#   print ('{:24s} {:10.4f}'.format (key, val))
#  print ('\n** GLM V**')
#  for key, val in gldv.items():
#    print ('{:24s} {:10.4f}'.format (key, val))
  flog = open (dsspath + rootname + '_Summary.log', 'w')
  print ('Quantity  Case1   Case2', file=flog)
  for key in ['Status', 'Mode', 'Number', 'LoadMult', 'NumDevices', 'NumBuses', 
          'NumNodes', 'Iterations', 'ControlMode', 'ControlIterations', 'MaxPuVoltage',
          'MinPuVoltage', 'TotalMW', 'TotalMvar', 'MWLosses', 'pctLosses',
          'MvarLosses', 'Frequency']:
    print (key, s1[key], s2[key], file=flog)

  print ('\nRegulator, Case 1 Tap, Case 2 Tap', file=flog)
  for bus in t1:
    if bus in t2:
      print (bus, str(t1[bus]), str(t2[bus]), file=flog)
    else:
      print (bus, str(t1[bus]), '**ABSENT**', file=flog)
  for bus in t2:
    if bus not in t1:
      print (bus, '**ABSENT**', str(t2[bus]), file=flog)
  flog.close()

  # bus naming convention will be "bus name"_A, _B, or _C
  vdiff = {}
  for bus in v1:
    if bus in v2:
      vdiff [bus] = abs(v1[bus] - v2[bus])
  sorted_vdiff = sorted(vdiff.items(), key=operator.itemgetter(1))
  err_v_dss = error_norm (sorted_vdiff, 0.8)
  fcsv = open (dsspath + rootname + '_Compare_Voltages_DSS.csv', 'w')
  print ('bus_phs,vbase,vdss,vdiff', file=fcsv)
  for row in sorted_vdiff:
    if row[1] < 0.8:
      bus = row[0]
      print (bus, '{:.5f}'.format(v1[bus]), '{:.5f}'.format(v2[bus]), 
               '{:.5f}'.format(row[1]), sep=',', file=fcsv)
  fcsv.close()

  # bus naming convention will be "bus name"_A, _B, or _C
  err_v_glm = -1.0
  if do_gld:
    vdiff = {}
    for bus in v1:
      if bus in gldv:
        vdiff [bus] = abs(v1[bus] - gldv[bus])
    sorted_vdiff = sorted(vdiff.items(), key=operator.itemgetter(1))
    err_v_glm = error_norm (sorted_vdiff, 0.8)
    fcsv = open (dsspath + rootname + '_Compare_Voltages_GLM.csv', 'w')
    print ('bus_phs,vbase,vglm,vdiff', file=fcsv)
    for row in sorted_vdiff:
      if row[1] < 0.8:
        bus = row[0]
        print (bus, '{:.5f}'.format(v1[bus]), '{:.5f}'.format(gldv[bus]), 
                 '{:.5f}'.format(row[1]), sep=',', file=fcsv)
    fcsv.close()

  ftxt = open (dsspath + rootname + '_Missing_Nodes_DSS.txt', 'w')
  nmissing_1 = 0
  nmissing_2 = 0
  for bus in v1:
    if not bus in v2:
      print (bus, 'not in Case 2', file=ftxt)
      nmissing_2 += 1
  for bus in v2:
    if not bus in v1:
      print (bus, 'not in Case 1', file=ftxt)
      nmissing_1 += 1
  print (len(v1), 'Case 1 nodes,', nmissing_2, 'not in Case 2', file=ftxt)
  print (len(v2), 'Case 2 nodes,', nmissing_1, 'not in Case 1', file=ftxt)
  ftxt.close()

  # branch (link) naming convention will be "class.instance".1, .2 or .3 for OpenDSS
  idiff = {}
  for link in i1:
    if link in i2:
      idiff [link] = abs(i1[link] - i2[link])
  sorted_idiff = sorted(idiff.items(), key=operator.itemgetter(1))
  err_i_dss = error_norm (sorted_idiff)
  fcsv = open (dsspath + rootname + '_Compare_Currents_DSS.csv', 'w')
  print ('class.name.phs,ibase,idss,idiff', file=fcsv)
  for row in sorted_idiff:
    link = row[0]
    print (link, '{:.3f}'.format(i1[link]), '{:.3f}'.format(i2[link]), 
            '{:.3f}'.format(row[1]), sep=',', file=fcsv)
  fcsv.close()

  # from GridLAB-D the link names will start with line_, swt_, reg_ or xf_
  # if there are non-zero magA, magB or magC values, 
  #   look for the next phase current 1, 2, or 3 from the matching OpenDSS branch name
  # for example, GridLAB-D line_632670_A corresponds to OpenDSS Line.632670.1
  err_i_glm = -1.0
  if do_gld:
    idiff = {}
    for link in gldlink:
      dsslink = ''
      if link.startswith('LINE_'):
        dsslink = 'LINE.' + link[len('LINE_'):].upper()
      elif link.startswith('XF_'):
        dsslink = 'TRANSFORMER.' + link[len('XF_'):].upper()
      elif link.startswith('SWT_'):
        dsslink = 'LINE.' + link[len('SWT_'):].upper()
      elif link.startswith('REG_'):
        dsslink = 'TRANSFORMER.' + link[len('REG_'):].upper()
      for gldphs, dssphs in zip(['_A', '_B', '_C'], ['.1', '.2', '.3']):
        gldtarget = link + gldphs
        dsstarget = dsslink + dssphs
  #      print ('Looking for gld target {:s} matching dss target {:s}'.format (gldtarget, dsstarget))
        if gldtarget in gldi and dsstarget in i1:
          idiff [gldtarget] = [abs(i1[dsstarget] - gldi[gldtarget]), dsstarget]
    sorted_idiff = sorted(idiff.items(), key=operator.itemgetter(1))
    err_i_glm = error_norm_tuple (sorted_idiff)
    fcsv = open (dsspath + rootname + '_Compare_Currents_GLM.csv', 'w')
    print ('class_name_phs,ibase,iglm,idiff', file=fcsv)
    for row in sorted_idiff:
      gldtarget = row[0]
      phsdiff = row[1][0]
      dsstarget = row[1][1]
      print (gldtarget, '{:.3f}'.format(i1[dsstarget]), '{:.3f}'.format(gldi[gldtarget]), 
              '{:.3f}'.format(phsdiff), sep=',', file=fcsv)
    fcsv.close()

  ftxt = open (dsspath + rootname + '_Missing_Links_DSS.txt', 'w')
  nmissing_1 = 0
  nmissing_2 = 0
  for link in i1:
    if not link in i2:
      print (link, 'not in Case 2', file=ftxt)
      nmissing_2 += 1
  for link in i2:
    if not link in i1:
      print (link, 'not in Case 1', file=ftxt)
      nmissing_1 += 1
  print (len(i1), 'Case 1 links,', nmissing_2, 'not in Case 2', file=ftxt)
  print (len(i2), 'Case 2 links,', nmissing_1, 'not in Case 1', file=ftxt)
  ftxt.close()
  for fp in fps:
    print ('{:16s} Nbus=[{:6d},{:6d},{:6d}] Nlink=[{:6d},{:6d},{:6d}] MAEv=[{:7.4f},{:7.4f}] MAEi=[{:9.4f},{:9.4f}]'.format (
      rootname, len(v1), len(v2), len(gldv), len(i1), len(i2), len(gldi), err_v_dss, err_v_glm, err_i_dss, err_i_glm),
      file=fp)

def compare_cases (cases, rstFile=None, rstMode='w'):
  global dir1, dir2, dir3
  fps = []
  fps.append (sys.stdout)
  if rstFile is not None:
    fp = open (rstFile, rstMode)
    fps.append (fp)
  for row in cases:
    root = row['root']
    bases = row['bases']
    dir1 = row['path_xml']
    dir2 = row['outpath_dss']
    dir3 = row['outpath_glm']
    check_branches = []
    do_gld = False  # unless outpath_glm specified and skip_gld is not True
    if len(dir3) > 0:
      do_gld = True
    if 'skip_gld' in row:
      do_gld = not row['skip_gld']      
    if 'check_branches' in row:
      check_branches = row['check_branches']
    for i in range(len(bases)):
      bases[i] /= math.sqrt(3.0)
    write_comparisons (dir1, dir2, dir3, root, bases, check_branches, do_gld, fps)
  if rstFile is not None:
    fp.close()

# run this from the command line for GridAPPS-D platform scripts
if __name__ == "__main__":
  for row in casefiles:
    root = row['root']
    bases = row['bases']
    for i in range(len(bases)):
      bases[i] /= math.sqrt(3.0)
    write_comparisons (dir1, dir2, dir3, root, bases, check_branches=row['check_branches'], do_gld=row['do_gld'])

