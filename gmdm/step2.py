# Copyright (C) 2022 Battelle Memorial Institute
# file: step2.py; for appending to adapt_gmdm.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
from SPARQLWrapper import SPARQLWrapper2

cfg_json = '../queries/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)

# patch up the model with applied logic:
sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'
qinserts = []
qdeletes = []

def PostInserts (sparql, qinserts):
  print ('==> inserting', len(qinserts), 'sets of triples')
  qinserts.append ('}')
  qstr = CIMHubConfig.prefix + ' INSERT DATA { ' + ''.join(qinserts)
  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
#  print (ret)
  return

def PostDeletes (sparql, qdeletes):
  print ('==> posting', len(qdeletes), 'delete operations')
  qdeletes.append ('}')
  qstr = CIMHubConfig.prefix + ' DELETE DATA { ' + ''.join(qdeletes)
  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
#  print (ret)
  return

#  list the EquipmentContainer mRIDs
q1 = CIMHubConfig.prefix + """# lists all the equipment container names, types, and ids
SELECT DISTINCT ?name ?type ?id
WHERE {
 {?eq c:Equipment.EquipmentContainer ?container.}
  UNION
 {?eq c:Equipment.AdditionalEquipmentContainer ?container.}
 ?container c:IdentifiedObject.mRID ?id.
 ?container c:IdentifiedObject.name ?name.
 ?container r:type ?rawtype.
  bind(strafter(str(?rawtype),\"#\") as ?type)
}
ORDER BY ?type ?name
"""

fdr_id = None
sparql.setQuery(q1)
ret = sparql.query()
print ('Equipment Containers:')
for b in ret.bindings:
  if b['type'].value == 'Feeder':
    fdr_id = b['id'].value
  print ('  ', b['type'].value, b['name'].value, b['id'].value)
print ('Feeder mRID:', fdr_id)

#  make sure EquipmentContainer is the feeder for Breaker, PowerTransformer, EnergySource
q2 = CIMHubConfig.prefix + """# shows substation equipment that has a missing feeder equipment container
SELECT DISTINCT ?name ?type ?id ?container ?additional
WHERE {
 {?eq r:type c:Breaker.}
  UNION
 {?eq r:type c:PowerTransformer.}
  UNION
 {?eq r:type c:EnergySource.}
 ?eq c:IdentifiedObject.mRID ?id.
 ?eq c:IdentifiedObject.name ?name.
 ?eq r:type ?rawtype.
  bind(strafter(str(?rawtype),\"#\") as ?type)
 OPTIONAL {?eq c:Equipment.EquipmentContainer ?ct1.
          ?ct1 c:IdentifiedObject.mRID ?container.}
 OPTIONAL {?eq c:Equipment.AdditionalEquipmentContainer ?ct2.
          ?ct2 c:IdentifiedObject.mRID ?additional.}
}
ORDER BY ?name
"""
ins_fdr_template = """
 <urn:uuid:{res}> c:Equipment.EquipmentContainer <urn:uuid:{resFdr}>."""
sparql.setQuery(q2)
ret = sparql.query()
print ('Adding Feeder Equipment Containers:')
for b in ret.bindings:
  if 'container' not in b:
    print ('  set Equipment.EquipmentContainer to', fdr_id, 'on', b['type'].value, b['name'].value, b['id'].value)
    ins = ins_fdr_template.format(res=b['id'].value, resFdr=fdr_id, ns=CIMHubConfig.cim_ns)
    qinserts.append(ins)

#  populate LinearShuntCompensator.sections and bPerSection from phases
q3 = CIMHubConfig.prefix + """# find bPerSection and sections for LinearShuntCompensator from its phases
SELECT ?name ?id ?phs ?n ?b WHERE {
 ?s r:type c:LinearShuntCompensator.
 ?s c:IdentifiedObject.name ?name.
 ?s c:IdentifiedObject.mRID ?id.
 ?scp c:ShuntCompensatorPhase.ShuntCompensator ?s.
 ?scp c:ShuntCompensatorPhase.phase ?phsraw.
   bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs)
 ?scp c:LinearShuntCompensatorPhase.bPerSection ?b.
 ?scp c:ShuntCompensatorPhase.sections ?n.
}
ORDER by ?name ?phs
"""
ins_cap_template = """
 <urn:uuid:{res}> c:LinearShuntCompensator.bPerSection \"{bsect}\".
 <urn:uuid:{res}> c:ShuntCompensator.sections \"{nsect}\"."""
caps = {}
sparql.setQuery(q3)
ret = sparql.query()
print ('Accumulating Capacitor Bank Phases:')
for b in ret.bindings:
  key = b['id'].value
  if key in caps:
    caps[key]['nphs'] += 1
    caps[key]['nsect'] += int(b['n'].value)
    caps[key]['bsect'] += float(b['b'].value)
  else:
    caps[key] = {'nphs':1, 'bsect':float(b['b'].value), 'nsect':int(b['n'].value)}
for key, row in caps.items():
  row['bsect'] /= row['nphs']
  row['nsect'] /= row['nphs']
  ins = ins_cap_template.format(res=key, bsect=row['bsect'], nsect=row['nsect'])
  qinserts.append(ins)
print ('  ', caps)

#  populate Switch.ratedCurrent and Switch.normalOpen from phases on Breaker, Fuse, LoadBreakSwitch, Recloser
q4 = CIMHubConfig.prefix + """# find ratedCurrent and normalOpen from SwitchPhases
SELECT DISTINCT ?type ?name ?id ?rated ?open WHERE {
 ?s r:type c:SwitchPhase.
 ?s c:SwitchPhase.ratedCurrent ?rated.
 ?s c:SwitchPhase.normalOpen ?open.
 ?s c:SwitchPhase.Switch ?swt.
 ?swt c:IdentifiedObject.name ?name.
 ?swt c:IdentifiedObject.mRID ?id.
 ?swt r:type ?rawtype.
  bind(strafter(str(?rawtype),\"#\") as ?type)
}
ORDER by ?type ?name
"""
ins_swt_template = """
 <urn:uuid:{res}> c:Switch.ratedCurrent \"{ratedCurrent}\".
 <urn:uuid:{res}> c:Switch.normalOpen \"{normalOpen}\"."""
swts = {}
sparql.setQuery(q4)
ret = sparql.query()
print ('Accumulating Switch Phases:')
for b in ret.bindings:
  key = b['id'].value
  if key in swts:
    swts[key]['rated'] = min(swts[key]['rated'], float(b['rated'].value))
  else:
    swts[key] = {'type':b['type'].value, 'name':b['name'].value, 'open':b['open'].value, 'rated':float(b['rated'].value)}
for key, row in swts.items():
  print (' ', key, row)
  ins = ins_swt_template.format(res=key, ratedCurrent=row['rated'], normalOpen=row['open'])
  qinserts.append(ins)

#  put a base voltage on Breaker and EnergySource
q5 = CIMHubConfig.prefix + """# find the BaseVoltage for Breaker and EnergySource
SELECT DISTINCT ?type ?name ?id ?bvid ?nomu
WHERE {
 {?eq r:type c:Breaker.}
  UNION
 {?eq r:type c:EnergySource.}
 ?eq c:IdentifiedObject.mRID ?id.
 ?eq c:IdentifiedObject.name ?name.
 ?eq r:type ?rawtype.
  bind(strafter(str(?rawtype),\"#\") as ?type)
 ?eq c:Equipment.AdditionalEquipmentContainer ?ctr.
 ?ctr c:IdentifiedObject.mRID ?addid.
 ?ctr r:type ?rawctrtype.
  bind(strafter(str(?rawctrtype),\"#\") as ?addtype)
 ?ctr c:VoltageLevel.BaseVoltage ?bv.
 ?bv c:IdentifiedObject.mRID ?bvid.
 ?bv c:BaseVoltage.nominalVoltage ?nomu.
}
ORDER BY ?type ?name
"""
ins_bv_template = """
 <urn:uuid:{res}> c:ConductingEquipment.BaseVoltage <urn:uuid:{resBv}>."""
bvs = {}
sparql.setQuery(q5)
ret = sparql.query()
print ('Assign BaseVoltage to Breaker and EnergySource:')
for b in ret.bindings:
  key = b['id'].value
  bvs[key] = {'type':b['type'].value, 'name':b['name'].value, 'bvid':b['bvid'].value, 'nomu':float(b['nomu'].value)}
for key, row in bvs.items():
  print (' ', key, row)
  ins = ins_bv_template.format(res=key, resBv=row['bvid'])
  qinserts.append(ins)

#  populate RegulatingControl.enabled as true
q6 = CIMHubConfig.prefix + """# list RegulatingControl and TapChangerControl to populate enabled
SELECT DISTINCT ?type ?name ?id ?enabled
WHERE {
 {?ctl r:type c:RegulatingControl.}
  UNION
 {?ctl r:type c:TapChangerControl.}
 ?ctl c:IdentifiedObject.mRID ?id.
 ?ctl c:IdentifiedObject.name ?name.
 ?ctl r:type ?rawtype.
  bind(strafter(str(?rawtype),\"#\") as ?type)
 OPTIONAL {?ctl c:RegulatingControl.enabled ?enabled.}
}
ORDER BY ?type ?name
"""
ins_regenabled_template = """
 <urn:uuid:{res}> c:RegulatingControl.enabled \"{enabled}\"."""
regctls = {}
sparql.setQuery(q6)
ret = sparql.query()
print ('Populating RegulatingControl.enabled where not present:')
for b in ret.bindings:
  if 'enabled' not in b:
    key = b['id'].value
    regctls[key] = {'type':b['type'].value, 'name':b['name'].value}
for key, row in regctls.items():
  print (' ', key, row)
  ins = ins_regenabled_template.format(res=key, enabled="true")
  qinserts.append(ins)

#  populate RatioTapChanger.normalStep as 0
q7 = CIMHubConfig.prefix + """# list RatioTapChanger to populate normalStep
SELECT DISTINCT ?type ?name ?id ?normalStep
WHERE {
 ?ctl r:type c:RatioTapChanger.
 ?ctl c:IdentifiedObject.mRID ?id.
 ?ctl c:IdentifiedObject.name ?name.
 ?ctl r:type ?rawtype.
  bind(strafter(str(?rawtype),\"#\") as ?type)
 OPTIONAL {?ctl c:TapChanger.normalStep ?normalStep.}
}
ORDER BY ?type ?name
"""
ins_rtc_template = """
 <urn:uuid:{res}> c:TapChanger.normalStep \"{normalStep}\"."""
rtcs = {}
sparql.setQuery(q7)
ret = sparql.query()
print ('Populating RatioTapChanger.normalStep as 0 where not present:')
for b in ret.bindings:
  if 'normalStep' not in b:
    key = b['id'].value
    rtcs[key] = {'type':b['type'].value, 'name':b['name'].value}
for key, row in rtcs.items():
  print (' ', key, row)
  ins = ins_rtc_template.format(res=key, normalStep=0)
  qinserts.append(ins)

#  populate RatioTapChanger.TransformerEnd from TransformerEnd.RatioTapChanger
q8 = CIMHubConfig.prefix + """# list TransformerEnd=>RatioTapChanger associations to reverse
SELECT DISTINCT ?rtcname ?rtcid ?endname ?endid
WHERE {
 ?end c:TransformerEnd.RatioTapChanger ?rtc.
 ?end c:IdentifiedObject.mRID ?endid.
 ?end c:IdentifiedObject.name ?endname.
 ?rtc c:IdentifiedObject.mRID ?rtcid.
 ?rtc c:IdentifiedObject.name ?rtcname.
}
ORDER BY ?rtcname
"""
ins_end_template = """
 <urn:uuid:{res}> c:RatioTapChanger.TransformerEnd <urn:uuid:{resEnd}>."""
rtcends = {}
sparql.setQuery(q8)
ret = sparql.query()
print ('Associating RatioTapChanger back to TransformerEnd:')
for b in ret.bindings:
  key = b['rtcid'].value
  rtcends[key] = {'name':b['rtcname'].value, 'endname':b['endname'].value, 'endid':b['endid'].value}
for key, row in rtcends.items():
  print (' ', key, row)
  ins = ins_end_template.format(res=key, resEnd=row['endid'])
  qinserts.append(ins)

#  populate RegulatingControl.RegulatingCondEq from RegulatingCondEq.RegulatingControl
# list RegulatingCondEq=>RegulatingControl associations to reverse
q8b = CIMHubConfig.prefix + """SELECT DISTINCT ?regname ?regid ?ctlname ?ctlid
WHERE {
 ?reg c:RegulatingCondEq.RegulatingControl ?ctl.
 ?reg c:IdentifiedObject.mRID ?regid.
 ?reg c:IdentifiedObject.name ?regname.
 ?ctl c:IdentifiedObject.mRID ?ctlid.
 ?ctl c:IdentifiedObject.name ?ctlname.
}
ORDER BY ?regname
"""
ins_regctl_template = """
 <urn:uuid:{res}> c:RegulatingControl.RegulatingCondEq <urn:uuid:{resReg}>."""
regctls = {}
sparql.setQuery(q8b)
ret = sparql.query()
print ('Associating RegulatingControl back to RegulatingCondEq:')
for b in ret.bindings:
  key = b['ctlid'].value
  regctls[key] = {'name':b['regname'].value, 'ctlname':b['ctlname'].value, 'regid':b['regid'].value}
for key, row in regctls.items():
  print (' ', key, row)
  qinserts.append(ins_regctl_template.format(res=key, resReg=row['regid']))

#  targetValueUnitMultiplier on targetValue and targetDeadband?  It's either 'none' or 'k'
q9 = CIMHubConfig.prefix + """# list RegulatingControl and TapChangerControl to incorporate targetValueUnitMultiplier
SELECT DISTINCT ?type ?name ?id ?mult ?target ?deadband
WHERE {
 {?ctl r:type c:RegulatingControl.}
  UNION
 {?ctl r:type c:TapChangerControl.}
 ?ctl c:IdentifiedObject.mRID ?id.
 ?ctl c:IdentifiedObject.name ?name.
 ?ctl r:type ?rawtype.
  bind(strafter(str(?rawtype),\"#\") as ?type)
 ?ctl c:RegulatingControl.targetValueUnitMultiplier ?rawmult.
  bind(strafter(str(?rawmult),\"#UnitMultiplier.\") as ?mult)
 ?ctl c:RegulatingControl.targetValue ?target.
 ?ctl c:RegulatingControl.targetDeadband ?deadband.
}
ORDER BY ?type ?name
"""
ins_mult_template = """
 <urn:uuid:{res}> c:RegulatingControl.targetValue \"{target}\".
 <urn:uuid:{res}> c:RegulatingControl.targetDeadband \"{deadband}\"."""
del_mult_template = """
  <urn:uuid:{res}> c:RegulatingControl.targetValue \"{oldTarget}\".
  <urn:uuid:{res}> c:RegulatingControl.targetDeadband \"{oldDeadband}\"."""
mults = {}
sparql.setQuery(q9)
ret = sparql.query()
print ('Applying targetValueUnitMultiplier (only k supported):')
for b in ret.bindings:
  key = b['id'].value
  mult = b['mult'].value
  if mult == 'k':
    mults[key] = {'name':b['name'].value, 'type':b['type'].value, 'scale':1000.0,
      'target':float(b['target'].value), 'deadband':float(b['deadband'].value)}
for key, row in mults.items():
  print (' ', key, row)
  ins = ins_mult_template.format(res=key, target=row['scale']*row['target'], 
                                 deadband=row['scale']*row['deadband'])
  qinserts.append(ins)
  qdeletes.append(del_mult_template.format(res=key, oldTarget=row['target'], 
                                           oldDeadband=row['deadband']))

#
#  the inverter in this example has PV, wind, and storage units connected. Neither OpenDSS nor GridLAB-D support that.
#    a) if more than one PEU points at the same PEC, list them and accumulate the results
#    b) accumulate the minP and maxP into a PhotovoltaicUnit, or a BatteryUnit if storedE available
#    c) mark the accumulated PEU for connection to a PEC
#  this is like making a 'virtual battery' for a transactive system, but need to set the batteryState properly (TODO)
q10 = CIMHubConfig.prefix + """# sum the maxP, minP, storedE, ratedE for units connected to an inverter
# also list the battery state, but this may be modified by output of parallel DC sources
SELECT ?invname ?invid ?unitname ?unitid ?minP ?maxP ?ratedE ?storedE ?state
WHERE {
 ?peu c:PowerElectronicsUnit.PowerElectronicsConnection ?pec.
 ?peu c:IdentifiedObject.mRID ?unitid.
 ?peu c:IdentifiedObject.name ?unitname.
 ?peu c:PowerElectronicsUnit.minP ?minP.
 ?peu c:PowerElectronicsUnit.maxP ?maxP.
 ?pec c:IdentifiedObject.mRID ?invid.
 ?pec c:IdentifiedObject.name ?invname.
 OPTIONAL {?peu c:BatteryUnit.storedE ?storedE.
           ?peu c:BatteryUnit.ratedE ?ratedE.
           ?peu c:BatteryUnit.batteryState ?stateraw.
            bind(strafter(str(?stateraw),\"BatteryStateKind.\") as ?state)}
}
ORDER BY ?invname
"""
ins_peu_template = """
 <urn:uuid:{res}> c:BatteryUnit.ratedE \"{ratedE}\".
 <urn:uuid:{res}> c:BatteryUnit.storedE \"{storedE}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.maxP \"{maxP}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.minP \"{minP}\"."""
del_peu_template = """
 <urn:uuid:{res}> c:BatteryUnit.ratedE \"{oldRatedE}\".
 <urn:uuid:{res}> c:BatteryUnit.storedE \"{oldStoredE}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.maxP \"{oldMaxP}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.minP \"{oldMinP}\"."""
link_pec_template = """
 <urn:uuid:{res}> c:PowerElectronicsConnection.PowerElectronicsUnit <urn:uuid:{resPEU}>."""
pecs = {}
sparql.setQuery(q10)
ret = sparql.query()
print ('Accumulating PowerElectronicUnits to PowerElectronicConnections (OpenDSS/GridLAB-D only allow one PEU (no Wind) per PEC):')
for b in ret.bindings:
  key = b['invid'].value
  if key in pecs:
    pecs[key]['minP'] -= float(b['minP'].value)
    pecs[key]['maxP'] += float(b['maxP'].value)
    pecs[key]['nunits'] += 1
    if 'ratedE' in b: # update to the most recent battery
      pecs[key]['unitid'] = b['unitid'].value
      pecs[key]['unitname'] = b['unitname'].value
      pecs[key]['ratedE'] += float(b['ratedE'].value)
      pecs[key]['storedE'] += float(b['storedE'].value)
  else:
    pecs[key] = {'invname':b['invname'].value, 'minP':float(b['minP'].value), 'maxP':float(b['maxP'].value), 'nunits':1}
    pecs[key]['unitid'] = b['unitid'].value
    pecs[key]['unitname'] = b['unitname'].value
    if 'ratedE' in b:
      pecs[key]['ratedE'] = float(b['ratedE'].value)
      pecs[key]['storedE'] = float(b['storedE'].value)
    else:
      pecs[key]['ratedE'] = 0.0
      pecs[key]['storedE'] = 0.0
    pecs[key]['oldRatedE'] = pecs[key]['ratedE']
    pecs[key]['oldStoredE'] = pecs[key]['storedE']
    pecs[key]['oldMinP'] = pecs[key]['minP']
    pecs[key]['oldMaxP'] = pecs[key]['maxP']
for key, row in pecs.items():
  print (' ', key, row)
  qinserts.append(ins_peu_template.format(res=row['unitid'], ratedE=row['ratedE'], storedE=row['storedE'],
                                          minP=row['minP'], maxP=row['maxP']))
  qinserts.append(link_pec_template.format(res=key, resPEU=row['unitid']))
  qdeletes.append(del_peu_template.format(res=row['unitid'], oldRatedE=row['oldRatedE'], oldStoredE=row['oldStoredE'],
                                          oldMinP=row['oldMinP'], oldMaxP=row['oldMaxP']))

#  for PEC with only one PEU, populate PowerElectronicsUnit.PowerElectronicsConnection from PowerElectronicsConnection.PowerElectronicsUnit
#  for the accumulated PEUs, also populate PowerElectronicsUnit.PowerElectronicsConnection from PowerElectronicsConnection.PowerElectronicsUnit

#  add a PowerElectronicsConnection.controlMode

q11 = CIMHubConfig.prefix + """# list PowerElectronicsConnection to populate with controlMode 'constantPowerFactor'
SELECT ?name ?id ?controlMode
WHERE {
 ?pec r:type c:PowerElectronicsConnection.
 ?pec c:IdentifiedObject.mRID ?id.
 ?pec c:IdentifiedObject.name ?name.
 OPTIONAL {?pec c:PowerElectronicsConnection.controlMode ?modeRaw.
  bind(strafter(str(?modeRaw),\"ConverterControlModeKind.\") as ?controlMode)}
}
ORDER BY ?name
"""
ins_pec_template = """
 <urn:uuid:{res}> c:PowerElectronicsConnection.controlMode {ns}ConverterControlModeKind.{mode}>.
"""
pecmodes = {}
sparql.setQuery(q11)
ret = sparql.query()
print ('Populate PowerElectronicsConnection.controlMode with constantPowerFactor:')
for b in ret.bindings:
  key = b['id'].value
  pecmodes[key] = {'name':b['name'].value, 'mode':'constantPowerFactor'}
for key, row in pecmodes.items():
  print (' ', key, row)
  inspec = ins_pec_template.format(res=key, mode=row['mode'], ns=CIMHubConfig.cim_ns)
  qinserts.append(inspec)

# use fdr_id as the ConnectivityNodeContainer for all buses, so DistBus query will succeeed
q12 = CIMHubConfig.prefix + """# shows ConnectivityNode that have no ConnectivityNodeContainer
SELECT DISTINCT ?name ?id ?container 
WHERE {
 ?cn r:type c:ConnectivityNode.
 ?cn c:IdentifiedObject.mRID ?id.
 ?cn c:IdentifiedObject.name ?name.
 OPTIONAL {?cn c:ConnectivityNode.ConnectivityNodeContainer ?ct1.
          ?ct1 c:IdentifiedObject.mRID ?container.}
}
ORDER BY ?name
"""
ins_cn_template = """
 <urn:uuid:{res}> c:ConnectivityNode.ConnectivityNodeContainer <urn:uuid:{resFdr}>."""
sparql.setQuery(q12)
ret = sparql.query()
print ('Adding Connectivity Node Containers:')
for b in ret.bindings:
  if 'container' not in b:
    print ('  set ConnectivityNode.ConnectivityNodeContainer to', fdr_id, 'on', b['name'].value, b['id'].value)
    ins = ins_cn_template.format(res=b['id'].value, resFdr=fdr_id, ns=CIMHubConfig.cim_ns)
    qinserts.append(ins)
PostDeletes (sparql, qdeletes)
PostInserts (sparql, qinserts)

