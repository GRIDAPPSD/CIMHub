from SPARQLWrapper import SPARQLWrapper2#, JSON
import re
import uuid
import os
import sys
import json
import cimhub.CIMHubConfig as CIMHubConfig

# try to re-use the mRID, otherwise make a new one and save it
def getMeasurementID (key, uuidDict):
  if key in uuidDict:
    return uuidDict[key]
  idNew = uuid.uuid4()
  # if not measid starts with _ then prepend it, this is here for consistency. 
  # otherwise the mrids are uploaded without the initial _
  if (not str(idNew).startswith("_")):
    idNew = "_" + str (idNew)
  uuidDict[key] = idNew
  return idNew

sparql = None
uuidDict = {}
batch_size = 150
qtriples = []

def InsertMeasurement (meascls, measid, eqname, eqid, trmid, meastype, phases):
  global qtriples
  #if not measid starts with _ then prepend it, this is here for consistency. otherwise the mrids are uploaded without the initial _
  if (not str(measid).startswith("_")):
    measid = "_"+str(measid)

  resource = '<' + CIMHubConfig.blazegraph_url + '#' + str(measid) + '>'
  equipment = '<' + CIMHubConfig.blazegraph_url + '#' + str(eqid) + '>'
  terminal = '<' + CIMHubConfig.blazegraph_url + '#' + str(trmid) + '>'
  ln1 = resource + ' a c:' + meascls + '. ' 
  ln2 = resource + ' c:IdentifiedObject.mRID \"' + str(measid) + '\". '
  ln3 = resource + ' c:IdentifiedObject.name \"' + str(eqname) + '\". '
  ln4 = resource + ' c:Measurement.PowerSystemResource ' + equipment + '. '
  ln5 = resource + ' c:Measurement.Terminal ' + terminal + '. '
  ln6 = (resource + ' c:Measurement.phases ' + CIMHubConfig.cim_ns
    + 'PhaseCode.' + phases + '>. ')
  ln7 = resource + ' c:Measurement.measurementType \"' + meastype + '\".'
#  qstr = (CIMHubConfig.prefix + 'INSERT DATA { ' + ln1 + ln2 + ln3 + ln4 +
#    ln5 + ln6 + ln7 + '}')
  qtriples.append (ln1 + ln2 + ln3 + ln4 + ln5 + ln6 + ln7)
  return

def PostMeasurements (fname):
  global qtriples
  print ('inserting', len(qtriples), 'measurements from', fname)
  qtriples.append ('}')
  qstr = CIMHubConfig.prefix + 'INSERT DATA { ' + ''.join(qtriples)
#  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
#  print (ret)
  return

def insert_measurements (fname, uuidfile=None, cfg_file=None):
  global sparql, uuidDict, qtriples

  fp = open (fname, 'r')
  if uuidfile is not None:
    if os.path.exists (uuidfile):
      fp_uuid = open (uuidfile).read()
      uuidDict = json.loads(fp_uuid)

  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2 (CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'

  lines = fp.readlines()
  for ln in lines:
    toks = re.split('[,\s]+', ln)
    if toks[0] == 'LinearShuntCompensator':
      bus = toks[2]
      phases = toks[3]
      eqid = toks[4]
      trmid = toks[5]
      name = 'LinearShuntCompensator_' + toks[1]
      key = name + ':' + bus + ':' + phases
      id1 = getMeasurementID (key + ':PNV', uuidDict)
      id2 = getMeasurementID (key + ':VA', uuidDict)
      id3 = getMeasurementID (key + ':Pos', uuidDict)
      InsertMeasurement ('Analog', id1, name, eqid, trmid, 'PNV', phases)
      InsertMeasurement ('Analog', id2, name, eqid, trmid, 'VA', phases)
      InsertMeasurement ('Discrete', id3, name, eqid, trmid, 'Pos', phases)
    if toks[0] == 'PowerTransformer' and toks[1] == 'RatioTapChanger':
      bus = toks[4]
      phases = toks[5]
      eqid = toks[6]
      trmid = toks[7]
      name = 'RatioTapChanger_' + toks[2]
      key = name + ':' + bus + ':' + phases
      id1 = getMeasurementID (key + ':Pos', uuidDict)
      InsertMeasurement ('Discrete', id1, name, eqid, trmid, 'Pos', phases)
    if toks[0] == 'EnergyConsumer':
      bus = toks[2]
      phases = toks[3]
      eqid = toks[4]
      trmid = toks[5]
      name = 'EnergyConsumer_' + toks[1]
      key = name + ':' + bus + ':' + phases
      id1 = getMeasurementID (key + ':PNV', uuidDict)
      id2 = getMeasurementID (key + ':VA', uuidDict)
      InsertMeasurement ('Analog', id1, name, eqid, trmid, 'PNV', phases)
      InsertMeasurement ('Analog', id2, name, eqid, trmid, 'VA', phases)
    if toks[0] == 'SynchronousMachine':
      bus = toks[2]
      phases = toks[3]
      eqid = toks[4]
      trmid = toks[5]
      name = 'SynchronousMachine_' + toks[1]
      key = name + ':' + bus + ':' + phases
      id1 = getMeasurementID (key + ':PNV', uuidDict)
      id2 = getMeasurementID (key + ':VA', uuidDict)
      InsertMeasurement ('Analog', id1, name, eqid, trmid, 'PNV', phases)
      InsertMeasurement ('Analog', id2, name, eqid, trmid, 'VA', phases)
    if toks[0] == 'PowerElectronicsConnection' and toks[1] == 'PhotovoltaicUnit':
      bus = toks[4]
      phases = toks[5]
      eqid = toks[6]
      trmid = toks[7]
      name = 'PowerElectronicsConnection_PhotovoltaicUnit_' + toks[3]
      key = name + ':' + bus + ':' + phases
      id1 = getMeasurementID (key + ':PNV', uuidDict)
      id2 = getMeasurementID (key + ':VA', uuidDict)
      InsertMeasurement ('Analog', id1, name, eqid, trmid, 'PNV', phases)
      InsertMeasurement ('Analog', id2, name, eqid, trmid, 'VA', phases)
    if toks[0] == 'PowerElectronicsConnection' and toks[1] == 'BatteryUnit':
      bus = toks[4]
      phases = toks[5]
      eqid = toks[6]
      trmid = toks[7]
      name = 'PowerElectronicsConnection_BatteryUnit_' + toks[3]
      key = name + ':' + bus + ':' + phases
      if phases == 'SoC':
        id1 = getMeasurementID (key + ':SoC', uuidDict)
        InsertMeasurement ('Analog', id1, name, eqid, trmid, 'SoC', 'none')
      else:
        id1 = getMeasurementID (key + ':PNV', uuidDict)
        id2 = getMeasurementID (key + ':VA', uuidDict)
        InsertMeasurement ('Analog', id1, name, eqid, trmid, 'PNV', phases)
        InsertMeasurement ('Analog', id2, name, eqid, trmid, 'VA', phases)
    if toks[0] == 'PowerTransformer' and toks[1] == 'PowerTransformerEnd':
      what = toks[2]
      bus = toks[5]
      phases = toks[6]
      eqid = toks[7]
      trmid = toks[8]
      name = 'PowerTransformer_' + toks[3]
      key = name + ':' + bus + ':' + phases
      if 'v' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':PNV', uuidDict), name + '_Voltage', eqid, trmid, 'PNV', phases)
      elif 's' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':VA', uuidDict), name + '_Power', eqid, trmid, 'VA', phases)
      elif 'i' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':A', uuidDict), name + '_Current', eqid, trmid, 'A', phases)
    if toks[0] == 'PowerTransformer' and toks[1] == 'TransformerTankEnd':
      what = toks[2]
      bus = toks[5]
      phases = toks[6]
      eqid = toks[7]
      trmid = toks[8]
      name = 'TransformerTank_' + toks[3]
      key = name + ':' + bus + ':' + phases
      if 'v' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':PNV', uuidDict), name + '_Voltage', eqid, trmid, 'PNV', phases)
      elif 's' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':VA', uuidDict), name + '_Power', eqid, trmid, 'VA', phases)
      elif 'i' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':A', uuidDict), name + '_Current', eqid, trmid, 'A', phases)
    if toks[0] == 'ACLineSegment' or toks[0] == 'LoadBreakSwitch' or toks[0] == 'Breaker' or toks[0] == 'Recloser':
      what = toks[1]
      phases = toks[5]
      eqid = toks[6]
      name = toks[0] + '_' + toks[2]
      key = name + ':' + what + ':' + phases
      if '1' in what:
        trmid = toks[7]
        if toks[0] != 'ACLineSegment' and what == 'i1':
          id1 = uuid.uuid4()
          InsertMeasurement ('Discrete', getMeasurementID (key + ':Pos', uuidDict), name + '_State', eqid, trmid, 'Pos', phases)
      else:
        trmid = toks[8]
      id1 = uuid.uuid4()
      if 'v' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':PNV', uuidDict), name + '_Voltage', eqid, trmid, 'PNV', phases)
      elif 's' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':VA', uuidDict), name + '_Power', eqid, trmid, 'VA', phases)
      elif 'i' in what:
        InsertMeasurement ('Analog', getMeasurementID (key + ':A', uuidDict), name + '_Current', eqid, trmid, 'A', phases)
    if len(qtriples) >= batch_size:
      PostMeasurements (fname)
      qtriples = []

  if len(qtriples) > 0:
    PostMeasurements (fname)
    qtriples = []

  fp.close()
  if uuidfile is not None:
    json_fp = open (uuidfile, 'w')
    json.dump (uuidDict, json_fp, indent=2)
    json_fp.close()

# run from command line for GridAPPS-D platform circuits
if __name__ == '__main__':
  cfg_file = sys.argv[1]
  fname = sys.argv[2]
  uuidfile = None
  if len(sys.argv) > 3:
    uuidfile = sys.argv[3]
  insert_measurements (fname, uuidfile, cfg_file)
