# Copyright (C) 2022-2023 Battelle Memorial Institute
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  10 13:34:29 2023

@author: wang109
"""
# translates raw XML (PSLF/PSSE) to CIM XML
#
# using Python 3 XML module as documented at:
#   https://docs.python.org/3/library/xml.etree.elementtree.html
# CIMHub uses lxml:
#   from lxml import etree
#   from lxml.etree import Element, ElementTree, QName

import uuid
import os
import re
import numpy as np
import pandas as pd
from lxml import etree as et
import scipy.constants
import math
import sys

RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
CIM_NS = 'http://iec.ch/TC57/CIM100#'

BASE_MVA = 100.0
OMEGA = 377.0
# a branch could be overhead or underground line, series capacitor, or possibly switching device
#  TODO: how to identify a series reactor from the attributes?
OHD_BRANCH = 'ohd'
UG_BRANCH = 'ug'
SWT_BRANCH = 'swt'
CAP_BRANCH = 'cap'
RCT_BRANCH = 'rct'
UNK_BRANCH = 'unk'

#%%
def GetCIMID(cls, nm, uuids, identify=False):
    if nm is not None:
        key = cls + ':' + nm
        if key not in uuids:
            uuids[key] = str(uuid.uuid4()).upper()
        elif identify:
            print('Found existing ID for ', key)
        return uuids[key]
    return str(uuid.uuid4()).upper() # for unidentified CIM instances

def GetBaseVoltageID(bus, Buses, VoltageLevels):
    return VoltageLevels[Buses[bus]['VoltageLevel']]['mRID']

def GetBaseVoltageKV(bus, Buses, VoltageLevels):
    return VoltageLevels[Buses[bus]['VoltageLevel']]['kV']

#%%
preamble_template = """<?xml version="1.0" encoding="utf-8"?>
<!-- un-comment this line to enable validation
-->
<rdf:RDF xmlns:cim="{CIM_NS}" xmlns:rdf="{RDF_NS}">
<!--
-->
"""

# CIM has a hierarchy of containers for Line, Plant, VoltageLevel (in a substation), etc. 
# We may not need any of this for EMT, so for now, creating an abstract instance as placeholder
container_template = """<cim:ConnectivityNodeContainer rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:IdentifiedObject.description>{desc}</cim:IdentifiedObject.description>
</cim:ConnectivityNodeContainer>
"""

basevoltage_template = """<cim:BaseVoltage rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:BaseVoltage.nominalVoltage>{volts}</cim:BaseVoltage.nominalVoltage>
</cim:BaseVoltage>
"""

# Not using TopologicalNode or OperationalLimitSet attributes.
# The original bus numbers were unique, so use those as name,
#   put the text name and kv into an optional description attribute
bus_template = """<cim:ConnectivityNode rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:IdentifiedObject.description>{desc}</cim:IdentifiedObject.description>
    <cim:ConnectivityNode.ConnectivityNodeContainer rdf:resource="urn:uuid:{contID}"/>
</cim:ConnectivityNode>
"""

# The CIM terminal splices ConnectivityNode to ConductingEquipment.
term_template = """<cim:Terminal rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Terminal.ConductingEquipment rdf:resource="urn:uuid:{eqRef}"/>
    <cim:ACDCTerminal.sequenceNumber>{seq}</cim:ACDCTerminal.sequenceNumber>
    <cim:Terminal.ConnectivityNode rdf:resource="urn:uuid:{cnRef}"/>
</cim:Terminal>
"""

def WriteCIMTerminals(fp, eqID, buses, uuids):
    seq = 1
    for bus in buses:
        cnID = GetCIMID('ConnectivityNode', str(bus), uuids)
        trmName = '{:s}_T{:d}'.format(eqID, seq) # use eqID in the name to ensure uniqueness of these names created on-the-fly
        trmID = GetCIMID('Terminal', trmName, uuids)
        fp.write (term_template.format(mRID=trmID, name=trmName, eqRef=eqID, cnRef=cnID, seq=seq))
        seq += 1

# CIM balanced, transposed line segment 
acline_template = """<cim:ACLineSegment rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Equipment.EquipmentContainer rdf:resource="urn:uuid:{contID}"/>
    <cim:ConductingEquipment.BaseVoltage rdf:resource="urn:uuid:{bvID}"/>
    <cim:Conductor.length>{length}</cim:Conductor.length>
    <cim:ACLineSegment.r>{r}</cim:ACLineSegment.r>
    <cim:ACLineSegment.r0>{r0}</cim:ACLineSegment.r0>
    <cim:ACLineSegment.x>{x}</cim:ACLineSegment.x>
    <cim:ACLineSegment.x0>{x0}</cim:ACLineSegment.x0>
    <cim:ACLineSegment.bch>{bch}</cim:ACLineSegment.bch>
    <cim:ACLineSegment.bch0>{bch0}</cim:ACLineSegment.bch0>
</cim:ACLineSegment>
"""

# CIM balanced series capacitor (x<0) or reactor (x>0)
seriescap_template = """<cim:SeriesCompensator rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Equipment.EquipmentContainer rdf:resource="urn:uuid:{contID}"/>
    <cim:ConductingEquipment.BaseVoltage rdf:resource="urn:uuid:{bvID}"/>
    <cim:SeriesCompensator.r>{r}</cim:SeriesCompensator.r>
    <cim:SeriesCompensator.r0>{r0}</cim:SeriesCompensator.r0>
    <cim:SeriesCompensator.x>{x}</cim:SeriesCompensator.x>
    <cim:SeriesCompensator.x0>{x0}</cim:SeriesCompensator.x0>
</cim:SeriesCompensator>
"""

load_template="""<cim:EnergyConsumer rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Equipment.EquipmentContainer rdf:resource="urn:uuid:{contID}"/>
    <cim:ConductingEquipment.BaseVoltage rdf:resource="urn:uuid:{bvID}"/>
    <cim:EnergyConsumer.LoadResponse rdf:resource="urn:uuid:{lrID}"/>
    <cim:EnergyConsumer.p>{p}</cim:EnergyConsumer.p>
    <cim:EnergyConsumer.q>{q}</cim:EnergyConsumer.q>
</cim:EnergyConsumer>
"""

zip_template="""<cim:LoadResponseCharacteristic rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:LoadResponseCharacteristic.exponentModel>false</cim:LoadResponseCharacteristic.exponentModel>
    <cim:LoadResponseCharacteristic.pConstantImpedance>{Zp}</cim:LoadResponseCharacteristic.pConstantImpedance>
    <cim:LoadResponseCharacteristic.pConstantCurrent>{Ip}</cim:LoadResponseCharacteristic.pConstantCurrent>
    <cim:LoadResponseCharacteristic.pConstantPower>{Pp}</cim:LoadResponseCharacteristic.pConstantPower>
    <cim:LoadResponseCharacteristic.qConstantImpedance>{Zq}</cim:LoadResponseCharacteristic.qConstantImpedance>
    <cim:LoadResponseCharacteristic.qConstantCurrent>{Iq}</cim:LoadResponseCharacteristic.qConstantCurrent>
    <cim:LoadResponseCharacteristic.qConstantPower>{Pq}</cim:LoadResponseCharacteristic.qConstantPower>
    <cim:LoadResponseCharacteristic.pVoltageExponent>0</cim:LoadResponseCharacteristic.pVoltageExponent>
    <cim:LoadResponseCharacteristic.qVoltageExponent>0</cim:LoadResponseCharacteristic.qVoltageExponent>
    <cim:LoadResponseCharacteristic.pFrequencyExponent>0</cim:LoadResponseCharacteristic.pFrequencyExponent>
    <cim:LoadResponseCharacteristic.qFrequencyExponent>0</cim:LoadResponseCharacteristic.qFrequencyExponent>
</cim:LoadResponseCharacteristic>
"""

# for shunt template, get {nomU} from basevoltage kV*1000, {sections} from raw BINIT/B1,
# {bSection} is raw B1 / kv / kv
shunt_template="""<cim:LinearShuntCompensator rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Equipment.EquipmentContainer rdf:resource="urn:uuid:{contID}"/>
    <cim:ConductingEquipment.BaseVoltage rdf:resource="urn:uuid:{bvID}"/>
    <cim:ShuntCompensator.nomU>{nomU}</cim:ShuntCompensator.nomU>
    <cim:LinearShuntCompensator.bPerSection>{bSection}</cim:LinearShuntCompensator.bPerSection>
    <cim:LinearShuntCompensator.gPerSection>{gSection}</cim:LinearShuntCompensator.gPerSection>
    <cim:ShuntCompensator.maximumSections>{N1}</cim:ShuntCompensator.maximumSections>
    <cim:ShuntCompensator.sections>{sections}</cim:ShuntCompensator.sections>
</cim:LinearShuntCompensator>
"""

# p, q, s, u in SI units, generator convention
ibr_template="""<cim:PowerElectronicsConnection rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Equipment.EquipmentContainer rdf:resource="urn:uuid:{contID}"/>
    <cim:PowerElectronicsConnection.PowerElectronicsUnit rdf:resource="urn:uuid:{unitID}"/>
    <cim:PowerElectronicsConnection.maxIFault>{ifltpu}</cim:PowerElectronicsConnection.maxIFault>
    <cim:PowerElectronicsConnection.p>{p}</cim:PowerElectronicsConnection.p>
    <cim:PowerElectronicsConnection.q>{q}</cim:PowerElectronicsConnection.q>
    <cim:PowerElectronicsConnection.ratedS>{ratedS}</cim:PowerElectronicsConnection.ratedS>
    <cim:PowerElectronicsConnection.ratedU>{ratedU}</cim:PowerElectronicsConnection.ratedU>
    <cim:PowerElectronicsConnection.maxQ>{maxQ}</cim:PowerElectronicsConnection.maxQ>
    <cim:PowerElectronicsConnection.minQ>{minQ}</cim:PowerElectronicsConnection.minQ>
</cim:PowerElectronicsConnection>
"""

# These are associated with PowerElectronicsConnection (ibr_template)
# cls can be Photovoltaic or Battery (energy and state-of-charge attributes not available
# minP < 0 for charging
pecunit_template="""<cim:{cls}Unit rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:PowerElectronicsUnit.maxP>{maxP}</cim:PowerElectronicsUnit.maxP>
    <cim:PowerElectronicsUnit.minP>{minP}</cim:PowerElectronicsUnit.minP>
</cim:{cls}Unit>
"""

# TODO: determine {vgrp} from delta, wye, angle data if available in the raw file
xfmr_template="""<cim:PowerTransformer rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Equipment.EquipmentContainer rdf:resource="urn:uuid:{contID}"/>
    <cim:PowerTransformer.vectorGroup>{vgrp}</cim:PowerTransformer.vectorGroup>
</cim:PowerTransformer>
"""

# put one of these on each winding (two or three) for each PowerTransformer
# the endNumber is to be sequential from 1, starting with highest voltage winding
# ratedS in VA, ratedU in V line-to-line, r is the DC winding resistance (from impedance data in raw file?)
# TODO: figure out connectionKind, phaseAngleClock from the vector group
end_template="""<cim:PowerTransformerEnd rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:PowerTransformerEnd.PowerTransformer rdf:resource="urn:uuid:{xfRef}"/>
    <cim:PowerTransformerEnd.ratedS>{ratedS}</cim:PowerTransformerEnd.ratedS>
    <cim:PowerTransformerEnd.ratedU>{ratedU}</cim:PowerTransformerEnd.ratedU>
    <cim:PowerTransformerEnd.r>{r}</cim:PowerTransformerEnd.r>
    <cim:PowerTransformerEnd.connectionKind rdf:resource="http://iec.ch/TC57/CIM100#WindingConnection.{conn}"/>
    <cim:PowerTransformerEnd.phaseAngleClock>{phaseAngleClock}</cim:PowerTransformerEnd.phaseAngleClock>
    <cim:TransformerEnd.grounded>{grounded}</cim:TransformerEnd.grounded>
    <cim:TransformerEnd.endNumber>{end}</cim:TransformerEnd.endNumber>
    <cim:TransformerEnd.Terminal rdf:resource="urn:uuid:{trmRef}"/>
    <cim:TransformerEnd.BaseVoltage rdf:resource="urn:uuid:{bvRef}"/>
</cim:PowerTransformerEnd>
"""

# put this on the lowest voltage PowerTransformerEnd. Meghana to calculate g [mhos] and b[Siemens] from excitation data
core_template="""<cim:TransformerCoreAdmittance rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:TransformerCoreAdmittance.g>{g}</cim:TransformerCoreAdmittance.g>
    <cim:TransformerCoreAdmittance.b>{b}</cim:TransformerCoreAdmittance.b>
    <cim:TransformerCoreAdmittance.TransformerEnd rdf:resource="urn:uuid:{endRef}"/>
</cim:TransformerCoreAdmittance>
"""

# put one of these between each pair of PowerTransformerEnds. Meghana to calculate r and x (ohms) from the impedance data,
#  referred to the highest-voltage winding of the pair involved.  If zero-sequence data not available, set equal to positive sequence
mesh_template="""<cim:TransformerMeshImpedance rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:TransformerMeshImpedance.r>{r}</cim:TransformerMeshImpedance.r>
    <cim:TransformerMeshImpedance.r0>{r0}</cim:TransformerMeshImpedance.r0>
    <cim:TransformerMeshImpedance.x>{x}</cim:TransformerMeshImpedance.x>
    <cim:TransformerMeshImpedance.x0>{x0}</cim:TransformerMeshImpedance.x0>
    <cim:TransformerMeshImpedance.FromTransformerEnd rdf:resource="urn:uuid:{end1ref}"/>
    <cim:TransformerMeshImpedance.ToTransformerEnd rdf:resource="urn:uuid:{end2ref}"/>
</cim:TransformerMeshImpedance>
"""

# according to object "SynchronousMachine" in .eap file
# earthing: boolean; voltageRegulationRange: percent
# contID: query by bus
gen_template="""<cim:SynchronousMachine rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:Equipment.EquipmentContainer rdf:resource="urn:uuid:{contID}"/>
    <cim:RotatingMachine.p>{p}</cim:RotatingMachine.p>
    <cim:RotatingMachine.q>{q}</cim:RotatingMachine.q>
    <cim:RotatingMachine.ratedS>{ratedS}</cim:RotatingMachine.ratedS>
    <cim:RotatingMachine.ratedU>{ratedU}</cim:RotatingMachine.ratedU>
    <cim:RotatingMachine.GeneratingUnit rdf:resource="urn:uuid:{unitID}"/>
    <cim:SynchronousMachine.maxQ>{maxQ}</cim:SynchronousMachine.maxQ>
    <cim:SynchronousMachine.minQ>{minQ}</cim:SynchronousMachine.minQ>
    <cim:SynchronousMachine.satDirectSyncX>{Xd}</cim:SynchronousMachine.satDirectSyncX>
    <cim:SynchronousMachine.satDirectTransX>{Xdp}</cim:SynchronousMachine.satDirectTransX>
    <cim:SynchronousMachine.satDirectSubtransX>{Xdpp}</cim:SynchronousMachine.satDirectSubtransX>
    <cim:SynchronousMachine.Ra>{Ra}</cim:SynchronousMachine.Ra>
    <cim:SynchronousMachine.X0>{X0}</cim:SynchronousMachine.X0>
    <cim:SynchronousMachine.X1>{X1}</cim:SynchronousMachine.X1>
    <cim:SynchronousMachine.Xq>{Xq}</cim:SynchronousMachine.Xq>
    <cim:SynchronousMachine.Xqp>{Xqp}</cim:SynchronousMachine.Xqp>
    <cim:SynchronousMachine.Xqpp>{Xqpp}</cim:SynchronousMachine.Xqpp>
    <cim:SynchronousMachine.Tdop>{Tdop}</cim:SynchronousMachine.Tdop>
    <cim:SynchronousMachine.Tdopp>{Tdopp}</cim:SynchronousMachine.Tdopp>
    <cim:SynchronousMachine.Tqop>{Tqop}</cim:SynchronousMachine.Tqop>
    <cim:SynchronousMachine.Tqopp>{Tqopp}</cim:SynchronousMachine.Tqopp>
</cim:SynchronousMachine>
"""

# according to object "ExcST1A" in .eap file, Table 14
exc_template="""<cim:ExcitationSystem rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:ExcitationSystem.SynchronousMachine rdf:resource="urn:uuid:{syncID}"/>
    <cim:ExcitationSystem.ilr>{ilr}</cim:ExcitationSystem.ilr>
    <cim:ExcitationSystem.ka>{ka}</cim:ExcitationSystem.ka>
    <cim:ExcitationSystem.kc>{kc}</cim:ExcitationSystem.kc>
    <cim:ExcitationSystem.kf>{kf}</cim:ExcitationSystem.kf>
    <cim:ExcitationSystem.klr>{klr}</cim:ExcitationSystem.klr>
    <cim:ExcitationSystem.ta>{ta}</cim:ExcitationSystem.ta>
    <cim:ExcitationSystem.tb>{tb}</cim:ExcitationSystem.tb>
    <cim:ExcitationSystem.tb1>{tb1}</cim:ExcitationSystem.tb1>
    <cim:ExcitationSystem.tc>{tc}</cim:ExcitationSystem.tc>
    <cim:ExcitationSystem.tc1>{tc1}</cim:ExcitationSystem.tc1>
    <cim:ExcitationSystem.tf>{tf}</cim:ExcitationSystem.tf>
    <cim:ExcitationSystem.vamax>{vamax}</cim:ExcitationSystem.vamax>
    <cim:ExcitationSystem.vamin>{vamin}</cim:ExcitationSystem.vamin>
    <cim:ExcitationSystem.vimax>{vimax}</cim:ExcitationSystem.vimax>
    <cim:ExcitationSystem.vimin>{vimin}</cim:ExcitationSystem.vimin>
    <cim:ExcitationSystem.vrmax>{vrmax}</cim:ExcitationSystem.vrmax>
    <cim:ExcitationSystem.vrmin>{vrmin}</cim:ExcitationSystem.vrmin>
</cim:ExcitationSystem>
"""

# according to object "GovHydroIEEE0" in .eap file, Table 15
# for "unknown" or hydro turbine/governor
gov_hydro_template="""<cim:TurbineGovernor rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:TurbineGovernor.SynchronousMachine rdf:resource="urn:uuid:{syncID}"/>
    <cim:TurbineGovernor.k1>{k1}</cim:TurbineGovernor.k1>
    <cim:TurbineGovernor.t1>{t1}</cim:TurbineGovernor.t1>
    <cim:TurbineGovernor.t2>{t2}</cim:TurbineGovernor.t2>
    <cim:TurbineGovernor.t3>{t3}</cim:TurbineGovernor.t3>
    <cim:TurbineGovernor.pmax>{pmax}</cim:TurbineGovernor.pmax>
    <cim:TurbineGovernor.pmin>{pmin}</cim:TurbineGovernor.pmin>
</cim:TurbineGovernor>
"""

# according to object "PSSIEEE1A" in .eap file, Table 16
pss_template="""<cim:PowerSystemStabilizer rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:PowerSystemStabilizer.ExcitationSystem rdf:resource="urn:uuid:{ExciterID}"/>
    <cim:PowerSystemStabilizer.a1>{a1}</cim:PowerSystemStabilizer.a1>
    <cim:PowerSystemStabilizer.a2>{a2}</cim:PowerSystemStabilizer.a2>
    <cim:PowerSystemStabilizer.t1>{t1}</cim:PowerSystemStabilizer.t1>
    <cim:PowerSystemStabilizer.t2>{t2}</cim:PowerSystemStabilizer.t2>
    <cim:PowerSystemStabilizer.t3>{t3}</cim:PowerSystemStabilizer.t3>
    <cim:PowerSystemStabilizer.t4>{t4}</cim:PowerSystemStabilizer.t4>
    <cim:PowerSystemStabilizer.t5>{t5}</cim:PowerSystemStabilizer.t5>
    <cim:PowerSystemStabilizer.t6>{t6}</cim:PowerSystemStabilizer.t6>
    <cim:PowerSystemStabilizer.vstmax>{vstmax}</cim:PowerSystemStabilizer.vstmax>
    <cim:PowerSystemStabilizer.vstmin>{vstmin}</cim:PowerSystemStabilizer.vstmin>
    <cim:PowerSystemStabilizer.ks>{ks}</cim:PowerSystemStabilizer.ks>
</cim:PowerSystemStabilizer>
"""

# These are associated with RotatingMachine descendants (gen_template)
# cls can be HydroGenerating, WindGeneration, NuclearGenerating, ThermalGenerating
# according to object "GeneratorTypeAsset" in .eap file
genunit_template="""<cim:{cls}Unit rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:GeneratingUnit.maxOperatingP>{maxP}</cim:GeneratingUnit.maxOperatingP>
    <cim:GeneratingUnit.minOperatingP>{minP}</cim:GeneratingUnit.minOperatingP>
</cim:{cls}Unit>
"""

# WECC generator-coverter model
regca_template = """<cim:WeccREGCA rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:WeccREGCA.PowerElectronicsConnection rdf:resource="urn:uuid:{PEID}"/>
    <cim:WeccREGCA.mvab>{mvab}</cim:WeccREGCA.mvab>
    <cim:WeccREGCA.brkpt>{brkpt}</cim:WeccREGCA.brkpt>
    <cim:WeccREGCA.iolim>{iolim}</cim:WeccREGCA.iolim>
    <cim:WeccREGCA.iqrmax>{iqrmax}</cim:WeccREGCA.iqrmax>
    <cim:WeccREGCA.iqrmin>{iqrmin}</cim:WeccREGCA.iqrmin>
    <cim:WeccREGCA.ivpl1>{ivpl1}</cim:WeccREGCA.ivpl1>
    <cim:WeccREGCA.ivplsw>{ivplsw}</cim:WeccREGCA.ivplsw>
    <cim:WeccREGCA.ivpnt0>{ivpnt0}</cim:WeccREGCA.ivpnt0>
    <cim:WeccREGCA.ivpnt1>{ivpnt1}</cim:WeccREGCA.ivpnt1>
    <cim:WeccREGCA.khv>{khv}</cim:WeccREGCA.khv>
    <cim:WeccREGCA.rrpwr>{rrpwr}</cim:WeccREGCA.rrpwr>
    <cim:WeccREGCA.tfltr>{tfltr}</cim:WeccREGCA.tfltr>
    <cim:WeccREGCA.tg>{tg}</cim:WeccREGCA.tg>
    <cim:WeccREGCA.volim>{volim}</cim:WeccREGCA.volim>
    <cim:WeccREGCA.zerox>{zerox}</cim:WeccREGCA.zerox>
</cim:WeccREGCA>
"""

# WECC PQ controller and current limit logic
reeca_template = """<cim:WeccREECA rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:WeccREECA.WeccREGCA rdf:resource="urn:uuid:{regcaID}"/>
    <cim:WeccREECA.mvab>{mvab}</cim:WeccREECA.mvab>
    <cim:WeccREECA.db1>{db1}</cim:WeccREECA.db1>
    <cim:WeccREECA.db2>{db2}</cim:WeccREECA.db2>
    <cim:WeccREECA.dPmax>{dPmax}</cim:WeccREECA.dPmax>
    <cim:WeccREECA.dPmin>{dPmin}</cim:WeccREECA.dPmin>
    <cim:WeccREECA.imax>{imax}</cim:WeccREECA.imax>
    <cim:WeccREECA.iqfrz>{iqfrz}</cim:WeccREECA.iqfrz>
    <cim:WeccREECA.iqh1>{iqh1}</cim:WeccREECA.iqh1>
    <cim:WeccREECA.iql1>{iql1}</cim:WeccREECA.iql1>
    <cim:WeccREECA.kqi>{kqi}</cim:WeccREECA.kqi>
    <cim:WeccREECA.kqp>{kqp}</cim:WeccREECA.kqp>
    <cim:WeccREECA.kqv>{kqv}</cim:WeccREECA.kqv>
    <cim:WeccREECA.kvi>{kvi}</cim:WeccREECA.kvi>
    <cim:WeccREECA.kvp>{kvp}</cim:WeccREECA.kvp>
    <cim:WeccREECA.pfFlag>{pfFlag}</cim:WeccREECA.pfFlag>
    <cim:WeccREECA.pFlag>{pFlag}</cim:WeccREECA.pFlag>
    <cim:WeccREECA.pqFlag>{pqFlag}</cim:WeccREECA.pqFlag>
    <cim:WeccREECA.qFlag>{qFlag}</cim:WeccREECA.qFlag>
    <cim:WeccREECA.vFlag>{vFlag}</cim:WeccREECA.vFlag>
    <cim:WeccREECA.pmax>{pmax}</cim:WeccREECA.pmax>
    <cim:WeccREECA.pmin>{pmin}</cim:WeccREECA.pmin>
    <cim:WeccREECA.qmax>{qmax}</cim:WeccREECA.qmax>
    <cim:WeccREECA.qmin>{qmin}</cim:WeccREECA.qmin>
    <cim:WeccREECA.thld>{thld}</cim:WeccREECA.thld>
    <cim:WeccREECA.thld2>{thld2}</cim:WeccREECA.thld2>
    <cim:WeccREECA.tiq>{tiq}</cim:WeccREECA.tiq>
    <cim:WeccREECA.tp>{tp}</cim:WeccREECA.tp>
    <cim:WeccREECA.tpord>{tpord}</cim:WeccREECA.tpord>
    <cim:WeccREECA.trv>{trv}</cim:WeccREECA.trv>
    <cim:WeccREECA.vdi1i1>{vdi1i1}</cim:WeccREECA.vdi1i1>
    <cim:WeccREECA.vdi1i2>{vdi1i2}</cim:WeccREECA.vdi1i2>
    <cim:WeccREECA.vdi1i3>{vdi1i3}</cim:WeccREECA.vdi1i3>
    <cim:WeccREECA.vdi1i4>{vdi1i4}</cim:WeccREECA.vdi1i4>
    <cim:WeccREECA.vdi1v1>{vdi1v1}</cim:WeccREECA.vdi1v1>
    <cim:WeccREECA.vdi1v2>{vdi1v2}</cim:WeccREECA.vdi1v2>
    <cim:WeccREECA.vdi1v3>{vdi1v3}</cim:WeccREECA.vdi1v3>
    <cim:WeccREECA.vdi1v4>{vdi1v4}</cim:WeccREECA.vdi1v4>
    <cim:WeccREECA.vdi2i1>{vdi2i1}</cim:WeccREECA.vdi2i1>
    <cim:WeccREECA.vdi2i2>{vdi2i2}</cim:WeccREECA.vdi2i2>
    <cim:WeccREECA.vdi2i3>{vdi2i3}</cim:WeccREECA.vdi2i3>
    <cim:WeccREECA.vdi2i4>{vdi2i4}</cim:WeccREECA.vdi2i4>
    <cim:WeccREECA.vdi2v1>{vdi2v1}</cim:WeccREECA.vdi2v1>
    <cim:WeccREECA.vdi2v2>{vdi2v2}</cim:WeccREECA.vdi2v2>
    <cim:WeccREECA.vdi2v3>{vdi2v3}</cim:WeccREECA.vdi2v3>
    <cim:WeccREECA.vdi2v4>{vdi2v4}</cim:WeccREECA.vdi2v4>
    <cim:WeccREECA.vdip>{vdip}</cim:WeccREECA.vdip>
    <cim:WeccREECA.vmax>{vmax}</cim:WeccREECA.vmax>
    <cim:WeccREECA.vmin>{vmin}</cim:WeccREECA.vmin>
    <cim:WeccREECA.vref0>{vref0}</cim:WeccREECA.vref0>
    <cim:WeccREECA.vref1>{vref1}</cim:WeccREECA.vref1>
    <cim:WeccREECA.vup>{vup}</cim:WeccREECA.vup>
</cim:WeccREECA>
"""

# WECC plant controller
repca_template = """<cim:WeccREPCA rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:WeccREPCA.WeccREECA rdf:resource="urn:uuid:{reecaID}"/>
    <cim:WeccREPCA.mvab>{mvab}</cim:WeccREPCA.mvab>
    <cim:WeccREPCA.db>{db}</cim:WeccREPCA.db>
    <cim:WeccREPCA.ddn>{ddn}</cim:WeccREPCA.ddn>
    <cim:WeccREPCA.dup>{dup}</cim:WeccREPCA.dup>
    <cim:WeccREPCA.emax>{emax}</cim:WeccREPCA.emax>
    <cim:WeccREPCA.emin>{emin}</cim:WeccREPCA.emin>
    <cim:WeccREPCA.fdbd1>{fdbd1}</cim:WeccREPCA.fdbd1>
    <cim:WeccREPCA.fdbd2>{fdbd2}</cim:WeccREPCA.fdbd2>
    <cim:WeccREPCA.femax>{femax}</cim:WeccREPCA.femax>
    <cim:WeccREPCA.femin>{femin}</cim:WeccREPCA.femin>
    <cim:WeccREPCA.frqFlag>{frqFlag}</cim:WeccREPCA.frqFlag>
    <cim:WeccREPCA.refFlag>{refFlag}</cim:WeccREPCA.refFlag>
    <cim:WeccREPCA.vcmpFlag>{vcmpFlag}</cim:WeccREPCA.vcmpFlag>
    <cim:WeccREPCA.kc>{kc}</cim:WeccREPCA.kc>
    <cim:WeccREPCA.ki>{ki}</cim:WeccREPCA.ki>
    <cim:WeccREPCA.kig>{kig}</cim:WeccREPCA.kig>
    <cim:WeccREPCA.kp>{kp}</cim:WeccREPCA.kp>
    <cim:WeccREPCA.kpg>{kpg}</cim:WeccREPCA.kpg>
    <cim:WeccREPCA.pmax>{pmax}</cim:WeccREPCA.pmax>
    <cim:WeccREPCA.pmin>{pmin}</cim:WeccREPCA.pmin>
    <cim:WeccREPCA.qmax>{qmax}</cim:WeccREPCA.qmax>
    <cim:WeccREPCA.qmin>{qmin}</cim:WeccREPCA.qmin>
    <cim:WeccREPCA.rc>{rc}</cim:WeccREPCA.rc>
    <cim:WeccREPCA.vfrz>{vfrz}</cim:WeccREPCA.vfrz>
    <cim:WeccREPCA.xc>{xc}</cim:WeccREPCA.xc>
    <cim:WeccREPCA.tfltr>{tfltr}</cim:WeccREPCA.tfltr>
    <cim:WeccREPCA.tft>{tft}</cim:WeccREPCA.tft>
    <cim:WeccREPCA.tfv>{tfv}</cim:WeccREPCA.tfv>
    <cim:WeccREPCA.tlag>{tlag}</cim:WeccREPCA.tlag>
    <cim:WeccREPCA.tp>{tp}</cim:WeccREPCA.tp>
</cim:WeccREPCA>
"""

# WECC drive-train model
wtgta_template = """<cim:WeccWTGTA rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:WeccWTGTA.WeccREECA rdf:resource="urn:uuid:{reecaID}"/>
    <cim:WeccWTGTA.mvab>{mvab}</cim:WeccWTGTA.mvab>
    <cim:WeccWTGTA.dshaft>{dshaft}</cim:WeccWTGTA.dshaft>
    <cim:WeccWTGTA.kshaft>{kshaft}</cim:WeccWTGTA.kshaft>
    <cim:WeccWTGTA.hg>{hg}</cim:WeccWTGTA.hg>
    <cim:WeccWTGTA.ht>{ht}</cim:WeccWTGTA.ht>
    <cim:WeccWTGTA.wo>{wo}</cim:WeccWTGTA.wo>
</cim:WeccWTGTA>
"""

# WECC Aero-Dynamic Model
wtgaa_template = """<cim:WeccWTGAA rdf:about="urn:uuid:{mRID}">
    <cim:IdentifiedObject.mRID>{mRID}</cim:IdentifiedObject.mRID>
    <cim:IdentifiedObject.name>{name}</cim:IdentifiedObject.name>
    <cim:WeccWTGAA.WeccWTGTA rdf:resource="urn:uuid:{wtgtaID}"/>
    <cim:WeccWTGAA.mvab>{mvab}</cim:WeccWTGAA.mvab>
    <cim:WeccWTGAA.ka>{ka}</cim:WeccWTGAA.ka>
    <cim:WeccWTGAA.Theta0>{Theta0}</cim:WeccWTGAA.Theta0>
</cim:WeccWTGAA>
"""

#%%
def convertRawtoCIM(workpath, xmlname, addon_fueltype, cimname, fuidname, containername, containerdesc):
    
    fuidname = workpath+fuidname
    xmlname = workpath+xmlname
    cimname = workpath+cimname
    addon_fueltype = workpath+addon_fueltype
    addon_exist = False
    if os.path.exists(addon_fueltype):
        addon_exist = True

    # The general approach is to read raw XML into Python dictionaries,
    #   which may be cross-referenced by key.
    # Then we can write out CIM XML by traversing the dictionaries.
    VoltageLevels = {}
    Buses = {}
    Branches = {}
    Loads = {}
    Transformers = {}
    Shunts = {}
    FixedShunts = {}
    Generators = {}
    
    tree = et.parse(xmlname)
    root = tree.getroot()

    #%% fuel type for generator 
    if addon_exist:
        fueltype = pd.read_excel(addon_fueltype, index_col=None, header=1)
        k_gen = 0
    
    for child in root:
        if child.tag == 'BUSDATA':
            busname = child.find('BusName').text.strip()
            busnum = int(child.find('BusNo').text.strip())
            buskv = float(child.find('NormKV').text.strip())
            # The most convenient key, for lookups, is probably busnum.
            # Buses[busnum] = {'Name':busname, 'kV': buskv}
            vlevel = 'BV_{:.2f}'.format(buskv)
            Buses[busnum] = {'Name':busname, 'kV': buskv, 'VoltageLevel': vlevel}
            if vlevel not in VoltageLevels:
                VoltageLevels[vlevel] = {'kV': buskv}
            # print ('{:5d} {:12s} {:7.3f}'.format(busnum, busname, buskv))
        elif child.tag == 'BRANCHDATA':
            bus1 = int(child.find('I').text.strip())
            bus2 = int(child.find('J').text.strip())
            ckt = int(child.find('CKT').text.strip())
            # stat = int(child.find('STAT').text.strip())
            stat = 1 #TODO: user can load from raw data instead
            r = float(child.find('R').text.strip())
            x = float(child.find('X').text.strip())
            b = float(child.find('B').text.strip())
            # l = float(child.find('LEN').text.strip())
            l = 0.0 #TODO: user can load from raw data instead
            key = '{:d}_{:d}_{:d}'.format(bus1, bus2, ckt)
            Branches[key] = {'bus1': bus1, 'bus2': bus2, 'ckt':ckt, 'r':r, 'x':x, 'b':b, 'len':l, 'stat':stat}
        elif child.tag == 'LOADDATA':
            bus = int(child.find('I').text.strip())
            ckt = int(child.find('ID').text.strip())
            stat = int(child.find('STAT').text.strip())
            key = '{:d}_{:d}'.format(bus, ckt)
            scale = float(child.find('SCALE').text.strip()) # assume scaling of just the ZIP loads
            Pp = float(child.find('PL').text.strip())
            Qp = float(child.find('QL').text.strip())
            Pi = float(child.find('IP').text.strip())
            Qi = float(child.find('IQ').text.strip())
            Pz = float(child.find('YP').text.strip())
            Qz = float(child.find('YQ').text.strip())
            Loads[key] = {'bus':bus, 'ckt': ckt, 'stat': stat, 'Pp': Pp, 'Qp': Qp, 'Pi': Pi, 'Qi': Qi, 'Pz': Pz, 'Qz': Qz, 'scale': scale}
        elif child.tag == 'GENERATORDATA':
            bus = int(child.find('I').text.strip())
            gen_id = child.find('ID').text.strip()
            pg = float(child.find('PG').text.strip())
            qg = float(child.find('QG').text.strip())
            qt = float(child.find('QT').text.strip())
            qb = float(child.find('QB').text.strip())
            vs = float(child.find('VS').text.strip())
            ireg = int(child.find('IREG').text.strip())
            mbase = float(child.find('MBASE').text.strip())
            zr = float(child.find('ZR').text.strip())
            zx = float(child.find('ZX').text.strip())
            rt = float(child.find('RT').text.strip())
            xt = float(child.find('XT').text.strip())
            gtap = float(child.find('GTAP').text.strip())
            stat = int(child.find('STAT').text.strip())
            rmpct = float(child.find('RMPCT').text.strip())
            pt = float(child.find('PT').text.strip())
            pb = float(child.find('PB').text.strip())
            o1 = int(child.find('O1').text.strip())
            f1 = float(child.find('F1').text.strip())
            # classify generators 
            if addon_exist:
                fuel_gen = fueltype.loc[k_gen, 'Fuel Type']
                k_gen += 1
                if fuel_gen == 'SOL (Solar)':
                    ftype = 'Photovoltaic'
                elif fuel_gen == 'WND (Wind)':
                    ftype = 'WindGenerating'
                elif fuel_gen == 'NUC (Nuclear)':
                    ftype = 'NuclearGenerating'
                elif fuel_gen == 'HYD (Hydro)':
                    ftype = 'HydroGenerating'
                else:
                    ftype = 'ThermalGenerating'
            else: 
                ftype = 'ThermalGenerating'
            key = '{:d}_{:s}'.format(bus, gen_id)
            try:
                o2 = int(child.find('O2').text.strip())
                f2 = float(child.find('F2').text.strip())
                o3 = int(child.find('O3').text.strip())
                f3 = float(child.find('F3').text.strip())
                o4 = int(child.find('O4').text.strip())
                f4 = float(child.find('F4').text.strip())
                wmod = int(child.find('WMOD').text.strip())
                wpf = float(child.find('WPF').text.strip())
                # print('Generator: long recording with fuel of ', ftype)
            except:
                o2 = 0
                f2 = 0.0
                o3 = 0
                f3 = 0.0
                o4 = 0
                f4 = 0.0
                wmod = 0
                wpf = 0.0
            Generators[key] = {'bus': bus, 'id': gen_id, 'pg': pg, 'qg': qg, 
                               'qt': qt, 'qb': qb, 'vs': vs, 'ireg': ireg, 
                               'mbase': mbase, 'zr': zr, 'zx': zx,
                               'rt': rt, 'xt': xt, 'gtap': gtap, 'stat': stat, 
                               'rmpct': rmpct, 'pt': pt, 'pb': pb, 'o1': o1, 
                               'f1': f1, 'o2': o2, 'f2': f2, 
                               'o3': o3, 'f3': f3, 'o4': o4, 'f4': f4, 
                               'wmod': wmod, 'wpf': wpf, 'ftype': ftype}
        elif child.tag == 'TRANSFORMERDATA':
            bus1 = int(child.find('I').text.strip())
            bus2 = int(child.find('J').text.strip())
            bus3 = int(child.find('K').text.strip())
            ckt = int(child.find('CKT').text.strip())
            key = '{:d}_{:d}_{:d}_{:d}'.format(bus1, bus2, bus3, ckt)
            cw = int(child.find('CW').text.strip())
            cz = int(child.find('CZ').text.strip())
            cm = int(child.find('CM').text.strip())
            mag1 = float(child.find('MAG1').text.strip())
            mag2 = float(child.find('MAG2').text.strip())
            nmetr = int(child.find('NMETR').text.strip())
            stat = int(child.find('STAT').text.strip())
            o1 = int(child.find('O1').text.strip())
            f1 = float(child.find('F1').text.strip())
            o2 = int(child.find('O2').text.strip())
            f2 = float(child.find('F2').text.strip())
            o3 = int(child.find('O3').text.strip())
            f3 = float(child.find('F3').text.strip())
            o4 = int(child.find('O4').text.strip())
            f4 = float(child.find('F4').text.strip())
            r12 = float(child.find('R12').text.strip())
            x12 = float(child.find('X12').text.strip())
            sbase12 = float(child.find('SBASE12').text.strip())
            windv1 = float(child.find('WINDV1').text.strip())
            windv2 = float(child.find('WINDV2').text.strip())
            nomv1 = float(child.find('NOMV1').text.strip())
            nomv2 = float(child.find('NOMV2').text.strip())
            Transformers[key] = {'bus1':bus1, 'bus2':bus2, 'bus3':bus3, 'ckt':ckt, 
                                 'cw':cw, 'cz':cz, 'cm':cm, 
                                 'mag1':mag1, 'mag2':mag2, 
                                 'nmetr':nmetr, 'stat':stat, 
                                 'o1':o1, 'f1':f1, 'o2':o2, 'f2':f2, 'o3':o3, 'f3':f3, 'o4':o4, 'f4':f4, 
                                 'r1-2':r12, 'x1-2':x12, 'sbase1-2':sbase12,  
                                 'windv1':windv1, 'nomv1':nomv1, 'windv2':windv2, 'nomv2':nomv2}
        elif child.tag == 'SWITCHEDSHUNTDATA':
            bus = int(child.find('I').text.strip())
            modsw = int(child.find('MODSW').text.strip())
            adjm = int(child.find('ADJM').text.strip())
            key = '{:d}_{:d}_{:d}'.format(bus, modsw, adjm)
            st = int(child.find('ST').text.strip())
            vswhi = float(child.find('VSWHI').text.strip())
            vswlo = float(child.find('VSWLO').text.strip())
            swreg = int(child.find('SWREG').text.strip())
            rmpct = float(child.find('RMPCT').text.strip())
            binit = float(child.find('BINIT').text.strip())
            n1 = int(child.find('N1').text.strip())
            b1 = float(child.find('B1').text.strip())
            Shunts[key] = {'bus':bus, 'modsw': modsw, 'adjm': adjm, 'st': st, 'vswhi': vswhi, 'vswlo': vswlo, 
                           'swreg': swreg, 'rmpct': rmpct, 'binit': binit, 'n1': n1, 'b1': b1}
        elif child.tag == "FIXEDSHUNTDATA":
            bus = int(child.find('I').text.strip())
            shunt_id = child.find('ID').text.strip()
            key = '{:d}_{:s}'.format(bus, shunt_id)
            bl = float(child.find('BL').text.strip())
            gl = float(child.find('GL').text.strip())
            FixedShunts[key] = {'bus': bus, 'bl': bl, 'gl': gl}
            
    print ('Found', len(Buses), 'buses,', len(VoltageLevels), 'voltage levels,', len(Branches), 'branches,',
        len (Loads), 'loads,', len(Generators), 'generators,', len(Transformers), 'transformers,', len(Shunts), 'shunts')
    
    #%% convert the line data from pu to SI, make sure the lengths are not zero
    # TODO: handle series reactors and switching devices (if present)
    nOHD = 0
    nUG = 0
    nCAP = 0
    for key, row in Branches.items():
        kvbase = Buses[row['bus1']]['kV']
        zbase = kvbase * kvbase / BASE_MVA
        row['kV'] = kvbase
        row['r'] = row['r'] * zbase
        row['x'] = row['x'] * zbase
        row['b'] = row['b'] * BASE_MVA / kvbase / kvbase
        # infer overhead vs. underground
        row['type'] = UNK_BRANCH
        if row['x'] < 0.0:
            row['type'] = CAP_BRANCH
            row['r0'] = row['r']
            row['x0'] = row['x']
            nCAP += 1
        else:
            inductance = row['x'] / OMEGA
            capacitance = row['b'] / OMEGA
            if capacitance > 0.0:
                zsurge = math.sqrt(inductance/capacitance)
            else:
                zsurge = 400.0
            if zsurge < 100.0:
                row['type'] = UG_BRANCH
                row['r0'] = row['r']
                row['x0'] = row['x']
                row['b0'] = row['b']
                nUG += 1
            else:
                row['type'] = OHD_BRANCH
                row['r0'] = 2.0 * row['r']
                row['x0'] = 2.0 * row['x']
                row['b0'] = 0.6 * row['b']
                nOHD += 1
            if row['len'] <= 0.0:
                if row['type'] == UG_BRANCH: # underground, guess 0.2 ohms/mile
                    row['len'] = scipy.constants.mile * row['x'] / 0.2
                elif kvbase >= 345.0: # bundled overhead, 0.6 ohms/mile
                    row['len'] = scipy.constants.mile * row['x'] / 0.6
                else:
                    row['len'] = scipy.constants.mile * row['x'] / 0.8
        # print ('Line {:s}, {:6.2f} km, {:6.2f} kV, Type={:s}'.format(key, row['len'] * 0.001, row['kV'], row['type']))
    print ('nOHD={:d}, nUG={:d}, nCAP={:d}, nUNK={:d}'.format(nOHD, nUG, nCAP, len(Branches)-nOHD-nUG-nCAP))

    #%% manage a persistent set of mRIDs, indexed by CIMClass:Name
    uuids = {}
    if os.path.exists(fuidname):
        print ('reading instance mRIDs from ', fuidname)
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
    
    #%% write 
    fp = open(cimname, 'w')
    fp.write(preamble_template.format(RDF_NS=RDF_NS, CIM_NS=CIM_NS))
    
    # write container
    contID = GetCIMID('ConnectivityNodeContainer', containername, uuids)
    fp.write(container_template.format(mRID=contID, name=containername, desc=containerdesc))
    
    # write voltage level
    for key, row in VoltageLevels.items():
        mRID = GetCIMID('BaseVoltage', key, uuids)
        VoltageLevels[key]['mRID'] = mRID
        fp.write (basevoltage_template.format(mRID=mRID, name=key, volts=row['kV']*1000.0))

    # write bus
    for key, row in Buses.items():
        name = str(key)
        desc = '{:s}: {:.2f} kV'.format(row['Name'], row['kV'])
        mRID = GetCIMID('ConnectivityNode', name, uuids)
        fp.write (bus_template.format(mRID=mRID, name=name, desc=desc, contID=contID))
        
    # write branch
    for key, row in Branches.items():
        name = str(key)
        if row['stat'] < 1:
            continue
        elif row['type'] == OHD_BRANCH:
            mRID = GetCIMID('ACLineSegment', name, uuids)
            fp.write (acline_template.format(mRID=mRID, name=name, contID=contID, bvID=GetBaseVoltageID(row['bus1'], Buses, VoltageLevels), 
                                            length=row['len'], r=row['r'], x=row['x'], bch=row['b'], r0=row['r0'], 
                                            x0=row['x0'], bch0=row['b0']))
        elif row['type'] == UG_BRANCH:
            mRID = GetCIMID('ACLineSegment', name, uuids)
            fp.write (acline_template.format(mRID=mRID, name=name, contID=contID, bvID=GetBaseVoltageID(row['bus1'], Buses, VoltageLevels), 
                                            length=row['len'], r=row['r'], x=row['x'], bch=row['b'], r0=row['r0'], 
                                            x0=row['x0'], bch0=row['b0']))
        elif row['type'] == CAP_BRANCH:
            mRID = GetCIMID('SeriesCompensator', name, uuids)
            fp.write (seriescap_template.format(mRID=mRID, name=name, contID=contID, bvID=GetBaseVoltageID(row['bus1'], Buses, VoltageLevels), 
                                                r=row['r'], x=row['x'], r0=row['r0'], x0=row['x0']))
        else:
            print ('unrecognized branch {:s} of type {:s}'.format(name, row['type']))
            continue
        WriteCIMTerminals(fp, mRID, [row['bus1'], row['bus2']], uuids)
        
    # write load
    LoadResponseCharacteristics = {}
    for key, row in Loads.items():
        name = str(key)
        if row['stat'] < 1:
            continue
        p = (row['Pp'] + row['Pi'] + row['Pz']) * row['scale'] * 1.0e6 # remember, load P is MW in CIM but W in CIMHub
        q = (row['Qp'] + row['Qi'] + row['Qz']) * row['scale'] * 1.0e6 # remember, load Q is MVAR in CIM but VAR in CIMHub
        # create LoadResponseCharacteristics on the fly for ZIP coefficients
        # choosing the defaults to match WECC 240
        Zp = 0.0
        Ip = 100.0
        Pp = 0.0
        Zq = 100.0
        Iq = 0.0
        Pq = 0.0
        Pmag = abs(row['Pp']) +  abs(row['Pi']) +  abs(row['Pz'])
        if Pmag > 0.0:
            Zp = 100.0 * abs(row['Pz']) / Pmag
            Ip = 100.0 * abs(row['Pi']) / Pmag
            Pp = 100.0 * abs(row['Pp']) / Pmag
        Qmag = abs(row['Qp']) +  abs(row['Qi']) +  abs(row['Qz'])
        if Qmag > 0.0:
            Zq = 100.0 * abs(row['Qz']) / Qmag
            Iq = 100.0 * abs(row['Qi']) / Qmag
            Pq = 100.0 * abs(row['Qp']) / Qmag
        LRkey = 'LoadResp_Zp={:.3f}_Ip={:.3f}_Pp={:.3f}_Zq={:.3f}_Iq={:.3f}_Pq={:.3f}'.format(Zp, Ip, Pp, Zq, Iq, Pq)
        if LRkey not in LoadResponseCharacteristics:
            LoadResponseCharacteristics[LRkey] = {'mRID': GetCIMID('LoadResponseCharacteristic', LRkey, uuids),
                                                'Zp': Zp, 'Ip': Ip, 'Pp': Pp, 'Zq': Zq, 'Iq': Iq, 'Pq': Pq}
        mRID = GetCIMID('EnergyConsumer', name, uuids)
        fp.write (load_template.format(mRID=mRID, name=name, p=p, q=q, bvID=GetBaseVoltageID(row['bus'], Buses, VoltageLevels), 
                                        lrID=LoadResponseCharacteristics[LRkey]['mRID'], contID=contID))
        WriteCIMTerminals(fp, mRID, [row['bus']], uuids)

    print ('created', len(LoadResponseCharacteristics), 'load response characteristics')
    for key, row in LoadResponseCharacteristics.items():
        fp.write (zip_template.format(mRID=row['mRID'], name=key, Zp=row['Zp'], Ip=row['Ip'], Pp=row['Pp'],
                                Zq=row['Zq'], Iq=row['Iq'], Pq=row['Pq']))
    
    # write switched shunt
    for key, row in Shunts.items():
        name = str(key)
        kv = GetBaseVoltageKV(row['bus'], Buses, VoltageLevels)
        nomU = kv*1000
        bSection = row['b1']/kv/kv
        N1 = row['n1']
        sections = row['binit']/row['b1']
        mRID = GetCIMID('LinearShuntCompensator', name, uuids)
        fp.write(shunt_template.format(mRID=mRID, name=name, contID=contID,
                                        bvID=GetBaseVoltageID(row['bus'], Buses, VoltageLevels), 
                                        nomU=nomU, gSection=0, bSection=bSection, 
                                        N1=N1, sections=sections))
        WriteCIMTerminals(fp, mRID, [row['bus']], uuids)
    
    # write fixed shunt
    for key, row in FixedShunts.items():
        name = str(key)
        kv = GetBaseVoltageKV(row['bus'], Buses, VoltageLevels)
        bvID=GetBaseVoltageID(row['bus'], Buses, VoltageLevels)
        nomU = kv*1000
        bSection = row['bl']*1.0e6/nomU/nomU
        gSection = row['gl']*1.0e6/nomU/nomU
        N1 = 1
        sections = 1
        mRID = GetCIMID('LinearShuntCompensator', name, uuids)
        fp.write(shunt_template.format(mRID=mRID, name=name, contID=contID,bvID=bvID, 
                                        nomU=nomU, gSection=gSection, bSection=bSection, 
                                        N1=N1, sections=sections))
        WriteCIMTerminals(fp, mRID, [row['bus']], uuids)
        
    # write transformer; highest-voltage ends and terminals come first, and must match
    for key, row in Transformers.items():
        # xfmr
        xfmr_name = str(key)
        xfmr_mRID = GetCIMID('PowerTransformer', xfmr_name, uuids)
        if row['nomv1'] == 0:
            row['nomv1'] = GetBaseVoltageKV(row['bus1'], Buses, VoltageLevels)
        if row['nomv2'] == 0:
            row['nomv2'] = GetBaseVoltageKV(row['bus2'], Buses, VoltageLevels)
        if row['nomv2'] > row['nomv1']:
            bus_list = [row['bus2'], row['bus1']]
            NomV_list = [row['nomv2'], row['nomv1']]
            print('Swapping buses for transformer {:s} to be: '.format(key), NomV_list, bus_list)
        else:
            bus_list = [row['bus1'], row['bus2']]
            NomV_list = [row['nomv1'], row['nomv2']]
        if min(NomV_list)>20:
            vgrp = 'Yy'
        else:
            vgrp = 'Yd1'
        fp.write(xfmr_template.format(mRID=xfmr_mRID, name=xfmr_name, contID=contID, vgrp=vgrp))
        # terminal x2
        WriteCIMTerminals(fp, xfmr_mRID, bus_list, uuids)
        trmmRID_list = []
        for i in range(2):
            trmName = '{:s}_T{:d}'.format(xfmr_mRID, i+1)
            trmmRID = GetCIMID('Terminal', trmName, uuids, False)
            trmmRID_list.append(trmmRID)
        # end x2
        end_name_list = []
        end_mRID_list = []
        ratedS_list = []
        ratedU_list = []
        zbase_list = []
        r_list = []
        phaseAngleClock_list = []
        conn_list = []
        grounded_list = []
        trmRef_list = []
        bvRef_list = []
        for i in range(2):
            end_name = str(key)+'_End_'+str(i+1)
            end_name_list.append(end_name)
            end_mRID = GetCIMID('PowerTransformerEnd', end_name, uuids)
            end_mRID_list.append(end_mRID)
            ratedS_list.append(row['sbase1-2']*1e6) #[VA]
            ratedU_list.append(NomV_list[i]*1e3) #[V]
            zbase = NomV_list[i]**2/row['sbase1-2']
            zbase_list.append(zbase)
            r_list.append(row['r1-2']/2/zbase)
            if vgrp[i]=='Y' or vgrp[i]=='y':
                conn_list.append('Y')
                grounded_list.append('true')
                phaseAngleClock_list.append(0)
            else:
                conn_list.append('D')
                grounded_list.append('false')
                phaseAngleClock_list.append(1)
            trmRef_list.append(trmmRID_list[i])
            bvRef = GetBaseVoltageID(bus_list[i], Buses, VoltageLevels)
            bvRef_list.append(bvRef)
        for i in range(2):
            fp.write(end_template.format(mRID=end_mRID_list[i], name=end_name_list[i], xfRef=xfmr_mRID, 
                                         ratedS=ratedS_list[i], ratedU=ratedU_list[i], r=r_list[i], conn=conn_list[i],
                                         phaseAngleClock=phaseAngleClock_list[i], grounded=grounded_list[i], 
                                         end=i+1, trmRef=trmRef_list[i], bvRef=bvRef_list[i]))
        # core
        core_name = str(key)+'_Core'
        core_mRID = GetCIMID('TransformerCoreAdmittance', end_name, uuids)
        g = 0
        b = 0
        endRef = end_mRID_list[1]
        fp.write(core_template.format(mRID=core_mRID, name=core_name, g=g, b=b, endRef=endRef))
        # mesh
        mesh_name = str(key)+'_Mesh'
        mesh_mRID = GetCIMID('TransformerMeshImpedance', mesh_name, uuids)
        r_mesh = row['r1-2']*zbase_list[0]
        x_mesh = row['x1-2']*zbase_list[0]
        end1ref = end_mRID_list[0]
        end2ref = end_mRID_list[1]
        fp.write(mesh_template.format(mRID=mesh_mRID, name=mesh_name, r=r_mesh, r0=r_mesh, 
                                      x=x_mesh, x0=x_mesh, end1ref=end1ref, end2ref=end2ref))
    
    # write generator (hydro, nuclear, thermal, wind, solar only)
    sum_ratedS_hydro = 0
    sum_ratedS_wind = 0
    sum_ratedS_solar = 0
    sum_ratedS_nuclear = 0
    sum_ratedS_thermal = 0
    nh = 0
    nw = 0
    ns = 0 
    nn = 0
    nt = 0
    
    for key, row in Generators.items():
        
        if row['ftype'] in ['HydroGenerating', 'ThermalGenerating', 'NuclearGenerating']:
            # mRIDs
            gen_name = str(key)
            gen_mRID = GetCIMID('SynchronousMachine', gen_name, uuids)
            
            genunit_name = str(key)+'_GenUnit'
            genunit_mRID = GetCIMID('GeneratingUnit', genunit_name, uuids)
            
            exc_name = str(key)+'_Exc'
            exc_mRID = GetCIMID('ExcitationSystem', exc_name, uuids)
            
            gov_name = str(key)+'_Gov'
            gov_mRID = GetCIMID('TurbineGovernor', gov_name, uuids)
            
            pss_name = str(key)+'_PSS'
            pss_mRID = GetCIMID('PowerSystemStabilizer', pss_name, uuids)            
            
            # generator
            p = row['pg']*1e6
            q = row['qg']*1e6
            ratedS = row['mbase']*1e6
            kv = GetBaseVoltageKV(row['bus'], Buses, VoltageLevels)
            ratedU = kv*1e3
            maxQ = row['qt']*1e6
            minQ = row['qb']*1e6
            Ra = 0.001
            X1 = 0.096
            X0 = 0.096
            Xd = 1.43
            Xdp = 0.146
            Xdpp = 0.114
            Xq = 1.33
            Xqp = 0.258
            Xqpp = 0.114
            Tdop = 7.563
            Tdopp = 0.017
            Tqop = 1.133
            Tqopp = 0.05
            fp.write(gen_template.format(mRID=gen_mRID, name=gen_name, contID=contID, 
                                         p=p, q=q, ratedS=ratedS, ratedU=ratedU, unitID=genunit_mRID, 
                                         ExciterID=exc_mRID, GovernorID=gov_mRID, PSSIEEE1AID=pss_mRID, 
                                         maxQ=maxQ, minQ=minQ, Xd=Xd, Xdp=Xdp, Xdpp=Xdpp, 
                                         Ra=Ra, X0=X0, X1=X1, Xq=Xq, Xqp=Xqp, Xqpp=Xqpp, 
                                         Tdop=Tdop, Tdopp=Tdopp, Tqop=Tqop, Tqopp=Tqopp))
            
            # generating unit
            genunit_cls = row['ftype']
            genunit_maxP = row['mbase']*1e6
            genunit_minP = 0
            
            # write generating unit
            fp.write(genunit_template.format(mRID=genunit_mRID, name=genunit_name, cls=genunit_cls,
                                             maxP=genunit_maxP, minP=genunit_minP))
            
            # exciter
            ilr = 4.4
            ka = 40
            kc =0.038
            kf = 0
            klr = 4.54
            ta = 0
            tb = 10
            tb1 = 0
            tc = 1
            tc1 = 0
            tf = 1
            vamax = 999
            vamin = -999
            vimax = 0.1
            vimin = -0.1
            vrmax = 4.5
            vrmin = -4
            fp.write(exc_template.format(mRID=exc_mRID, name=exc_name, syncID=gen_mRID,
                                         ilr=ilr, ka=ka, 
                                         kc=kc, kf=kf, klr=klr, ta=ta, tb=tb, tb1=tb1, 
                                         tc=tc, tc1=tc1, tf=tf, vamax=vamax, vamin=vamin, 
                                         vimax=vimax, vimin=vimin, vrmax=vrmax, vrmin=vrmin))
            
            # governor
            gov_k1 = 25
            gov_t1 = 5
            gov_t2 = 5
            gov_t3 = 0.1
            gov_pmax = 0.9
            gov_pmin = 0.05
            fp.write(gov_hydro_template.format(mRID=gov_mRID, name=gov_name, syncID=gen_mRID,
                                               k1=gov_k1, t1=gov_t1, t2=gov_t2, t3=gov_t3, 
                                               pmax=gov_pmax, pmin=gov_pmin))
        
            # ps stabilizer
            pss_a1 = 0
            pss_a2 = 0
            pss_t1 = 1
            pss_t2 = 0.5
            pss_t3 = 2
            pss_t4 = 0.1
            pss_t5 = 10
            pss_t6 = 0
            pss_vstmax = 0.2
            pss_vstmin = -0.2
            pss_ks = 2
            fp.write(pss_template.format(mRID=pss_mRID, name=pss_name, ExciterID=exc_mRID,
                                         a1=pss_a1, a2=pss_a2,
                                         t1=pss_t1, t2=pss_t2, t3=pss_t3, t4=pss_t4, 
                                         t5=pss_t5, t6=pss_t6, vstmax=pss_vstmax, vstmin=pss_vstmin, ks=pss_ks))
            
            # terminal
            WriteCIMTerminals(fp, gen_mRID, [row['bus']], uuids)
            
            if row['ftype'] == 'HydroGenerating':
              sum_ratedS_hydro += ratedS*1e-6
              nh += 1
            if row['ftype'] == 'NuclearGenerating':
              sum_ratedS_nuclear += ratedS*1e-6
              nn += 1
            if row['ftype'] == 'ThermalGenerating':
              sum_ratedS_thermal += ratedS*1e-6
              nt += 1

            
    # write wind turbine generator
    for key, row in Generators.items():
        
        if row['ftype'] == 'WindGenerating':
            # mRIDs
            PEname = str(key)+'_Connection'
            PEID = GetCIMID('PowerElectronicsConnection', PEname, uuids)
            unitname = str(key)+'_Unit'
            unitID = GetCIMID('PowerElectronicsUnit', unitname, uuids)
            repcaname = str(key)+'_REPCA'
            repcaID = GetCIMID('REPCA', repcaname, uuids)
            regcaname = str(key)+'_REGCA'
            regcaID = GetCIMID('REGCA', regcaname, uuids)
            reecaname = str(key)+'_REECA'
            reecaID = GetCIMID('REECA', reecaname, uuids)
            wtgtaname = str(key)+'_WTGTA'
            wtgtaID = GetCIMID('WTGTA', wtgtaname, uuids)
            wtgaaname = str(key)+'_WTGAA'
            wtgaaID = GetCIMID('WTGAA', wtgaaname, uuids)

            # power electronics connection
            ifltpu = 1.00 # TODO: to be determined, max current
            p = row['pg']*1e6
            q = row['qg']*1e6
            ratedS = row['mbase']*1e6
            kv = GetBaseVoltageKV(row['bus'], Buses, VoltageLevels)
            ratedU = kv*1e3
            maxQ = row['qt']*1e6
            minQ = row['qb']*1e6
            fp.write(ibr_template.format(mRID=PEID, name=PEname, 
                                         contID=contID, unitID=unitID, regcaID=regcaID,
                                         ifltpu=ifltpu, p=p, q=q, ratedS=ratedS, ratedU=ratedU,
                                         maxQ=maxQ, minQ=minQ))

            # power electronics unit
            unit_cls = row['ftype']
            unit_maxP = row['mbase']*1e6
            unit_minP = 0
            fp.write(pecunit_template.format(mRID=unitID, name=unitname, cls=unit_cls,
                                             maxP=unit_maxP, minP=unit_minP))

            # REPC_A
            MVAbase = row['mbase']
            fp.write(repca_template.format(mRID=repcaID, name=repcaname, 
                                           reecaID=reecaID, mvab=MVAbase, 
                                           db=0, ddn=20, dup=0, emax=999, emin=-999,
                                           fdbd1=-0.01, fdbd2=0.01, femax=999, femin=-999,
                                           frqFlag=1, refFlag=1, vcmpFlag=1, 
                                           kc=0.02, ki=5.0, kig=0.05, kp=10.0, kpg=0.1,
                                           pmax=1, pmin=0, qmax=0.7, qmin=-0.7, 
                                           rc=0, vfrz=0.35, xc=0,
                                           tfltr=0.02, tft=0.00, tfv=0.08, tlag=0.08, tp=0.03))

            # REGC_A
            fp.write(regca_template.format(mRID=regcaID, name=regcaname, 
                                           PEID=PEID, reecaID=reecaID, 
                                           mvab=MVAbase, brkpt=0.9, iolim=-1.2,
                                           iqrmax=999.9, iqrmin=-999.9, ivpl1=1.2, ivplsw=0, 
                                           ivpnt0=0.4, ivpnt1=0.8, khv=0.7, rrpwr=10, tfltr=0.015, 
                                           tg=0.02, volim=1.2, zerox=0.4))
            
            # REEC_A
            fp.write(reeca_template.format(mRID=reecaID, name=reecaname, 
                                           regcaID=regcaID, repcaID=repcaID, wtgtaID=wtgtaID,
                                           mvab=MVAbase, db1=-0.05, db2=0.05,
                                           dPmax=999, dPmin=-999, imax=1.2, 
                                           iqfrz=0.05, iqh1=1.05, iql1=-1.05,
                                           kqi=0.1, kqp=0.1, kqv=5, kvi=1.0, kvp=5.0, 
                                           pfFlag=0, pFlag=1, pqFlag=0, qFlag=1, vFlag=1,
                                           pmax=1, pmin=0, qmax=0.7, qmin=-0.7, 
                                           thld=0, thld2=0, tiq=0.015, tp=0.05, 
                                           tpord=0.03, trv=0.03, 
                                           vdi1i1=1, vdi1i2=1,vdi1i3=0, vdi1i4=0, 
                                           vdi1v1=-1, vdi1v2=2, vdi1v3=0, vdi1v4=0,
                                           vdi2i1=1, vdi2i2=1, vdi2i3=0, vdi2i4=0,
                                           vdi2v1=-1, vdi2v2=2, vdi2v3=0, vdi2v4=0, vdip=0.87,
                                           vmax=1.07, vmin=0.9, vref0=1, vref1=0, vup=1.15))
            
            # WTGT_A
            MVAbase = row['mbase']
            fp.write(wtgta_template.format(mRID=wtgtaID, name=wtgtaname, reecaID=reecaID, wtgaaID=wtgaaID, 
                                           mvab=MVAbase, ht=4.134, hg=0.62, dshaft=1.5, kshaft=0, wo=1))
            
            # WTGA_RA
            MVAbase = row['mbase']
            fp.write(wtgaa_template.format(mRID=wtgaaID, name=wtgaaname, wtgtaID=wtgtaID, 
                                           mvab=MVAbase, ka=0.01, Theta0=0))
            
            # terminal
            WriteCIMTerminals(fp, PEID, [row['bus']], uuids)
            
            sum_ratedS_wind += ratedS*1e-6
            nw += 1
    
    # write solar (PV plant)
    for key, row in Generators.items():
        
        if row['ftype'] == 'Photovoltaic':
            # mRIDs
            PEname = str(key)+'_Connection'
            PEID = GetCIMID('PowerElectronicsConnection', PEname, uuids)
            unitname = str(key)+'_Unit'
            unitID = GetCIMID('PowerElectronicsUnit', unitname, uuids)
            repcaname = str(key)+'_REPCA'
            repcaID = GetCIMID('REPCA', repcaname, uuids)
            regcaname = str(key)+'_REGCA'
            regcaID = GetCIMID('REGCA', regcaname, uuids)
            reecaname = str(key)+'_REECA'
            reecaID = GetCIMID('REECA', reecaname, uuids)
            wtgtaname = str(key)+'_WTGTA'
            wtgtaID = GetCIMID('WTGTA', wtgtaname, uuids)
            wtgaaname = str(key)+'_WTGAA'
            wtgaaID = GetCIMID('WTGAA', wtgaaname, uuids)

            # power electronics connection
            ifltpu = 0.0 # TODO: to be determined
            p = row['pg']*1e6
            q = row['qg']*1e6
            ratedS = row['mbase']*1e6
            kv = GetBaseVoltageKV(row['bus'], Buses, VoltageLevels)
            ratedU = kv*1e3
            maxQ = row['qt']*1e6
            minQ = row['qb']*1e6
            fp.write(ibr_template.format(mRID=PEID, name=PEname, 
                                         contID=contID, unitID=unitID, regcaID=regcaID,
                                         ifltpu=ifltpu, p=p, q=q, ratedS=ratedS, ratedU=ratedU,
                                         maxQ=maxQ, minQ=minQ))

            # power electronics unit
            unit_cls = row['ftype']
            unit_maxP = row['mbase']*1e6
            unit_minP = 0
            fp.write(pecunit_template.format(mRID=unitID, name=unitname, cls=unit_cls,
                                             maxP=unit_maxP, minP=unit_minP))

            # REPC_A
            MVAbase = row['mbase']
            fp.write(repca_template.format(mRID=repcaID, name=repcaname, 
                                           reecaID=reecaID, mvab=MVAbase, 
                                           db=0, ddn=20, dup=0, emax=999, emin=-999,
                                           fdbd1=-0.01, fdbd2=0.01, femax=999, femin=-999,
                                           frqFlag=1, refFlag=1, vcmpFlag=1, 
                                           kc=0.02, ki=4.3, kig=0.05, kp=10.9, kpg=0.1,
                                           pmax=1, pmin=0, qmax=0.7, qmin=-0.7, 
                                           rc=0, vfrz=0.35, xc=0,
                                           tfltr=0.02, tft=0.00, tfv=0.08, tlag=0.08, tp=0.03))
            
            # REGC_A
            fp.write(regca_template.format(mRID=regcaID, name=regcaname, 
                                           PEID=PEID, reecaID=reecaID, 
                                           mvab=MVAbase, brkpt=0.9, iolim=-1.2,
                                           iqrmax=999.9, iqrmin=-999.9, ivpl1=1.2, ivplsw=0, 
                                           ivpnt0=0.4, ivpnt1=0.8, khv=0.7, rrpwr=10, tfltr=0.015, 
                                           tg=0.02, volim=1.2, zerox=0.4))
            
            # REEC_A
            tmp_name = str(key)+'_REECA'
            tmp_mRID = GetCIMID('REECA', tmp_name, uuids)
            fp.write(reeca_template.format(mRID=reecaID, name=reecaname, 
                                           regcaID=regcaID, repcaID=repcaID, wtgtaID=wtgtaID,
                                           mvab=MVAbase, db1=-0.05, db2=0.05,
                                           dPmax=999, dPmin=-999, imax=1.2, 
                                           iqfrz=0.05, iqh1=1.05, iql1=-1.05,
                                           kqi=0.0, kqp=0.0, kqv=5, kvi=1.2, kvp=4.1, 
                                           pfFlag=0, pFlag=0, pqFlag=0, qFlag=1, vFlag=1,
                                           pmax=1, pmin=0, qmax=0.7, qmin=-0.7, 
                                           thld=0, thld2=0, tiq=0.015, tp=0.05, 
                                           tpord=0.03, trv=0.03, 
                                           vdi1i1=1, vdi1i2=1,vdi1i3=0, vdi1i4=0, 
                                           vdi1v1=-1, vdi1v2=2, vdi1v3=0, vdi1v4=0,
                                           vdi2i1=1, vdi2i2=1, vdi2i3=0, vdi2i4=0,
                                           vdi2v1=-1, vdi2v2=2, vdi2v3=0, vdi2v4=0, vdip=0.87,
                                           vmax=1.07, vmin=0.9, vref0=1, vref1=0, vup=1.15))
            
            # terminal
            WriteCIMTerminals(fp, PEID, [row['bus']], uuids)
            
            sum_ratedS_solar += ratedS*1e-6
            ns += 1
    
    print('Hydro generators:   {:8.1f} MW in {:3d} units'.format(sum_ratedS_hydro, nh))
    print('Nuclear generators: {:8.1f} MW in {:3d} units'.format(sum_ratedS_nuclear, nn))
    print('Thermal generators: {:8.1f} MW in {:3d} units'.format(sum_ratedS_thermal, nt))
    print('Wind generators:    {:8.1f} MW in {:3d} units'.format(sum_ratedS_wind, nw))
    print('Solar generators:   {:8.1f} MW in {:3d} units'.format(sum_ratedS_solar, ns))
    
    fp.write('</rdf:RDF>')
    fp.close()
    
    #%% save the mRIDs for re-use
    print('saving instance mRIDs to ', fuidname)
    fuid = open(fuidname, 'w')
    for key, val in uuids.items():
        print('{:s},{:s}'.format(key.replace(':', ',', 1), val), file=fuid)
    fuid.close()

#%%
if __name__ == "__main__":
    
    # user selected model
    for model in ["IEEE118", "WECC240"]:
    
      if model == "IEEE118": 
          workpath = 'ieee118/'
          xmlname = 'IEEE118.xml'
          addon_fueltype = 'gen_fuel_type.xlsx'
          
          cimname = 'IEEE118_CIM.xml'
          fuidname = 'IEEE118mRID.dat'
          containername = 'IEEE118'
          containerdesc = 'IEEE118 System'
      elif model == "WECC240":
          workpath = 'wecc240/'
          xmlname = 'WECC240.xml'
          addon_fueltype = 'gen_fuel_type.xlsx'
          
          cimname = 'WECC240_CIM.xml'
          fuidname = 'WECC240mRID.dat'
          containername = 'WECC240'
          containerdesc = 'WECC240 System'
      else:
          sys.exit("this model is not supported")
      
      convertRawtoCIM(workpath, xmlname, addon_fueltype, 
                      cimname, fuidname, containername, containerdesc)
      
    