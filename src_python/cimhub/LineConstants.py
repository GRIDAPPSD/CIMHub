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

# helper functions
def deri(sig, w): # (3), (8)
  return 1.0/cmath.sqrt(1j*w*MU0*sig)

def rho_c(rdc, ro, ri): # (1)
  return rdc*PI*(ro*ro-ri*ri)

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

def line_constants (spdata, ohdata=None, cndata=None, tsdata=None):
  # converting Hz, feet, miles, inches to SI
  w = spdata['f'] * 2.0 * PI
  dlen = spdata['len'] * scipy.constants.mile
  nc = len(spdata['y'])
  nphs = spdata['nph']
  ngw = nc - nphs
  y = np.array(spdata['y']) * scipy.constants.foot
  x = np.array(spdata['x']) * scipy.constants.foot
  sig_e = 1.0 / spdata['rho'] # (7)
  De = deri (sig_e, w) # (8)
  if cndata:
    nc = 2 * nphs + ngw  # TODO: ngw not supported for CN
  elif tsdata:
    nc = 2 * nphs + ngw
  zprim = np.zeros((nc, nc), dtype=complex)
  pprim = np.zeros((nc, nc), dtype=float)

  if ohdata:
    Roph = ohdata['odphs'] * 0.5 * scipy.constants.inch
    Riph = ohdata['idphs'] * 0.5 * scipy.constants.inch
    Rogw = ohdata['odgw'] * 0.5 * scipy.constants.inch
    Rigw = ohdata['idgw'] * 0.5 * scipy.constants.inch
    Sb = ohdata['sb'] * scipy.constants.foot
    Rdcph = ohdata['rdcph'] * (ohdata['Mph']+ohdata['T2ph'])/(ohdata['Mph']+ohdata['T1ph']) / scipy.constants.mile
    Rdcgw = ohdata['rdcgw'] * (ohdata['Mgw']+ohdata['T2gw'])/(ohdata['Mgw']+ohdata['T1gw']) / scipy.constants.mile
    nb = ohdata['nb']
    if nb < 1:
      nb = 1.0
    r = rbeq (Roph, nb, Sb)
    for i in range(nc): # form the primitive matrices for overhead lines
      if i >= nphs:
        zprim[i,i] = z_int(Rdcgw, Rogw, Rigw, w) + z_ext_ii (y[i], De, Rogw, w) # (14)
        pprim[i,i] = p_ii(y[i], Rogw) # (16)
      else:
        zprim[i,i] = (z_int(Rdcph, Roph, Riph, w) / nb) + z_ext_ii (y[i], De, r, w) # (14)
        pprim[i,i] = p_ii(y[i], r) # (16)
      for j in range(i):
        zprim[i,j] = z_ext_ij (y[i], y[j], x[i], x[j], De, w) # (15)
        zprim[j,i] = zprim[i,j]
        pprim[i,j] = p_ij (y[i], y[j], x[i], x[j]) # (17)
        pprim[j,i] = pprim[i,j]
  elif cndata:
    k = cndata['k']
    rs = 0.5 * cndata['dia_s'] * scipy.constants.inch
    ro = 0.5 * cndata['dia_ph'] * scipy.constants.inch
    rac_ph = cndata['rac_ph'] / scipy.constants.mile
    gmr_ph = cndata['gmr_ph'] * scipy.constants.inch
    rac_cn = cndata['rac_s'] / scipy.constants.mile / k # (18)
    rcn = 0.5 * (cndata['dia_cable'] - cndata['dia_s']) * scipy.constants.inch # (19)
    rs = 0.5 * cndata['dia_s'] * scipy.constants.inch
    gmr_s = cndata['gmr_s'] * scipy.constants.inch
    gmr_cn = math.pow (gmr_s * k * math.pow (rcn, k-1), 1.0/k)  # (20)
    Ccn = 2.0 * PI * EPS0 * cndata['eps'] / (math.log(rcn/ro) - (1.0/k)*math.log(k*rs/rcn)) # (21)
    Ycn = w * Ccn
    zint_ph = z_int(rac_ph, ro, 0.0, w)
    zint_cn = z_int(rac_cn, rcn, 0.0, w)
    zint_ph = complex (rac_ph, zint_ph.imag)
    zint_cn = complex (rac_cn, zint_cn.imag)
    for i in range(nphs): # form the primitive matrices for concentric neutral cables
      icn = i+nphs
      pprim[i,i] = 1.0 / Ccn
      pprim[icn, icn] = 1.0
      zprim[i,i] = zint_ph + z_ext_ii (abs(y[i]), De, ro, w)
      #TODO, with rcn, does not exactly match Kersting p. 103, 
      #  the following yields 1.2391+j1.3636 per mile instead of 1.2391+j1.3296
      zprim[icn,icn] = zint_cn + z_ext_ii (abs(y[i]+rcn), De, rcn, w) 
      # print (zprim[icn,icn] * scipy.constants.mile)
    for i in range(nc): # get all the off-diagonal terms
      if i < nphs:
        xi = x[i]
        yi = y[i]
      else:
        xi = x[i-nphs]
        yi = y[i-nphs] + rcn
      for j in range(i):
        if j < nphs:
          xj = x[j]
          yj = y[j]
        else:
          xj = x[j-nphs]
          yj = y[j-nphs] + rcn
        zprim[i,j] = z_ext_ij (yi, yj, xi, xj, De, w)
        zprim[j,i] = zprim[i,j]
  elif tsdata:
    rac_ph = tsdata['rac_ph'] / scipy.constants.mile
    rac_n = tsdata['rac_n'] / scipy.constants.mile
    gmr_ph = tsdata['gmr_ph'] * scipy.constants.inch
    gmr_n = tsdata['gmr_n'] * scipy.constants.inch
    r_ph = 0.5 * tsdata['dia_ph'] * scipy.constants.inch
    r_n = 0.5 * tsdata['dia_n'] * scipy.constants.inch
    dod = tsdata['dia_shield'] * scipy.constants.inch
    r_ts = 0.5 * dod
    tape = tsdata['tape'] * scipy.constants.inch
    # TODO; Kersting's (4.89) is different than (22)
    rac_ts = 0.3183 * RHO_TS / (dod * tape * math.sqrt(50.0/(100.0 - tsdata['lap_pct']))) # (22)
    gmr_ts = 0.5 * (dod - tape) # (23)
#    print (rac_ts * scipy.constants.mile)
    C = 2.0 * PI * EPS0 * tsdata['eps'] / math.log((r_ts - tape) / r_ph) # (24)
    zint_ph = z_int(rac_ph, r_ph, 0.0, w)
    zint_ts = z_int(rac_ts, r_ts, 0.0, w)
    zint_n = z_int(rac_n, r_n, 0.0, w)
    zint_ph = complex (rac_ph, zint_ph.imag)
    zint_ts = complex (rac_ts, zint_ts.imag)
    zint_n = complex (rac_n, zint_n.imag)
#   print (zint_ph * scipy.constants.mile)
#   print (zint_ts * scipy.constants.mile)
#   print (zint_n * scipy.constants.mile)
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
#    print (zprim * scipy.constants.mile)

  zprim *= dlen
  pprim /= dlen
  yprim = 1j*w*np.linalg.inv(pprim)

  zpp = zprim[0:nphs,0:nphs]
  zpn = zprim[0:nphs,nphs:nc]
  znp = zprim[nphs:nc,0:nphs]
  znn = zprim[nphs:nc,nphs:nc]
# if cndata:
#   print ('Zpp\n', zpp)
#   print ('Zpn\n', zpn)
#   print ('Znp\n', znp)
#   print ('Znn\n', znn)
  zphs = zpp - np.matmul(zpn, np.matmul(np.linalg.inv(znn), znp)) # (27)

  ppp = pprim[0:nphs,0:nphs]
  ppn = pprim[0:nphs,nphs:nc]
  pnp = pprim[nphs:nc,0:nphs]
  pnn = pprim[nphs:nc,nphs:nc]
  pphs = ppp - np.matmul(ppn, np.matmul(np.linalg.inv(pnn), pnp)) # (28)

  yphs = 1j*w*np.linalg.inv(pphs)

  return zphs, yphs

def phs_to_seq(Z):
  return np.matmul(Ainv,np.matmul(Z,A))

if __name__ == '__main__':
  spdata = {'y':[45.0, 45.0, 45.0, 60.0], 'x': [-25.0, 0.0, 25.0, 0.0], 'nph': 3,
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 345.0}
  ohdata = {'odphs': 1.108, 'idphs': 0.408, 'rdcph': 0.1129, 
    'odgw': 0.36, 'idgw': 0.0, 'rdcgw': 6.74, 'nb': 2, 'sb': 1.5, 
    'T1ph': 20.0, 'T2ph': 75.0, 'Mph': 228.1,
    'T1gw': 20.0, 'T2gw': 20.0, 'Mgw': 228.1}
  zphs, yphs = line_constants (spdata, ohdata=ohdata)
  zseq = phs_to_seq(zphs)
  yseq = phs_to_seq(yphs)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y0 = yseq[0,0]
  y1 = yseq[1,1]
# m0 = -zseq[0,1]/z1
# m2 = -zseq[0,2]/z1
# MVAch = spdata['kv']*spdata['kv']*y1
  print ('Overhead Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('Overhead Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('Overhead Y0 = j{:.4e}'.format (y0.imag))
  print ('Overhead Y1 = j{:.4e}'.format (y1.imag))

  spdata = {'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47,
    'y': [-4.0, -4.0, -4.0], 'x': [-0.5, 0.0, 0.5], 'nph': 3}
  cndata = {'dia_ph': 0.567, 'gmr_ph':0.2052, 'rac_ph': 0.41, 'eps': 2.3,
    'ins': 0.220, 'dia_ins': 1.06, 'dia_cable': 1.29,
    'k': 13, 'dia_s': 0.0641, 'gmr_s': 0.02496, 'rac_s': 14.8722}
  zcn, ycn = line_constants(spdata, cndata=cndata)
#  print ('Zcn\n', zcn)
  zseq = phs_to_seq(zcn)
  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y1 = ycn[0,0]
  print ('CN Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
  print ('CN Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('CN Y1 = j{:.4e}'.format (y1.imag))

  spdata = {'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47,
    'y': [-4.0, -4.0], 'x': [0.0, 0.25], 'nph': 1}
  tsdata = {'dia_ph': 0.368, 'gmr_ph': 0.13320, 'rac_ph': 0.97, 'eps': 2.3,
    'ins': 0.220, 'dia_ins': 0.82, 'dia_cable': 1.06, 'dia_shield': 0.88, 'tape': 0.005, 'lap_pct': 20.0,
    'dia_n': 0.368, 'gmr_n': 0.13356, 'rac_n': 0.607}
  zts, yts = line_constants(spdata, tsdata=tsdata)
#  print ('Zts\n', zts)
#  print ('Yts\n', yts)
  z1 = zts[0,0]
  y1 = yts[0,0]
  print ('TS Z = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
  print ('TS Y = j{:.4e}'.format (y1.imag))


