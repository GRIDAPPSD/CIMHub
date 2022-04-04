# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_xfmr.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import subprocess
import stat
import shutil
import os

cwd = os.getcwd()

# make some random UUID values for additional feeders, from "import uuid;idNew=uuid.uuid4();print(str(idNew).upper())"
# 1D4B98E2-62AB-411A-813E-F125F29ABD48
# 

cfg_json = 'cimhubconfig.json'
cases = [
  {'dssname':'YYBal',    'root':'YYBal',    'mRID':'161B1872-2B5C-4CBF-9ED0-7193495CBE79','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'YYUnBal',    'root':'YYUnBal',    'mRID':'CCB9EF29-23DF-429E-B609-B06EFB4945BA','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'YDBal',    'root':'YDBal',    'mRID':'D09B6037-6236-42CA-AA11-811FE941AF5B','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'LINE.LINE2', 'dss_bus': 'N3', 'gld_link': 'LINE_LINE2', 'gld_bus': 'N3'}]},
  {'dssname':'YDUnBal',    'root':'YDUnBal',    'mRID':'13A48073-FBD8-42B6-8957-746E3F4FECC9','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'LINE.LINE2', 'dss_bus': 'N3', 'gld_link': 'LINE_LINE2', 'gld_bus': 'N3'}]},
  {'dssname':'GYDBal',   'root':'GYDBal',   'mRID':'0EC1B5A1-1EF7-4BDE-BA05-7391020BCE47','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'LINE.LINE2', 'dss_bus': 'N3', 'gld_link': 'LINE_LINE2', 'gld_bus': 'N3'}]},
  {'dssname':'GYDUnBal',   'root':'GYDUnBal',   'mRID':'275E77E2-F477-414B-969D-F596DADC1A7A','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'LINE.LINE2', 'dss_bus': 'N3', 'gld_link': 'LINE_LINE2', 'gld_bus': 'N3'}]},
  {'dssname':'DDBal',    'root':'DDBal',    'mRID':'D9A6F0E3-DD90-46AD-9CB1-7EDF15C41F9F','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'DDUnBal',    'root':'DDUnBal',    'mRID':'9DAB9DF4-60B3-42A5-A24F-958A2D2E3B0E','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'DYBal',    'root':'DYBal',    'mRID':'7319BD48-9C66-4038-B0AC-30DBD289A4A6','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'DYUnBal',    'root':'DYUnBal',    'mRID':'764ED62E-142A-4906-BE17-1F9BD5856B93','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'SCTBal', 'root':'SCTBal', 'mRID':'43946E3D-232A-4B5F-B0C4-BEAECD347C8C','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'SCTUnBal', 'root':'SCTUnBal', 'mRID':'AA782F4B-C424-4D54-AE39-9E6B108A7E0A','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'OYODBal',  'root':'OYODBal',  'mRID':'FE17C848-D906-499B-8EAD-F0ECF1F8A2AB','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LINE.LINE2', 'dss_bus': 'N3'}]},
  {'dssname':'OYODUnBal',  'root':'OYODUnBal',  'mRID':'8FDAE9BB-0BE3-4103-A1CD-B12067583D9C','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LINE.LINE2', 'dss_bus': 'N3'}]},
  {'dssname':'OnePh',    'root':'OnePh',    'mRID':'088F22EA-893E-4ED5-BB7B-E74585EB3DA1','glmvsrc': 7200.00,'bases':[4160.0, 12470.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'TRANSFORMER.T1', 'dss_bus': 'N2', 'gld_link': 'XF_T1', 'gld_bus': 'N2'}]},
  {'dssname':'YYD',  'root':'YYD',  'mRID':'8C63A72C-9B64-42E7-B021-3FD00B4EBCEE','glmvsrc': 39837.17,'bases':[4160.0, 13200.0, 69000.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LINE.DLINE3-4', 'dss_bus': 'B4'}]},
  {'dssname':'YYDXn',  'root':'YYDXn',  'mRID':'2921AE75-39A1-40D1-98DE-8E7BE5DC3A66','glmvsrc': 39837.17,'bases':[4160.0, 13200.0, 69000.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LINE.DLINE3-4', 'dss_bus': 'B4'}]},
  {'dssname':'YYD1Tank',  'root':'YYD1Tank',  'mRID':'5F0B3FFA-C2D4-47D6-AB25-54231CEEA4B6','glmvsrc': 39837.17,'bases':[4160.0, 13200.0, 69000.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LINE.DLINE3-4', 'dss_bus': 'B4'}]},
  {'dssname':'IMYD',  'root':'IMYD',  'mRID':'73BB36C0-6DB3-4480-A8B2-822B4AADD390','bases':[240.0, 12470.0],
   'export_options':' -l=1.0 -p=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LOAD.MOTOR', 'dss_bus': 'LOADBUS'}]},
  {'dssname':'IMOYODlag', 'root':'IMOYODlag',  'mRID':'EF222C39-6F6C-44BC-9A11-26EAE5AA4EF0','bases':[240.0, 12470.0],
   'export_options':' -l=1.0 -p=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LOAD.MOTOR', 'dss_bus': 'LOADBUS'}]},
  {'dssname':'IMOYODlead',  'root':'IMOYODlead',  'mRID':'083167E5-2729-4397-BCC5-6037C2E4E8F5','bases':[240.0, 12470.0],
   'export_options':' -l=1.0 -p=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LOAD.MOTOR', 'dss_bus': 'LOADBUS'}]},
  {'dssname':'AutoHLT',  'root':'AutoHLT',  'mRID':'94BEE3C7-5EF1-465A-B872-FF43E62AA81B','bases':[13800.0, 161000.0, 345000.0],
    'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
    'check_branches':[{'dss_link': 'LOAD.TEST', 'dss_bus': 'LOW'}]},
  {'dssname':'Auto1bus',  'root':'Auto1bus',  'mRID':'7AE1360F-8A58-49FE-8716-8CF8794B9F9A','bases':[13800.0, 161000.0, 345000.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LOAD.TEST', 'dss_bus': 'LOW'}]},
  {'dssname':'Auto3bus',  'root':'Auto3bus',  'mRID':'7528323E-ABA2-420F-B8B8-DA51E172BB46','bases':[13800.0, 161000.0, 345000.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LOAD.TEST', 'dss_bus': 'LOW'}]},
  {'dssname':'AutoAuto',  'root':'AutoAuto',  'mRID':'7FCDAD02-036A-48BA-B71D-1FE988F665CF','bases':[13800.0, 161000.0, 345000.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson', 'skip_gld': True,
   'check_branches':[{'dss_link': 'LOAD.TEST', 'dss_bus': 'LOW'}]},
]

# exluding cases with IndMotor: 4wire_lagging.dss, 4wire_leading.dss, 4wire_motor.dss, the three-winding cases and the open wye/delta cases
#cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')
#quit()

CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)

fp = open ('cim_test.dss', 'w')
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
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

shfile = './go.sh'
cimhub.make_blazegraph_script (cases, './', 'dss/', 'glm/', shfile)
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile, shell=True)

cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss')
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname='./glm/checkglm.sh')
shfile = './glm/checkglm.sh'
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call ('./checkglm.sh')

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')

