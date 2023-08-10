from SPARQLWrapper import SPARQLWrapper2
import re
import uuid
import os.path
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import math

CATA_MIN_SBYP = 1.0328
CATB_MIN_SBYP = 1.1135

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
 <urn:uuid:{res}> a c:PositionPoint.
 <urn:uuid:{res}> c:PositionPoint.Location <urn:uuid:{resLoc}>.
 <urn:uuid:{res}> c:PositionPoint.sequenceNumber \"{seq}\".
 <urn:uuid:{res}> c:PositionPoint.xPosition \"{x}\".
 <urn:uuid:{res}> c:PositionPoint.yPosition \"{y}\".
"""

ins_loc_template = """
 <urn:uuid:{res}> a c:Location.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:Location.CoordinateSystem <urn:uuid:{resCrs}>.
"""

ins_trm_template = """
 <urn:uuid:{res}> a c:Terminal.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:Terminal.ConductingEquipment <urn:uuid:{resEQ}>.
 <urn:uuid:{res}> c:ACDCTerminal.sequenceNumber \"1\".
 <urn:uuid:{res}> c:Terminal.ConnectivityNode <urn:uuid:{resCN}>.
"""

ins_pec_template = """
 <urn:uuid:{res}> a c:PowerElectronicsConnection.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:Equipment.EquipmentContainer  <urn:uuid:{resFdr}>.
 <urn:uuid:{res}> c:PowerElectronicsConnection.PowerElectronicsUnit <urn:uuid:{resUnit}>.
 <urn:uuid:{res}> c:PowerSystemResource.Location <urn:uuid:{resLoc}>.
 <urn:uuid:{res}> c:PowerElectronicsConnection.maxIFault \"1.111\".
 <urn:uuid:{res}> c:PowerElectronicsConnection.p \"{p}\".
 <urn:uuid:{res}> c:PowerElectronicsConnection.q \"{q}\".
 <urn:uuid:{res}> c:PowerElectronicsConnection.maxQ \"{maxQ}\".
 <urn:uuid:{res}> c:PowerElectronicsConnection.minQ \"{minQ}\".
 <urn:uuid:{res}> c:PowerElectronicsConnection.ratedS \"{ratedS}\".
 <urn:uuid:{res}> c:PowerElectronicsConnection.ratedU \"{ratedU}\".
 <urn:uuid:{res}> c:PowerElectronicsConnection.controlMode {ns}ConverterControlModeKind.{mode}>.
"""

ins_syn_template = """
 <urn:uuid:{res}> a c:SynchronousMachine.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:Equipment.EquipmentContainer  <urn:uuid:{resFdr}>.
 <urn:uuid:{res}> c:PowerSystemResource.Location <urn:uuid:{resLoc}>.
 <urn:uuid:{res}> c:RotatingMachine.p \"{p}\".
 <urn:uuid:{res}> c:RotatingMachine.q \"{q}\".
 <urn:uuid:{res}> c:RotatingMachine.ratedS \"{ratedS}\".
 <urn:uuid:{res}> c:RotatingMachine.ratedU \"{ratedU}\".
"""

ins_pep_template = """
 <urn:uuid:{res}> a c:PowerElectronicsConnectionPhase.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:PowerElectronicsConnectionPhase.phase {ns}SinglePhaseKind.{phs}>.
 <urn:uuid:{res}> c:PowerElectronicsConnectionPhase.PowerElectronicsConnection <urn:uuid:{resPEC}>.
 <urn:uuid:{res}> c:PowerElectronicsConnectionPhase.p \"{p}\".
 <urn:uuid:{res}> c:PowerElectronicsConnectionPhase.q \"{q}\".
 <urn:uuid:{res}> c:PowerSystemResource.Location <urn:uuid:{resLoc}>.
"""

ins_pv_template = """
 <urn:uuid:{res}> a c:PhotovoltaicUnit.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.minP \"{minP}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.maxP \"{maxP}\".
 <urn:uuid:{res}> c:PowerSystemResource.Location <urn:uuid:{resLoc}>.
"""

ins_bat_template = """
 <urn:uuid:{res}> a c:BatteryUnit.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.minP \"{minP}\".
 <urn:uuid:{res}> c:PowerElectronicsUnit.maxP \"{maxP}\".
 <urn:uuid:{res}> c:BatteryUnit.ratedE \"{ratedE}\".
 <urn:uuid:{res}> c:BatteryUnit.storedE \"{storedE}\".
 <urn:uuid:{res}> c:BatteryUnit.batteryState {ns}BatteryStateKind.{state}>.
 <urn:uuid:{res}> c:PowerSystemResource.Location <urn:uuid:{resLoc}>.
"""

def GetCIMID (cls, nm, uuids):
  if nm is not None:
    key = cls + ':' + nm
    if key not in uuids:
      uuids[key] = str(uuid.uuid4()).upper()
    return uuids[key]
  return str(uuid.uuid4()).upper() # for unidentified CIM instances

class ieee1547:
  def __init__(self):
    self.cimparms = {}
    self.cimparms['DERIEEEType1'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'DynamicsFunctionBlock.enabled': True,
      'DERIEEEType1.phaseToGroundApplicable': True,
      'DERIEEEType1.phaseToNeutralApplicable': False,
      'DERIEEEType1.phaseToPhaseApplicable': False,
      'DERDynamics.PowerElectronicsConnection':None
    }
    self.cimparms['DERNameplateData'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'DERNameplateData.DERIEEEType1':None,
      'DERNameplateData.normalOPcatKind':'NormalOPcatKind.catB',
      'DERNameplateData.supportsConstPFmode':True,
      'DERNameplateData.supportsConstQmode':True,
      'DERNameplateData.supportsQVmode':True,
      'DERNameplateData.supportsPVmode':True,
      'DERNameplateData.supportsQPmode':True,
      'DERNameplateData.supportsPFmode':False,
      'DERNameplateData.acVmax':0.0,
      'DERNameplateData.acVmin':0.0
    }
    self.cimparms['DERNameplateDataApplied'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'DERNameplateDataApplied.DERNameplateData':None,
      'DERNameplateDataApplied.pMax':0.0,
      'DERNameplateDataApplied.pMaxOverPF':0.0,
      'DERNameplateDataApplied.overPF':0.0,
      'DERNameplateDataApplied.pMaxUnderPF':0.0,
      'DERNameplateDataApplied.underPF':0.0,
      'DERNameplateDataApplied.sMax':0.0,
      'DERNameplateDataApplied.qMaxInj':0.0,
      'DERNameplateDataApplied.qMaxAbs':0.0,
      'DERNameplateDataApplied.pMaxCharge':0.0,
      'DERNameplateDataApplied.apparentPowerChargeMax':0.0,
      'DERNameplateDataApplied.acVnom':0.0
    }
    self.cimparms['ConstantReactivePowerSettings'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'ConstantReactivePowerSettings.DERIEEEType1':None,
      'ConstantReactivePowerSettings.enabled':False,
      'ConstantReactivePowerSettings.reactivePower':0.0
    }
    self.cimparms['ConstantPowerFactorSettings'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'ConstantPowerFactorSettings.DERIEEEType1':None,
      'ConstantPowerFactorSettings.enabled':False,
      'ConstantPowerFactorSettings.powerFactor':1.0,
      'ConstantPowerFactorSettings.constantPowerFactorExcitationKind':'ConstantPowerFactorSettingKind.abs'
    }
    self.cimparms['VoltVarSettings'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'VoltVarSettings.DERIEEEType1':None,
      'VoltVarSettings.enabled':False,
      'VoltVarSettings.vRefAutoModeEnabled':False,
      'VoltVarSettings.vRef':0.0,
      'VoltVarSettings.vRefOlrt':0.0,
      'VoltVarSettings.curveV1':0.0,
      'VoltVarSettings.curveV2':0.0,
      'VoltVarSettings.curveV3':0.0,
      'VoltVarSettings.curveV4':0.0,
      'VoltVarSettings.curveQ1':0.0,
      'VoltVarSettings.curveQ2':0.0,
      'VoltVarSettings.curveQ3':0.0,
      'VoltVarSettings.curveQ4':0.0,
      'VoltVarSettings.olrt':0.0
    }
    self.cimparms['VoltWattSettings'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'VoltWattSettings.DERIEEEType1':None,
      'VoltWattSettings.enabled':False,
      'VoltWattSettings.curveV1':0.0,
      'VoltWattSettings.curveV2':0.0,
      'VoltWattSettings.curveP1':0.0,
      'VoltWattSettings.curveP2gen':0.0,
      'VoltWattSettings.curveP2load':0.0,
      'VoltWattSettings.olrt':0.0
    }
    self.cimparms['WattVarSettings'] = {
      'IdentifiedObject.name':None,
      'IdentifiedObject.mRID':None,
      'WattVarSettings.DERIEEEType1':None,
      'WattVarSettings.enabled':False,
      'WattVarSettings.curveP1gen':0.0,
      'WattVarSettings.curveP2gen':0.0,
      'WattVarSettings.curveP3gen':0.0,
      'WattVarSettings.curveQ1gen':0.0,
      'WattVarSettings.curveQ2gen':0.0,
      'WattVarSettings.curveQ3gen':0.0,
      'WattVarSettings.curveP1load':0.0,
      'WattVarSettings.curveP2load':0.0,
      'WattVarSettings.curveP3load':0.0,
      'WattVarSettings.curveQ1load':0.0,
      'WattVarSettings.curveQ2load':0.0,
      'WattVarSettings.curveQ3load':0.0
    }

  def print_dicts(self):
    for tag in ['DERIEEEType1', 'DERNameplateData', 'DERNameplateDataApplied', 'ConstantReactivePowerSettings',
                'ConstantPowerFactorSettings', 'VoltVarSettings', 'VoltWattSettings', 'WattVarSettings']:
      dct = self.cimparms[tag]
      print ('**', tag)
      print (dct)

  def assign_pec(self, ratedS, kWmax, ratedU, category, ctrlMode, p, q, pecID, name, bBattery, uuids):
    bCatA = True
    if category == 'catB':
      bCatA = False

    nameDER = name + '_DER'
    nameND = name + '_ND'
    nameAD = name + '_AD'
    nameCQ = name + '_CQ'
    namePF = name + '_PF'
    nameVV = name + '_VV'
    nameVW = name + '_VW'
    nameWV = name + '_WV'
    uuidDER = GetCIMID ('DERIEEEType1', nameDER, uuids)
    uuidND = GetCIMID ('DERNameplateData', nameND, uuids)
    uuidAD = GetCIMID ('DERNameplateDataApplied', nameAD, uuids)
    uuidCQ = GetCIMID ('ConstantReactivePowerSettings', nameCQ, uuids)
    uuidPF = GetCIMID ('ConstantPowerFactorSettings', namePF, uuids)
    uuidVV = GetCIMID ('VoltVarSettings', nameVV, uuids)
    uuidVW = GetCIMID ('VoltWattSettings', nameVW, uuids)
    uuidWV = GetCIMID ('WattVarSettings', nameWV, uuids)

    dct = self.cimparms['DERIEEEType1']
    dct['IdentifiedObject.name'] = nameDER
    dct['IdentifiedObject.mRID'] = uuidDER
    dct['DERDynamics.PowerElectronicsConnection'] = pecID

    dct = self.cimparms['DERNameplateData']
    dct['IdentifiedObject.name'] = nameND
    dct['IdentifiedObject.mRID'] = uuidND
    dct['DERNameplateData.DERIEEEType1'] = uuidDER
    if bCatA:
      dct['DERNameplateData.normalOPcatKind'] = 'NormalOPcatKind.catA'
      dct['DERNameplateData.supportsPVmode'] = False
      dct['DERNameplateData.supportsQPmode'] = False
    else:
      dct['DERNameplateData.normalOPcatKind'] = 'NormalOPcatKind.catB'
      dct['DERNameplateData.supportsPVmode'] = True
      dct['DERNameplateData.supportsQPmode'] = True
    dct['DERNameplateData.acVmin'] = 0.95 * 1000.0 * ratedU
    dct['DERNameplateData.acVmax'] = 1.05 * 1000.0 * ratedU

    dct = self.cimparms['DERNameplateDataApplied']
    dct['IdentifiedObject.name'] = nameAD
    dct['IdentifiedObject.mRID'] = uuidAD
    dct['DERNameplateDataApplied.DERNameplateData'] = uuidND
    dct['DERNameplateDataApplied.acVnom'] = 1000.0 * ratedU
    dct['DERNameplateDataApplied.pMax'] = 1000.0 * kWmax
    dct['DERNameplateDataApplied.sMax'] = 1000.0 * ratedS
    dct['DERNameplateDataApplied.qMaxInj'] = 0.44 * 1000.0 * ratedS
    dct['DERNameplateDataApplied.pMaxOverPF'] = 1000.0 * kWmax
    dct['DERNameplateDataApplied.overPF'] = kWmax / ratedS
    dct['DERNameplateDataApplied.pMaxUnderPF'] = 1000.0 * kWmax
    dct['DERNameplateDataApplied.underPF'] = kWmax / ratedS
    if bCatA:
      dct['DERNameplateDataApplied.qMaxAbs'] = 0.25 * 1000.0 * ratedS
    else:
      dct['DERNameplateDataApplied.qMaxAbs'] = 0.44 * 1000.0 * ratedS
    if bBattery:
      dct['DERNameplateDataApplied.pMaxCharge'] = 1000.0 * kWmax
      dct['DERNameplateDataApplied.apparentPowerChargeMax'] = 1000.0 * ratedS
    else:
      dct['DERNameplateDataApplied.pMaxCharge'] = 0.0
      dct['DERNameplateDataApplied.apparentPowerChargeMax'] = 0.0

    dct = self.cimparms['ConstantReactivePowerSettings']
    dct['IdentifiedObject.name'] = nameCQ
    dct['IdentifiedObject.mRID'] = uuidCQ
    dct['ConstantReactivePowerSettings.DERIEEEType1'] = uuidDER
    if ctrlMode in ['CQ']:
      dct['ConstantReactivePowerSettings.enabled'] = True
    else:
      dct['ConstantReactivePowerSettings.enabled'] = False
    dct['ConstantReactivePowerSettings.reactivePower'] = 1000.0 * q

    dct = self.cimparms['ConstantPowerFactorSettings']
    dct['IdentifiedObject.name'] = namePF
    dct['IdentifiedObject.mRID'] = uuidPF
    dct['ConstantPowerFactorSettings.DERIEEEType1'] = uuidDER
    if ctrlMode in ['PF']:
      dct['ConstantPowerFactorSettings.enabled'] = True
    else:
      dct['ConstantPowerFactorSettings.enabled'] = False
    pf = 1.0
    s = math.sqrt(p*p + q*q);
    if s > 0.0:
      pf = p / s
    dct['ConstantPowerFactorSettings.powerFactor'] = pf
    if q < 0.0:
      dct['ConstantPowerFactorSettings.constantPowerFactorExcitationKind'] = 'ConstantPowerFactorSettingKind.abs'
    else:
      dct['ConstantPowerFactorSettings.constantPowerFactorExcitationKind'] = 'ConstantPowerFactorSettingKind.inj'

    dct = self.cimparms['VoltVarSettings']
    dct['IdentifiedObject.name'] = nameVV
    dct['IdentifiedObject.mRID'] = uuidVV
    dct['VoltVarSettings.DERIEEEType1'] = uuidDER
    if ctrlMode in ['VV', 'AVR', 'VV_VW']:
      dct['VoltVarSettings.enabled'] = True
    else:
      dct['VoltVarSettings.enabled'] = False
    if ctrlMode in ['AVR']:
      dct['VoltVarSettings.vRefAutoModeEnabled'] = True
    else:
      dct['VoltVarSettings.vRefAutoModeEnabled'] = False
    dct['VoltVarSettings.vRef'] = 1.00
    dct['VoltVarSettings.vRefOlrt'] = 300.0
    if bCatA:
      dct['VoltVarSettings.curveV1'] = 0.90
      dct['VoltVarSettings.curveV2'] = 1.00
      dct['VoltVarSettings.curveV3'] = 1.00
      dct['VoltVarSettings.curveV4'] = 1.10
      dct['VoltVarSettings.curveQ1'] = 0.25
      dct['VoltVarSettings.curveQ2'] = 0.00
      dct['VoltVarSettings.curveQ3'] = 0.00
      dct['VoltVarSettings.curveQ4'] =-0.25
      dct['VoltVarSettings.olrt'] = 10.0
    else:
      dct['VoltVarSettings.curveV1'] = 0.92
      dct['VoltVarSettings.curveV2'] = 0.98
      dct['VoltVarSettings.curveV3'] = 1.02
      dct['VoltVarSettings.curveV4'] = 1.08
      dct['VoltVarSettings.curveQ1'] = 0.44
      dct['VoltVarSettings.curveQ2'] = 0.00
      dct['VoltVarSettings.curveQ3'] = 0.00
      dct['VoltVarSettings.curveQ4'] =-0.44
      dct['VoltVarSettings.olrt'] = 5.0

    dct = self.cimparms['VoltWattSettings']
    dct['IdentifiedObject.name'] = nameVW
    dct['IdentifiedObject.mRID'] = uuidVW
    dct['VoltWattSettings.DERIEEEType1'] = uuidDER
    if ctrlMode in ['VW', 'VV_VW']:
      dct['VoltWattSettings.enabled'] = True
    else:
      dct['VoltWattSettings.enabled'] = False
    dct['VoltWattSettings.curveV1'] = 1.06
    dct['VoltWattSettings.curveV2'] = 1.10
    dct['VoltWattSettings.curveP1'] = 1.0
    dct['VoltWattSettings.curveP2gen'] = 0.2
    if bBattery:
      dct['VoltWattSettings.curveP2load'] = -1.0
    else:
      dct['VoltWattSettings.curveP2load'] = 0.0
    dct['VoltWattSettings.olrt'] = 10.0

    dct = self.cimparms['WattVarSettings']
    dct['IdentifiedObject.name'] = nameWV
    dct['IdentifiedObject.mRID'] = uuidWV
    dct['WattVarSettings.DERIEEEType1'] = uuidDER
    if ctrlMode in ['WVAR']:
      dct['WattVarSettings.enabled'] = True
    else:
      dct['WattVarSettings.enabled'] = False
    dct['WattVarSettings.curveP1gen'] = 0.2
    dct['WattVarSettings.curveP2gen'] = 0.5
    dct['WattVarSettings.curveP3gen'] = 1.0
    dct['WattVarSettings.curveQ1gen'] = 0.0
    dct['WattVarSettings.curveQ2gen'] = 0.0
    dct['WattVarSettings.curveQ3gen'] = 0.44
    if bBattery:
      dct['WattVarSettings.curveP1load'] = 0.2
      dct['WattVarSettings.curveP2load'] = 0.5
      dct['WattVarSettings.curveP3load'] = 1.0
    else:
      dct['WattVarSettings.curveP1load'] = 0.0
      dct['WattVarSettings.curveP2load'] = 0.0
      dct['WattVarSettings.curveP3load'] = 0.0
    dct['WattVarSettings.curveQ1load'] = 0.0
    dct['WattVarSettings.curveQ2load'] = 0.0
    if bCatA:
      dct['WattVarSettings.curveQ3load'] = 0.25
    else:
      dct['WattVarSettings.curveQ3load'] = 0.44
    return

  def append_cim_triples(self, qtriples):
    for tag in ['DERIEEEType1', 'DERNameplateData', 'DERNameplateDataApplied', 'ConstantReactivePowerSettings',
                'ConstantPowerFactorSettings', 'VoltVarSettings', 'VoltWattSettings', 'WattVarSettings']:
      dct = self.cimparms[tag]
      prefix = ' <urn:uuid:{:s}> '.format (dct['IdentifiedObject.mRID'])
      qtriples.append (prefix + 'a c:{:s}.\n'.format(tag))
      for key, val in dct.items():
        if ('.DER' in key) or ('.Power' in key):
          qtriples.append (prefix + 'c:{:s} <urn:uuid:{:s}>.\n'.format(key, str(val)))
        elif 'Kind' in key:
          qtriples.append (prefix + 'c:{:s} {:s}#{:s}>.\n'.format(key, CIMHubConfig.cim_ns, str(val)))
        else:
          qtriples.append (prefix + 'c:{:s} \"{:s}\".\n'.format (key, str(val)))

def ParsePhases (sphs):
  lst = []
  for code in ['A', 'B', 'C', 's1', 's2']:
    if code in sphs:
      lst.append(code)
  return lst

def PostDER (sparql, qtriples):
  print ('==> inserting', len(qtriples), 'instances for DER')
  qtriples.append ('}')
  qstr = CIMHubConfig.prefix + ' INSERT DATA { ' + ''.join(qtriples)
#  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
#  print (ret)
  return

def get_category (name, tok):
  if tok in ['catA', 'catB']:
    return tok
  print ('** {:s} has invalid category {:s}, setting to catA'.format (name, tok))
  return 'catA'

def get_control_mode (name, tok):
  if tok in ['CQ', 'PF', 'VV', 'VW', 'WVAR', 'AVR', 'VV_VW']:
    return tok
  print ('** {:s} has invalid control mode {:s}, setting to PF'.format (name, tok))
  return 'PF'

def get_cim_control_mode (mode):
  if mode == 'CQ':
    return 'constantReactivePower'
  elif mode == 'PF':
    return 'constantPowerFactor'
  return 'dynamic'

def insert_der (fname, cfg_file=None):
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
  settings = ieee1547()

  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'

  fp = open (fname, 'r')
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
        kWmax = float(toks[4])
        kVA = float(toks[5])
        kV = float(toks[6])
        kW = float(toks[7])
        kVAR = float(toks[8])
        maxQ = math.sqrt(kVA*kVA - kWmax*kWmax)
        minQ = -maxQ
        if unit == 'Battery' or unit == 'Photovoltaic':
          category = get_category (name, toks[9])
          ctrlMode = get_control_mode (name, toks[10])
          if unit == 'Battery':
            ratedkwh = float(toks[11])
            storedkwh = float(toks[12])
          else:
            ratedkwh = 0.0
            storedkwh = 0.0
        else:
          category = 'not supported'
          ctrlMode = 'not supported'
        nmUnit = name + '_' + unit
        nmTrm = name + '_T1'
        nmLoc = name + '_Loc'
        idLoc = GetCIMID('Location', nmLoc, uuids)
        idPt = GetCIMID('PositionPoint', None, uuids)
        idTrm = GetCIMID('Terminal', nmTrm, uuids)
        row = buses[nmCN]
        idCN = row['cn']
        keyXY = row['loc'] + ':' + str(row['seq'])
        pp = locs[keyXY]
        x = float(pp['x'])
        y = float(pp['y'])
        print ('create {:s} at {:s} CN {:s} location {:.4f},{:.4f}, IEEE 1547 {:s}:{:s}'.format (name, nmCN, idCN, x, y, category, ctrlMode))

        if unit == 'SynchronousMachine':
          idSYN = GetCIMID('SynchronousMachine', name, uuids)
          inssyn = ins_syn_template.format(url=CIMHubConfig.blazegraph_url, res=idSYN, nm=name, resLoc=idLoc, resFdr=fdr_id,
                                           resUnit=None, p=kW*1000.0, q=kVAR*1000.0, ratedS=kVA*1000.0, ratedU=kV*1000.0) 
          qtriples.append(inssyn)
        else:
          idUnit = GetCIMID(unit + 'Unit', nmUnit, uuids)
          if category == 'catA':
            if (kVA/kWmax) < CATA_MIN_SBYP:
              print ('** {:s} {:s} inverter kVA should be >= {:.3f} for category A'.format (unit, name, kWmax*CATA_MIN_SBYP))
          elif category == 'catB':
            if (kVA/kWmax) < CATB_MIN_SBYP:
              print ('** {:s} {:s} inverter kVA should be >= {:.3f} for category B'.format (unit, name, kWmax*CATB_MIN_SBYP))
          idPEC = GetCIMID('PowerElectronicsConnection', name, uuids)
          inspec = ins_pec_template.format(url=CIMHubConfig.blazegraph_url, res=idPEC, nm=name, resLoc=idLoc, resFdr=fdr_id, 
                                           resUnit=idUnit, p=kW*1000.0, q=kVAR*1000.0, ratedS=kVA*1000.0, ratedU=kV*1000.0,
                                           maxQ=maxQ, minQ=minQ,
                                           mode=get_cim_control_mode(ctrlMode), ns=CIMHubConfig.cim_ns)
          qtriples.append(inspec)
          if ctrlMode in ['VV','VW','WVAR','AVR','VV_VW']:
            if unit == 'Battery':
              settings.assign_pec(kVA, kWmax, kV, category, ctrlMode, kW, kVAR, idPEC, name, True, uuids)
            else:
              settings.assign_pec(kVA, kWmax, kV, category, ctrlMode, kW, kVAR, idPEC, name, False, uuids)
#            settings.print_dicts()
            settings.append_cim_triples(qtriples)

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
                                                       ratedE=ratedkwh*1000.0, storedE=storedkwh*1000.0, state=state, maxP=kWmax*1000.0, minP=-kWmax*1000.0)
          elif unit == 'Photovoltaic':
            insunit = ins_pv_template.format(url=CIMHubConfig.blazegraph_url, res=idUnit, nm=nmUnit, resLoc=idLoc, maxP=kWmax*1000.0, minP=0.1*kWmax*1000.0)
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
      PostDER (sparql, qtriples)
      qtriples = []

  fp.close()

  if len(qtriples) > 0:
    PostDER (sparql, qtriples)
    qtriples = []

  if fuidname is not None:
    print ('saving identifiable instance mRIDs to', fuidname)
    fuid = open (fuidname, 'w')
    for key, val in uuids.items():
      print ('{:s},{:s}'.format (key.replace(':', ',', 1), val), file=fuid)
    fuid.close()

# run from command line for GridAPPS-D platform circuits
if __name__ == '__main__':
  cfg_file = sys.argv[1]
  fname = sys.argv[2]
  insert_der (fname, cfg_file)

