from SPARQLWrapper import SPARQLWrapper2#, JSON
import cimhub.CIMHubConfig as CIMHubConfig
import sys

# the 'phases' arg may be PhaseCodeKind or OrderedPhaseCodeKind
def FlatPhases (phases):
  if len(phases) < 1:
    return ['A', 'B', 'C']
  if ('A' in phases) and ('B' in phases) and ('C' in phases):
    return ['A', 'B', 'C']
  if ('A' in phases) and ('B' in phases):
    return ['A', 'B']
  if ('B' in phases) and ('C' in phases):
    return ['B', 'C']
  if ('A' in phases) and ('C' in phases):
    return ['A', 'C']
  if 'A' in phases:
    return ['A']
  if 'B' in phases:
    return ['B']
  if 'C' in phases:
    return ['C']
  if 's12' in phases:
    return ['s12']
  if ('s1' in phases) and ('s2' in phases):
    return ['s1', 's2']
  if 's1' in phases:
    return ['s1']
  if 's2' in phases:
    return ['s2']
  return []

def list_measurables (froot, mRID, outpath=None, taxonomy=False, cfg_file=None):
  if outpath is not None:
    froot = './{:s}/{:s}'.format (outpath, froot)
  op = open (froot + '_special.txt', 'w')
  np = open (froot + '_node_v.txt', 'w')
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)

  fidselect = """ VALUES ?fdrid {\"""" + mRID + """\"}
   ?s c:Equipment.EquipmentContainer ?fdr.
   ?fdr c:IdentifiedObject.mRID ?fdrid. """

  #################### start by listing all the buses
  busphases = {}

  qstr = CIMHubConfig.prefix + """SELECT ?bus WHERE { VALUES ?fdrid {\"""" + mRID + """\"}
   ?fdr c:IdentifiedObject.mRID ?fdrid.
   ?s c:ConnectivityNode.ConnectivityNodeContainer ?fdr.
   ?s r:type c:ConnectivityNode.
   ?s c:IdentifiedObject.name ?bus.
  }
  ORDER by ?bus
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  for b in ret.bindings:
    busphases[b['bus'].value] = {'A':False, 'B':False, 'C':False, 's1': False, 's2': False}

  #################### capacitors

  qstr = CIMHubConfig.prefix + """SELECT ?name ?bus ?phases ?eqid ?trmid WHERE {""" + fidselect + """
   ?s r:type c:LinearShuntCompensator.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid. 
   ?t c:Terminal.ConductingEquipment ?s.
   ?t c:IdentifiedObject.mRID ?trmid. 
   ?t c:Terminal.ConnectivityNode ?cn. 
   ?cn c:IdentifiedObject.name ?bus.
   OPTIONAL {?scp c:ShuntCompensatorPhase.ShuntCompensator ?s.
   ?scp c:ShuntCompensatorPhase.phase ?phsraw.
     bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phases) } } ORDER by ?name ?bus ?phases
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  #print ('\nLinearShuntCompensator binding keys are:',ret.variables)
  for b in ret.bindings:
    bus = b['bus'].value
    if 'phases' in b: # was OPTIONAL in the query
      phases = FlatPhases (b['phases'].value)
    else:
      phases = FlatPhases ('ABC')
    for phs in phases:
      busphases[bus][phs] = True
      print ('LinearShuntCompensator',b['name'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=op)

  #################### regulators

  qstr = CIMHubConfig.prefix + """ SELECT ?name ?bus ?tname ?wnum ?orderedPhases ?eqid ?trmid ?fdrid WHERE { """ + fidselect + """
   ?rtc r:type c:RatioTapChanger.
  ?rtc c:IdentifiedObject.name ?rname.
  ?rtc c:IdentifiedObject.mRID ?rtcid.
  ?rtc c:RatioTapChanger.TransformerEnd ?end.
  ?end c:TransformerEnd.endNumber ?wnum.
  ?end c:TransformerEnd.Terminal ?trm.
  ?trm c:Terminal.ConnectivityNode ?cn. 
  ?cn c:IdentifiedObject.name ?bus.
  ?trm c:IdentifiedObject.mRID ?trmid. 
    {?end c:PowerTransformerEnd.PowerTransformer ?s.}
  UNION
    {?end c:TransformerTankEnd.TransformerTank ?tank.
  ?tank c:IdentifiedObject.name ?tname.
  OPTIONAL {?end c:TransformerTankEnd.orderedPhases ?phsraw.
  bind(strafter(str(?phsraw),"OrderedPhaseCodeKind.") as ?orderedPhases)}
  ?tank c:TransformerTank.PowerTransformer ?s.}
  ?s c:IdentifiedObject.name ?name.
  ?s c:IdentifiedObject.mRID ?eqid.
  }
  ORDER BY ?pname ?tname ?rname ?wnum ?orderedPhases
  """
#  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
#  print ('\nRatioTapChanger binding keys are:',ret.variables)
  for b in ret.bindings:
    if 'orderedPhases' in b: # was OPTIONAL in the query
      phases = FlatPhases (b['orderedPhases'].value)
    else:
      phases = FlatPhases ('ABC')
    for phs in phases:
      print ('PowerTransformer','RatioTapChanger',b['name'].value,b['wnum'].value,b['bus'].value,phs,b['eqid'].value,b['trmid'].value,file=op)
#      print ('PowerTransformer','RatioTapChanger',b['name'].value,b['wnum'].value,b['bus'].value,phs,b['eqid'].value,b['trmid'].value)

  ####################### - Storage

  qstr = CIMHubConfig.prefix + """SELECT ?name ?uname ?bus (group_concat(distinct ?phs;separator=\"\") as ?phases) ?eqid ?trmid WHERE {
    SELECT ?name ?uname ?bus ?phs ?eqid ?trmid WHERE {""" + fidselect + """
   ?s r:type c:PowerElectronicsConnection.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid. 
   ?peu r:type c:BatteryUnit.
   ?peu c:IdentifiedObject.name ?uname.
   ?s c:PowerElectronicsConnection.PowerElectronicsUnit ?peu.
   ?t1 c:Terminal.ConductingEquipment ?s.
   ?t1 c:IdentifiedObject.mRID ?trmid. 
   ?t1 c:ACDCTerminal.sequenceNumber "1".
   ?t1 c:Terminal.ConnectivityNode ?cn1. 
   ?cn1 c:IdentifiedObject.name ?bus.
   OPTIONAL {?pep c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?s.
   ?pep c:PowerElectronicsConnectionPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) } } ORDER BY ?name ?phs
   } GROUP BY ?name ?uname ?bus ?eqid ?trmid
   ORDER BY ?name ?bus ?phases
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  #print ('\nPowerElectronicsConnection->BatteryUnit binding keys are:',ret.variables)
  for b in ret.bindings:
    phases = FlatPhases (b['phases'].value)
    bus = b['bus'].value
    print ('PowerElectronicsConnection','BatteryUnit',b['name'].value,b['uname'].value,bus,'SoC',b['eqid'].value,b['trmid'].value,file=op)
    for phs in phases:
      busphases[bus][phs] = True
      print ('PowerElectronicsConnection','BatteryUnit',b['name'].value,b['uname'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=op)

  ####################### - Solar

  qstr = CIMHubConfig.prefix + """SELECT ?name ?uname ?bus (group_concat(distinct ?phs;separator=\"\") as ?phases) ?eqid ?trmid WHERE {
    SELECT ?name ?uname ?bus ?phs ?eqid ?trmid WHERE {""" + fidselect + """
   ?s r:type c:PowerElectronicsConnection.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid. 
   ?peu r:type c:PhotovoltaicUnit.
   ?peu c:IdentifiedObject.name ?uname.
   ?s c:PowerElectronicsConnection.PowerElectronicsUnit ?peu.
   ?t1 c:Terminal.ConductingEquipment ?s.
   ?t1 c:IdentifiedObject.mRID ?trmid. 
   ?t1 c:ACDCTerminal.sequenceNumber "1".
   ?t1 c:Terminal.ConnectivityNode ?cn1. 
   ?cn1 c:IdentifiedObject.name ?bus.
   OPTIONAL {?pep c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?s.
   ?pep c:PowerElectronicsConnectionPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) } } ORDER BY ?name ?phs
   } GROUP BY ?name ?uname ?bus ?eqid ?trmid
   ORDER BY ?name ?bus ?phases
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  #print ('\nPowerElectronicsConnection->PhotovoltaicUnit binding keys are:',ret.variables)
  for b in ret.bindings:
    phases = FlatPhases (b['phases'].value)
    bus = b['bus'].value
    for phs in phases:
      busphases[bus][phs] = True
      print ('PowerElectronicsConnection','PhotovoltaicUnit',b['name'].value,b['uname'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=op)

  #################### LoadBreakSwitches, Breakers and Reclosers
  op.close()
  op = open (froot + '_switch_i.txt', 'w')

  qstr = CIMHubConfig.prefix + """SELECT ?cimtype ?name ?bus1 ?bus2 (group_concat(distinct ?phs1;separator=\"\") as ?phases1) ?eqid ?trm1id ?trm2id WHERE {
    SELECT ?cimtype ?name ?bus1 ?bus2 ?phs1 ?eqid ?trm1id ?trm2id WHERE {""" + fidselect + """
   VALUES ?cimraw {c:LoadBreakSwitch c:Recloser c:Breaker}
   ?s r:type ?cimraw.
    bind(strafter(str(?cimraw),"#") as ?cimtype)
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid. 
   ?t1 c:Terminal.ConductingEquipment ?s.
   ?t1 c:ACDCTerminal.sequenceNumber "1".
   ?t1 c:IdentifiedObject.mRID ?trm1id. 
   ?t1 c:Terminal.ConnectivityNode ?cn1. 
   ?cn1 c:IdentifiedObject.name ?bus1.
   ?t2 c:Terminal.ConductingEquipment ?s.
   ?t2 c:ACDCTerminal.sequenceNumber "2".
   ?t2 c:IdentifiedObject.mRID ?trm2id. 
   ?t2 c:Terminal.ConnectivityNode ?cn2. 
   ?cn2 c:IdentifiedObject.name ?bus2.
   OPTIONAL {?scp c:SwitchPhase.Switch ?s.
   ?scp c:SwitchPhase.phaseSide1 ?phs1raw.
    bind(strafter(str(?phs1raw),\"SinglePhaseKind.\") as ?phs1) } } ORDER BY ?name ?phs1
   } GROUP BY ?cimtype ?name ?bus1 ?bus2 ?eqid ?trm1id ?trm2id
   ORDER BY ?cimtype ?name ?bus1 ?bus2 ?phs1
  """
  sparql.setQuery(qstr)
  ret = sparql.query()
  for b in ret.bindings:
    phases1 = FlatPhases (b['phases1'].value)
    bus1 = b['bus1'].value
    bus2 = b['bus2'].value
    if taxonomy and ('s' in phases1[0]):
      phases1 = []
    for phs1 in phases1:
      print (b['cimtype'].value,'i1',b['name'].value,bus1,bus2,phs1,b['eqid'].value,b['trm1id'].value,b['trm2id'].value,file=op)
      if not busphases[bus1][phs1]:
        print (b['cimtype'].value,'v1',b['name'].value,bus1,bus2,phs1,b['eqid'].value,b['trm1id'].value,b['trm2id'].value,file=np)
        busphases[bus1][phs1] = True
      if not busphases[bus2][phs1]:
        print (b['cimtype'].value,'v2',b['name'].value,bus1,bus2,phs1,b['eqid'].value,b['trm1id'].value,b['trm2id'].value,file=np)
        busphases[bus2][phs1] = True

  ##################### ACLineSegments
  op.close()
  op = open (froot + '_lines_pq.txt', 'w')

  qstr = CIMHubConfig.prefix + """SELECT ?name ?bus1 ?bus2 (group_concat(distinct ?phs;separator=\"\") as ?phases) ?eqid ?trm1id ?trm2id WHERE {
    SELECT ?name ?bus1 ?bus2 ?phs ?eqid ?trm1id ?trm2id WHERE {""" + fidselect + """
   ?s r:type c:ACLineSegment.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid. 
   ?t1 c:Terminal.ConductingEquipment ?s.
   ?t1 c:ACDCTerminal.sequenceNumber "1".
   ?t1 c:IdentifiedObject.mRID ?trm1id. 
   ?t1 c:Terminal.ConnectivityNode ?cn1. 
   ?cn1 c:IdentifiedObject.name ?bus1.
   ?t2 c:Terminal.ConductingEquipment ?s.
   ?t2 c:ACDCTerminal.sequenceNumber "2".
   ?t2 c:IdentifiedObject.mRID ?trm2id. 
   ?t2 c:Terminal.ConnectivityNode ?cn2. 
   ?cn2 c:IdentifiedObject.name ?bus2.
   OPTIONAL {?acp c:ACLineSegmentPhase.ACLineSegment ?s.
   ?acp c:ACLineSegmentPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) } } ORDER BY ?name ?phs
   } GROUP BY ?name ?bus1 ?bus2 ?eqid ?trm1id ?trm2id
   ORDER BY ?name ?bus1 ?bus2 ?phs
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  #print ('\nACLineSegment binding keys are:',ret.variables)
  for b in ret.bindings:
    phases = FlatPhases (b['phases'].value)
    bus1 = b['bus1'].value
    bus2 = b['bus2'].value
    for phs in phases:
      print ('ACLineSegment','s1',b['name'].value,bus1,bus2,phs,b['eqid'].value,b['trm1id'].value,b['trm2id'].value,file=op)
      if not busphases[bus1][phs]:
        print ('ACLineSegment','v1',b['name'].value,bus1,bus2,phs,b['eqid'].value,b['trm1id'].value,b['trm2id'].value,file=np)
        busphases[bus1][phs] = True
      if not busphases[bus2][phs]:
        print ('ACLineSegment','v2',b['name'].value,bus1,bus2,phs,b['eqid'].value,b['trm1id'].value,b['trm2id'].value,file=np)
        busphases[bus2][phs] = True

  ####################### - EnergyConsumer
  op.close()
  op = open (froot + '_loads.txt', 'w')

  qstr = CIMHubConfig.prefix + """SELECT ?name ?bus (group_concat(distinct ?phs;separator=\"\") as ?phases) ?eqid ?trmid WHERE {
    SELECT ?name ?bus ?phs ?eqid ?trmid WHERE {""" + fidselect + """
   ?s r:type c:EnergyConsumer.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid. 
   ?t1 c:Terminal.ConductingEquipment ?s.
   ?t1 c:IdentifiedObject.mRID ?trmid. 
   ?t1 c:ACDCTerminal.sequenceNumber "1".
   ?t1 c:Terminal.ConnectivityNode ?cn1. 
   ?cn1 c:IdentifiedObject.name ?bus.
   OPTIONAL {?acp c:EnergyConsumerPhase.EnergyConsumer ?s.
   ?acp c:EnergyConsumerPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) } } ORDER BY ?name ?phs
   } GROUP BY ?name ?bus ?eqid ?trmid
   ORDER BY ?name ?bus ?phs
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  #print ('\nEnergyConsumer binding keys are:',ret.variables)
  for b in ret.bindings:
    phases = FlatPhases (b['phases'].value)
    bus = b['bus'].value
    for phs in phases:
      print ('EnergyConsumer',b['name'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=op)

  ####################### - Synchronous Machines
  op.close()
  op = open (froot + '_machines.txt', 'w')

  qstr = CIMHubConfig.prefix + """SELECT ?name ?bus ?eqid ?trmid WHERE {""" + fidselect + """
   ?s r:type c:SynchronousMachine.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid. 
   ?t1 c:Terminal.ConductingEquipment ?s.
   ?t1 c:IdentifiedObject.mRID ?trmid. 
   ?t1 c:ACDCTerminal.sequenceNumber "1".
   ?t1 c:Terminal.ConnectivityNode ?cn1. 
   ?cn1 c:IdentifiedObject.name ?bus.
   }
   ORDER BY ?name ?bus
  """
  sparql.setQuery(qstr)
  ret = sparql.query()
  for b in ret.bindings:
    phases = FlatPhases ('ABC')
    bus = b['bus'].value
    for phs in phases:
      print ('SynchronousMachine',b['name'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=op)

  ####################### - PowerTransformer, no tanks
  op.close()
  op = open (froot + '_xfmr_pq.txt', 'w')

  qstr = CIMHubConfig.prefix + """SELECT ?name ?wnum ?bus ?eqid ?trmid WHERE {""" + fidselect + """
   ?s r:type c:PowerTransformer.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid.
   ?end c:PowerTransformerEnd.PowerTransformer ?s.
   ?end c:TransformerEnd.Terminal ?trm.
   ?end c:TransformerEnd.endNumber ?wnum.
   ?trm c:IdentifiedObject.mRID ?trmid. 
   ?trm c:Terminal.ConnectivityNode ?cn. 
   ?cn c:IdentifiedObject.name ?bus.
  }
  ORDER BY ?name ?wnum ?bus
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  #print ('\nPowerTransformer (no-tank) binding keys are:',ret.variables,'plus phases=ABC')
  for b in ret.bindings:
    bus = b['bus'].value
    for phs in 'ABC':
      print ('PowerTransformer','PowerTransformerEnd','s1',b['name'].value,b['wnum'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=op)
      if not busphases[bus][phs]:
        print ('PowerTransformer','PowerTransformerEnd','v1',b['name'].value,b['wnum'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=np)
        busphases[bus][phs] = True

  ####################### - PowerTransformer, with tanks

  qstr = CIMHubConfig.prefix + """SELECT ?name ?wnum ?bus ?orderedPhases ?eqid ?trmid WHERE {""" + fidselect + """
   ?s r:type c:PowerTransformer.
   ?s c:IdentifiedObject.name ?name.
   ?s c:IdentifiedObject.mRID ?eqid.
   ?tank c:TransformerTank.PowerTransformer ?s.
   ?end c:TransformerTankEnd.TransformerTank ?tank.
   ?end c:TransformerEnd.Terminal ?trm.
   ?end c:TransformerEnd.endNumber ?wnum.
   ?trm c:IdentifiedObject.mRID ?trmid. 
   ?trm c:Terminal.ConnectivityNode ?cn. 
   ?cn c:IdentifiedObject.name ?bus.
   OPTIONAL {?end c:TransformerTankEnd.orderedPhases ?phsraw.
    bind(strafter(str(?phsraw),"OrderedPhaseCodeKind.") as ?orderedPhases)}
  }
  ORDER BY ?name ?wnum ?bus ?orderedPhases
  """
  #print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
  #print ('\nPowerTransformer (with tank) binding keys are:',ret.variables)
  for b in ret.bindings:
    bus = b['bus'].value
    phases = FlatPhases (b['orderedPhases'].value)
    for phs in phases:
      print ('PowerTransformer','TransformerTankEnd','s1',b['name'].value,b['wnum'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=op)
      if not busphases[bus][phs]:
        print ('PowerTransformer','TransformerTankEnd','v1',b['name'].value,b['wnum'].value,bus,phs,b['eqid'].value,b['trmid'].value,file=np)
        busphases[bus][phs] = True

  op.close()
  np.close()

# run from command line for GridAPPS-D platform circuits
if __name__ == '__main__':
  cfg_file = sys.argv[1]
  froot = sys.argv[2]
  mRID = sys.argv[3]
  outpath = None
  taxonomy = False
  if len(sys.argv) > 4:
    outpath = sys.argv[4]
  if len(sys.argv) > 5:
    taxonomy = bool (int(sys.argv[5]))
  list_measurables (froot, mRID, outpath, taxonomy, cfg_file)