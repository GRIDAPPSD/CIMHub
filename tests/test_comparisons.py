# Copyright (C) 2021-22 Battelle Memorial Institute
# file: test_comparisons.py

import subprocess
import stat
import shutil
import os
import cimhub.api as cimhub
import sys

if sys.platform == 'win32':
  shfile_export = 'convert_xml.bat'
  shfile_glm = './glm/checkglm.bat'
  shfile_run = 'checkglm.bat'
else:
  shfile_export = './convert_xml.sh'
  shfile_glm = './glm/checkglm.sh'
  shfile_run = './checkglm.sh'

cwd = os.getcwd()

casefiles = [{'dssname':'IEEE13_Assets', 'root':'IEEE13_Assets', 
              'substation':'sub1', 'region':'test_region', 'subregion':'test_subregion', 
              'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 115000.0]},
             {'dssname':'IEEE13_CDPSM', 'root':'IEEE13_CDPSM', 
              'substation':'sub2', 'region':'test_region', 'subregion':'test_subregion', 
              'glmvsrc': 66395.3, 'bases':[480.0, 4160.0, 13200.0, 115000.0]}]

cimhub.make_dss2xml_script (casefiles=casefiles,
                            inpath='../example',
                            outpath='../tests',
                            outfile='cim_test.dss')
p1 = subprocess.Popen ('opendsscmd cim_test.dss', shell=True)
p1.wait()

cimhub.make_blazegraph_script (casefiles=casefiles, xmlpath='./', dsspath='./dss/', glmpath='./glm/', scriptname=shfile_export)
st = os.stat (shfile_export)
os.chmod (shfile_export, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
p1 = subprocess.call (shfile_export, shell=True)

cimhub.make_dssrun_script (casefiles=casefiles, scriptname='./dss/check.dss')
os.chdir('./dss')
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()

os.chdir(cwd)
cimhub.make_glmrun_script (casefiles=casefiles, inpath='./glm/', outpath='./glm/', scriptname=shfile_glm)
st = os.stat (shfile_glm)
os.chmod (shfile_glm, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.chdir('./glm')
p1 = subprocess.call (shfile_run)

os.chdir(cwd)
cimhub.compare_cases (casefiles=casefiles, basepath='./', dsspath='./dss/', glmpath='./glm/')
