from SPARQLWrapper import SPARQLWrapper2
import sys
import re
import uuid
import os.path
import CIMHubConfig

qbus_template = """# list the bus name, cn id, terminal id, sequence number, eq id and loc id
SELECT ?bus ?cnid ?tid ?seq ?eqid ?locid WHERE {{
VALUES ?fdrid {{"{:s}"}}
 ?fdr c:IdentifiedObject.mRID ?fdrid.
 ?cn c:ConnectivityNode.ConnectivityNodeContainer ?fdr.
 ?trm c:Terminal.ConnectivityNode ?cn.
 ?trm c:ACDCTerminal.sequenceNumber ?seq.
 ?trm c:Terminal.ConductingEquipment ?eq.
 ?eq c:PowerSystemResource.Location ?loc.
 ?trm c:IdentifiedObject.mRID ?tid.
 ?cn c:IdentifiedObject.mRID ?cnid.
 ?cn c:IdentifiedObject.name ?bus.
 ?eq c:IdentifiedObject.mRID ?eqid.
 ?loc c:IdentifiedObject.mRID ?locid.
}}
ORDER BY ?bus ?tid
"""

qloc_template = """# list the location id, with xy coordinates of each sequence number
SELECT DISTINCT ?locid ?seq ?x ?y ?ptid WHERE {{
VALUES ?fdrid {{"{:s}"}}
 ?fdr c:IdentifiedObject.mRID ?fdrid.
 ?cn c:ConnectivityNode.ConnectivityNodeContainer ?fdr.
 ?trm c:Terminal.ConnectivityNode ?cn.
 ?trm c:Terminal.ConductingEquipment ?eq.
 ?eq c:PowerSystemResource.Location ?loc.
 ?pt c:PositionPoint.Location ?loc.
 ?pt c:PositionPoint.xPosition ?x.
 ?pt c:PositionPoint.yPosition ?y.
 ?pt c:PositionPoint.sequenceNumber ?seq.
   bind(strafter(str(?pt),"#") as ?ptid).
 ?loc c:IdentifiedObject.mRID ?locid.
}}
ORDER BY ?locid ?seq
"""

crs_query = """SELECT DISTINCT ?name ?mrid WHERE {{
 VALUES ?id {{"{:s}"}}
  ?fdr c:IdentifiedObject.mRID ?id .
  ?fdr c:PowerSystemResource.Location ?loc .
  ?loc c:Location.CoordinateSystem ?crs .
  ?crs c:IdentifiedObject.mRID ?mrid.
  ?crs c:IdentifiedObject.name ?name.
# ?crs r:type c:CoordinateSystem.
# ?crs c:IdentifiedObject.mRID ?id.
# ?crs c:IdentifiedObject.name ?name.
}}
ORDER by ?name
"""

ins_pt_template = """
 <{url}#{res}> a c:PositionPoint.
 <{url}#{res}> c:PositionPoint.Location <{url}#{resLoc}>.
 <{url}#{res}> c:PositionPoint.sequenceNumber \"{seq}\".
 <{url}#{res}> c:PositionPoint.xPosition \"{x}\".
 <{url}#{res}> c:PositionPoint.yPosition \"{y}\".
"""

ins_loc_template = """
 <{url}#{res}> a c:Location.
 <{url}#{res}> c:IdentifiedObject.mRID \"{res}\".
 <{url}#{res}> c:IdentifiedObject.name \"{nm}\".
 <{url}#{res}> c:Location.CoordinateSystem <{url}#{resCrs}>.
"""

ins_trm_template = """
 <{url}#{res}> a c:Terminal.
 <{url}#{res}> c:IdentifiedObject.mRID \"{res}\".
 <{url}#{res}> c:IdentifiedObject.name \"{nm}\".
 <{url}#{res}> c:Terminal.ConductingEquipment <{url}#{resEQ}>.
 <{url}#{res}> c:ACDCTerminal.sequenceNumber \"1\".
 <{url}#{res}> c:Terminal.ConnectivityNode <{url}#{resCN}>.
"""

ins_pec_template = """
 <{url}#{res}> a c:PowerElectronicsConnection.
 <{url}#{res}> c:IdentifiedObject.mRID \"{res}\".
 <{url}#{res}> c:IdentifiedObject.name \"{nm}\".
 <{url}#{res}> c:Equipment.EquipmentContainer  <{url}#{resFdr}>.
 <{url}#{res}> c:PowerElectronicsConnection.PowerElectronicsUnit <{url}#{resUnit}>.
 <{url}#{res}> c:PowerSystemResource.Location <{url}#{resLoc}>.
 <{url}#{res}> c:PowerElectronicsConnection.maxIFault \"1.111\".
 <{url}#{res}> c:PowerElectronicsConnection.p \"{p}\".
 <{url}#{res}> c:PowerElectronicsConnection.q \"{q}\".
 <{url}#{res}> c:PowerElectronicsConnection.ratedS \"{ratedS}\".
 <{url}#{res}> c:PowerElectronicsConnection.ratedU \"{ratedU}\".
"""

ins_syn_template = """
 <{url}#{res}> a c:SynchronousMachine.
 <{url}#{res}> c:IdentifiedObject.mRID \"{res}\".
 <{url}#{res}> c:IdentifiedObject.name \"{nm}\".
 <{url}#{res}> c:Equipment.EquipmentContainer  <{url}#{resFdr}>.
 <{url}#{res}> c:PowerSystemResource.Location <{url}#{resLoc}>.
 <{url}#{res}> c:SynchronousMachine.p \"{p}\".
 <{url}#{res}> c:SynchronousMachine.q \"{q}\".
 <{url}#{res}> c:SynchronousMachine.ratedS \"{ratedS}\".
 <{url}#{res}> c:SynchronousMachine.ratedU \"{ratedU}\".
"""

ins_pep_template = """
 <{url}#{res}> a c:PowerElectronicsConnectionPhase.
 <{url}#{res}> c:IdentifiedObject.mRID \"{res}\".
 <{url}#{res}> c:IdentifiedObject.name \"{nm}\".
 <{url}#{res}> c:PowerElectronicsConnectionPhase.phase {ns}SinglePhaseKind.{phs}>.
 <{url}#{res}> c:PowerElectronicsConnectionPhase.PowerElectronicsConnection <{url}#{resPEC}>.
 <{url}#{res}> c:PowerElectronicsConnectionPhase.p \"{p}\".
 <{url}#{res}> c:PowerElectronicsConnectionPhase.q \"{q}\".
 <{url}#{res}> c:PowerSystemResource.Location <{url}#{resLoc}>.
"""

ins_pv_template = """
 <{url}#{res}> a c:PhotovoltaicUnit.
 <{url}#{res}> c:IdentifiedObject.mRID \"{res}\".
 <{url}#{res}> c:IdentifiedObject.name \"{nm}\".
 <{url}#{res}> c:PowerSystemResource.Location <{url}#{resLoc}>.
"""

ins_bat_template = """
 <{url}#{res}> a c:BatteryUnit.
 <{url}#{res}> c:IdentifiedObject.mRID \"{res}\".
 <{url}#{res}> c:IdentifiedObject.name \"{nm}\".
 <{url}#{res}> c:BatteryUnit.ratedE \"{ratedE}\".
 <{url}#{res}> c:BatteryUnit.storedE \"{storedE}\".
 <{url}#{res}> c:BatteryUnit.batteryState {ns}BatteryState.{state}>.
 <{url}#{res}> c:PowerSystemResource.Location <{url}#{resLoc}>.
"""

def GetCIMID (cls, nm, uuids):
  if nm is not None:
    key = cls + ':' + nm
    if key not in uuids:
      uuids[key] = '_' + str(uuid.uuid4()).upper()
    return uuids[key]
  return '_' + str(uuid.uuid4()).upper() # for unidentified CIM instances

def ParsePhases (sphs):
  lst = []
  for code in ['A', 'B', 'C', 's1', 's2']:
    if code in sphs:
      lst.append(code)
  return lst

if len(sys.argv) < 3:
  print ('usage: python3 InsertDER.py cimhubconfig.json fname')
  print (' Blazegraph server must already be started')
  print (' cimhubconfig.json must define blazegraph_url and cim_ns')
  print (' fname must define feederID before creating any DG')
  exit()

CIMHubConfig.ConfigFromJsonFile (sys.argv[1])
sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'

fdr_id = ''
crs_id = ''
qbus = None
qloc = None
buses = {}
locs = {}
fuidname = None
uuids = {}
batch_size = 100
qtriples = []

def PostDER ():
  print ('==> inserting', len(qtriples), 'instances for DER')
  qtriples.append ('}')
  qstr = CIMHubConfig.prefix + ' INSERT DATA { ' + ''.join(qtriples)
#  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
#  print (ret)
  return

fp = open (sys.argv[2], 'r')
lines = fp.readlines()
for ln in lines:
  toks = re.split('[,\s]+', ln)
  if toks[0] == 'feederID':
    fdr_id = toks[1]
  elif toks[0] == 'uuid_file':
    fuidname = toks[1]
    if os.path.exists(fuidname):
      print ('reading identifiable instance mRIDs from', fuidname)
      fuid = open (fuidname, 'r')
      for uuid_ln in fuid.readlines():
        uuid_toks = re.split('[,\s]+', uuid_ln)
        if len(uuid_toks) > 2 and not uuid_toks[0].startswith('//'):
          cls = uuid_toks[0]
          nm = uuid_toks[1]
          key = cls + ':' + nm
          val = uuid_toks[2]
          uuids[key] = val
      fuid.close()

  if qbus is not None:  # have retrieved essential circuit information
    if not toks[0].startswith('//') and len(toks[0]) > 0:
      name = toks[0]
      nmCN = toks[1]
      phases = toks[2]
      unit = toks[3]
      kVA = float(toks[4])
      kV = float(toks[5])
      kW = float(toks[6])
      kVAR = float(toks[7])
      if unit == 'Battery':
        ratedkwh = float(toks[8])
        storedkwh = float(toks[9])
      else:
        ratedkwh = 0.0
        storedkwh = 0.0
      nmUnit = name + '_' + unit
      nmTrm = name + '_T1'
      nmLoc = name + '_Loc'
      idUnit = GetCIMID(unit + 'Unit', nmUnit, uuids)
      idLoc = GetCIMID('Location', nmLoc, uuids)
      idPt = GetCIMID('PositionPoint', None, uuids)
      idTrm = GetCIMID('Terminal', nmTrm, uuids)
      row = buses[nmCN]
      idCN = row['cn']
      keyXY = row['loc'] + ':' + str(row['seq'])
      pp = locs[keyXY]
      x = float(pp['x'])
      y = float(pp['y'])
      print ('create {:s} at {:s} CN {:s} location {:.4f},{:.4f}'.format (name, nmCN, idCN, x, y))

      if unit == "SynchronousMachine":
        idSYN = GetCIMID('SynchronousMachine', name, uuids)
        inssyn = ins_syn_template.format(url=CIMHubConfig.blazegraph_url, res=idSYN, nm=name, resLoc=idLoc, resFdr=fdr_id, resUnit=idUnit,
                                                  p=kW*1000.0, q=kVAR*1000.0, ratedS=kVA*1000.0, ratedU=kV*1000.0)
        qtriples.append(inssyn)
      else:
        idPEC = GetCIMID('PowerElectronicsConnection', name, uuids)
        inspec = ins_pec_template.format(url=CIMHubConfig.blazegraph_url, res=idPEC, nm=name, resLoc=idLoc, resFdr=fdr_id, resUnit=idUnit,
                                                  p=kW*1000.0, q=kVAR*1000.0, ratedS=kVA*1000.0, ratedU=kV*1000.0)
        qtriples.append(inspec)

        if len(phases) > 0 and phases != 'ABC':
          phase_list = ParsePhases (phases)
          nphs = len(phase_list)
          p=kW*1000.0/nphs
          q=kVAR*1000.0/nphs
          for phs in phase_list:
            nmPhs = '{:s}_{:s}'.format (name, phs)
            idPhs = GetCIMID('PowerElectronicsConnectionPhase', nmPhs, uuids)
            inspep = ins_pep_template.format (url=CIMHubConfig.blazegraph_url, res=idPhs, nm=nmPhs, resPEC=idPEC, resLoc=idLoc, ns=CIMHubConfig.cim_ns, phs=phs, p=p, q=q)
            qtriples.append(inspep)

        if unit == 'Battery':
          state = 'Waiting'
          if kW > 0.0:
            state = 'Discharging'
          elif kW < 0.0:
            state = 'Charging'
          insunit = ins_bat_template.format(url=CIMHubConfig.blazegraph_url, res=idUnit, nm=nmUnit, resLoc=idLoc, ns=CIMHubConfig.cim_ns,
                                                     ratedE=ratedkwh*1000.0, storedE=storedkwh*1000.0, state=state)
        elif unit == 'Photovoltaic':
          insunit = ins_pv_template.format(url=CIMHubConfig.blazegraph_url, res=idUnit, nm=nmUnit, resLoc=idLoc)
        else:
          insunit = '** Unsupported Unit ' + unit
        qtriples.append(insunit)

      if unit == "SynchronousMachine":
        instrm = ins_trm_template.format(url=CIMHubConfig.blazegraph_url, res=idTrm, nm=nmTrm, resCN=idCN, resEQ=idSYN)
      else:
        instrm = ins_trm_template.format(url=CIMHubConfig.blazegraph_url, res=idTrm, nm=nmTrm, resCN=idCN, resEQ=idPEC)
      qtriples.append(instrm)

      insloc = ins_loc_template.format(url=CIMHubConfig.blazegraph_url, res=idLoc, nm=nmLoc, resCrs=crs_id)
      qtriples.append(insloc)

      inspt = ins_pt_template.format(url=CIMHubConfig.blazegraph_url, res=idPt, resLoc=idLoc, seq=1, x=x, y=y)
      qtriples.append(inspt)

  elif len(fdr_id) > 0: # need to retrieve buses and locations for this feeder
    qbus = CIMHubConfig.prefix + qbus_template.format(fdr_id)
    qloc = CIMHubConfig.prefix + qloc_template.format(fdr_id)

    sparql.setQuery(qbus)
    ret = sparql.query()
    for b in ret.bindings:
      key = b['bus'].value
      cnid = b['cnid'].value
      tid = b['tid'].value
      eqid = b['eqid'].value
      locid = b['locid'].value
      seq = b['seq'].value
      buses[key] = {'cn':cnid, 'trm':tid, 'eq':eqid, 'seq': seq, 'loc': locid}
    print ('Retrieved', len(buses), 'connectivity from circuit model')

    sparql.setQuery(qloc)
    ret = sparql.query()
    for b in ret.bindings:
      key = b['locid'].value + ':' + b['seq'].value
      x = b['x'].value
      y = b['y'].value
      ppid = b['ptid'].value
      locs[key] = {'x': x, 'y': y, 'ppid':ppid}
    print ('Retrieved', len(locs), 'locations from circuit model')

    sparql.setQuery(CIMHubConfig.prefix + crs_query.format(fdr_id))
    ret = sparql.query()
    for b in ret.bindings:
      crs_id = b['mrid'].value
      print ('Retrieved Coordinate System', b['name'].value, crs_id, 'on Feeder', fdr_id)
      break

  if len(qtriples) >= batch_size:
    PostDER()
    qtriples = []

fp.close()

if len(qtriples) > 0:
  PostDER()

if fuidname is not None:
  print ('saving identifiable instance mRIDs to', fuidname)
  fuid = open (fuidname, 'w')
  for key, val in uuids.items():
    print ('{:s},{:s}'.format (key.replace(':', ',', 1), val), file=fuid)
  fuid.close()

