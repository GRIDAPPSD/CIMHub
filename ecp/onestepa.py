# Copyright (C) 2022 Battelle Memorial Institute
# file: onestepa.py
#
# usage: python onestepa.py
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
import subprocess

template_files = {}

template_files['ecp_daily_edits.dss'] = """New Loadshape.Cloud npts=86401 sinterval=1 csvfile=../base/pcloud.dat action=normalize
New Loadshape.Clear npts=86401 sinterval=1 csvfile=../base/pclear.dat action=normalize"""

template_files['ecp_daily_run.dss'] = """redirect ecp_daily_base.dss
new monitor.pv1 pvsystem.pv1 1 mode=1 ppolar=no
new monitor.pv2 pvsystem.pv2 1 mode=1 ppolar=no
new monitor.load1 load.load1 1 mode=1 ppolar=no
new monitor.load2 load.load2 1 mode=1 ppolar=no
new monitor.gen1 generator.gen1 1 mode=1 ppolar=no
new monitor.gen2 generator.gen2 1 mode=1 ppolar=no
solve
solve mode=daily stepsize=1s number=86400
export monitors gen1
export monitors gen2
export monitors pv1
export monitors pv2
export monitors load1
export monitors load2"""

template_files['ecp_duty_edits.dss'] = """// for duty cycle, runs for 2900 seconds or 0.81 hours
new loadshape.PVduty npts=2900 interval=(1.0 3600 /) mult=(File=../base/pvloadshape-1sec-2900pts.dat) Action=Normalize
New Loadshape.cycle npts=10 interval=0 hour=[0.00,0.09,0.10,0.29,0.30,0.49, 0.50, 0.69,0.70,0.82] 
~                                      mult=[0.00,0.00,1.00,1.00,0.00,0.00,-1.00,-1.00,0.00,0.00]
~ action=normalize"""

template_files['ecp_duty_run.dss'] = """redirect ecp_duty_base.dss
new monitor.pv1 pvsystem.pv1 1 mode=1 ppolar=no
new monitor.pv2 pvsystem.pv2 1 mode=1 ppolar=no
new monitor.bess1 storage.bess1 1 mode=1 ppolar=no
new monitor.bess2 storage.bess2 1 mode=1 ppolar=no
solve
solve mode=duty stepsize=1s number=2900
export monitors pv1
export monitors pv2
export monitors bess1
export monitors bess2"""

template_files['ecp_yearly_edits.dss'] = """new loadshape.YearlyPQ npts=8760 interval=1.0 mult=(File=../base/loadshape5_p.dat)  Qmult=(File=../base/loadshape5_q.dat) Action=Normalize"""

template_files['ecp_yearly_run.dss'] = """redirect ecp_yearly_base.dss
new monitor.pq1 load.load1 1 mode=1 ppolar=no
new monitor.pq2 load.load2 1 mode=1 ppolar=no
solve
solve mode=yearly stepsize=1h number=8760
export monitors pq1
export monitors pq2"""

template_files['ecp_growthcvr_edits.dss'] = """new growthshape.fast npts=2 year=[1 20] mult=[1.04 1.04]
new loadshape.cvr npts=25 interval=1
~ pmult=[0.4 0.4 0.4 0.4 0.4 0.4 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.4 0.4 0.4 0.4 0.4 0.4 0.4 0.4 0.4]
~ qmult=[2.0 2.0 2.0 2.0 2.0 2.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 2.0 2.0 2.0 2.0 2.0 2.0 2.0 2.0 2.0]"""

template_files['ecp_growthcvr_run.dss'] = """redirect ecp_growthcvr_base.dss
batchedit load..* vminpu=0.9
edit load.load3 cvrwatts=0.8 cvrvars=3.0
edit load.load4 cvrwatts=0.8 cvrvars=3.0
new monitor.load1 load.load1 1 mode=1 ppolar=no
new monitor.load2 load.load2 1 mode=1 ppolar=no
new monitor.load3 load.load3 1 mode=1 ppolar=no
new monitor.load4 load.load4 1 mode=1 ppolar=no
new monitor.load5 load.load5 1 mode=1 ppolar=no
solve
set year=10
solve mode=daily stepsize=1h number=24
export monitors load1
export monitors load2
export monitors load3
export monitors load4
export monitors load5"""

template_files['ecp_temperature_edits.dss'] = """New Loadshape.MyIrrad npts=781 minterval=1 csvfile=../base/irrad.dat
New Tshape.MyTemp npts=781 minterval=1 csvfile=../base/temp.dat
New XYCurve.MyPvsT npts=4  xarray=[0  25  75  100]  yarray=[1.2 1.0 0.8  0.6] 
New XYCurve.MyEff npts=4  xarray=[.1  .2  .4  1.0]  yarray=[.94  .96  .96  .96]"""

template_files['ecp_temperature_run.dss'] = """redirect ecp_temperature_base.dss
batchedit pvsystem..* effcurve=MyEff irradiance=0.983 // back out exported effect of MyEff: 0.983*0.96=0.944 in base file
edit pvsystem.pv2 P-TCurve=MyPvsT
new monitor.pv1_pq PVSystem.pv1  1 mode=1 ppolar=no
new monitor.pv1_vi PVSystem.pv1  1 
new monitor.pv2_pq PVSystem.pv2  1 mode=1 ppolar=no
new monitor.pv2_vi PVSystem.pv2  1 
solve
solve mode=daily stepsize=1m number=781
export monitors pv1_pq
export monitors pv2_pq
export monitors pv1_vi
export monitors pv2_vi"""

template_files['ecp_harmonic_edits.dss'] = """// using built-in spectra"""

template_files['ecp_harmonic_run.dss'] = """redirect ecp_harmonic_base.dss
new monitor.pv1 pvsystem.pv1 1 mode=96 ppolar=yes
new monitor.pv2 pvsystem.pv2 1 mode=96 ppolar=yes
new monitor.bess1 storage.bess1 1 mode=96 ppolar=yes
new monitor.bess2 storage.bess2 1 mode=96 ppolar=yes
new monitor.load1 load.load1 1 mode=96 ppolar=yes
new monitor.load2 load.load2 1 mode=96 ppolar=yes
new monitor.gen1 generator.gen1 1 mode=96 ppolar=yes
new monitor.gen2 generator.gen2 1 mode=96 ppolar=yes
solve
solve mode=harmonic
export monitors pv1
export monitors pv2
export monitors bess1
export monitors bess2
export monitors load1
export monitors load2
export monitors gen1
export monitors gen2"""

template_files['gld_daily_edits.dss'] = """New Loadshape.Cloud npts=86401 sinterval=1 csvfile=../base/pcloud.dat action=normalize
New Loadshape.Clear npts=86401 sinterval=1 csvfile=../base/pclear.dat action=normalize
New Loadshape.cycle npts=10 interval=0 hour=[0.0,4.0,4.1,8.0,8.1,16.0,16.1,20.0,20.1,24.0] 
~                                      mult=[0.0,0.0,1.0,1.0,0.0, 0.0,-1.0,-1.0, 0.0, 0.0]
New Loadshape.bump npts=6 interval=0 hour=[0.0,6.0,7.0,19.0,20.0,24.0] 
~                                    mult=[0.0,0.0,1.0, 1.0, 0.0, 0.0]
New Loadshape.peaking npts=6 interval=0 hour=[0.0,12.0,12.1,17.0,17.1,24.0] 
~                                       mult=[0.0, 0.0, 1.0, 1.0, 0.0, 0.0]"""

template_files['gld_daily_run.dss'] = """redirect gld_daily_base.dss
batchedit storage..* %reserve=5
new monitor.bess1 storage.bess1 1 mode=1 ppolar=no
new monitor.bess2 storage.bess2 1 mode=1 ppolar=no
new monitor.pv1 pvsystem.pv1 1 mode=1 ppolar=no
new monitor.pv2 pvsystem.pv2 1 mode=1 ppolar=no
new monitor.load1 load.load1 1 mode=1 ppolar=no
new monitor.load2 load.load2 1 mode=1 ppolar=no
new monitor.gen1 generator.gen1 1 mode=1 ppolar=no
new monitor.gen2 generator.gen2 1 mode=1 ppolar=no
solve
solve mode=daily stepsize=1s number=86400
export monitors gen1
export monitors gen2
export monitors pv1
export monitors pv2
export monitors load1
export monitors load2
export monitors bess1
export monitors bess2"""

cfg_json = '../queries/cimhubconfig.json'

if sys.platform == 'win32':
  shfile_upload = '_upload.bat'
  shfile_export = '_export.bat'
  dssfile_run = '_check.dss'
else:
  shfile_upload = './_upload.sh'
  shfile_export = './_export.sh'
  dssfile_run = '_check.dss'

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile (cfg_json)

  fp = open('cases.json')
  cases = json.load(fp)
  fp.close()

  dssout = './dssa/'
  for row in cases:
    row['outpath_csv'] = ''
    row['outpath_glm'] = ''
    row['outpath_dss'] = dssout
    row['export_options'] = ' -l=1.0 -m=1 -a=1 -e=carson'

  cimhub.make_upload_script (cases, scriptname=shfile_upload, bClearDB=True)
  p1 = subprocess.call (shfile_upload, shell=True)

  cimhub.make_export_script (cases, scriptname=shfile_export, bClearOutput=True)
  p1 = subprocess.call (shfile_export, shell=True)

  dp = open (dssfile_run, 'w')
  for row in cases:
    print ('cd {:s}'.format (os.path.abspath(row['outpath_dss'])), file=dp)
    print ('redirect {:s}_run.dss'.format (row['root']), file=dp)
    for tok in ['edits', 'run']:
      fname = '{:s}_{:s}.dss'.format(row['root'], tok)
      fpath = os.path.join(row['outpath_dss'], fname)
      fp = open(fpath, 'w')
      print (template_files[fname], file=fp)
      fp.close()
  dp.close()
  p1 = subprocess.Popen ('opendsscmd {:s}'.format(dssfile_run), shell=True)
  p1.wait()

