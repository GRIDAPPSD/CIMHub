# Copyright (C) 2022 Battelle Memorial Institute
# file: testgld.py
#
# usage: python testgld.py
#
# input: from cases.json
#
# exports dss and glm with profiles
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

template_files = {}

template_files['ecp_daily_edits.glm'] = """New Loadshape.Cloud npts=86401 sinterval=1 csvfile=..\\base\\pcloud.dat action=normalize
New Loadshape.Clear npts=86401 sinterval=1 csvfile=..\\base\\pclear.dat action=normalize"""

template_files['ecp_daily_run.glm'] = """clock {
  timezone EST+5EDT;
  starttime '2000-01-01 0:00:00';
  stoptime '2000-01-01 0:00:00';
};
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
#include "ecp_daily_base.glm";
#ifdef WANT_VI_DUMP
object voltdump {
  filename ecp_daily_volt.csv;
  mode POLAR;
};
object currdump {
  filename ecp_daily_curr.csv;
  mode POLAR;
};
#endif"""

if sys.platform == 'win32':
  cfg_json = '../queries/cimhubconfig.json'
  shfile_upload = '_upload.bat'
  shfile_export = '_export.bat'
  shfile_glm = '_checkglm.bat'
  dssfile_run = '_check.dss'
else:
  cfg_json = '../queries/cimhubdocker.json'
  shfile_upload = './_upload.sh'
  shfile_export = './_export.sh'
  shfile_glm = './_checkglm.sh'
  dssfile_run = '_check.dss'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()
  cases[:] = [x for x in cases if x['root'] == 'ecp_daily']

  glmout = './glma/'
  for row in cases:
    row['outpath_csv'] = ''
    row['outpath_dss'] = ''
    row['outpath_glm'] = glmout
    row['export_options'] = ' -l=1.0 -m=1 -a=1 -e=carson'

  cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=True)
  p1 = subprocess.call (shfile_upload, shell=True)

  cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=True)
  p1 = subprocess.call (shfile_export, shell=True)
  shutil.copyfile('../support/commercial_schedules.glm', './glma/commercial_schedules.glm')

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

