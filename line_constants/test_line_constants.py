# Copyright (C) 2022 Battelle Memorial Institute
# file: test_line_constants.py

import cimhub.api as cimhub

# spacing units are feet, miles, Hz
spdata_ercot = cimhub.convert_spdata_to_si ({'y':[45.0, 45.0, 45.0, 60.0], 'x': [-25.0, 0.0, 25.0, 0.0], 'nph': 3, # bundled w OHGW
  'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 345.0})
spdata_k47 = cimhub.convert_spdata_to_si ({'y':[29.0, 29.0, 29.0, 25.0], 'x': [0.0, 2.5, 7.0, 4.0], 'nph': 3, # 3-phase MGN
  'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47})
spdata_515 = cimhub.convert_spdata_to_si ({'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47,  # 3 CN
  'y': [-4.0, -4.0, -4.0], 'x': [-0.5, 0.0, 0.5], 'nph': 3})
spdata_520 = cimhub.convert_spdata_to_si ({'f': 60.0, 'rho': 100.0, 'len': 1.0, 'kv': 12.47, # 1 TS w bare neutral
  'y': [-4.0, -4.0], 'x': [0.0, 0.25], 'nph': 1})
# wire and cable units are inches and ohms per mile
wdata_795 = cimhub.convert_wdata_to_si ({'od': 1.108, 'id': 0.408, 'rdc': 0.1129, 'rac': 0.139, #'gmr': 0.45, # TODO: not handling the bundle correctly with GMR?
  'nb': 2, 'sb': 18.0, 'T1': 20.0, 'T2': 70.0, 'M': 228.1})
wdata_ehs = cimhub.convert_wdata_to_si ({'od': 0.36, 'id': 0.0, 'rdc': 6.74,
  'T1': 20.0, 'T2': 20.0, 'M': 228.1})
wdata_336 = cimhub.convert_wdata_to_si ({'od': 0.721, 'id': 0.2652, 'rdc': 0.2668, 'rac': 0.306, 'gmr': 0.2928,
  'nb': 1, 'sb': 0.0, 'T1': 20.0, 'T2': 56.0, 'M': 228.1})
wdata_4o = cimhub.convert_wdata_to_si ({'od': 0.563, 'id': 0.1878, 'rdc': 0.4199, 'rac': 0.592, 'gmr': 0.09768, # would need rdc=0.517 to get rac=0.592
  'T1': 20.0, 'T2': 56.0, 'M': 228.1})
wdata_1oCu = cimhub.convert_wdata_to_si ({'od': 0.368, 'gmr': 0.13356, 'rac': 0.607, 'M': 241.5})
cndata_250 = cimhub.convert_cndata_to_si ({'dia_ph': 0.567, 'gmr_ph':0.2052, 'rac_ph': 0.41, 'eps': 2.3,
  'ins': 0.220, 'dia_ins': 1.06, 'dia_cable': 1.29,
  'k': 13, 'dia_s': 0.0641, 'gmr_s': 0.02496, 'rac_s': 14.8722})
tsdata_1oCu = cimhub.convert_tsdata_to_si ({'dia': 0.368, 'gmr': 0.13320, 'rac': 0.97, 'eps': 2.3,
  'ins': 0.220, 'dia_ins': 0.82, 'dia_cable': 1.06, 'dia_shield': 0.88, 'tape': 0.005, 'lap_pct': 20.0})

zphs, yphs = cimhub.line_constants (spdata=spdata_ercot, ohdata=wdata_795, ndata=wdata_ehs, bPrintPrim=False)
zseq = cimhub.phs_to_seq(zphs)
yseq = cimhub.phs_to_seq(yphs)
z0 = zseq[0,0]
z1 = zseq[1,1]
y0 = yseq[0,0]
y1 = yseq[1,1]
c0 = 1.0e9*y0.imag/377.0
c1 = 1.0e9*y1.imag/377.0
print ('\nERCOT Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
print ('ERCOT Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
print ('ERCOT C1 = {:.4f} nF'.format (c1))
print ('ERCOT C0 = {:.4f} nF'.format (c0))
cimhub.print_matrix ('Zphase', zphs)

zphs, yphs = cimhub.line_constants (spdata=spdata_k47, ohdata=wdata_336, ndata=wdata_4o)
zseq = cimhub.phs_to_seq(zphs)
yseq = cimhub.phs_to_seq(yphs)
z0 = zseq[0,0]
z1 = zseq[1,1]
y0 = yseq[0,0]
y1 = yseq[1,1]
c0 = 1.0e9*y0.imag/377.0
c1 = 1.0e9*y1.imag/377.0
print ('\nK47 Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
print ('K47 Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))
print ('K47 C1 = {:.4f} nF'.format (c1))
print ('K47 C0 = {:.4f} nF'.format (c0))

# three-phase concentric neutral (IEEE 13 & Kersting example)
zcn, ycn = cimhub.line_constants(spdata_515, cndata=cndata_250, bPrintPrim=False)
zseq = cimhub.phs_to_seq(zcn)
z0 = zseq[0,0]
z1 = zseq[1,1]
y1 = ycn[0,0]
c1 = 1.0e9*y1.imag/377.0
print ('\nCN3 Z1 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
print ('CN3 C1 = {:.4f} nF'.format (c1))
print ('CN3 Z0 = {:.4f} + j{:.4f}'.format (z0.real, z0.imag))

# single-phase tape shield cable with separate bare neutral (IEEE 13 & Kersting example)
zts, yts = cimhub.line_constants(spdata_520, tsdata=tsdata_1oCu, ndata=wdata_1oCu)
z1 = zts[0,0]
y1 = yts[0,0]
c1 = 1.0e9*y1.imag/377.0
print ('\nTS1 Z11 = {:.4f} + j{:.4f}'.format (z1.real, z1.imag))
print ('TS1 C11 = {:.4f} nF'.format (c1))

