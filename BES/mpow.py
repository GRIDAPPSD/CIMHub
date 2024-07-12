# Copyright (C) 2023-2024 Battelle Memorial Institute
import sys
import os
import math
import subprocess
import numpy as np
import i2x.mpow_utilities as mpow

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 
   'name': 'IEEE118', 
   'swingbus':'131',
   'load_scale':0.6748,
   'softlims': False,
   'glpk_opts': None,
   'min_kv_to_upgrade': 100.0,
   'min_contingency_mva': 400.0,
   'mva_upgrades': None,
   'gen_PG': [
     [31, 150.0],
     [57, 20.0],
     [58, 25.0],
     [59, 20.0],
     [60, 50.0],
     [61, 20.0],
     [62, 5.0],
     [63, 10.0],
     [64, 5.0],
     [65, 30.0],
     [66, 10.0],
     [67, 30.0],
     [68, 20.0],
     [69, 20.0],
     [70, 10.0],
     [71, 2.0],
     [72, 10.0],
     [73, 10.0],
     [74, 25.0],
     [75, 30.0]
     ],
   'edits': None,
   'edits_dont': [
     [1, 1.0, 'CT_TGEN', 31, 'PG', 'CT_REP', 150.0]]
  },
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 
   'name': 'WECC240', 
   'swingbus':'2438',
   'load_scale':1.0425,
   'softlims': False,
   'glpk_opts': None, # {'glpk.opts.itlim': 5},
   'min_kv_to_upgrade': 10.0,
   'min_contingency_mva': 5000.0,
   'mva_upgrades': [
     {'branch_number': 50, 'new_mva':1200.0},
     {'branch_number': 52, 'new_mva':1700.0},
     {'branch_number': 53, 'new_mva':1200.0},
     {'branch_number': 54, 'new_mva':1200.0},
     {'branch_number': 55, 'new_mva':1200.0},
     {'branch_number': 56, 'new_mva':1800.0},
     {'branch_number':264, 'new_mva':7200.0},
     {'branch_number':307, 'new_mva':2168.0},
     {'branch_number':332, 'new_mva':1200.0},
     {'branch_number':333, 'new_mva':1200.0},
     {'branch_number':406, 'new_mva': 750.0},
     {'branch_number':422, 'new_mva':3300.0},
     {'branch_number':430, 'new_mva':1500.0},
     {'branch_number':442, 'new_mva':1000.0},
     {'branch_number':443, 'new_mva':1000.0},
     {'branch_number':449, 'new_mva':1500.0}],
   'gen_PG': None,
   'edits': None},
  {'id': None,
   'name': 'IEEE39',
   'swingbus':'31',
   'load_scale':1.0000,
   'softlims': False,
   'glpk_opts': None,
   'min_kv_to_upgrade': 500.0,
   'min_contingency_mva': 1000.0,
   'mva_upgrades': None,
   'gen_PG': None,
   'edits': None}
  ]


# global constants
SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180.0 / math.pi
MVA_BASE = 100.0

# example in Octave:

# cd c:\src\cimhub\bes
# mpc = loadcase(WECC240);
# case_info(mpc)
# mpc = scale_load(1.0425,mpc);
# results=runpf(mpc);
# define_constants
# codes=matpower_gen_type(results.gentype);
# mg=[results.gen(:,GEN_BUS),results.gen(:,PG),results.gen(:,QG),codes]
# mb=[results.bus(:,VM),results.bus(:,VA)]
# csvwrite('wecc240mg.txt',mg)
# csvwrite('wecc240mb.txt',mb)

# mpc = loadcase(IEEE118);
# case_info(mpc)
# mpc = scale_load (0.6748, mpc);
# results=runpf(mpc);
# define_constants
# codes=matpower_gen_type(results.gentype);
# mg=[results.gen(:,GEN_BUS),results.gen(:,PG),results.gen(:,QG),codes]
# mb=[results.bus(:,VM),results.bus(:,VA)]
# csvwrite('ieee118mg.txt',mg)
# csvwrite('ieee118mb.txt',mb)

# sample code from TESP that automates Matpower in Octave
# https://github.com/pnnl/tesp/blob/develop/examples/capabilities/ercot/case8/tso_most.py

def write_solve_file (root, load_scale=1.0, editfile=None, pg=None):
  fscript = 'solve{:s}.m'.format(root)
  fsolved = '{:s}solved.m'.format(root)
  fsummary = '{:s}summary.txt'.format(root)
  fp = open (fscript, 'w')
  print ("""clear;""", file=fp)
  print ("""cd {:s}""".format (os.getcwd()), file=fp)
  print ("""define_constants;""", file=fp)
  if editfile is None:
    print ("""mpc = loadcase({:s});""".format (root.upper()), file=fp)
  else:
    print("""mpcbase = loadcase({:s});""".format (root.upper()), file=fp)
    print("""chgtab = {:s};""".format(editfile), file=fp)
    print("""mpc = apply_changes (1, mpcbase, chgtab);""", file=fp)
  if pg is not None:
    for row in pg:
      print ("""mpc.gen({:d},PG) = {:.2f};""".format (row[0], row[1]), file=fp)
  print ("""mpc = scale_load({:.5f},mpc);""".format (load_scale), file=fp)
  print ("""opt1 = mpoption('out.all', 0, 'verbose', 0);""", file=fp)
  print ("""results=runpf(mpc, opt1);""", file=fp)
  print ("""opt2 = mpoption('out.sys_sum', 1, 'out.bus', 0, 'out.branch', 0);""", file=fp)
  print ("""fd = fopen('{:s}', 'w');""".format (fsummary), file=fp)
  print ("""fprintf(fd,'results.success = %d\\n', results.success);""", file=fp)
  print ("""fprintf(fd,'results.iterations = %d\\n', results.iterations);""", file=fp)
  print ("""fprintf(fd,'results.et = %.4f\\n', results.et);""", file=fp)
  print ("""printpf(results, fd, opt2);""", file=fp)
  print ("""fclose(fd);""", file=fp)
  print ("""savecase('{:s}', results);""".format (fsolved), file=fp)
  print ("""codes=matpower_gen_type(results.gentype);""", file=fp)
  print ("""mg=[results.gen(:,GEN_BUS),results.gen(:,PG),results.gen(:,QG),codes];""", file=fp)
  print ("""mb=[results.bus(:,VM),results.bus(:,VA)];""", file=fp)
  print ("""csvwrite('{:s}mg.txt',mg);""".format (root), file=fp)
  print ("""csvwrite('{:s}mb.txt',mb);""".format (root), file=fp)
  print ("""exit;""", file=fp)
  fp.close()
  return fscript, fsolved, fsummary

def write_edits(edits, root):
  fp = open ('{:s}_edits.m'.format (root), 'w')
  print('function chgtab = {:s}_edits'.format(root), file=fp)
  mpow.write_most_table_indices(fp)
  print('  % label   prob   table   row col      chgtype  newval', file=fp)
  print('  chgtab = [', file=fp)
  for row in edits:
    print (' {:5d} {:9.7f} {:8s} {:4d} {:8s} {:8s} {:11.7f};'.format (row[0], row[1], row[2], row[3], row[4], row[5], row[6]), file=fp)
  print('  ];', file=fp)
  print('end', file=fp)
  fp.close()
  return '{:s}_edits'.format (root)

def summarize_overloads(d):
  print ('Overloads:')
  g = d['gen']
  ng = g.shape[0]
  b = d['branch']
  nb = b.shape[0]

  for i in range(ng):
    if g[i][mpow.PG] > g[i][mpow.PMAX]:
      print ('  Generator {:d} at {:d} has {:.2f} MW > {:.2f} MW'.format (i+1, int(g[i][mpow.GEN_BUS]), g[i][mpow.PG], g[i][mpow.PMAX]))
  for i in range(nb):
    if b[i][mpow.RATE_A] > 0.0:
      s1 = math.sqrt (b[i][mpow.PF]*b[i][mpow.PF] + b[i][mpow.QF]*b[i][mpow.QF])
      s2 = math.sqrt (b[i][mpow.PT]*b[i][mpow.PT] + b[i][mpow.QT]*b[i][mpow.QT])
      smax = max(s1, s2)
      if smax > b[i][mpow.RATE_A]: 
        print ('  Branch {:d} from {:d}-{:d} has {:.2f} MVA > {:.2f} MVA'.format (i+1, int(b[i][mpow.F_BUS]), int(b[i][mpow.T_BUS]), smax, b[i][mpow.RATE_A]))

if __name__ == '__main__':
  case_id = 0
  if len(sys.argv) > 1:
    case_id = int(sys.argv[1])
  sys_name = CASES[case_id]['name']
  load_scale = CASES[case_id]['load_scale']
  d = mpow.read_matpower_casefile ('{:s}.m'.format (sys_name))
  mpow.summarize_casefile (d, 'Input')
  edits = CASES[case_id]['edits']
  if edits is not None:
    editfile = write_edits (edits, sys_name)
  else:
    editfile = None
  fscript, fsolved, fsummary = write_solve_file (sys_name, load_scale, editfile, CASES[case_id]['gen_PG'])

  mpow.run_matpower_and_wait (fscript)

  mpow.print_solution_summary (fsummary, details=True)
  r = mpow.read_matpower_casefile (fsolved)
  mpow.summarize_casefile (r, 'Solved')
  print ('Min and max bus voltages=[{:.4f},{:.4f}]'.format (np.min(r['bus'][:,mpow.VM]),np.max(r['bus'][:,mpow.VM])))
  print ('Load = {:.3f} + j{:.3f} MVA'.format (np.sum(r['bus'][:,mpow.PD]),np.sum(r['bus'][:,mpow.QD])))
  print ('Gen =  {:.3f} + j{:.3f} MVA'.format (np.sum(r['gen'][:,mpow.PG]),np.sum(r['gen'][:,mpow.QG])))
  gen_online = np.array(r['gen'][:,mpow.GEN_STATUS]>0)
  print ('{:d} of {:d} generators on line'.format (int(np.sum(gen_online)),r['gen'].shape[0]))
  pgmax = np.sum(r['gen'][:,mpow.PMAX], where=gen_online)
  qgmax = np.sum(r['gen'][:,mpow.QMAX], where=gen_online)
  qgmin = np.sum(r['gen'][:,mpow.QMIN], where=gen_online)
  print ('Online capacity = {:.2f} MW, {:.2f} to {:.2f} MVAR'.format (pgmax, qgmin, qgmax))
  summarize_overloads (r)

