# Copyright (C) 2022 Battelle Memorial Institute
# file: adapt_gmdm.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import argparse
from SPARQLWrapper import SPARQLWrapper2

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
sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'

#  list the EquipmentContainer mRIDs
#  make sure EquipmentContainer is the feeder for Breaker, PowerTransformer, EnergySource
#  populate LinearShuntCompensator.sections and bPerSection from phases
#  populate Switch.ratedCurrent and Switch.normalOpen from phases on Breaker, Fuse, LoadBreakSwitch, Recloser
#  put a base voltage on Breaker and EnergySource
#  populate RegulatingControl.enabled as true
#  populate RatioTapChanger.normalStep as 0
#  populate RatioTapChanger.TransformerEnd from TransformerEnd.RatioTapChanger
#  targetValueUnitMultiplier on targetValue and targetDeadband?  It's either 'none' or 'k'
#
#  the inverter in this example has PV, wind, and storage units connected. Neither OpenDSS nor GridLAB-D support that.
#    a) if more than one PEU points at the same PEC, list them and accumulate the results
#    b) accumulate the minP and maxP into a PhotovoltaicUnit, or a BatteryUnit if storedE available
#    c) mark the accumulated PEU for connection to a PEC
#  for PEC with only one PEU, populate PowerElectronicsUnit.PowerElectronicsConnection from PowerElectronicsConnection.PowerElectronicsUnit
#  for the accumulated PEUs, also populate PowerElectronicsUnit.PowerElectronicsConnection from PowerElectronicsConnection.PowerElectronicsUnit
#
#  add a PowerElectronicsConnection.controlMode

# export OpenDSS and GridLAB-D models, do not select on the feeder mRID

# run and summarize power flows


# TODO - a command-line argument for each vendor's input directory
