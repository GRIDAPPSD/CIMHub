# Copyright (C) 2022 Battelle Memorial Institute
# file: adapt_gmdm.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import argparse

# combine a planning assembly into one file
fnames = ['D Plan Basic Golden InstanceSet.xml',
          'D SSH Golden InstanceSet.xml',
          'Planning Golden Assembly.xml',
          'T Plan Basic Golden InstanceSet.xml',
          'T SSH Golden InstanceSet.xml',
          'TD Basic Golden InstanceSet.xml']

cimhub.combine_xml_files (input_root_name='./planning/', 
                          output_filename='planning.xml', 
                          extensions=fnames)

# adapt the GMDM profile to CIMHub
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', nargs=1)
parser.add_argument('-o', '--output', nargs=1)
args = parser.parse_args('-i planning.xml -o adapted.xml'.split())
cimhub.epri_to_pnnl (args)

# clear the database
cfg_json = '../queries/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)
cimhub.clear_db (cfg_json)
print ('=== the database should be empty now ===')
cimhub.summarize_db (cfg_json)

# curl in the new adapted.xml, count the class instances
xml_name = 'adapted.xml'
cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_name + ' -X POST ' + CIMHubConfig.blazegraph_url
os.system (cmd)
print ('=== the database now contains ===')
cimhub.summarize_db (cfg_json)

# patch up the model with applied logic:
os.system ('python step2.py')

# export OpenDSS and GridLAB-D models, do not select on the feeder mRID
cases = [
  {'root':'testing', 'export_options':' -l=1.0 -i=1.0 -e=carson',
   'glmvsrc': 39837.17, 'bases':[240.0, 480.0, 12470.0, 69000.0],
    'check_branches':[{'dss_link': 'TRANSFORMER.XFM1', 'dss_bus': '633', 'gld_link': 'XF_XFM1', 'gld_bus': '633'},
                      {'dss_link': 'LINE.670671', 'dss_bus': '670', 'gld_link': 'LINE_670671', 'gld_bus': '670'}]}] 
cimhub.make_export_script ('export.bat', cases, dsspath='dss/', glmpath='glm/', clean_dirs=True)
os.system ('export.bat')

# run and summarize power flows


# TODO - a command-line argument for each vendor's input directory
