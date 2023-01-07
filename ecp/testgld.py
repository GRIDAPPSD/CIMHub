# Copyright (C) 2022 Battelle Memorial Institute
# file: testgld.py
#
# usage: python testgld.py
#
# input: from cases.json
#
# exports glm with profiles
# pre-conditions:
#    onestep.py has created the xml files
#    blazegraph engine is running

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import json
import sys
import os
import shutil
import subprocess
import numpy as np

template_files = {}

template_files['gld_daily_edits.glm'] = """class player {
  double value;
}
object player {
  name ClearPV;
  file "pclear.player";
  loop 1;
}
object player {
  name CloudyPV;
  file "pcloud.player";
  loop 1;
}
object player {
  name BumpPlayer;
  file "bump.player";
  loop 1;
}
object player {
  name Peaking;
  file "peaking.player";
  loop 1;
}
// minutes hours days months weekdays value
schedule BumpSched {
    * 0-5  * * * 0.0;
   0-5  6  * * * 0.0;
   6-11 6  * * * 0.1;
  12-17 6  * * * 0.2;
  18-23 6  * * * 0.3;
  24-29 6  * * * 0.4;
  30-35 6  * * * 0.5;
  36-41 6  * * * 0.6;
  42-47 6  * * * 0.7;
  48-53 6  * * * 0.8;
  54-59 6  * * * 0.9;
  *  7-18  * * * 1.0;
   0-5  19 * * * 1.0;
   6-11 19 * * * 0.9;
  12-17 19 * * * 0.8;
  18-23 19 * * * 0.7;
  24-29 19 * * * 0.6;
  30-35 19 * * * 0.5;
  36-41 19 * * * 0.4;
  42-47 19 * * * 0.3;
  48-53 19 * * * 0.2;
  54-59 19 * * * 0.1;
   * 20-23 * * * 0.0;
}
schedule CycleSched {
  interpolated;
  *   0-3 * * *  0.0;
  *   4-7 * * *  1.0;
  *  8-15 * * *  0.0;
  * 16-19 * * * -1.0;
  * 20-23 * * *  0.0;
}
schedule DssDefault {
  interpolated;
  *  0 * * * 0.6770;
  *  1 * * * 0.6256;
  *  2 * * * 0.6087;
  *  3 * * * 0.5833;
  *  4 * * * 0.58028;
  *  5 * * * 0.6025;
  *  6 * * * 0.657;
  *  7 * * * 0.7477;
  *  8 * * * 0.832;
  *  9 * * * 0.88;
  * 10 * * * 0.94;
  * 11 * * * 0.989;
  * 12 * * * 0.985;
  * 13 * * * 0.98;
  * 14 * * * 0.9898;
  * 15 * * * 0.999;
  * 16 * * * 1.000;
  * 17 * * * 0.958;
  * 18 * * * 0.936;
  * 19 * * * 0.913;
  * 20 * * * 0.876;
  * 21 * * * 0.876;
  * 22 * * * 0.828;
  * 23 * * * 0.756;
}"""

bump_player = """2022-08-01 0:00:00,0.0
+6h,0.0
+6m,0.1
+6m,0.2
+6m,0.3
+6m,0.4
+6m,0.5
+6m,0.6
+6m,0.7
+6m,0.8
+6m,0.9
+6m,1.0
+12h,1.0
+6m,0.9
+6m,0.8
+6m,0.7
+6m,0.6
+6m,0.5
+6m,0.4
+6m,0.3
+6m,0.2
+6m,0.1
+6m,0.0
+4h,0.0
"""

peaking_player = """2022-08-01 0:00:00,0.0
+11h,0.0
+6m,1.0
+54m,1.0
+4h,1.0
+6m,0.0
+54m,0.0
+7h,0.0
"""

template_files['gld_daily_run.glm'] = """clock {
  timezone EST+5EDT;
  starttime '2022-08-01 0:00:00';
  stoptime '2022-08-02 0:00:05';
};
#set complex_output_format=RECT  // compatible with Python and Pandas
#set relax_naming_rules=1
#set profiler=1
module powerflow {
  solver_method NR;
  line_capacitance TRUE;
};
module climate;
module generators;
module tape;
module reliability {
  report_event_log false;
};
object climate {
  name climate;
  latitude 45.0;
  solar_direct 93.4458; // 92.902;
}
#include "commercial_schedules.glm";
#define VSOURCE=7621.02
#include "gld_daily_base.glm";
#ifdef WANT_VI_DUMP
object voltdump {
  filename gld_daily_volt.csv;
  mode POLAR;
};
object currdump {
  filename gld_daily_curr.csv;
  mode POLAR;
};
#endif
object multi_recorder {
  file meters.csv;
  interval 5;
  property bess1_stmtr:measured_power,bess2_stmtr:measured_power,gen1_dgmtr:measured_power,gen2_dgmtr:measured_power,pv1_pvmtr:measured_power,pv2_pvmtr:measured_power,ld_load1:measured_power,ld_load2:measured_power;
}"""

cfg_json = '../queries/cimhubconfig.json'

if sys.platform == 'win32':
  shfile_upload = '_upload.bat'
  shfile_export = '_export.bat'
  shfile_glm = '_checkglm.bat'
  dssfile_run = '_check.dss'
else:
  shfile_upload = './_upload.sh'
  shfile_export = './_export.sh'
  shfile_glm = './_checkglm.sh'
  dssfile_run = '_check.dss'

def convert_dss_loadshape (dssfile, glmfile, tstart, tstep):
  data = np.loadtxt (dssfile)
  data /= max(data)
  fp = open (glmfile, 'w')
  print('{:s},{:.6f}'.format (tstart, data[0]), file=fp)
  for val in data[1:]:
    print ('{:s},{:.6f}'.format (tstep, val), file=fp)
  fp.close()

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()
  cases[:] = [x for x in cases if x['root'] == 'gld_daily']

  glmout = './glma/'
  for row in cases:
    row['outpath_csv'] = ''
    row['outpath_dss'] = ''
    row['outpath_glm'] = glmout
    row['export_options'] = ' -l=1.0 -m=1 -a=1 -e=carson'

  cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=True)
  p1 = subprocess.call (shfile_upload, shell=True)

  cimhub.insert_profiles ('gld_daily.dat')

  cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=True)
  p1 = subprocess.call (shfile_export, shell=True)
  shutil.copyfile('../support/commercial_schedules.glm', './glma/commercial_schedules.glm')
  convert_dss_loadshape ('base/pcloud.dat', 'glma/pcloud.player', '2022-08-01 0:00:00', '+1s')
  convert_dss_loadshape ('base/pclear.dat', 'glma/pclear.player', '2022-08-01 0:00:00', '+1s')
  fp = open ('glma/bump.player', 'w')
  print (bump_player, file=fp)
  fp.close()
  fp = open ('glma/peaking.player', 'w')
  print (peaking_player, file=fp)
  fp.close()

  dp = open (shfile_glm, 'w')
  for row in cases:
    print ('cd {:s}'.format (os.path.abspath(row['outpath_glm'])), file=dp)
    print ('gridlabd -D WANT_VI_DUMP=1 {:s}_run.glm >{:s}.log'.format (row['root'],row['root']), file=dp)
    for tok in ['edits', 'run']:
      fname = '{:s}_{:s}.glm'.format(row['root'], tok)
      fpath = os.path.join(row['outpath_glm'], fname)
      fp = open(fpath, 'w')
      print (template_files[fname], file=fp)
      fp.close()
  dp.close()
  p1 = subprocess.call (shfile_glm, shell=True)

