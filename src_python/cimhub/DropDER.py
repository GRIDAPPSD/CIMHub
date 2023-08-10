from SPARQLWrapper import SPARQLWrapper2
import re
import uuid
import os.path
import cimhub.CIMHubConfig as CIMHubConfig
import sys

drop_pt_template = """DELETE {{
 ?m a ?class.
 ?m c:PositionPoint.Location ?locid.
 ?m c:PositionPoint.sequenceNumber ?seq.
 ?m c:PositionPoint.xPosition ?x.
 ?m c:PositionPoint.yPosition ?y.
}} WHERE {{
 VALUES ?locid {{<urn:uuid:{res}>}}
 VALUES ?class {{c:PositionPoint}}
 ?m a ?class.
 ?m c:PositionPoint.Location ?locid.
 ?m c:PositionPoint.sequenceNumber ?seq.
 ?m c:PositionPoint.xPosition ?x.
 ?m c:PositionPoint.yPosition ?y.
}}"""

drop_loc_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Location.CoordinateSystem ?crs.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:Location}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Location.CoordinateSystem ?crs.
}}
"""

drop_trm_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Terminal.ConductingEquipment ?eq.
 ?m c:ACDCTerminal.sequenceNumber ?seq.
 ?m c:Terminal.ConnectivityNode ?cn.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:Terminal}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Terminal.ConductingEquipment ?eq.
 ?m c:ACDCTerminal.sequenceNumber ?seq.
 ?m c:Terminal.ConnectivityNode ?cn.
}}
"""

drop_pec_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerElectronicsConnection.PowerElectronicsUnit ?unit.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:PowerElectronicsConnection.maxIFault ?flt.
 ?m c:PowerElectronicsConnection.p ?p.
 ?m c:PowerElectronicsConnection.q ?q.
 ?m c:PowerElectronicsConnection.maxQ ?maxQ.
 ?m c:PowerElectronicsConnection.minQ ?minQ.
 ?m c:PowerElectronicsConnection.ratedS ?S.
 ?m c:PowerElectronicsConnection.ratedU ?U.
 ?m c:PowerElectronicsConnection.controlMode ?controlMode.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:PowerElectronicsConnection}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerElectronicsConnection.PowerElectronicsUnit ?unit.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:PowerElectronicsConnection.maxIFault ?flt.
 ?m c:PowerElectronicsConnection.p ?p.
 ?m c:PowerElectronicsConnection.q ?q.
 ?m c:PowerElectronicsConnection.maxQ ?maxQ.
 ?m c:PowerElectronicsConnection.minQ ?minQ.
 ?m c:PowerElectronicsConnection.ratedS ?S.
 ?m c:PowerElectronicsConnection.ratedU ?U.
 ?m c:PowerElectronicsConnection.controlMode ?controlMode.
}}
"""

drop_syn_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:RotatingMachine.p ?p.
 ?m c:RotatingMachine.q ?q.
 ?m c:RotatingMachine.ratedS ?S.
 ?m c:RotatingMachine.ratedU ?U.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:SynchronousMachine}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:Equipment.EquipmentContainer ?fdr.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:RotatingMachine.p ?p.
 ?m c:RotatingMachine.q ?q.
 ?m c:RotatingMachine.ratedS ?S.
 ?m c:RotatingMachine.ratedU ?U.
}}
"""

drop_pep_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerElectronicsConnectionPhase.phase ?phs.
 ?m c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
 ?m c:PowerElectronicsConnectionPhase.p ?p.
 ?m c:PowerElectronicsConnectionPhase.q ?q.
 ?m c:PowerSystemResource.Location ?loc.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:PowerElectronicsConnectionPhase}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerElectronicsConnectionPhase.phase ?phs.
 ?m c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
 ?m c:PowerElectronicsConnectionPhase.p ?p.
 ?m c:PowerElectronicsConnectionPhase.q ?q.
 ?m c:PowerSystemResource.Location ?loc.
}}
"""

drop_pv_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:PowerElectronicsUnit.maxP ?maxP.
 ?m c:PowerElectronicsUnit.minP ?minP.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:PhotovoltaicUnit}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerSystemResource.Location ?loc.
 ?m c:PowerElectronicsUnit.maxP ?maxP.
 ?m c:PowerElectronicsUnit.minP ?minP.
}}
"""

drop_bat_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerElectronicsUnit.maxP ?maxP.
 ?m c:PowerElectronicsUnit.minP ?minP.
 ?m c:BatteryUnit.ratedE ?rated.
 ?m c:BatteryUnit.storedE ?stored.
 ?m c:BatteryUnit.batteryState ?state.
 ?m c:PowerSystemResource.Location ?loc.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:BatteryUnit}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:PowerElectronicsUnit.maxP ?maxP.
 ?m c:PowerElectronicsUnit.minP ?minP.
 ?m c:BatteryUnit.ratedE ?rated.
 ?m c:BatteryUnit.storedE ?stored.
 ?m c:BatteryUnit.batteryState ?state.
 ?m c:PowerSystemResource.Location ?loc.
}}
"""

drop_ieee_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:DynamicsFunctionBlock.enabled ?enabled.
 ?m c:DERIEEEType1.phaseToGroundApplicable ?pg.
 ?m c:DERIEEEType1.phaseToNeutralApplicable ?pn.
 ?m c:DERIEEEType1.phaseToPhaseApplicable ?pp.
 ?m c:DERDynamics.PowerElectronicsConnection ?pec.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:DERIEEEType1}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:DynamicsFunctionBlock.enabled ?enabled.
 ?m c:DERIEEEType1.phaseToGroundApplicable ?pg.
 ?m c:DERIEEEType1.phaseToNeutralApplicable ?pn.
 ?m c:DERIEEEType1.phaseToPhaseApplicable ?pp.
 ?m c:DERDynamics.PowerElectronicsConnection ?pec.
}}
"""

drop_nd_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:DERNameplateData.DERIEEEType1 ?der.
 ?m c:DERNameplateData.normalOPcatKind ?cat.
 ?m c:DERNameplateData.supportsConstPFmode ?pf.
 ?m c:DERNameplateData.supportsConstQmode ?cq.
 ?m c:DERNameplateData.supportsQVmode ?qv.
 ?m c:DERNameplateData.supportsPVmode ?pv.
 ?m c:DERNameplateData.supportsQPmode ?qp.
 ?m c:DERNameplateData.supportsPFmode ?droop.
 ?m c:DERNameplateData.acVmax ?vmax.
 ?m c:DERNameplateData.acVmin ?vmin.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:DERNameplateData}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:DERNameplateData.DERIEEEType1 ?der.
 ?m c:DERNameplateData.normalOPcatKind ?cat.
 ?m c:DERNameplateData.supportsConstPFmode ?pf.
 ?m c:DERNameplateData.supportsConstQmode ?cq.
 ?m c:DERNameplateData.supportsQVmode ?qv.
 ?m c:DERNameplateData.supportsPVmode ?pv.
 ?m c:DERNameplateData.supportsQPmode ?qp.
 ?m c:DERNameplateData.supportsPFmode ?droop.
 ?m c:DERNameplateData.acVmax ?vmax.
 ?m c:DERNameplateData.acVmin ?vmin.
}}
"""

drop_ad_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:DERNameplateDataApplied.DERNameplateData ?nd.
 ?m c:DERNameplateDataApplied.pMax ?pmax.
 ?m c:DERNameplateDataApplied.pMaxOverPF ?pmaxOverPF.
 ?m c:DERNameplateDataApplied.overPF ?overPF.
 ?m c:DERNameplateDataApplied.pMaxUnderPF ?pmaxUnderPF.
 ?m c:DERNameplateDataApplied.underPF ?underPF.
 ?m c:DERNameplateDataApplied.sMax ?sMax.
 ?m c:DERNameplateDataApplied.qMaxInj ?qMaxInj.
 ?m c:DERNameplateDataApplied.qMaxAbs ?qMaxAbs.
 ?m c:DERNameplateDataApplied.pMaxCharge ?pMaxCharge.
 ?m c:DERNameplateDataApplied.apparentPowerChargeMax ?sMaxCharge.
 ?m c:DERNameplateDataApplied.acVnom ?vNom.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:DERNameplateDataApplied}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:DERNameplateDataApplied.DERNameplateData ?nd.
 ?m c:DERNameplateDataApplied.pMax ?pmax.
 ?m c:DERNameplateDataApplied.pMaxOverPF ?pmaxOverPF.
 ?m c:DERNameplateDataApplied.overPF ?overPF.
 ?m c:DERNameplateDataApplied.pMaxUnderPF ?pmaxUnderPF.
 ?m c:DERNameplateDataApplied.underPF ?underPF.
 ?m c:DERNameplateDataApplied.sMax ?sMax.
 ?m c:DERNameplateDataApplied.qMaxInj ?qMaxInj.
 ?m c:DERNameplateDataApplied.qMaxAbs ?qMaxAbs.
 ?m c:DERNameplateDataApplied.pMaxCharge ?pMaxCharge.
 ?m c:DERNameplateDataApplied.apparentPowerChargeMax ?sMaxCharge.
 ?m c:DERNameplateDataApplied.acVnom ?vNom.
}}
"""

drop_pf_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:ConstantPowerFactorSettings.DERIEEEType1 ?der.
 ?m c:ConstantPowerFactorSettings.enabled ?enabled.
 ?m c:ConstantPowerFactorSettings.constantPowerFactorExcitationKind ?kind.
 ?m c:ConstantPowerFactorSettings.powerFactor ?pf.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:ConstantPowerFactorSettings}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:ConstantPowerFactorSettings.DERIEEEType1 ?der.
 ?m c:ConstantPowerFactorSettings.enabled ?enabled.
 ?m c:ConstantPowerFactorSettings.constantPowerFactorExcitationKind ?kind.
 ?m c:ConstantPowerFactorSettings.powerFactor ?pf.
}}
"""

drop_cq_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:ConstantReactivePowerSettings.DERIEEEType1 ?der.
 ?m c:ConstantReactivePowerSettings.enabled ?enabled.
 ?m c:ConstantReactivePowerSettings.reactivePower ?q.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:ConstantReactivePowerSettings}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:ConstantReactivePowerSettings.DERIEEEType1 ?der.
 ?m c:ConstantReactivePowerSettings.enabled ?enabled.
 ?m c:ConstantReactivePowerSettings.reactivePower ?q.
}}
"""

drop_vvar_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:VoltVarSettings.DERIEEEType1 ?der.
 ?m c:VoltVarSettings.enabled ?enabled.
 ?m c:VoltVarSettings.vRefAutoModeEnabled ?vRefEnabled.
 ?m c:VoltVarSettings.vRef ?vRef.
 ?m c:VoltVarSettings.vRefOlrt ?vRefOlrt.
 ?m c:VoltVarSettings.curveV1 ?V1.
 ?m c:VoltVarSettings.curveV2 ?V2.
 ?m c:VoltVarSettings.curveV3 ?V3.
 ?m c:VoltVarSettings.curveV4 ?V4.
 ?m c:VoltVarSettings.curveQ1 ?Q1.
 ?m c:VoltVarSettings.curveQ2 ?Q2.
 ?m c:VoltVarSettings.curveQ3 ?Q3.
 ?m c:VoltVarSettings.curveQ4 ?Q4.
 ?m c:VoltVarSettings.olrt ?olrt.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:VoltVarSettings}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:VoltVarSettings.DERIEEEType1 ?der.
 ?m c:VoltVarSettings.enabled ?enabled.
 ?m c:VoltVarSettings.vRefAutoModeEnabled ?vRefEnabled.
 ?m c:VoltVarSettings.vRef ?vRef.
 ?m c:VoltVarSettings.vRefOlrt ?vRefOlrt.
 ?m c:VoltVarSettings.curveV1 ?V1.
 ?m c:VoltVarSettings.curveV2 ?V2.
 ?m c:VoltVarSettings.curveV3 ?V3.
 ?m c:VoltVarSettings.curveV4 ?V4.
 ?m c:VoltVarSettings.curveQ1 ?Q1.
 ?m c:VoltVarSettings.curveQ2 ?Q2.
 ?m c:VoltVarSettings.curveQ3 ?Q3.
 ?m c:VoltVarSettings.curveQ4 ?Q4.
 ?m c:VoltVarSettings.olrt ?olrt.
}}
"""

drop_vwatt_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:VoltWattSettings.DERIEEEType1 ?der.
 ?m c:VoltWattSettings.enabled ?enabled.
 ?m c:VoltWattSettings.curveV1 ?V1.
 ?m c:VoltWattSettings.curveV2 ?V2.
 ?m c:VoltWattSettings.curveP1 ?P1.
 ?m c:VoltWattSettings.curveP2gen ?P2gen.
 ?m c:VoltWattSettings.curveP2load ?P2load.
 ?m c:VoltWattSettings.olrt ?olrt.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:VoltWattSettings}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:VoltWattSettings.DERIEEEType1 ?der.
 ?m c:VoltWattSettings.enabled ?enabled.
 ?m c:VoltWattSettings.curveV1 ?V1.
 ?m c:VoltWattSettings.curveV2 ?V2.
 ?m c:VoltWattSettings.curveP1 ?P1.
 ?m c:VoltWattSettings.curveP2gen ?P2gen.
 ?m c:VoltWattSettings.curveP2load ?P2load.
 ?m c:VoltWattSettings.olrt ?olrt.
}}
"""

drop_wattvar_template = """DELETE {{
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:WattVarSettings.DERIEEEType1 ?der.
 ?m c:WattVarSettings.enabled ?enabled.
 ?m c:WattVarSettings.curveP1gen ?P1gen.
 ?m c:WattVarSettings.curveP2gen ?P2gen.
 ?m c:WattVarSettings.curveP3gen ?P3gen.
 ?m c:WattVarSettings.curveQ1gen ?Q1gen.
 ?m c:WattVarSettings.curveQ2gen ?Q2gen.
 ?m c:WattVarSettings.curveQ3gen ?Q3gen.
 ?m c:WattVarSettings.curveP1load ?P1load.
 ?m c:WattVarSettings.curveP2load ?P2load.
 ?m c:WattVarSettings.curveP3load ?P3load.
 ?m c:WattVarSettings.curveQ1load ?Q1load.
 ?m c:WattVarSettings.curveQ2load ?Q2load.
 ?m c:WattVarSettings.curveQ3load ?Q3load.
}} WHERE {{
 VALUES ?uuid {{\"{res}\"}}
 VALUES ?class {{c:WattVarSettings}}
 ?m a ?class.
 ?m c:IdentifiedObject.mRID ?uuid.
 ?m c:IdentifiedObject.name ?name.
 ?m c:WattVarSettings.DERIEEEType1 ?der.
 ?m c:WattVarSettings.enabled ?enabled.
 ?m c:WattVarSettings.curveP1gen ?P1gen.
 ?m c:WattVarSettings.curveP2gen ?P2gen.
 ?m c:WattVarSettings.curveP3gen ?P3gen.
 ?m c:WattVarSettings.curveQ1gen ?Q1gen.
 ?m c:WattVarSettings.curveQ2gen ?Q2gen.
 ?m c:WattVarSettings.curveQ3gen ?Q3gen.
 ?m c:WattVarSettings.curveP1load ?P1load.
 ?m c:WattVarSettings.curveP2load ?P2load.
 ?m c:WattVarSettings.curveP3load ?P3load.
 ?m c:WattVarSettings.curveQ1load ?Q1load.
 ?m c:WattVarSettings.curveQ2load ?Q2load.
 ?m c:WattVarSettings.curveQ3load ?Q3load.
}}
"""

def drop_der (uuid_fname, cfg_file=None):
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'

  fp = open (uuid_fname, 'r')
  for ln in fp.readlines():
    toks = re.split('[,\s]+', ln)
    if len(toks) > 2 and not toks[0].startswith('//'):
      cls = toks[0]
      nm = toks[1]
      mRID = toks[2]
    qstr = None
    if cls == 'PowerElectronicsConnection':
      qstr = CIMHubConfig.prefix + drop_pec_template.format(res=mRID)
    elif cls == 'PowerElectronicsConnectionPhase':
      qstr = CIMHubConfig.prefix + drop_pep_template.format(res=mRID)
    elif cls == 'VoltWattSettings':
      qstr = CIMHubConfig.prefix + drop_vwatt_template.format(res=mRID)
    elif cls == 'VoltVarSettings':
      qstr = CIMHubConfig.prefix + drop_vvar_template.format(res=mRID)
    elif cls == 'WattVarSettings':
      qstr = CIMHubConfig.prefix + drop_wattvar_template.format(res=mRID)
    elif cls == 'ConstantReactivePowerSettings':
      qstr = CIMHubConfig.prefix + drop_cq_template.format(res=mRID)
    elif cls == 'ConstantPowerFactorSettings':
      qstr = CIMHubConfig.prefix + drop_pf_template.format(res=mRID)
    elif cls == 'DERIEEEType1':
      qstr = CIMHubConfig.prefix + drop_ieee_template.format(res=mRID)
    elif cls == 'DERNameplateData':
      qstr = CIMHubConfig.prefix + drop_nd_template.format(res=mRID)
    elif cls == 'DERNameplateDataApplied':
      qstr = CIMHubConfig.prefix + drop_ad_template.format(res=mRID)
    elif cls == 'Terminal':
      qstr = CIMHubConfig.prefix + drop_trm_template.format(res=mRID)
    elif cls == 'Location':
      qstr = CIMHubConfig.prefix + drop_pt_template.format(res=mRID)
      sparql.setQuery(qstr)
      ret = sparql.query()
      print('deleting', cls+'(PositionPoint)', nm, ret.response.msg)
      qstr = CIMHubConfig.prefix + drop_loc_template.format(res=mRID)
    elif cls == 'PhotovoltaicUnit':
      qstr = CIMHubConfig.prefix + drop_pv_template.format(res=mRID)
    elif cls == 'BatteryUnit':
      qstr = CIMHubConfig.prefix + drop_bat_template.format(res=mRID)
    elif cls == 'SynchronousMachine':
      qstr = CIMHubConfig.prefix + drop_syn_template.format(res=mRID)
    elif cls == 'SynchronousMachinePhase':
      print ('*** ERROR: do not know how to drop SynchronousMachinePhase')
      print ('          (only 3-phase machines are currently supported)')
      exit()
    else:
      print ('*** ERROR: do not know how to drop', cls, '(continuing).')

    if qstr is not None:
  #    print (qstr)
      sparql.setQuery(qstr)
      ret = sparql.query()
      print('deleting', cls, nm, ret.response.msg)
  fp.close()

# run from command line for GridAPPS-D platform circuits
if __name__ == '__main__':
  cfg_file = sys.argv[1]
  uuid_fname = sys.argv[2]
  drop_der (uuid_fname, cfg_file)

