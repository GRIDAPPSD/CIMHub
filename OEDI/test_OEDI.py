# Copyright (C) 2021 Battelle Memorial Institute
# file: test_OEDI.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import subprocess
import stat
import shutil 

cfg_json = 'cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)
ckt_mRID = '_E407CBB6-8C8D-9BC9-589C-AB83FBF0826D'
froot = 'IEEE123_PV'
cwd = os.getcwd()

cases = [
  {'root':froot, 'mRID':'E407CBB6-8C8D-9BC9-589C-AB83FBF0826D','glmvsrc': 2400.00,'bases':[4160.0],
   'export_options':' -l=1.0 -z=1.0 -e=carson',
   'check_branches':[{'dss_link': 'LINE.L114', 'dss_bus': '135', 'gld_link': 'LINE_L114', 'gld_bus': '135'}]},
  ]

# create the CIM XML and base case solution from GridAPPS-D's model
p1 = subprocess.Popen ('opendsscmd convert.dss', shell=True)
p1.wait()

# upload the CIM XML file to Blazegraph
cimhub.clear_db (cfg_json)
cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file {:s}.xml -X POST '.format (froot) + CIMHubConfig.blazegraph_url
os.system (cmd)
cimhub.list_feeders ()

# insert measurements
cimhub.list_measurables (cfg_json, froot, ckt_mRID)
for mtxt in ['node_v', 'xfmr_pq', 'lines_pq', 'switch_i', 'loads', 'machines', 'special']:
  mfile = '{:s}_{:s}.txt'.format (froot, mtxt)
  cimhub.insert_measurements (cfg_json, mfile, froot + '_msid.json')
cimhub.summarize_db (cfg_json)

# create the OpenDSS, GridLAB-D and CSV versions
shfile = './go.sh'
cimhub.make_export_script (shfile, cases, dsspath='dss/', glmpath='glm/', csvpath='csv/')
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile, shell=True)

# run some load flow comparisons
cimhub.make_dssrun_script (casefiles=cases, scriptname='./dss/check.dss')
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=cases, inpath='./glm/', outpath='./glm/', scriptname='./glm/checkglm.sh', movefiles=False)
shfile = './glm/checkglm.sh'
st = os.stat (shfile)
os.chmod (shfile, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call ('./checkglm.sh')

os.chdir(cwd)
cimhub.compare_cases (casefiles=cases, basepath='./', dsspath='./dss/', glmpath='./glm/')

