# Copyright (C) 2022 Battelle Memorial Institute
# file: adapt_gmdm.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import sys
import argparse
import subprocess
import stat
import shutil
import glob

cases = [
  {'root':'testing', 'export_options':' -l=1.0 -i=1.0 -e=carson',
   'glmvsrc': 39837.17, 'bases':[240.0, 480.0, 12470.0, 69000.0],
   'check_branches':[#, 'gld_link': 'SWT_FBKR_A', 'gld_bus': 'J'},# 'gld_link': 'XF_XF1', 'gld_bus': 'E'},
     {'dss_link': 'TRANSFORMER.XF3_1', 'dss_bus': 'J1'}, 
     {'dss_link': 'LINE.FBKR_A', 'dss_bus': 'J'},
     {'dss_link': 'STORAGE.INDIV_RES_BATTERY', 'dss_bus': 'E1'}, 
     {'dss_link': 'CAPACITOR.CAP_A1', 'dss_bus': 'I1'},
     {'dss_link': 'LOAD.AGGREGATE_A_PH_LOAD', 'dss_bus': 'G1', 'bLoad':True},
     {'dss_link': 'LOAD.AGGREGATE_B_PH_LOAD', 'dss_bus': 'G2', 'bLoad':True},
     {'dss_link': 'LOAD.AGGREGATE_C_PH_LOAD', 'dss_bus': 'G3', 'bLoad':True},
     {'dss_link': 'LOAD.BOX_STORE_LOAD', 'dss_bus': 'B1', 'bLoad':True},
     {'dss_link': 'LOAD.G_AND_G_COMM_LOAD', 'dss_bus': 'D2', 'bLoad':True},
     {'dss_link': 'LOAD.G_AND_G_RES_LOAD', 'dss_bus': 'D2', 'bLoad':True},
     {'dss_link': 'LOAD.INDIV_RES_120/240_LOAD', 'dss_bus': 'E1', 'bLoad':True},
   ]}] 

cwd = os.getcwd()
vendor_dir = './planning/'
dsspath = 'dss/'
glmpath = 'glm/'
if len(sys.argv) > 1:
  vendor_dir = sys.argv[1]
  dsspath = vendor_dir + 'dss/'
  glmpath = vendor_dir + 'glm/'

#cimhub.write_dss_flows (dsspath=dsspath, rootname=cases[0]['root'], check_branches=cases[0]['check_branches'])
#quit()

# combine a planning assembly into one file
fnames = ['D Plan Basic Golden InstanceSet.xml',
          'D SSH Golden InstanceSet.xml',
          'Planning Golden Assembly.xml',
          'T Plan Basic Golden InstanceSet.xml',
          'T SSH Golden InstanceSet.xml',
          'TD Basic Golden InstanceSet.xml']

for debris in ['adapted.xml', 'planning.xml']:
  fname = vendor_dir + debris
  if os.path.exists(fname):
    os.remove(fname)
fnames = glob.glob(vendor_dir+'*.xml')
print ('Importing')
for fn in fnames:
  print ('  ', fn)
#quit()
cimhub.combine_xml_files (input_root_name='./', # vendor_dir, 
                          output_filename=vendor_dir + 'planning.xml', 
                          extensions=fnames)

# adapt the GMDM profile to CIMHub
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', nargs=1)
parser.add_argument('-o', '--output', nargs=1)
cmdline = '-i {:s}planning.xml -o {:s}adapted.xml'.format (vendor_dir, vendor_dir)
args = parser.parse_args(cmdline.split())
cimhub.epri_to_pnnl (args)

# clear the database
cfg_json = '../queries/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)
print ('=== the database should be empty now ===')
cimhub.summarize_db (cfg_json)

# curl in the new adapted.xml, count the class instances
xml_name = vendor_dir + 'adapted.xml'
cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_name + ' -X POST ' + CIMHubConfig.blazegraph_url
os.system (cmd)
print ('=== the database now contains ===')
cimhub.summarize_db (cfg_json)

# patch up the model with applied logic:
os.system ('python step2.py')

# export OpenDSS and GridLAB-D models, do not select on the feeder mRID
cimhub.make_export_script ('export.bat', cases, dsspath=dsspath, glmpath=glmpath, clean_dirs=True)
os.system ('export.bat')

# run and summarize power flows
cimhub.make_dssrun_script (casefiles=cases, scriptname=dsspath+'check.dss', bControls=False)
os.chdir(dsspath)
p1 = subprocess.Popen ('opendsscmd check.dss', shell=True)
p1.wait()
os.chdir(cwd)
cimhub.write_dss_flows (dsspath=dsspath, rootname=cases[0]['root'], check_branches=cases[0]['check_branches'])

#os.chdir(cwd)
#cimhub.make_glmrun_script (casefiles=cases, inpath=glmpath, outpath=glmpath, scriptname=glmpath+'check_glm.bat')
#os.chdir(glmpath)
#p1 = subprocess.call ('check_glm.bat')

os.chdir(cwd)
#cimhub.write_glm_flows (glmpath=glmpath, rootname=cases[0]['root'], 
#                        voltagebases=cases[0]['bases'], 
#                        check_branches=cases[0]['check_branches'])



