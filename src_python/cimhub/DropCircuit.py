from SPARQLWrapper import SPARQLWrapper2
import re
import uuid
import os.path
import cimhub.CIMHubConfig as CIMHubConfig

prefix = ''
sparql = None

feeder_template = """delete {{?s ?attr ?val}} where {{
  values ?fdrid {{\"{fdrid}\"}}
  ?s a c:Feeder.
  ?s c:IdentifiedObject.mRID ?fdrid.
  ?s ?attr ?val.
}}
"""

direct_template = """delete {{?s ?attr ?val}} where {{
  values ?fdrid {{\"{fdrid}\"}}
  ?fdr c:IdentifiedObject.mRID ?fdrid.
  ?s c:{target} ?fdr.
  ?s ?attr ?val.
}}
"""

no_parent_template = """delete {{?s ?attr ?val}} where {{
  ?s c:{target} ?targ.
  ?s ?attr ?val.
  FILTER NOT EXISTS {{?targ c:IdentifiedObject.mRID ?id}}
}}
"""

not_used_template = """delete {{?s ?attr ?val}} where {{
  ?s a c:{cls}.
  ?s ?attr ?val.
  FILTER NOT EXISTS {{?ref c:{usage} ?s}}
}}
"""

remove_base_voltage = """delete {?s ?attr ?val} where {
  ?s a c:BaseVoltage.
  ?s ?attr ?val.
  FILTER (NOT EXISTS {?end c:TransformerEnd.BaseVoltage ?s} && NOT EXISTS {?eq c:ConductingEquipment.BaseVoltage ?s})
}
"""

remove_oplimit_set = """delete {?s ?attr ?val} where {
  ?s a c:OperationalLimitSet.
  ?s ?attr ?val.
  FILTER (NOT EXISTS {?end c:ACDCTerminal.OperationalLimitSet ?s} && NOT EXISTS {?eq c:ConnectivityNode.OperationalLimitSet ?s})
}
"""

remove_oplimit_type = """delete {?s ?attr ?val} where {
  ?s a c:OperationalLimitType.
  ?s ?attr ?val.
  FILTER NOT EXISTS {?targ c:OperationalLimit.OperationalLimitType ?s}
}
"""

# Step 1 AssetInfo cleanup - remove the dangling Asset associations to PSR
remove_asset_links = """delete {?s ?attr ?psr} where {
  ?s a c:Asset.
  ?s c:Asset.PowerSystemResources ?psr.
  ?s ?attr ?psr.
  FILTER NOT EXISTS {?psr c:IdentifiedObject.mRID ?id}
}
"""

# Step 2 AssetInfo cleanup - remove Asset objects that don't have any PSR links
remove_asset_objects = """delete {?s ?attr ?val} where {
  ?s a c:Asset.
  ?s ?attr ?val.
  FILTER NOT EXISTS {?s c:Asset.PowerSystemResources ?psr}
}
"""
# step 3 AssetInfo descendants that are targets of Asset.AssetInfo
asset_leaf_template = """delete {{?s ?attr ?val}} where {{
  ?s a c:{cls}.
  ?s ?attr ?val.
  FILTER NOT EXISTS {{?asset c:Asset.AssetInfo ?s}}
}}
"""

def print_count (lbl, resp):
  cnt = 0
  cnt_str = resp.decode().partition ('mutationCount=')[2]
  if len(cnt_str) > 0:
    cnt = int (cnt_str.partition('<')[0])
  print ('{:8d} {:s} tuples deleted'.format (cnt, lbl))

def run_query (lbl, qstr):
#  print (qstr)
  sparql.setQuery (prefix + qstr)
  ret = sparql.query()
  print_count (lbl, ret.response.read())

def drop_circuit (mRID, cfg_file=None):
  cim_ns = ''
  blz_url = ''
  global sparql, prefix

  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2 (CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'
  prefix = CIMHubConfig.prefix

  # in general, the order of these deletion queries will matter

  # remove the Feeder and objects that reference it directly
  run_query ('ConductingEquipment', direct_template.format(target='Equipment.EquipmentContainer', fdrid=mRID))
  run_query ('ConnectivityNode', direct_template.format(target='ConnectivityNode.ConnectivityNodeContainer', fdrid=mRID))
  run_query ('Feeder', feeder_template.format(fdrid=mRID))

  run_query ('SwitchPhase', no_parent_template.format(target='SwitchPhase.Switch'))
  run_query ('ACLineSegmentPhase', no_parent_template.format(target='ACLineSegmentPhase.ACLineSegment'))
  run_query ('EnergyConsumerPhase', no_parent_template.format(target='EnergyConsumerPhase.EnergyConsumer'))
  run_query ('ShuntCompensatorPhase', no_parent_template.format(target='ShuntCompensatorPhase.ShuntCompensator'))
  run_query ('PowerElectronicsConnectionPhase', no_parent_template.format(target='PowerElectronicsConnectionPhase.PowerElectronicsConnection'))

  run_query ('BatteryUnit', not_used_template.format(cls='BatteryUnit', usage='PowerElectronicsConnection.PowerElectronicsUnit'))
  run_query ('PhotovoltaicUnit', not_used_template.format(cls='PhotovoltaicUnit', usage='PowerElectronicsConnection.PowerElectronicsUnit'))
  run_query ('LoadResponseCharacteristic', not_used_template.format(cls='LoadResponseCharacteristic', usage='EnergyConsumer.LoadResponse'))
  run_query ('PerLengthSequenceImpedance', not_used_template.format(cls='PerLengthSequenceImpedance', usage='ACLineSegment.PerLengthImpedance'))
  run_query ('PerLengthPhaseImpedance', not_used_template.format(cls='PerLengthPhaseImpedance', usage='ACLineSegment.PerLengthImpedance'))
  run_query ('PhaseImpedanceData', no_parent_template.format(target='PhaseImpedanceData.PhaseImpedance'))
  run_query ('PowerTransformerEnd', no_parent_template.format(target='PowerTransformerEnd.PowerTransformer'))
  run_query ('TransformerTankEnd', no_parent_template.format(target='TransformerTankEnd.TransformerTank'))
  run_query ('RatioTapChanger', no_parent_template.format(target='RatioTapChanger.TransformerEnd'))
  run_query ('RegulatingControl', no_parent_template.format(target='RegulatingControl.RegulatingCondEq'))
  run_query ('TransformerMeshImpedance', no_parent_template.format(target='TransformerMeshImpedance.FromTransformerEnd'))
  run_query ('TransformerCoreAdmittance', no_parent_template.format(target='TransformerCoreAdmittance.TransformerEnd'))
  run_query ('TapChangerControl', not_used_template.format(cls='TapChangerControl', usage='TapChanger.TapChangerControl'))
  run_query ('Substation', not_used_template.format(cls='Substation', usage='Feeder.NormalEnergizingSubstation'))
  run_query ('SubGeographicalRegion', not_used_template.format(cls='SubGeographicalRegion', usage='Substation.Region'))
  run_query ('GeographicalRegion', not_used_template.format(cls='GeographicalRegion', usage='SubGeographicalRegion.Region'))
  run_query ('TopologicalNode', not_used_template.format(cls='TopologicalNode', usage='ConnectivityNode.TopologicalNode'))
  run_query ('TopologicalIsland', not_used_template.format(cls='TopologicalIsland', usage='TopologicalNode.TopologicalIsland'))

  run_query ('Terminal', no_parent_template.format(target='Terminal.ConductingEquipment'))
  run_query ('Location', not_used_template.format(cls='Location', usage='PowerSystemResource.Location'))
  run_query ('PositionPoint', no_parent_template.format(target='PositionPoint.Location'))
  run_query ('CoordinateSystem', not_used_template.format(cls='CoordinateSystem', usage='Location.CoordinateSystem'))

  run_query ('BaseVoltage', remove_base_voltage)
  run_query ('OperationalLimitSet', remove_oplimit_set)
  run_query ('VoltageLimit and CurrentLimit', no_parent_template.format(target='OperationalLimit.OperationalLimitSet'))
  run_query ('OperationalLimitType', remove_oplimit_type)

  # flush unused catalog entries linked via Asset
#  run_query ('Asset=>PSR', remove_asset_links)
#  run_query ('Asset', remove_asset_objects)
#  run_query ('TapChangerInfo', asset_leaf_template.format(cls='TapChangerInfo'))
#  run_query ('TransformerTankInfo', asset_leaf_template.format(cls='TransformerTankInfo'))
#  run_query ('PowerTransformerInfo', not_used_template.format(cls='PowerTransformerInfo', usage='TransformerTankInfo.PowerTransformerInfo'))
#  run_query ('TransformerEndInfo', no_parent_template.format(target='TransformerEndInfo.TransformerTankInfo'))
#  run_query ('NoLoadTest', no_parent_template.format(target='NoLoadTest.EnergisedEnd'))
#  run_query ('ShortCircuitTest', no_parent_template.format(target='ShortCircuitTest.EnergisedEnd'))

  # TransformerTankInfo, then cascade to TransformerTankEndInfo, NoLoadTest, ShortCircuitTest
  run_query ('TransformerTankInfo', not_used_template.format(cls='TransformerTankInfo', usage='TransformerTank.TransformerTankInfo'))
  run_query ('TransformerEndInfo', no_parent_template.format(target='TransformerEndInfo.TransformerTankInfo'))
  run_query ('NoLoadTest', no_parent_template.format(target='NoLoadTest.EnergisedEnd'))
  run_query ('ShortCircuitTest', no_parent_template.format(target='ShortCircuitTest.EnergisedEnd'))

  # ACLineSegment => WireSpacingInfo and then cascade to WirePosition.WireSpacingInfo
  run_query ('WireSpacingInfo', not_used_template.format(cls='WireSpacingInfo', usage='ACLineSegment.WireSpacingInfo'))
  run_query ('WirePosition', no_parent_template.format(target='WirePosition.WireSpacingInfo'))
  # ACLineSegmentPhase => WireInfo
  run_query ('ConcentricNeutralCableInfo', not_used_template.format(cls='ConcentricNeutralCableInfo', usage='ACLineSegmentPhase.WireInfo'))
  run_query ('TapeShieldCableInfo', not_used_template.format(cls='TapeShieldCableInfo', usage='ACLineSegmentPhase.WireInfo'))
  run_query ('OverheadWireInfo', not_used_template.format(cls='OverheadWireInfo', usage='ACLineSegmentPhase.WireInfo'))

  # IEEE1547 controllers
  run_query ('DERIEEIType1', not_used_template.format(cls='DERIEEEType1', usage='DERDynamics.PowerElectronicsConnection'))
  run_query ('DERNameplateData', not_used_template.format(cls='DERNameplateData', usage='DERNameplateData.DERIEEEType1'))
  run_query ('DERNameplateDataApplied', not_used_template.format(cls='DERNameplateDataApplied', usage='DERNameplateDataApplied.DERNameplateData'))
  run_query ('WattVarSettings', not_used_template.format(cls='WattVarSettings', usage='WattVarSettings.DERIEEEType1'))
  run_query ('VoltVarSettings', not_used_template.format(cls='VoltVarSettings', usage='VoltVarSettings.DERIEEEType1'))
  run_query ('VoltWattSettings', not_used_template.format(cls='VoltWattSettings', usage='VoltWattSettings.DERIEEEType1'))
  run_query ('ConstantPowerFactorSettings', not_used_template.format(cls='ConstantPowerFactorSettings', usage='ConstantPowerFactorSettings.DERIEEEType1'))
  run_query ('ConstantReactivePowerSettings', not_used_template.format(cls='ConstantReactivePowerSettings', usage='ConstantReactivePowerSettings.DERIEEEType1'))

  # measurements and houses
  run_query ('Measurement', no_parent_template.format(target='Measurement.PowerSystemResource'))
  run_query ('House', no_parent_template.format(target='House.EnergyConsumer'))

