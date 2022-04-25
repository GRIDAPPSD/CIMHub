import numpy as np
import scipy.constants
import math
import cmath

# reference: https://doi.org/10.1109/PES.2007.386165

# physical and math constants
EPS0 = scipy.constants.epsilon_0
MU0 = scipy.constants.mu_0
PI = scipy.constants.pi

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

def line_constants (idata):
  # converting Hz, feet, miles, inches to SI
  w = idata['f'] * 2.0 * PI
  dlen = idata['len'] * scipy.constants.mile
  nc = len(idata['y'])
  nphs = idata['nph']
  ngw = nc - nphs
  y = np.array(idata['y']) * scipy.constants.foot
  x = np.array(idata['x']) * scipy.constants.foot
  Roph = idata['odphs'] * 0.5 * scipy.constants.inch
  Riph = idata['idphs'] * 0.5 * scipy.constants.inch
  Rogw = idata['odgw'] * 0.5 * scipy.constants.inch
  Rigw = idata['idgw'] * 0.5 * scipy.constants.inch
  Sb = idata['sb'] * scipy.constants.foot
  Rdcph = idata['rdcph'] * (idata['Mph']+idata['T2ph'])/(idata['Mph']+idata['T1ph']) / scipy.constants.mile
  Rdcgw = idata['rdcgw'] * (idata['Mgw']+idata['T2gw'])/(idata['Mgw']+idata['T1gw']) / scipy.constants.mile
  sig_e = 1.0 / idata['rho'] # (7)
  De = deri (sig_e, w) # (8)
  nb = idata['nb']
  if nb < 1:
    nb = 1.0
  r = rbeq (Roph, nb, Sb)

  zprim = np.zeros((nc, nc), dtype=complex)
  pprim = np.zeros((nc, nc), dtype=float)
  for i in range(nc):
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

  zprim *= dlen
  pprim /= dlen
  yprim = 1j*w*np.linalg.inv(pprim)

  zpp = zprim[0:nphs,0:nphs]
  zpn = zprim[0:nphs,nphs:nc]
  znp = zprim[nphs:nc,0:nphs]
  znn = zprim[nphs:nc,nphs:nc]
  zphs = zpp - zpn*np.linalg.inv(znn)*znp # (27)

  ppp = pprim[0:nphs,0:nphs]
  ppn = pprim[0:nphs,nphs:nc]
  pnp = pprim[nphs:nc,0:nphs]
  pnn = pprim[nphs:nc,nphs:nc]
  pphs = ppp - ppn*np.linalg.inv(pnn)*pnp # (28)

  yphs = 1j*w*np.linalg.inv(pphs)

  return zphs, yphs

def phs_to_seq(Z):
  return np.matmul(Ainv,np.matmul(Z,A))

if __name__ == '__main__':
  idata = {'y':[45.0, 45.0, 45.0, 60.0], 'x': [-25.0, 0.0, 25.0, 0.0], 'nph': 3,
    'odphs': 1.108, 'idphs': 0.408, 'rdcph': 0.1129, 'odgw': 0.36, 'idgw': 0.0, 'rdcgw': 6.74,
    'f': 60.0, 'rho': 100.0, 'len': 1.0, 'nb': 2, 'sb': 1.5, 'kv': 345.0,
    'T1ph': 20.0, 'T2ph': 75.0, 'Mph': 228.1,
    'T1gw': 20.0, 'T2gw': 20.0, 'Mgw': 228.1}

  zphs, yphs = line_constants (idata)
  zseq = phs_to_seq(zphs)
  yseq = phs_to_seq(yphs)

  z0 = zseq[0,0]
  z1 = zseq[1,1]
  y0 = yseq[0,0]
  y1 = yseq[1,1]
  m0 = -zseq[0,1]/z1
  m2 = -zseq[0,2]/z1

  print ('Zseq =', z0, z1)
  print ('Yseq =', y0, y1)
  print ('m0=', m0)
  print ('m2=', m2)
  print ('charging=', idata['kv']*idata['kv']*y1, 'MVA')

