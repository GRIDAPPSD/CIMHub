import numpy as np
import scipy.constants
import math
import cmath

# reference: https://doi.org/10.1109/PES.2007.386165

# physical and math constants
EPS0 = scipy.constants.epsilon_0
MU0 = scipy.constants.mu_0
PI = scipy.constants.pi
RHO_TS = 2.3718e-8 # for copper tape shield
OMEGA = 2.0 * 60.0 * math.pi

# symmetrical components transformation
a = -0.5 + 1j*0.5*math.sqrt(3.0)
a2 = a*a
A = np.ones((3,3),dtype=complex)
A[1,1] = a2
A[1,2] = a
A[2,2] = A[1,1]
A[2,1] = A[1,2]
Ainv = np.ones((3,3),dtype=complex)
Ainv[1,1] = a
Ainv[1,2] = a2
Ainv[2,2] = Ainv[1,1]
Ainv[2,1] = Ainv[1,2]
Ainv /= 3.0

def print_matrix (label, z):
  print ('\n{:s}'.format(label))
  if 'complex' in str(z.dtype):
    for i in range(z.shape[0]):
      print (' '.join('{:.4f}+j{:.4f}'.format(val.real, val.imag) for val in z[i]))
  elif 'float' in str(z.dtype):
    for i in range(z.shape[0]):
      print (' '.join('{:.4e}'.format(val) for val in z[i]))

# helper functions
def deri(sig, w): # (3), (8)
  return 1.0/cmath.sqrt(1j*w*MU0*sig)

def rho_c(rdc, ro, ri): # (1)
  return rdc*PI*(ro*ro-ri*ri)

def z_int_gmr(rac, gmr, w):
  return rac + (1j*w*MU0/2.0/PI) * math.log (1.0/gmr)

def z_int(rdc, ro, ri, w): # (2), (4)-(7)
  sig_c = 1.0 / rho_c(rdc, ro, ri)
  dc = deri(sig_c, w)
  zhigh = 1.0 / 2.0 / PI / sig_c / dc / ro
  return cmath.sqrt(rdc*rdc + zhigh*zhigh)

def z_ext_ii(h, d, r, w): # (11)
  return (1j*w*MU0/2.0/PI) * cmath.log (2.0*(h+d)/r)

def z_ext_ij(hi, hj, xi, xj, d, w): # (12)
  d1 = 2.0*d+hi+hj
  d2 = xi-xj
  n1 = hi-hj
  n2 = d2
  return (1j*w*MU0/4.0/PI) * cmath.log ((d1*d1 + d2*d2)/(n1*n1 + n2*n2))

def rbeq(ro, nb, sb): # (9) - (10)
  if nb > 1 and sb > 0.0:
    rb = 0.5*sb/math.sin(PI/nb)
    return math.pow(ro*nb*math.pow(rb,nb-1), 1.0/nb)
  return ro

def p_ii(h, r): # (16)
  return (0.5/PI/EPS0) * math.log (2.0*h/r)

def p_ij(hi, hj, xi, xj): # (17)
  d1 = hi+hj
  d2 = xi-xj
  n1 = hi-hj
  n2 = d2
  arg = (d1*d1 + d2*d2) / (n1*n1 + n2*n2)
  return (0.5/PI/EPS0) * math.log (math.sqrt(arg))

def convert_wdata_to_si(wdata):
  if 'od' in wdata:
    wdata['od'] = wdata['od'] * scipy.constants.inch
  if 'id' in wdata:
    wdata['id'] = wdata['id'] * scipy.constants.inch
  if 'sb' in wdata:
    wdata['sb'] = wdata['sb'] * scipy.constants.inch
  if 'T1' in wdata and 'T1' in wdata and 'M' in wdata and 'rdc' in wdata:
    wdata['rdc'] = wdata['rdc'] * (wdata['M']+wdata['T2'])/(wdata['M']+wdata['T1']) / scipy.constants.mile
  if 'rac' in wdata:
    wdata['rac'] = wdata['rac'] / scipy.constants.mile
  if 'gmr' in wdata:
    wdata['gmr'] = wdata['gmr'] * scipy.constants.inch
  return wdata

def convert_cndata_to_si(cndata):
  cndata['dia_s'] = cndata['dia_s'] * scipy.constants.inch
  cndata['dia_ph'] = cndata['dia_ph'] * scipy.constants.inch
  cndata['dia_cable'] = cndata['dia_cable'] * scipy.constants.inch
  cndata['dia_ins'] = cndata['dia_ins'] * scipy.constants.inch
  cndata['ins'] = cndata['ins'] * scipy.constants.inch
  cndata['gmr_ph'] = cndata['gmr_ph'] * scipy.constants.inch
  cndata['gmr_s'] = cndata['gmr_s'] * scipy.constants.inch
  cndata['rac_ph'] = cndata['rac_ph'] / scipy.constants.mile
  cndata['rac_s'] = cndata['rac_s'] / scipy.constants.mile
  return cndata

def convert_tsdata_to_si(tsdata):
  tsdata['dia'] = tsdata['dia'] * scipy.constants.inch
  tsdata['dia_shield'] = tsdata['dia_shield'] * scipy.constants.inch
  tsdata['dia_cable'] = tsdata['dia_cable'] * scipy.constants.inch
  tsdata['dia_ins'] = tsdata['dia_ins'] * scipy.constants.inch
  tsdata['ins'] = tsdata['ins'] * scipy.constants.inch
  tsdata['tape'] = tsdata['tape'] * scipy.constants.inch
  tsdata['gmr'] = tsdata['gmr'] * scipy.constants.inch
  tsdata['rac'] = tsdata['rac'] / scipy.constants.mile
  return tsdata

def convert_spdata_to_si(spdata):
  spdata['len'] = spdata['len'] * scipy.constants.mile
  spdata['w'] = spdata['f'] * 2.0 * PI
  for i in range(len(spdata['y'])):
    spdata['y'][i] *= scipy.constants.foot
    spdata['x'][i] *= scipy.constants.foot
  return spdata

def line_constants (spdata, ohdata=None, cndata=None, tsdata=None, ndata=None, bPrintPrim=False):
  # converting Hz, feet, miles, inches to SI
  w = spdata['w']
  dlen = spdata['len']
  nc = len(spdata['y'])
  nphs = spdata['nph']
  ngw = nc - nphs
  y = np.array(spdata['y'])
  x = np.array(spdata['x'])
  sig_e = 1.0 / spdata['rho'] # (7)
  De = deri (sig_e, w) # (8)
  if cndata:
    nc = 2 * nphs + ngw
  elif tsdata:
    nc = 2 * nphs + ngw
  zprim = np.zeros((nc, nc), dtype=complex)
  pprim = np.zeros((nc, nc), dtype=float)

  if ohdata:
    Roph = ohdata['od'] * 0.5
    Riph = ohdata['id'] * 0.5
    Sb = ohdata['sb']
    Rdcph = ohdata['rdc']
    nb = ohdata['nb']
    if nb < 1:
      nb = 1.0
    r_ph = rbeq (Roph, nb, Sb)
    if 'rac' in ohdata and 'gmr' in ohdata:
      rac_ph = ohdata['rac']
      gmr_ph = ohdata['gmr']
      z_int_ph = z_int_gmr(rac_ph, gmr_ph, w) / nb
      rext_ph = 1.0
    else:
      z_int_ph = z_int(Rdcph, Roph, Riph, w) / nb
      rext_ph = r_ph
    if ngw > 0:
      Rogw = ndata['od'] * 0.5
      Rigw = ndata['id'] * 0.5
      Rdcgw = ndata['rdc']
      if 'rac' in ndata and 'gmr' in ndata:
        rac_gw = ndata['rac']
        gmr_gw = ndata['gmr']
        z_int_gw = z_int_gmr(rac_gw, gmr_gw, w)
        rext_gw = 1.0
      else:
        z_int_gw = z_int(Rdcgw, Rogw, Rigw, w)
        rext_gw = Rogw
    for i in range(nc): # form the primitive matrices for overhead lines
      if i >= nphs:
        zprim[i,i] = z_int_gw + z_ext_ii (y[i], De, rext_gw, w) # (14)
        pprim[i,i] = p_ii(y[i], Rogw) # (16)
      else:
        zprim[i,i] = z_int_ph + z_ext_ii (y[i], De, rext_ph, w) # (14)
        pprim[i,i] = p_ii(y[i], r_ph) # (16)
      for j in range(i):
        zprim[i,j] = z_ext_ij (y[i], y[j], x[i], x[j], De, w) # (15)
        zprim[j,i] = zprim[i,j]
        pprim[i,j] = p_ij (y[i], y[j], x[i], x[j]) # (17)
        pprim[j,i] = pprim[i,j]
  elif cndata:
    k = cndata['k']
    r_ph = 0.5 * cndata['dia_ph']
    rac_ph = cndata['rac_ph']
    gmr_ph = cndata['gmr_ph']
    rac_cn = cndata['rac_s'] / k # (18)
    r_cn = 0.5 * (cndata['dia_cable'] - cndata['dia_s']) # (19)
    r_s = 0.5 * cndata['dia_s']
    gmr_s = cndata['gmr_s']
    gmr_cn = math.pow (gmr_s * k * math.pow (r_cn, k-1), 1.0/k)  # (20)
    Ccn = 2.0 * PI * EPS0 * cndata['eps'] / (math.log(r_cn/r_ph) - (1.0/k)*math.log(k*r_s/r_cn)) # (21)
    Ycn = w * Ccn
    zint_ph = z_int(rac_ph, r_ph, 0.0, w)
    zint_cn = z_int(rac_cn, r_cn, 0.0, w)
    zint_ph = complex (rac_ph, zint_ph.imag)
    zint_cn = complex (rac_cn, zint_cn.imag)
    if ngw > 0:
      rac_n = ndata['rac']
      r_n = 0.5 * ndata['od']
      zint_n = z_int(rac_n, r_n, 0.0, w)
      zint_n = complex (rac_n, zint_n.imag)
    for i in range(nc): # primitive P matrix for CN cable
      if i < nphs:
        pprim[i,i] = 1.0 / Ccn
      else:
        pprim[i,i] = 1.0
    for i in range(nphs): # diagonal terms of primitive Z matrix
      zprim[i,i] = zint_ph + z_ext_ii (abs(y[i]), De, r_ph, w) # phase conductor
      #TODO, with rcn, does not exactly match Kersting p. 103,
      #  the following yields 1.2391+j1.3636 per mile instead of 1.2391+j1.3296
      zprim[i+nphs,i+nphs] = zint_cn + z_ext_ii (abs(y[i]+r_cn), De, r_cn, w) # concentric neutral
      for j in range(i): # off diagonals from phases to other phases, and CNs to other CNs or phases
        zprim[i,j] = z_ext_ij (y[i], y[j], x[i], x[j], De, w)  # phase-phase
        zprim[j,i] = zprim[i,j]
        zprim[i+nphs,j+nphs] = zprim[i,j] # CN-CN
        zprim[j+nphs,i+nphs] = zprim[i,j]
        zprim[i+nphs,j] = zprim[i,j] # CN-phase
        zprim[j,i+nphs] = zprim[i,j]
        zprim[j+nphs,i] = zprim[i,j]
        zprim[i,j+nphs] = zprim[i,j]
      zprim[i,i+nphs] = z_ext_ij (r_cn, 0.0, 0.0, 0.0, De, w) # off diagonal from CNs to their own phases
      zprim[i+nphs,i] = zprim[i,i+nphs]
    for i in range(ngw): # diagonal terms of buried bare neutrals
      igw = i + 2*nphs
      zprim[igw,igw] = zint_n + z_ext_ii (abs(y[i+nphs]), De, r_n, w) # separate neutral
      for j in range(nphs): # neutral off-diagonals to phases and tape shields
        zprim[igw,j] = z_ext_ij (y[i+nphs], y[j], x[i+nphs], x[j], De, w)
        zprim[j,igw] = zprim[igw,j]
        zprim[igw,j+nphs] = zprim[igw,j]
        zprim[j+nphs,igw] = zprim[igw,j]
  elif tsdata:
    rac_ph = tsdata['rac']
    gmr_ph = tsdata['gmr']
    r_ph = 0.5 * tsdata['dia']
    dod = tsdata['dia_shield']
    r_ts = 0.5 * dod
    tape = tsdata['tape']
    # TODO; Kersting's (4.89) is different than (22)
    rac_ts = 0.3183 * RHO_TS / (dod * tape * math.sqrt(50.0/(100.0 - tsdata['lap_pct']))) # (22)
    gmr_ts = 0.5 * (dod - tape) # (23)
    C = 2.0 * PI * EPS0 * tsdata['eps'] / math.log((r_ts - tape) / r_ph) # (24)
    zint_ph = z_int(rac_ph, r_ph, 0.0, w)
    zint_ts = z_int(rac_ts, r_ts, 0.0, w)
    zint_ph = complex (rac_ph, zint_ph.imag)
    zint_ts = complex (rac_ts, zint_ts.imag)
    if ndata is not None:
      rac_n = ndata['rac']
      r_n = 0.5 * ndata['od']
      zint_n = z_int(rac_n, r_n, 0.0, w)
      zint_n = complex (rac_n, zint_n.imag)
    for i in range(nc): # primitive P matrix for TS cable
      if i < nphs:
        pprim[i,i] = 1.0 / C
      else:
        pprim[i,i] = 1.0
    for i in range(nphs): # diagonal terms of primitive Z matrix
      zprim[i,i] = zint_ph + z_ext_ii (abs(y[i]), De, r_ph, w) # phase conductor
      zprim[i+nphs,i+nphs] = zint_ts + z_ext_ii (abs(y[i]), De, r_ts, w) # tape shield
      for j in range(i): # off diagonals from phases to other phases, and tape shields to other tape shields or phases
        zprim[i,j] = z_ext_ij (y[i], y[j], x[i], x[j], De, w)  # phase-phase
        zprim[j,i] = zprim[i,j]
        zprim[i+nphs,j+nphs] = zprim[i,j] # TS-TS
        zprim[j+nphs,i+nphs] = zprim[i,j]
        zprim[i+nphs,j] = zprim[i,j] # TS-phase
        zprim[j,i+nphs] = zprim[i,j]
        zprim[j+nphs,i] = zprim[i,j]
        zprim[i,j+nphs] = zprim[i,j]
      zprim[i,i+nphs] = z_ext_ij (gmr_ts, 0.0, 0.0, 0.0, De, w) # off diagonal from tape shields to their own phases
      zprim[i+nphs,i] = zprim[i,i+nphs]
    for i in range(ngw): # diagonal terms of buried bare neutrals
      igw = i + 2*nphs
      zprim[igw,igw] = zint_n + z_ext_ii (abs(y[i+nphs]), De, r_n, w) # separate neutral
      for j in range(nphs): # neutral off-diagonals to phases and tape shields
        zprim[igw,j] = z_ext_ij (y[i+nphs], y[j], x[i+nphs], x[j], De, w)
        zprim[j,igw] = zprim[igw,j]
        zprim[igw,j+nphs] = zprim[igw,j]
        zprim[j+nphs,igw] = zprim[igw,j]

  if bPrintPrim:
    print_matrix ('Zprim', zprim * scipy.constants.mile)
    print_matrix ('Pprim', pprim)

  zprim *= dlen
  pprim /= dlen
  yprim = 1j*w*np.linalg.inv(pprim)

  zpp = zprim[0:nphs,0:nphs]
  zpn = zprim[0:nphs,nphs:nc]
  znp = zprim[nphs:nc,0:nphs]
  znn = zprim[nphs:nc,nphs:nc]
  if znn.size > 0:
    zphs = zpp - np.matmul(zpn, np.matmul(np.linalg.inv(znn), znp)) # (27)
  else:
    zphs = zpp

  ppp = pprim[0:nphs,0:nphs]
  ppn = pprim[0:nphs,nphs:nc]
  pnp = pprim[nphs:nc,0:nphs]
  pnn = pprim[nphs:nc,nphs:nc]
  if pnn.size > 0:
    pphs = ppp - np.matmul(ppn, np.matmul(np.linalg.inv(pnn), pnp)) # (28)
  else:
    pphs = ppp

  yphs = 1j*w*np.linalg.inv(pphs)

  return zphs, yphs

def phs_to_seq(Z):
  return np.matmul(Ainv,np.matmul(Z,A))

if __name__ == '__main__':
  spdata_ercot = convert_spdata_to_si ({'y':[45.0, 45.0, 45.0, 60.0], 'x': [-25.0, 0.0, 25.0, 0.0], 'nph': 3, # bundled w OHGW
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 345.0})
  spdata_k47 = convert_spdata_to_si ({'y':[29.0, 29.0, 29.0, 25.0], 'x': [0.0, 2.5, 7.0, 4.0], 'nph': 3, # 3-phase MGN
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47})
  spdata_500 = convert_spdata_to_si ({'y':[28.0, 28.0, 28.0, 24.0], 'x': [-4.0, -1.0, 3.0, 0.0], 'nph': 3, # 3-phase MGN
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47})
  spdata_500d = convert_spdata_to_si ({'y':[28.0, 28.0, 28.0], 'x': [-4.0, -1.0, 3.0], 'nph': 3, # 3-phase ungrounded
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47})
  spdata_505 = convert_spdata_to_si ({'y':[28.0, 28.0, 24.0], 'x': [-4.0, 3.0, 0.0], 'nph': 2, # 2-phase MGN
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47})
  spdata_510 = convert_spdata_to_si ({'y':[29.0, 24.0], 'x': [0.5, 0.0], 'nph': 1, # 1-phase MGN
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47})
  spdata_515 = convert_spdata_to_si ({'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47,  # 3 CN
    'y': [-4.0, -4.0, -4.0], 'x': [-0.5, 0.0, 0.5], 'nph': 3})
  spdata_515x = convert_spdata_to_si ({'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47, # 3 CN w bare neutral
    'y': [-4.0, -4.0, -4.0, -4.0], 'x': [-0.5, 0.0, 0.5, 0.25], 'nph': 3})
  spdata_520 = convert_spdata_to_si ({'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47, # 1 TS w bare neutral
    'y': [-4.0, -4.0], 'x': [0.0, 0.25], 'nph': 1})
  spdata_520x = convert_spdata_to_si ({'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47, # 3 TS w bare neutral
    'y': [-4.0, -4.0, -4.0, -4.0], 'x': [0.0, 0.25, 0.50, 0.75], 'nph': 3})

  # if rac given, bypass the temperature correction
  # if gmr given, bypass the penetration depth on conductors
  wdata_795 = convert_wdata_to_si ({'od': 1.108, 'id': 0.408, 'rdc': 0.1129, 'rac': 0.139, #'gmr': 0.45, # TODO: not handling the bundle correctly with GMR?
    'nb': 2, 'sb': 18.0, 'T1': 20.0, 'T2': 70.0, 'M': 228.1})
  wdata_ehs = convert_wdata_to_si ({'od': 0.36, 'id': 0.0, 'rdc': 6.74,
    'T1': 20.0, 'T2': 20.0, 'M': 228.1})
  wdata_556 = convert_wdata_to_si ({'od': 0.927, 'id': 0.3414, 'rdc': 0.1613, 'rac': 0.186, 'gmr': 0.3732,
    'nb': 1, 'sb': 0.0, 'T1': 20.0, 'T2': 56.0, 'M': 228.1})
  wdata_336 = convert_wdata_to_si ({'od': 0.721, 'id': 0.2652, 'rdc': 0.2668, 'rac': 0.306, 'gmr': 0.2928,
    'nb': 1, 'sb': 0.0, 'T1': 20.0, 'T2': 56.0, 'M': 228.1})
  wdata_4o = convert_wdata_to_si ({'od': 0.563, 'id': 0.1878, 'rdc': 0.4199, 'rac': 0.592, 'gmr': 0.09768, # would need rdc=0.517 to get rac=0.592
    'T1': 20.0, 'T2': 56.0, 'M': 228.1})
  wdata_1o = convert_wdata_to_si ({'od': 0.398, 'id': 0.1327, 'rdc': 0.8144, 'rac': 1.12, 'gmr': 0.05352,
    'nb': 1, 'sb': 0.0, 'T1': 20.0, 'T2': 75.0, 'M': 228.1})
  wdata_1oCu = convert_wdata_to_si ({'od': 0.368, 'gmr': 0.13356, 'rac': 0.607, 'M': 241.5})
  cndata_250 = convert_cndata_to_si ({'dia_ph': 0.567, 'gmr_ph':0.2052, 'rac_ph': 0.41, 'eps': 2.3,
    'ins': 0.220, 'dia_ins': 1.06, 'dia_cable': 1.29,
    'k': 13, 'dia_s': 0.0641, 'gmr_s': 0.02496, 'rac_s': 14.8722})
  tsdata_1oCu = convert_tsdata_to_si ({'dia': 0.368, 'gmr': 0.13320, 'rac': 0.97, 'eps': 2.3,
    'ins': 0.220, 'dia_ins': 0.82, 'dia_cable': 1.06, 'dia_shield': 0.88, 'tape': 0.005, 'lap_pct': 20.0})

  # four-conductor, three-phase overhead line (ERCOT example with bundling and OHGW)
  zphs, yphs = line_constants (spdata=spdata_ercot, ohdata=wdata_795, ndata=wdata_ehs, bPrintPrim=False)
  zseq = phs_to_seq(zphs)
  yseq = phs_to_seq(yphs)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y0 = yseq[0,0]
  y1 = yseq[1,1]
  c0 = 1.0e9*y0.imag/OMEGA
  c1 = 1.0e9*y1.imag/OMEGA
# m0 = -zseq[0,1]/z1
# m2 = -zseq[0,2]/z1
# MVAch = spdata['kv']*spdata['kv']*y1
  print ('\nERCOT Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('ERCOT Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('ERCOT C1 = {:.4f} nF'.format (c1))
  print ('ERCOT C0 = {:.4f} nF'.format (c0))

  # four-conductor, three-phase overhead line (Kersting example 4.1)
  zphs, yphs = line_constants (spdata=spdata_k47, ohdata=wdata_336, ndata=wdata_4o)
  zseq = phs_to_seq(zphs)
  yseq = phs_to_seq(yphs)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y0 = yseq[0,0]
  y1 = yseq[1,1]
  c0 = 1.0e9*y0.imag/OMEGA
  c1 = 1.0e9*y1.imag/OMEGA
  print ('\nK47 Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('K47 Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('K47 C1 = {:.4f} nF'.format (c1))
  print ('K47 C0 = {:.4f} nF'.format (c0))

  # four-conductor, three-phase overhead line (IEEE 13 example)
  zphs, yphs = line_constants (spdata_500, ohdata=wdata_556, ndata=wdata_4o)
  zseq = phs_to_seq(zphs)
  yseq = phs_to_seq(yphs)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y0 = yseq[0,0]
  y1 = yseq[1,1]
  c0 = 1.0e9*y0.imag/OMEGA
  c1 = 1.0e9*y1.imag/OMEGA
  print ('\nOH601 Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('OH601 Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('OH601 C1 = {:.4f} nF'.format (c1))
  print ('OH601 C0 = {:.4f} nF'.format (c0))

  # three-conductor, three-phase overhead line (delta example)
  zphs, yphs = line_constants (spdata_500d, ohdata=wdata_556)
  zseq = phs_to_seq(zphs)
  yseq = phs_to_seq(yphs)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y0 = yseq[0,0]
  y1 = yseq[1,1]
  c0 = 1.0e9*y0.imag/OMEGA
  c1 = 1.0e9*y1.imag/OMEGA
  print ('\nOH601d Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('OH601d Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('OH601d C1 = {:.4f} nF'.format (c1))
  print ('OH601d C0 = {:.4f} nF'.format (c0))

  # three-conductor, two-phase overhead line (IEEE 13 example)
  zphs, yphs = line_constants (spdata_505, ohdata=wdata_1o, ndata=wdata_1o)
  print ('\nOH603 Z11 = {:.4f} + j{:.4f}'.format (zphs[0,0].real, zphs[0,0].imag))
  print ('OH603 Z21 = {:.4f} + j{:.4f}'.format (zphs[1,0].real, zphs[1,0].imag))
  print ('OH603 Z22 = {:.4f} + j{:.4f}'.format (zphs[1,1].real, zphs[1,1].imag))
  print ('OH603 C11 = {:.4f} nF'.format (1.0e9*yphs[0,0].imag/OMEGA))
  print ('OH603 C21 = {:.4f} nF'.format (1.0e9*yphs[1,0].imag/OMEGA))
  print ('OH603 C22 = {:.4f} nF'.format (1.0e9*yphs[1,1].imag/OMEGA))

  # two-conductor, single-phase overhead line (IEEE 13 example)
  zphs, yphs = line_constants (spdata=spdata_510, ohdata=wdata_1o, ndata=wdata_1o)
  print ('\nOH605 Z11 = {:.4f} + j{:.4f}'.format (zphs[0,0].real, zphs[0,0].imag))
  print ('OH605 C11 = {:.4f} nF'.format (1.0e9*yphs[0,0].imag/OMEGA))

  # three-phase concentric neutral (IEEE 13 & Kersting example)
  zcn, ycn = line_constants(spdata_515, cndata=cndata_250, bPrintPrim=False)
  zseq = phs_to_seq(zcn)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y1 = ycn[0,0]
  c1 = 1.0e9*y1.imag/OMEGA
  print ('\nCN3 Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('CN3 C1 = {:.4f} nF'.format (c1))
  print ('CN3 Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))

  # single-phase tape shield cable with separate bare neutral (IEEE 13 & Kersting example)
  zts, yts = line_constants(spdata_520, tsdata=tsdata_1oCu, ndata=wdata_1oCu)
  z1 = zts[0,0]
  y1 = yts[0,0]
  c1 = 1.0e9*y1.imag/OMEGA
  print ('\nTS1 Z11 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('TS1 C11 = {:.4f} nF'.format (c1))

  # three-phase tape shield cable with separate bare neutral
  zts, yts = line_constants(spdata_520x, tsdata=tsdata_1oCu, ndata=wdata_1oCu, bPrintPrim=False)
  zseq = phs_to_seq(zts)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y1 = yts[0,0]
  c1 = 1.0e9*y1.imag/OMEGA
  print ('\nTS3 Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('TS3 Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('TS3 C1 = {:.4f} nF'.format (c1))

  # three-phase concentric neutral cable with separate bare neutral
  zcn, ycn = line_constants(spdata_515x, cndata=cndata_250, ndata=wdata_1oCu)
  zseq = phs_to_seq(zcn)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y1 = ycn[0,0]
  c1 = 1.0e9*y1.imag/OMEGA
  print ('\nCN3n Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('CN3n Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('CN3n C1 = {:.4f} nF'.format (c1))

