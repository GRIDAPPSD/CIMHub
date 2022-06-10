'''
Module to extract EnergyConsumers from the CIM database and replace loads with
houses, HVAC systems, and plug loads. We may also want water heaters.

Created on Jun 1, 2018

@author: thay838
'''
#******************************************************************************
# IMPORTS + PATH
#******************************************************************************
# Standard library:
import logging
import math
from uuid import uuid4
import json
import os
import sys

# Installed packages:
import numpy as np
import pandas as pd
from cimhub.CreateHouses import CreateHouses
from SPARQLWrapper import SPARQLWrapper2
import cimhub.CIMHubConfig as CIMHubConfig

# insert groups of triples to minimize the number of queries
batch_size = 100
qtriples = []

sparql = None
def ConfigureCIMHub (fname): # this is now required before initiating SPARQL engine
  global sparql
  CIMHubConfig.ConfigFromJsonFile (fname)
  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'

def PostHouses ():
  print ('inserting', len(qtriples), 'houses')
  qtriples.append ('}')
  qstr = CIMHubConfig.prefix + 'INSERT DATA { ' + ''.join(qtriples)
#  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  return

#******************************************************************************
# CONSTANTS
#******************************************************************************

# We have to convert nominal voltages from three-phase phase-to-phase to phase
# to ground. At the time of writing, even 240V loads use sqrt(3)...
NOMVFACTOR = 3**0.5
# Triplex loads come back as 208V... This is wrong, but that's what's in the
# CIM database.
TRIPLEX_V = 208
# We'll let the user know how many 480 volt loads are in there, even though we 
# won't be adding houses to them.
COMMERCIAL_V = 480

# We need to define which housing properties are enumerations, as this uses 
# a different syntax for sparql updates.
ENUM = {'coolingSystem': 'HouseCooling', 'heatingSystem': 'HouseHeating',
    'thermalIntegrity': 'HouseThermalIntegrity'}

# Do initial log setup
LOG = logging.getLogger(__name__)

#******************************************************************************
# METHODS
#******************************************************************************
def main(fdrid, region, loglevel='INFO', logfile=None, seed=None, uuidfile=None, scale=1.0):
  """
  """
  global qtriples

  print ('Seeding is', seed, 'mRID file is', uuidfile)
  uuidDict = {}
  if uuidfile is not None:
    if os.path.exists (uuidfile):
      fp_uuid = open (uuidfile).read()
      uuidDict = json.loads(fp_uuid)


  # Setup log:
  setupLog(logger=LOG, loglevel=loglevel, logfile=logfile)
  # 
    
  # Get the EnergyConsumers, commercial loads, and total magnitude of 
  # residential energy consumer loads.
  ec, no_houses, magS = getEnergyConsumers(fdrid=fdrid)

  LOG.info('Total EnergyConsumers: {}'.format(ec.shape[0]))
  LOG.info('Total 120/240V split phase residential load apparent power '
       'magnitude: {:.2f} kVA, scale by {:.2f}'.format(0.001 * magS, scale))
  
  # Alert user about loads which will not be converted.
#  if len(no_houses) > 0:
#    LOG.info('The following details loads, keyed by voltage level, which '
#         'will\n\tNOT have houses/buildings added to them '
#         'because they are not at the correct voltage\n\tlevel '
#         'and/or are not split phase:\n{}'.format(
#          json.dumps(no_houses, indent=2)))

  # If 'ec' is empty, exit the program.
  if ec.shape[0] < 1:
    LOG.error('There are no 120/240V split-phase loads present in '
          'the given model,\n\t'
          'so no houses will be added.\n\t'
          'Exiting...')
    sys.exit(1)

  # Initialize a "CreateHouses" object
  obj = CreateHouses(region=region, log=LOG, seed=seed)
  
  # Generate houses. NOTE: it may technically be more efficient if the house
  # objects were inserted into the triplstore CIM database 'on the fly' as
  # they're generated, but since this functionality doesn't particularly rely
  # on speed, we'll make things more modular and readable by "double-looping"
  housingDict = obj.genHousesForFeeder(loadDf=ec, magS=magS, scale=scale)
  
  LOG.info('All houses generated. Inserting into database.')
    
  # Loop over residential energy consumers, push associated houses into 
  # the CIM triplestore.
  for load, tup in housingDict.items():
    # Grab first element of the tuple: the dataframe representing houses.
    houseDf = tup[0]
    
    # Grab the MRID for this load
    mrid = ec.loc[load, 'mrid']
    
    # Loop over the houses and insert into CIM triplestore
    for row, houseData in houseDf.iterrows():
      # Insert into database.
      insertHouse(ecName=load, ecID=mrid, houseNum=row, houseData=houseData, uuids=uuidDict)
      if len(qtriples) >= batch_size:
        PostHouses()
        qtriples = []

  if len(qtriples) > 0:
    PostHouses()
      
  LOG.info('All houses inserted into database.')
  if uuidfile is not None:
    json_fp = open (uuidfile, 'w')
    json.dump (uuidDict, json_fp, indent=2)
    json_fp.close()

  
def setupLog(logger, loglevel, logfile):
  """Helper function to setup the module's log.
  """
  # level
  level = getattr(logging, loglevel.upper())
  logger.setLevel(level)
  
  # file/stream handler
  if logfile is None:
    h = logging.StreamHandler(sys.stdout)
  else:
    h = logging.FileHandler(filename=logfile)
    
  h.setLevel(level)
  
  # formatting
  fmt = '[%(asctime)s] [%(levelname)s]: %(message)s'
  formatter = logging.Formatter(fmt, datefmt='%H:%M:%S')
  h.setFormatter(formatter)
  
  # add handler
  logger.addHandler(h)


def getEnergyConsumers(fdrid):
  """Method to get nominal voltages from each 'EnergyConsumer.'
  
  Query source is Powergrid-Models/blazegraph/queries.txt, and it was 
  modified from there.
  
  For now, we'll just get the 'bus' (which is really the object name in
  the GridLAB-D model) and nominal voltage. Nominal voltage is given
  as 3-phase phase-to-phase, even if we're talking about a split-phase.
  I suppose that's what you get when you apply a transmission standard
  to the secondary side of a distribution system...
  
  TODO: Later, we may want to act according to the load connection/phases
  """
  
  query = \
    (CIMHubConfig.prefix +
    r'SELECT ?name ?mrid ?bus ?basev ?p ?q ?conn (group_concat(distinct ?phs;separator=",") as ?phases) '
    "WHERE {{ "
      "?s r:type c:EnergyConsumer. "
      'VALUES ?fdrid {{"{fdrid}"}} '
      "?s c:Equipment.EquipmentContainer ?fdr. "
      "?fdr c:IdentifiedObject.mRID ?fdrid. " 
      "?s c:IdentifiedObject.name ?name. "
      "?s c:IdentifiedObject.mRID ?mrid. "
      "?s c:ConductingEquipment.BaseVoltage ?bv. "
      "?bv c:BaseVoltage.nominalVoltage ?basev. "
      "?s c:EnergyConsumer.p ?p."
      "?s c:EnergyConsumer.q ?q."
      "?s c:EnergyConsumer.phaseConnection ?connraw. "
      'bind(strafter(str(?connraw),"PhaseShuntConnectionKind.") as ?conn) '
      "OPTIONAL {{ "
        "?ecp c:EnergyConsumerPhase.EnergyConsumer ?s. "
        "?ecp c:EnergyConsumerPhase.phase ?phsraw. "
        'bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) '
      "}} "
      "?t c:Terminal.ConductingEquipment ?s. "
      "?t c:Terminal.ConnectivityNode ?cn. " 
      "?cn c:IdentifiedObject.name ?bus "
    "}} "
    "GROUP BY ?name ?mrid ?bus ?basev ?p ?q ?conn "
    "ORDER by ?name "
    ).format(fdrid=fdrid)
  
  # Set and execute the query.
  sparql.setQuery(query)
  ret = sparql.query()
  
  # Initialize output
  ec = pd.DataFrame(columns=['p', 'q', 'magS', 'mrid'])
  no_houses = {}
  totalRes = 0+0*1j

  # Loop over the return
  for el in ret.bindings:
    # grab variables
    v = float(el['basev'].value)
    phs = el['phases'].value
    name = el['name'].value
    mrid = el['mrid'].value
    p = float(el['p'].value)
    q = float(el['q'].value)

    # At this time, we're only adding houses to split-phase
    # loads. In the future we will likely want to support
    # three-phase loads.
    if v == TRIPLEX_V and (('s1' in phs) or ('s2' in phs)):
      # Triplex (split-phase) load.
      ec.loc[name, ['p', 'q', 'magS', 'mrid']] = \
        [p, q, math.sqrt((p**2 + q**2)), mrid]

      # Increment counter of total residential power
      totalRes += p + 1j*q
      
    else:
      # Track other voltages/phasing
      try:
        # Attempt to increment the count for this voltage level.
        no_houses[v]['num'] += 1
      except KeyError:
        # Initialize a dictionary for this voltage level.
        no_houses[v] = {'power': p + q*1j, 'num': 1}
      else:
        # Increment the total power for this voltage.
        no_houses[v]['power'] += p + q*1j

  # Update all the 'power' fields in no_houses to be strings.
  # This is a cheap hack to ensure it's json serializable.
  for sub_dict in no_houses.values():
    sub_dict['power'] = '{:.2f} VA'.format(abs(sub_dict['power']))
    
  return ec, no_houses, abs(totalRes)

def insertHouse (ecName, ecID, houseNum, houseData, uuids):
  """Insert a single house into the CIM triplestore.
  """
  global qtriples
  
  # Get MRIDs as strings
  ecIDStr = str(ecID)
  key = ecName + '_house_' + str(houseNum) # relies on unique names within EnergyConsumers
  if key in uuids: # re-use
    hIDStr = uuids[key]
  else: # make a new one, save it for re-use
    hIDStr = str(uuid4())
    uuids[key] = hIDStr

  # Define strings for the house and energy consumer.
#  house = '<' + CIMHubConfig.blazegraph_url + '#' + hIDStr + '>'
#  ec = '<' + CIMHubConfig.blazegraph_url + '#' + ecIDStr + '>'
  house = '<urn:uuid:' + hIDStr + '>'
  ec = '<urn:uuid:' + ecIDStr + '>'
  
  # Define string for attaching house to energy consumer
  qdata = (house + ' a c:House. ' +
      house + ' c:IdentifiedObject.mRID \"' + hIDStr + '\". ' +
      (house + ' c:IdentifiedObject.name \"' + key + '\". ') +
      house + ' c:House.EnergyConsumer ' + ec + '. ')
  
  # Loop over attributes 
  atts = ''
  for name, value in houseData.iteritems():
    # If the value is nan, skip it. e.g. if we don't have a cooling system
    # the cooling setpoint will be nan.
    if pd.isnull(value):
      continue
     
    # Enumerations are handled differently
    try:
      valStr = CIMHubConfig.cim_ns + ENUM[name] + '.' + str(value) + '>. ' 
    except KeyError:
      valStr = '\"' + str(value) + '\". '

    atts += (house + ' c:House.' + name + ' ' + valStr)    
  qtriples.append (qdata + atts)

def insert_houses (cfgfile, mRID, region, seed, uuidfile, scale):
  ConfigureCIMHub (cfgfile)
  main (fdrid=mRID, region=region, seed=seed, uuidfile=uuidfile, scale=scale)

# run from command line for GridAPPS-D platform circuits
if __name__ == "__main__":
  # Get command line arguments
  import argparse
  
  # Initialize parser
  parser = argparse.ArgumentParser(description="Add houses to a CIM model.")

  # must lead off with CIMHub configuration file
  parser.add_argument("config", help=("JSON file to define CIM namespace (cim_ns) and Blazegraph URL (blazegraph_url)."))
  
  # We'll need a fdrid
  parser.add_argument("fdrid", help=("Full UUID of the feeder "
                     "to add houses to."))
  
  # Also grab the region qualifier.
  parser.add_argument("region", help=("Climate region the feeder "
                    "exists in. Valid options "
                    "are 1, 2, 3, 4, or 5."))
  
  parser.add_argument("seed", help=("Specify a value for repeatable randomizations."), nargs='?', default=None)

  parser.add_argument("uuid", help=("Specify a file to read (if available) and rewrite a file of mRID values. "
                    "This only makes sense if a seed value is also specified."), nargs='?', default=None)

  parser.add_argument("scale", help=("Downscale the load before deciding number of houses to add. "
                    "Use to avoid transformer overloads and excess voltage drop."), nargs='?', default=None)

  # Get args
  seed = None
  scale = 1.0

  args = parser.parse_args()
  if args.config is not None:
    ConfigureCIMHub (args.config)
  else:
    print ('cimhubconfig.json must be provided as the first argument, or named config argument')
    quit()
  if args.seed is not None:
    seed = int(args.seed)
  if args.scale is not None:
    scale = float(args.scale)
  
  # Call main function.
  main(fdrid=args.fdrid, region=args.region, seed=seed, uuidfile=args.uuid, scale=scale)
  
  
