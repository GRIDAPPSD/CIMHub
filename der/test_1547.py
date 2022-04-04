# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_1547.py
# for DER modeled with IEC CIM Dynamics

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os

cwd = os.getcwd()

# make some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
#
# 2C2944C1-FF54-4662-B12A-5BE94CA5BB30
# 3F3FFAAC-D309-4B9A-9F99-1AAC003B8216
# 1C8206E3-44F6-4B91-989F-CF3883DFD6FA
# 

cfg_json = 'cimhubconfig.json'
cases = [
  {'dssname':'local_unity_a', 'root':'local_unity_a', 'mRID':'B3600BC3-18B5-4720-9CC6-5997E35E8158',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_optpf_a', 'root':'local_optpf_a', 'mRID':'3D9154FE-8514-40BA-8AE1-7DB8B134617D',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_optpf_b', 'root':'local_optpf_b', 'mRID':'43728B05-D922-4477-99DA-F980D27811ED',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_fixq_a', 'root':'local_fixq_a', 'mRID':'A0BABA6C-3323-412C-A87A-E8F15456031C',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_combo_a', 'root':'local_combo_a', 'mRID':'1D4B98E2-62AB-411A-813E-F125F29ABD48',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_combo_b', 'root':'local_combo_b', 'mRID':'7C1EEB79-9E9C-43E5-BAE9-0F0F99B41384',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_vvar_a', 'root':'local_vvar_a', 'mRID':'D1D5E183-EE39-44E6-9D5C-A1519F0D8709',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_vvar_b', 'root':'local_vvar_b', 'mRID':'3D840B6D-4A97-4BDA-A488-4EEF2F4F5FBD',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_avr_b', 'root':'local_avr_b', 'mRID':'3CC2D836-CE11-4D4F-B93D-B2851B1E79B5',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_vwatt_b', 'root':'local_vwatt_b', 'mRID':'0A81F3A8-0985-423B-A5F5-2A7A0319A9B6',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'remote_vvar_a', 'root':'remote_vvar_a', 'mRID':'DA89ACD5-8AB1-46E4-959E-5BDE188DC12F',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'remote_vvar_b', 'root':'remote_vvar_b', 'mRID':'5824790B-58F9-4428-BB11-6D56CE013C73',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'remote_avr_b', 'root':'remote_avr_b', 'mRID':'408201DC-BBAB-4CDE-85DF-7F8D1E2CF258',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'remote_vwatt_b', 'root':'remote_vwatt_b', 'mRID':'4C7345DE-E5D1-4A00-ACC4-0F85B9016F03',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'remote_combo_b', 'root':'remote_combo_b', 'mRID':'58EAA940-6023-4F38-B09B-3D445BAB4429',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_chcurve_b', 'root':'local_chcurve_b', 'mRID':'6A7D5722-8D9D-4C54-861D-56E1CDA52231',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'local_wvar_b', 'root':'local_wvar_b', 'mRID':'746C6392-9F8B-4537-98C4-E978AB9547D4',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},

  {'dssname':'remote_1phase_b', 'root':'remote_1phase_b', 'mRID':'520E4BC8-D3C2-4745-B784-AE23361E94BB',
   'glmvsrc': 8002.0747,'bases':[208.0, 400.0, 13200.0], 'skip_gld': False,
   'check_branches':[{'dss_link': 'REACTOR.THEV', 'dss_bus': 'HIGH', 'gld_link': 'REAC_THEV', 'gld_bus': 'HIGH'}]},

  {'dssname':'default_avr_b', 'root':'default_avr_b', 'mRID':'57AA3D7E-E023-4C09-A9A7-81C44C2EE87E',
   'glmvsrc': 8002.0747,'bases':[400.0, 13200.0], 'skip_gld': True,
   'check_branches':[{'dss_link': 'TRANSFORMER.DER', 'dss_bus': 'HIGH', 'gld_link': 'XF_DER', 'gld_bus': 'HIGH'}]},
]

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

os.chdir('./base')
fp = open ('convert_1547.dss', 'w')
for row in cases:
  root = row['root']
  mRID = row['mRID']
  print ('redirect {:s}.dss'.format (root), file=fp)
  print ('uuids {:s}_uuids.dat'.format (root.lower()), file=fp)
  print ('export cim100 fid={:s} substation=sub1 subgeo=subgeo1 geo=geo1 file={:s}.xml'.format (mRID, root), file=fp)
  print ('export uuids {:s}_uuids.dat'.format (root), file=fp)
  print ('export summary  {:s}_s.csv'.format (root), file=fp)
  print ('export voltages {:s}_v.csv'.format (root), file=fp)
  print ('export currents {:s}_i.csv'.format (root), file=fp)
  print ('export taps     {:s}_t.csv'.format (root), file=fp)
  print ('export nodeorder {:s}_n.csv'.format (root), file=fp)
fp.close ()
p1 = subprocess.Popen ('opendsscmd convert_1547.dss', shell=True)
p1.wait()

os.chdir(cwd)
shfile = './upload_1547.sh'
cimhub.make_blazegraph_script (cases, 'base/', 'dss/', 'glm/', shfile)
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile, shell=True)

cimhub.make_dssrun_script (casefiles=cases, bControls=True, scriptname='./dss/check.dss')
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
shfile = './checkglm.sh'
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname=shfile)
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile)

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./base/', dsspath='./dss/', glmpath='./glm/')

