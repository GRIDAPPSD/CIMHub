package gov.pnnl.gridappsd.cimhub;
// ----------------------------------------------------------
// Copyright (c) 2017-2022, Battelle Memorial Institute
// All rights reserved.
// ----------------------------------------------------------

import java.io.*;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;
import java.util.HashMap;

import gov.pnnl.gridappsd.cimhub.CIMImporter;
import gov.pnnl.gridappsd.cimhub.components.DistComponent;
import gov.pnnl.gridappsd.cimhub.components.DistBreaker;
import gov.pnnl.gridappsd.cimhub.components.DistDisconnector;
import gov.pnnl.gridappsd.cimhub.components.DistFuse;
import gov.pnnl.gridappsd.cimhub.components.DistGroundDisconnector;
import gov.pnnl.gridappsd.cimhub.components.DistJumper;
import gov.pnnl.gridappsd.cimhub.components.DistLoadBreakSwitch;
import gov.pnnl.gridappsd.cimhub.components.DistRecloser;
import gov.pnnl.gridappsd.cimhub.components.DistSectionaliser;

public class CIMQuerySetter extends Object {

  HashMap<String,String> mapQueries = new HashMap<>();
  HashMap<String,String> mapSwitchClasses = new HashMap<>();

  public CIMQuerySetter () {

    mapSwitchClasses.put ("DistBreaker", DistBreaker.szCIMClass);
    mapSwitchClasses.put ("DistDisconnector", DistDisconnector.szCIMClass);
    mapSwitchClasses.put ("DistFuse", DistFuse.szCIMClass);
    mapSwitchClasses.put ("DistGroundDisconnector", DistGroundDisconnector.szCIMClass);
    mapSwitchClasses.put ("DistJumper", DistJumper.szCIMClass);
    mapSwitchClasses.put ("DistLoadBreakSwitch", DistLoadBreakSwitch.szCIMClass);
    mapSwitchClasses.put ("DistRecloser", DistRecloser.szCIMClass);
    mapSwitchClasses.put ("DistSectionaliser", DistSectionaliser.szCIMClass);

    mapQueries.put ("DistBus",
      "SELECT DISTINCT ?id ?name WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?bus c:ConnectivityNode.ConnectivityNodeContainer ?fdr."+
      " ?bus r:type c:ConnectivityNode."+
      " ?bus c:IdentifiedObject.name ?name."+
      " ?bus c:IdentifiedObject.mRID ?id."+
      "} ORDER by ?name");

    mapQueries.put ("DistBaseVoltage",
      "SELECT DISTINCT ?vnom WHERE {"+      
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " {?s c:ConductingEquipment.BaseVoltage ?lev.}"+
      "  UNION "+
      " { ?end c:PowerTransformerEnd.PowerTransformer|c:TransformerTankEnd.TransformerTank ?s."+
      "  ?end c:TransformerEnd.BaseVoltage ?lev.}"+
      " ?lev r:type c:BaseVoltage."+
      " ?lev c:BaseVoltage.nominalVoltage ?vnom."+
      "} ORDER BY ?vnom");

    mapQueries.put ("DistCapacitor",
       "SELECT ?name ?basev ?nomu ?bsection ?sections ?bus ?conn ?grnd"+
       " ?ctrlenabled ?discrete ?mode ?deadband ?setpoint ?delay ?monclass ?moneq ?monbus ?montrm ?monphs ?id ?fdrid ?t1id "+
     "(group_concat(distinct ?phs;separator=\"\") as ?phases) "+
     "WHERE {"+
       " ?s c:Equipment.EquipmentContainer ?fdr."+
       " ?fdr c:IdentifiedObject.mRID ?fdrid."+
       " ?s r:type c:LinearShuntCompensator."+
       " ?s c:IdentifiedObject.name ?name."+
       " ?s c:ConductingEquipment.BaseVoltage ?bv."+
       " ?bv c:BaseVoltage.nominalVoltage ?basev."+
       " ?s c:ShuntCompensator.nomU ?nomu."+
       " ?s c:LinearShuntCompensator.bPerSection ?bsection."+ 
       " ?s c:ShuntCompensator.sections ?sections."+
       " ?s c:ShuntCompensator.phaseConnection ?connraw."+
       "  bind(strafter(str(?connraw),\"PhaseShuntConnectionKind.\") as ?conn)"+
       " ?s c:ShuntCompensator.grounded ?grnd."+
       " OPTIONAL {?scp c:ShuntCompensatorPhase.ShuntCompensator ?s."+
       "  ?scp c:ShuntCompensatorPhase.phase ?phsraw."+
       "  bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) }"+
       " OPTIONAL {?ctl c:RegulatingControl.RegulatingCondEq ?s."+
       "  ?ctl c:RegulatingControl.discrete ?discrete."+
       "  ?ctl c:RegulatingControl.enabled ?ctrlenabled."+
       "  ?ctl c:RegulatingControl.mode ?moderaw."+
       "    bind(strafter(str(?moderaw),\"RegulatingControlModeKind.\") as ?mode)"+
       "  ?ctl c:RegulatingControl.monitoredPhase ?monraw."+
       "    bind(strafter(str(?monraw),\"PhaseCode.\") as ?monphs)"+
       "  ?ctl c:RegulatingControl.targetDeadband ?deadband."+
       "  ?ctl c:RegulatingControl.targetValue ?setpoint."+
       "  ?s c:ShuntCompensator.aVRDelay ?delay."+
       "  ?ctl c:RegulatingControl.Terminal ?trm."+
       "  ?trm c:Terminal.ConductingEquipment ?eq."+
       "  ?eq a ?classraw."+
       "    bind(strafter(str(?classraw),\"CIM100#\") as ?monclass)"+
       "  ?eq c:IdentifiedObject.mRID ?moneq."+
       "  ?trm c:Terminal.ConnectivityNode ?moncn."+
       "  ?moncn c:IdentifiedObject.mRID ?monbus."+
       "  ?trm c:ACDCTerminal.sequenceNumber ?montrm."+
       "  }" +
       " ?s c:IdentifiedObject.mRID ?id."+
       " ?t c:Terminal.ConductingEquipment ?s."+
       " ?t c:Terminal.ConnectivityNode ?cn."+ 
       " ?t c:IdentifiedObject.mRID ?t1id."+
       " ?cn c:IdentifiedObject.mRID ?bus" + 
       "}"+
     "GROUP BY ?name ?basev ?nomu ?bsection ?sections ?bus ?conn ?grnd ?ctrlenabled ?discrete ?mode ?deadband ?setpoint ?delay ?monclass ?moneq ?monbus ?montrm ?monphs ?id ?fdrid ?t1id "+
     "ORDER BY ?name");

    mapQueries.put ("DistConcentricNeutralCable",
      "SELECT DISTINCT ?name ?rad ?corerad ?gmr ?rdc ?r25 ?r50 ?r75 ?amps ?ins ?insmat ?id"+
      " ?insthick ?diacore ?diains ?diascreen ?diajacket ?sheathneutral ?epsr"+
      " ?strand_cnt ?strand_rad ?strand_gmr ?strand_rdc WHERE {"+
      " ?eq r:type c:ACLineSegment."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?acp c:ACLineSegmentPhase.ACLineSegment ?eq."+
      " ?acp c:ACLineSegmentPhase.WireInfo ?w."+
      " ?w r:type c:ConcentricNeutralCableInfo."+
      " ?w c:IdentifiedObject.name ?name."+
      " ?w c:IdentifiedObject.mRID ?id."+
      " ?w c:WireInfo.radius ?rad."+
      " ?w c:WireInfo.gmr ?gmr."+
      " OPTIONAL {?w c:WireInfo.rDC20 ?rdc.}"+
      " OPTIONAL {?w c:WireInfo.rAC25 ?r25.}"+
      " OPTIONAL {?w c:WireInfo.rAC50 ?r50.}"+
      " OPTIONAL {?w c:WireInfo.rAC75 ?r75.}"+
      " OPTIONAL {?w c:WireInfo.coreRadius ?corerad.}"+
      " OPTIONAL {?w c:WireInfo.ratedCurrent ?amps.}"+
      " OPTIONAL {?w c:WireInfo.insulationMaterial ?insraw."+
      "       bind(strafter(str(?insraw),\"WireInsulationKind.\") as ?insmat)}"+
      " OPTIONAL {?w c:WireInfo.insulated ?ins.}"+
      " OPTIONAL {?w c:WireInfo.insulationThickness ?insthick.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverCore ?diacore.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverJacket ?diajacket.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverInsulation ?diains.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverScreen ?diascreen.}"+
      " OPTIONAL {?w c:CableInfo.sheathAsNeutral ?sheathneutral.}"+
      " OPTIONAL {?w c:CableInfo.relativePermittivity ?epsr.}"+
      " OPTIONAL {?w c:ConcentricNeutralCableInfo.diameterOverNeutral ?dianeut.}"+
      " OPTIONAL {?w c:ConcentricNeutralCableInfo.neutralStrandCount ?strand_cnt.}"+
      " OPTIONAL {?w c:ConcentricNeutralCableInfo.neutralStrandGmr ?strand_gmr.}"+
      " OPTIONAL {?w c:ConcentricNeutralCableInfo.neutralStrandRadius ?strand_rad.}"+
      " OPTIONAL {?w c:ConcentricNeutralCableInfo.neutralStrandRDC20 ?strand_rdc.}"+
      "} ORDER BY ?name");

    mapQueries.put ("DistCoordinates",
      "SELECT ?class ?id ?seq ?x ?y WHERE {"+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?eq c:PowerSystemResource.Location ?loc."+
      " { ?eq c:IdentifiedObject.mRID ?id."+
      "   ?eq a ?classraw."+
      "   bind(strafter(str(?classraw),\"CIM100#\") as ?class)}"+
      "  UNION"+
      " { ?unit c:PowerElectronicsUnit.PowerElectronicsConnection ?eq."+
      "   ?unit c:IdentifiedObject.mRID ?id."+
      "   ?unit a ?classraw."+
      "   bind(strafter(str(?classraw),\"CIM100#\") as ?class)}"+
      " ?pt c:PositionPoint.Location ?loc."+
      " ?pt c:PositionPoint.xPosition ?x."+
      " ?pt c:PositionPoint.yPosition ?y."+
      " ?pt c:PositionPoint.sequenceNumber ?seq."+
      " FILTER (!regex(?class, \"Phase\"))."+
      " FILTER (!regex(?class, \"TapChanger\"))."+
      " FILTER (!regex(?class, \"Tank\"))."+
      " FILTER (!regex(?class, \"RegulatingControl\"))."+
      "}"+
      " ORDER BY ?class ?id ?seq ?x ?y");

    mapQueries.put ("DistFeeder",
       "SELECT ?feeder ?fid ?station ?sid ?subregion ?sgrid ?region ?rgnid WHERE {"+
       "?s r:type c:Feeder."+
       "?s c:IdentifiedObject.name ?feeder."+
       "?s c:IdentifiedObject.mRID ?fid."+
       "?s c:Feeder.NormalEnergizingSubstation ?sub."+
       "?sub c:IdentifiedObject.name ?station."+
       "?sub c:IdentifiedObject.mRID ?sid."+
       "?sub c:Substation.Region ?sgr."+
       "?sgr c:IdentifiedObject.name ?subregion."+
       "?sgr c:IdentifiedObject.mRID ?sgrid."+
       "?sgr c:SubGeographicalRegion.Region ?rgn."+
       "?rgn c:IdentifiedObject.name ?region."+
       "?rgn c:IdentifiedObject.mRID ?rgnid."+
       "}"+
       " ORDER by ?station ?feeder");

    mapQueries.put ("DistHouse",
      "SELECT ?name ?parent ?coolingSetpoint ?coolingSystem ?floorArea ?heatingSetpoint ?heatingSystem ?hvacPowerFactor ?numberOfStories ?thermalIntegrity ?id ?fdrid WHERE {" + 
          "?h r:type c:House. " + 
          "?h c:IdentifiedObject.name ?name. " + 
          "?h c:IdentifiedObject.mRID ?id. " + 
          "?h c:House.floorArea ?floorArea. " + 
          "?h c:House.numberOfStories ?numberOfStories. " + 
          "OPTIONAL{?h c:House.coolingSetpoint ?coolingSetpoint.} " + 
          "OPTIONAL{?h c:House.heatingSetpoint ?heatingSetpoint.} " + 
          "OPTIONAL{?h c:House.hvacPowerFactor ?hvacPowerFactor.} " + 
          "?h c:House.coolingSystem ?coolingSystemRaw. " + 
            "bind(strafter(str(?coolingSystemRaw),\"HouseCooling.\") as ?coolingSystem) " + 
          "?h c:House.heatingSystem ?heatingSystemRaw. " + 
            "bind(strafter(str(?heatingSystemRaw),\"HouseHeating.\") as ?heatingSystem) " + 
          "?h c:House.thermalIntegrity ?thermalIntegrityRaw " + 
            "bind(strafter(str(?thermalIntegrityRaw),\"HouseThermalIntegrity.\") as ?thermalIntegrity) " + 
          "?h c:House.EnergyConsumer ?econ. " + 
          "?econ c:IdentifiedObject.mRID ?parent. " +
          "?fdr c:IdentifiedObject.mRID ?fdrid. " +
          "?econ c:Equipment.EquipmentContainer ?fdr. " +
      "} ORDER BY ?name");

    mapQueries.put ("DistLinesCodeZ",
      "SELECT ?name ?id ?basev ?bus1 ?bus2 ?len ?codeid ?fdrid ?seq ?phs ?t1id ?t2id WHERE {"+
      " ?s r:type c:ACLineSegment."+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:ConductingEquipment.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev."+
      " ?s c:Conductor.length ?len."+
      " ?s c:ACLineSegment.PerLengthImpedance ?lcode."+
      " ?lcode c:IdentifiedObject.mRID ?codeid."+
      " ?t1 c:Terminal.ConductingEquipment ?s."+
      " ?t1 c:Terminal.ConnectivityNode ?cn1."+
      " ?t1 c:ACDCTerminal.sequenceNumber \"1\"."+
      " ?t1 c:IdentifiedObject.mRID ?t1id."+
      " ?cn1 c:IdentifiedObject.mRID ?bus1."+
      " ?t2 c:Terminal.ConductingEquipment ?s."+
      " ?t2 c:Terminal.ConnectivityNode ?cn2."+
      " ?t2 c:ACDCTerminal.sequenceNumber \"2\"."+
      " ?t2 c:IdentifiedObject.mRID ?t2id."+
      " ?cn2 c:IdentifiedObject.mRID ?bus2."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " OPTIONAL {?acp c:ACLineSegmentPhase.ACLineSegment ?s."+
      " ?acp c:ACLineSegmentPhase.sequenceNumber ?seq."+
      " ?acp c:ACLineSegmentPhase.phase ?phsraw."+
      "   bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) }"+
      "}"+
      " ORDER BY ?name ?seq ?phs");

    mapQueries.put ("DistLinesInstanceZ",
      "SELECT ?name ?id ?basev ?bus1 ?bus2 ?len ?r ?x ?b ?r0 ?x0 ?b0 ?fdrid ?t1id ?t2id WHERE {"+
      " ?s r:type c:ACLineSegment."+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?s c:ConductingEquipment.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev."+
      " ?s c:Conductor.length ?len."+
      " ?s c:ACLineSegment.r ?r."+
      " ?s c:ACLineSegment.x ?x."+
      " OPTIONAL {?s c:ACLineSegment.bch ?b.}"+
      " OPTIONAL {?s c:ACLineSegment.r0 ?r0.}"+
      " OPTIONAL {?s c:ACLineSegment.x0 ?x0.}"+
      " OPTIONAL {?s c:ACLineSegment.b0ch ?b0.}"+
      " ?t1 c:Terminal.ConductingEquipment ?s."+
      " ?t1 c:Terminal.ConnectivityNode ?cn1."+
      " ?t1 c:ACDCTerminal.sequenceNumber \"1\"."+
      " ?t1 c:IdentifiedObject.mRID ?t1id."+
      " ?cn1 c:IdentifiedObject.mRID ?bus1."+
      " ?t2 c:Terminal.ConductingEquipment ?s."+
      " ?t2 c:Terminal.ConnectivityNode ?cn2."+
      " ?t2 c:ACDCTerminal.sequenceNumber \"2\"."+
      " ?t2 c:IdentifiedObject.mRID ?t2id."+
      " ?cn2 c:IdentifiedObject.mRID ?bus2"+
      "}"+
      " GROUP BY ?name ?id ?basev ?bus1 ?bus2 ?len ?r ?x ?b ?r0 ?x0 ?b0 ?fdrid ?t1id ?t2id"+
      " ORDER BY ?name");

  mapQueries.put ("DistSeriesCompensator",
    "SELECT ?name ?id ?basev ?bus1 ?bus2 ?r ?x ?r0 ?x0 ?fdrid ?t1id ?t2id WHERE {"+
    " ?s r:type c:SeriesCompensator."+
    " ?s c:Equipment.EquipmentContainer ?fdr."+
    " ?fdr c:IdentifiedObject.mRID ?fdrid."+
    " ?s c:IdentifiedObject.name ?name."+
    " ?s c:IdentifiedObject.mRID ?id."+
    " ?s c:ConductingEquipment.BaseVoltage ?bv."+
    " ?bv c:BaseVoltage.nominalVoltage ?basev."+
    " ?s c:SeriesCompensator.r ?r."+
    " ?s c:SeriesCompensator.x ?x."+
    " OPTIONAL {?s c:SeriesCompensator.r0 ?r0.}"+
    " OPTIONAL {?s c:SeriesCompensator.x0 ?x0.}"+
    " ?t1 c:Terminal.ConductingEquipment ?s."+
    " ?t1 c:Terminal.ConnectivityNode ?cn1."+
    " ?t1 c:ACDCTerminal.sequenceNumber \"1\"."+
    " ?cn1 c:IdentifiedObject.mRID ?bus1."+
    " ?t2 c:Terminal.ConductingEquipment ?s."+
    " ?t2 c:Terminal.ConnectivityNode ?cn2."+
    " ?t2 c:ACDCTerminal.sequenceNumber \"2\"."+
    " ?cn2 c:IdentifiedObject.mRID ?bus2."+
    " ?t1 c:IdentifiedObject.mRID ?t1id."+
    " ?t2 c:IdentifiedObject.mRID ?t2id."+
    "}"+
    " GROUP BY ?name ?id ?basev ?bus1 ?bus2 ?r ?x ?b ?r0 ?x0 ?b0 ?fdrid ?t1id ?t2id"+
    " ORDER BY ?name");

    mapQueries.put ("DistLinesSpacingZ",
      "SELECT ?name ?id ?basev ?bus1 ?bus2 ?fdrid ?len ?spcid ?phs ?phid ?phclass ?t1id ?t2id"+
      " WHERE {"+
      " ?s r:type c:ACLineSegment."+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?s c:ConductingEquipment.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev."+
      " ?s c:Conductor.length ?len."+
      " ?s c:ACLineSegment.WireSpacingInfo ?inf."+
      " ?inf c:IdentifiedObject.mRID ?spcid."+
      " ?t1 c:Terminal.ConductingEquipment ?s."+
      " ?t1 c:Terminal.ConnectivityNode ?cn1."+
      " ?t1 c:ACDCTerminal.sequenceNumber \"1\"."+
      " ?t1 c:IdentifiedObject.mRID ?t1id."+
      " ?cn1 c:IdentifiedObject.mRID ?bus1."+
      " ?t2 c:Terminal.ConductingEquipment ?s."+
      " ?t2 c:Terminal.ConnectivityNode ?cn2."+
      " ?t2 c:ACDCTerminal.sequenceNumber \"2\"."+
      " ?t2 c:IdentifiedObject.mRID ?t2id."+
      " ?cn2 c:IdentifiedObject.mRID ?bus2."+
      " ?acp c:ACLineSegmentPhase.ACLineSegment ?s."+
      " ?acp c:ACLineSegmentPhase.sequenceNumber ?seq."+
      " ?acp c:ACLineSegmentPhase.phase ?phsraw."+
      "   bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs)."+
      " ?acp c:ACLineSegmentPhase.WireInfo ?phinf."+
      " ?phinf c:IdentifiedObject.mRID ?phid."+
      " ?phinf a ?phclassraw."+
      "   bind(strafter(str(?phclassraw),\"CIM100#\") as ?phclass)"+
      " }"+
      " ORDER BY ?id ?name ?seq ?phs");

    mapQueries.put ("DistLineSpacing",
      "SELECT DISTINCT ?name ?cable ?usage ?bundle_count ?bundle_sep ?id ?seq ?x ?y"+
      " WHERE {"+
      " ?eq r:type c:ACLineSegment."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?eq c:ACLineSegment.WireSpacingInfo ?w."+
      " ?w c:IdentifiedObject.name ?name."+
      " ?w c:IdentifiedObject.mRID ?id."+
      " ?pos c:WirePosition.WireSpacingInfo ?w."+
      " ?pos c:WirePosition.xCoord ?x."+
      " ?pos c:WirePosition.yCoord ?y."+
      " ?pos c:WirePosition.sequenceNumber ?seq."+
      " ?w c:WireSpacingInfo.isCable ?cable."+
      " ?w c:WireSpacingInfo.phaseWireCount ?bundle_count."+
      " ?w c:WireSpacingInfo.phaseWireSpacing ?bundle_sep."+
      " ?w c:WireSpacingInfo.usage ?useraw."+
      "   bind(strafter(str(?useraw),\"WireUsageKind.\") as ?usage)"+
      "} ORDER BY ?name ?seq");

    mapQueries.put ("DistEnergyConnectionProfile",
      "SELECT DISTINCT ?name ?id ?ldid ?dssDaily ?dssDuty ?dssLoadCvrCurve ?dssLoadGrowth"+
      " ?dssPVTDaily ?dssPVTDuty ?dssPVTYearly ?dssSpectrum ?dssYearly"+
      " ?gldPlayer ?gldSchedule WHERE {"+
      " ?s r:type c:EnergyConnectionProfile."+
      " ?ld c:Equipment.EquipmentContainer ?fdr."+
      " {?ld r:type c:SynchronousMachine.}"+
      "   UNION"+
      " {?ld r:type c:PowerElectronicsConnection.}"+
      "   UNION"+
      " {?ld r:type c:EnergyConsumer.}"+
      " ?ld c:IdentifiedObject.mRID ?ldid."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?ecp c:IdentifiedObject.name ?name."+
      " ?ecp c:IdentifiedObject.mRID ?id."+
      " ?ecp c:EnergyConnectionProfile.EnergyConnections ?ld."+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssDaily ?dssDaily.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssDuty ?dssDuty.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssLoadCvrCurve ?dssLoadCvrCurve.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssPVTDaily ?dssPVTDaily.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssPVTDuty ?dssPVTDuty.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssPVTYearly ?dssPVTYearly.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssSpectrum ?dssSpectrum.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.dssYearly ?dssYearly.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.gldPlayer ?gldPlayer.}"+
      " OPTIONAL {?ecp c:EnergyConnectionProfile.gldSchedule ?gldSchedule.}"+
      "}"+
      "ORDER by ?name ?ldid");

    mapQueries.put ("DistLoad",
      "SELECT ?name ?bus ?basev ?p ?q ?cnt ?conn ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?id ?fdrid ?t1id "+
      "(group_concat(distinct ?phs;separator=\"\\n\") as ?phases) "+
      "WHERE {"+
      " ?s r:type c:EnergyConsumer."+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:ConductingEquipment.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev."+
      " ?s c:EnergyConsumer.p ?p."+
      " ?s c:EnergyConsumer.q ?q."+
      " OPTIONAL {?s c:EnergyConsumer.customerCount ?cnt.}"+
      " ?s c:EnergyConsumer.phaseConnection ?connraw."+
      "       bind(strafter(str(?connraw),\"PhaseShuntConnectionKind.\") as ?conn)"+
      " ?s c:EnergyConsumer.LoadResponse ?lr."+
      " ?lr c:LoadResponseCharacteristic.pConstantImpedance ?pz."+
      " ?lr c:LoadResponseCharacteristic.qConstantImpedance ?qz."+
      " ?lr c:LoadResponseCharacteristic.pConstantCurrent ?pi."+
      " ?lr c:LoadResponseCharacteristic.qConstantCurrent ?qi."+
      " ?lr c:LoadResponseCharacteristic.pConstantPower ?pp."+
      " ?lr c:LoadResponseCharacteristic.qConstantPower ?qp."+
      " OPTIONAL {?lr c:LoadResponseCharacteristic.pVoltageExponent ?pe.}"+
      " OPTIONAL {?lr c:LoadResponseCharacteristic.qVoltageExponent ?qe.}"+
      " OPTIONAL {?ecp c:EnergyConsumerPhase.EnergyConsumer ?s."+
      " ?ecp c:EnergyConsumerPhase.phase ?phsraw."+
      "       bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) }"+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?t c:Terminal.ConductingEquipment ?s."+
      " ?t c:Terminal.ConnectivityNode ?cn."+
      " ?t c:IdentifiedObject.mRID ?t1id."+
      " ?cn c:IdentifiedObject.mRID ?bus"+
      "} "+
      "GROUP BY ?name ?bus ?basev ?p ?q ?cnt ?conn ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?id ?fdrid ?t1id "+
      "ORDER BY ?name");

    mapQueries.put ("DistMeasurement",
      "SELECT ?class ?type ?name ?bus ?phases ?eqtype ?eqid ?trmid ?id WHERE {"+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+ 
      " { ?s r:type c:Discrete. bind (\"Discrete\" as ?class)}"+
      "   UNION"+
      " { ?s r:type c:Analog. bind (\"Analog\" as ?class)}"+
      "  ?s c:IdentifiedObject.name ?name ."+
      "  ?s c:IdentifiedObject.mRID ?id ."+
      "  ?s c:Measurement.PowerSystemResource ?eq ."+
      "  ?s c:Measurement.Terminal ?trm ."+
      "  ?s c:Measurement.measurementType ?type ."+
      "  ?trm c:IdentifiedObject.mRID ?trmid."+
      "  ?eq c:IdentifiedObject.mRID ?eqid."+
      "  ?eq r:type ?typeraw."+
      "   bind(strafter(str(?typeraw),\"#\") as ?eqtype)"+
      "  ?trm c:Terminal.ConnectivityNode ?cn."+
      "  ?cn c:IdentifiedObject.mRID ?bus."+
      "  ?s c:Measurement.phases ?phsraw ."+
      "    {bind(strafter(str(?phsraw),\"PhaseCode.\") as ?phases)}"+
      " } ORDER BY ?class ?type ?name");

    mapQueries.put ("DistOverheadWire",
      "SELECT DISTINCT ?name ?rad ?corerad ?gmr ?rdc ?r25 ?r50 ?r75 ?amps ?ins ?insmat ?insthick ?id WHERE {"+
      " ?eq r:type c:ACLineSegment."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?acp c:ACLineSegmentPhase.ACLineSegment ?eq."+
      " ?acp c:ACLineSegmentPhase.WireInfo ?w."+
      " ?w r:type c:OverheadWireInfo."+
      " ?w c:IdentifiedObject.name ?name."+
      " ?w c:IdentifiedObject.mRID ?id."+
      " ?w c:WireInfo.radius ?rad."+
      " ?w c:WireInfo.gmr ?gmr."+
      " OPTIONAL {?w c:WireInfo.rDC20 ?rdc.}"+
      " OPTIONAL {?w c:WireInfo.rAC25 ?r25.}"+
      " OPTIONAL {?w c:WireInfo.rAC50 ?r50.}"+
      " OPTIONAL {?w c:WireInfo.rAC75 ?r75.}"+
      " OPTIONAL {?w c:WireInfo.coreRadius ?corerad.}"+
      " OPTIONAL {?w c:WireInfo.ratedCurrent ?amps.}"+
      " OPTIONAL {?w c:WireInfo.insulationMaterial ?insraw."+
      "       bind(strafter(str(?insraw),\"WireInsulationKind.\") as ?insmat)}"+
      " OPTIONAL {?w c:WireInfo.insulated ?ins.}"+
      " OPTIONAL {?w c:WireInfo.insulationThickness ?insthick.}"+
      "} ORDER BY ?name");

    mapQueries.put ("DistPhaseMatrix",
      "SELECT DISTINCT ?name ?cnt ?row ?col ?r ?x ?b ?id WHERE {"+
      " ?eq r:type c:ACLineSegment."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?eq c:ACLineSegment.PerLengthImpedance ?s."+
      " ?s r:type c:PerLengthPhaseImpedance."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:PerLengthPhaseImpedance.conductorCount ?cnt."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?elm c:PhaseImpedanceData.PhaseImpedance ?s."+
      " ?elm c:PhaseImpedanceData.row ?row."+
      " ?elm c:PhaseImpedanceData.column ?col."+
      " ?elm c:PhaseImpedanceData.r ?r."+
      " ?elm c:PhaseImpedanceData.x ?x."+
      " ?elm c:PhaseImpedanceData.b ?b"+
      "} ORDER BY ?name ?row ?col");

    mapQueries.put ("DistPowerXfmrCore",
      "SELECT ?pid ?enum ?b ?g WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p r:type c:PowerTransformer."+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?p c:IdentifiedObject.mRID ?pid."+
      " ?end c:PowerTransformerEnd.PowerTransformer ?p."+
      " {?adm c:TransformerCoreAdmittance.TransformerEnd ?end.}"+
      "  UNION"+
      " {?end c:TransformerEnd.CoreAdmittance ?adm.}"+
      " ?end c:TransformerEnd.endNumber ?enum."+
      " ?adm c:TransformerCoreAdmittance.b ?b."+
      " ?adm c:TransformerCoreAdmittance.g ?g."+
      "} ORDER BY ?pid");

    mapQueries.put ("DistPowerXfmrMesh",
      "SELECT ?pid ?fnum ?tnum ?r ?x WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p r:type c:PowerTransformer."+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?p c:IdentifiedObject.mRID ?pid."+
      " ?from c:PowerTransformerEnd.PowerTransformer ?p."+
      " ?imp c:TransformerMeshImpedance.FromTransformerEnd ?from."+
      " ?imp c:TransformerMeshImpedance.ToTransformerEnd ?to."+
      " ?imp c:TransformerMeshImpedance.r ?r."+
      " ?imp c:TransformerMeshImpedance.x ?x."+
      " ?from c:TransformerEnd.endNumber ?fnum."+
      " ?to c:TransformerEnd.endNumber ?tnum."+
      "} ORDER BY ?pid ?fnum ?tnum");

    mapQueries.put ("DistPowerXfmrWinding",
      "SELECT ?name ?id ?vgrp ?enum ?bus ?basev ?conn ?ratedS ?ratedU ?r ?ang ?grounded ?rground ?xground ?fdrid ?t1id ?eid WHERE {"+
      " ?p r:type c:PowerTransformer."+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p c:PowerTransformer.vectorGroup ?vgrp."+
      " ?p c:IdentifiedObject.mRID ?id."+
      " ?p c:IdentifiedObject.name ?name."+
      " ?end c:PowerTransformerEnd.PowerTransformer ?p."+
      " ?end c:TransformerEnd.endNumber ?enum."+
      " ?end c:PowerTransformerEnd.ratedS ?ratedS."+
      " ?end c:PowerTransformerEnd.ratedU ?ratedU."+
      " ?end c:PowerTransformerEnd.r ?r."+
      " ?end c:PowerTransformerEnd.phaseAngleClock ?ang."+
      " ?end c:IdentifiedObject.mRID ?eid."+
      " ?end c:PowerTransformerEnd.connectionKind ?connraw."+  
      "  bind(strafter(str(?connraw),\"WindingConnection.\") as ?conn)"+
      " ?end c:TransformerEnd.grounded ?grounded."+
      " OPTIONAL {?end c:TransformerEnd.rground ?rground.}"+
      " OPTIONAL {?end c:TransformerEnd.xground ?xground.}"+
      " ?end c:TransformerEnd.Terminal ?trm."+
      " ?trm c:Terminal.ConnectivityNode ?cn. "+
      " ?trm c:IdentifiedObject.mRID ?t1id."+
      " ?cn c:IdentifiedObject.mRID ?bus."+
      " ?end c:TransformerEnd.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev"+
      "}"+
      " ORDER BY ?name ?id ?enum");

    mapQueries.put ("DistRegulatorPrefix",
      "SELECT ?name ?id ?pid ?tid ?wnum ?orderedPhases ?incr ?mode ?enabled ?highStep ?lowStep ?neutralStep"+
      " ?normalStep ?neutralU ?step ?initDelay ?subDelay ?ltc ?vlim ?vmin"+
      " ?vset ?vbw ?ldc ?fwdR ?fwdX ?revR ?revX ?revEnabled ?revDelay ?revNeutral ?revThreshold ?revSet ?revBand"+
      " ?discrete ?ctl_enabled ?ctlmode"+
      " ?monphs ?ctRating ?ctRatio ?ptRatio ?fdrid"+
      " WHERE {"+
      " ?pxf c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?rtc r:type c:RatioTapChanger."+
      " ?rtc c:IdentifiedObject.name ?name."+
      " ?rtc c:RatioTapChanger.TransformerEnd ?end."+
      " ?end c:TransformerEnd.endNumber ?wnum.");

    mapQueries.put ("DistRegulatorBanked",
      " ?end c:PowerTransformerEnd.PowerTransformer ?pxf.");

    mapQueries.put ("DistRegulatorTanked",
      " ?end c:TransformerTankEnd.TransformerTank ?tank."+
      " ?tank c:IdentifiedObject.mRID ?tid."+
      "  OPTIONAL {?end c:TransformerTankEnd.orderedPhases ?phsraw."+
      "  bind(strafter(str(?phsraw),\"OrderedPhaseCodeKind.\") as ?orderedPhases)}"+
      " ?tank c:TransformerTank.PowerTransformer ?pxf.");

    mapQueries.put ("DistRegulatorSuffix",
      " ?pxf c:IdentifiedObject.mRID ?pid."+
      " ?rtc c:RatioTapChanger.stepVoltageIncrement ?incr."+
      " ?rtc c:TapChanger.controlEnabled ?enabled."+
      " ?rtc c:TapChanger.highStep ?highStep."+
      " ?rtc c:TapChanger.lowStep ?lowStep."+
      " ?rtc c:TapChanger.ltcFlag ?ltc."+
      " ?rtc c:TapChanger.neutralStep ?neutralStep."+
      " ?rtc c:TapChanger.neutralU ?neutralU."+
      " ?rtc c:TapChanger.normalStep ?normalStep."+
      " ?rtc c:TapChanger.step ?step."+
      " OPTIONAL {?rtc c:TapChanger.initialDelay ?initDelay."+
      " ?rtc c:TapChanger.subsequentDelay ?subDelay."+
      " ?rtc c:TapChanger.ctRating ?ctRating."+
      " ?rtc c:TapChanger.ctRatio ?ctRatio."+
      " ?rtc c:TapChanger.ptRatio ?ptRatio.}"+
      " OPTIONAL {?rtc c:TapChanger.TapChangerControl ?ctl."+
      " ?ctl c:TapChangerControl.maxLimitVoltage ?vlim."+
      " ?ctl c:TapChangerControl.minLimitVoltage ?vmin."+
      " ?ctl c:TapChangerControl.lineDropCompensation ?ldc."+
      " OPTIONAL {?ctl c:TapChangerControl.lineDropR ?fwdR.}"+
      " OPTIONAL {?ctl c:TapChangerControl.lineDropX ?fwdX.}"+
      " OPTIONAL {?ctl c:TapChangerControl.reverseLineDropR ?revR.}"+
      " OPTIONAL {?ctl c:TapChangerControl.reverseLineDropX ?revX.}"+
      " OPTIONAL {?ctl c:TapChangerControl.reversible ?revEnabled.}"+
      " OPTIONAL {?ctl c:TapChangerControl.reversingDelay ?revDelay.}"+
      " OPTIONAL{?ctl c:TapChangerControl.reverseToNeutral ?revNeutral.}"+
      " OPTIONAL{?ctl c:TapChangerControl.reversingPowerThreshold ?revThreshold.}"+
      " OPTIONAL{?ctl c:RegulatingControl.reverseTargetDeadband ?revBand.}"+
      " OPTIONAL{?ctl c:RegulatingControl.reverseTargetValue ?revSet.}"+
      " ?ctl c:RegulatingControl.discrete ?discrete."+
      " ?ctl c:RegulatingControl.enabled ?ctl_enabled."+
      " ?ctl c:RegulatingControl.mode ?ctlmoderaw."+
      "  bind(strafter(str(?ctlmoderaw),\"RegulatingControlModeKind.\") as ?ctlmode)"+
      " ?ctl c:RegulatingControl.monitoredPhase ?monraw."+
      "  bind(strafter(str(?monraw),\"PhaseCode.\") as ?monphs)"+
      " ?ctl c:RegulatingControl.targetDeadband ?vbw."+
      " ?ctl c:RegulatingControl.targetValue ?vset.}"+
      " ?rtc c:IdentifiedObject.mRID ?id."+
      "}"+
      " ORDER BY ?pid ?id ?tid ?wnum");

    mapQueries.put ("DistSequenceMatrix",
      "SELECT DISTINCT ?name ?r1 ?x1 ?b1 ?r0 ?x0 ?b0 ?id WHERE {"+
      " ?eq r:type c:ACLineSegment."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?eq c:ACLineSegment.PerLengthImpedance ?s."+
      " ?s r:type c:PerLengthSequenceImpedance."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?s c:PerLengthSequenceImpedance.r ?r1."+
      " ?s c:PerLengthSequenceImpedance.x ?x1."+
      " ?s c:PerLengthSequenceImpedance.bch ?b1."+
      " ?s c:PerLengthSequenceImpedance.r0 ?r0."+
      " ?s c:PerLengthSequenceImpedance.x0 ?x0."+
      " ?s c:PerLengthSequenceImpedance.b0ch ?b0"+
      "} ORDER BY ?name");

    mapQueries.put ("DistSolar",
      "SELECT ?name ?bus ?ratedS ?ratedU ?maxP ?minP ?maxQ ?minQ ?ipu ?p ?q ?controlMode ?id ?fdrid ?pecid ?t1id (group_concat(distinct ?phs;separator=\"\\n\") as ?phases) "+
      "WHERE {"+
      " ?s r:type c:PhotovoltaicUnit."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:PowerElectronicsUnit.maxP ?maxP."+
      " ?s c:PowerElectronicsUnit.minP ?minP."+
      " ?s c:PowerElectronicsUnit.PowerElectronicsConnection ?pec."+
      " ?pec c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?pec c:PowerElectronicsConnection.ratedS ?ratedS."+
      " ?pec c:PowerElectronicsConnection.ratedU ?ratedU."+
      " ?pec c:PowerElectronicsConnection.p ?p."+
      " ?pec c:PowerElectronicsConnection.q ?q."+
      " ?pec c:PowerElectronicsConnection.maxQ ?maxQ."+
      " ?pec c:PowerElectronicsConnection.minQ ?minQ."+
      " {?pec c:PowerElectronicsConnection.controlMode ?modeRaw."+
      " bind(strafter(str(?modeRaw),\"ConverterControlModeKind.\") as ?controlMode)}"+
      " ?pec c:PowerElectronicsConnection.maxIFault ?ipu."+
      " ?pec c:IdentifiedObject.mRID ?pecid."+
      " OPTIONAL {?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec."+
      " ?pecp c:PowerElectronicsConnectionPhase.phase ?phsraw."+
      "   bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) }"+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?t c:Terminal.ConductingEquipment ?pec."+
      " ?t c:Terminal.ConnectivityNode ?cn."+ 
      " ?t c:IdentifiedObject.mRID ?t1id."+
      " ?cn c:IdentifiedObject.mRID ?bus"+
      "} "+
      "GROUP by ?name ?bus ?ratedS ?ratedU ?maxP ?minP ?maxQ ?minQ ?ipu ?p ?q ?controlMode ?id ?fdrid ?pecid ?t1id "+
      "ORDER BY ?name");

    mapQueries.put ("DistStorage",
      "SELECT ?name ?bus ?ratedS ?ratedU ?maxP ?minP ?maxQ ?minQ ?ipu ?ratedE ?storedE ?state ?p ?q ?controlMode ?id ?fdrid ?pecid ?t1id (group_concat(distinct ?phs;separator=\"\\n\") as ?phases) "+
      "WHERE {"+
      " ?s r:type c:BatteryUnit."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:PowerElectronicsUnit.PowerElectronicsConnection ?pec."+
      " ?pec c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?pec c:PowerElectronicsConnection.ratedS ?ratedS."+
      " ?pec c:PowerElectronicsConnection.ratedU ?ratedU."+
      " ?pec c:PowerElectronicsConnection.p ?p."+
      " ?pec c:PowerElectronicsConnection.q ?q."+
      " ?pec c:PowerElectronicsConnection.maxQ ?maxQ."+
      " ?pec c:PowerElectronicsConnection.minQ ?minQ."+
      " {?pec c:PowerElectronicsConnection.controlMode ?modeRaw."+
      " bind(strafter(str(?modeRaw),\"ConverterControlModeKind.\") as ?controlMode)}"+
      " ?pec c:PowerElectronicsConnection.maxIFault ?ipu."+
      " ?pec c:IdentifiedObject.mRID ?pecid."+
      " ?s c:PowerElectronicsUnit.maxP ?maxP."+
      " ?s c:PowerElectronicsUnit.minP ?minP."+
      " ?s c:BatteryUnit.ratedE ?ratedE."+
      " ?s c:BatteryUnit.storedE ?storedE."+
      " ?s c:BatteryUnit.batteryState ?stateraw."+
      "   bind(strafter(str(?stateraw),\"BatteryStateKind.\") as ?state)"+
      " OPTIONAL {?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec."+
      " ?pecp c:PowerElectronicsConnectionPhase.phase ?phsraw."+
      "   bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) }"+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?t c:Terminal.ConductingEquipment ?pec."+
      " ?t c:Terminal.ConnectivityNode ?cn."+ 
      " ?t c:IdentifiedObject.mRID ?t1id."+
      " ?cn c:IdentifiedObject.mRID ?bus"+
      "} "+
      "GROUP by ?name ?bus ?ratedS ?ratedU ?maxP ?minP ?maxQ ?minQ ?ipu ?ratedE ?storedE ?state ?p ?q ?controlMode ?id ?fdrid ?pecid ?t1id "+
      "ORDER BY ?name");

    mapQueries.put ("DistSubstation",
      "SELECT ?name ?fdrname ?bus ?basev ?nomv ?vmag ?vang ?r1 ?x1 ?r0 ?x0 ?id ?t1id ?fdrid WHERE {" +
      " ?s r:type c:EnergySource." +
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?fdr c:IdentifiedObject.name ?fdrname."+
      " ?s c:IdentifiedObject.name ?name." +
      " ?s c:ConductingEquipment.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev."+
      " ?s c:EnergySource.nominalVoltage ?nomv." + 
      " ?s c:EnergySource.voltageMagnitude ?vmag." + 
      " ?s c:EnergySource.voltageAngle ?vang." + 
      " ?s c:EnergySource.r ?r1." + 
      " ?s c:EnergySource.x ?x1." + 
      " ?s c:EnergySource.r0 ?r0." + 
      " ?s c:EnergySource.x0 ?x0." + 
      " ?t c:Terminal.ConductingEquipment ?s." +
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?t c:Terminal.ConnectivityNode ?cn." + 
      " ?t c:IdentifiedObject.mRID ?t1id."+
      " ?cn c:IdentifiedObject.mRID ?bus" +
      "}");

    mapQueries.put ("DistSwitchSelect",
      "SELECT ?name ?id ?bus1 ?bus2 ?basev ?rated ?breaking (group_concat(distinct ?phs;separator=\"\\n\") as ?phases) ?open ?fdrid ?t1id ?t2id WHERE {");

    mapQueries.put ("DistSwitchWhere",
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:ConductingEquipment.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev."+
      " ?s c:Switch.normalOpen ?open."+
      " ?s c:Switch.ratedCurrent ?rated."+
      " OPTIONAL {?s c:ProtectedSwitch.breakingCapacity ?breaking.}"+
      " ?t1 c:Terminal.ConductingEquipment ?s."+
      " ?t1 c:Terminal.ConnectivityNode ?cn1."+
      " ?t1 c:ACDCTerminal.sequenceNumber \"1\"."+
      " ?t1 c:IdentifiedObject.mRID ?t1id."+
      " ?cn1 c:IdentifiedObject.mRID ?bus1."+
      " ?t2 c:Terminal.ConductingEquipment ?s."+
      " ?t2 c:Terminal.ConnectivityNode ?cn2."+
      " ?t2 c:ACDCTerminal.sequenceNumber \"2\"."+
      " ?t2 c:IdentifiedObject.mRID ?t2id."+
      " ?cn2 c:IdentifiedObject.mRID ?bus2."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " OPTIONAL {?swp c:SwitchPhase.Switch ?s."+
      " ?swp c:SwitchPhase.phaseSide1 ?phsraw."+
      "   bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) }"+
      "}"+
      " GROUP BY ?name ?basev ?bus1 ?bus2 ?rated ?breaking ?open ?id ?fdrid ?t1id ?t2id"+
      " ORDER BY ?name");

    mapQueries.put ("DistSyncMachine",
      "SELECT ?name ?bus (group_concat(distinct ?phs;separator=\"\\n\") as ?phases) ?ratedS ?ratedU ?p ?q ?id ?fdrid ?t1id WHERE {"+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s r:type c:SynchronousMachine."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:RotatingMachine.ratedS ?ratedS."+
      " ?s c:RotatingMachine.ratedU ?ratedU."+
      " ?s c:RotatingMachine.p ?p."+
      " ?s c:RotatingMachine.q ?q."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " OPTIONAL {?smp c:SynchronousMachinePhase.SynchronousMachine ?s."+
      "  ?smp c:SynchronousMachinePhase.phase ?phsraw."+
      " bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) }"+
      " ?t c:Terminal.ConductingEquipment ?s."+
      " ?t c:Terminal.ConnectivityNode ?cn."+ 
      " ?t c:IdentifiedObject.mRID ?t1id."+
      " ?cn c:IdentifiedObject.mRID ?bus" + 
      "} " +
      "GROUP by ?name ?bus ?ratedS ?ratedU ?p ?q ?id ?fdrid ?t1id " +
      "ORDER by ?name");

    mapQueries.put ("DistIEEE1547Connection",
      "SELECT ?name ?id ?fdrid (group_concat(distinct ?pid;separator=\"\\n\") as ?pids) WHERE {"+
      " ?pec c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s r:type c:DERIEEEType1."+
      " ?s c:DERDynamics.PowerElectronicsConnection ?pec."+
      " ?pec c:IdentifiedObject.mRID ?pid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:IdentifiedObject.mRID ?id."+
      "} "+
      "GROUP by ?name ?id ?fdrid "+
      "ORDER by ?name ?id");

    mapQueries.put ("DistIEEE1547Signal",
      "SELECT DISTINCT ?name ?id ?pecid ?rid ?kind ?tid ?fdrid WHERE {"+
      " ?pec c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s r:type c:DERIEEEType1."+
      " ?s c:DERDynamics.PowerElectronicsConnection ?pec."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?pec c:IdentifiedObject.mRID ?pecid."+
      " ?s c:DERDynamics.RemoteInputSignal ?rsig."+
      " ?rsig c:IdentifiedObject.mRID ?rid."+
      " ?rsig c:RemoteInputSignal.Terminal ?trm."+
      " ?rsig c:RemoteInputSignal.remoteSignalType ?kindraw. bind(strafter(str(?kindraw),\"RemoteSignalKind.\") as ?kind)"+
      " ?trm c:IdentifiedObject.mRID ?tid."+
      "} "+
      "ORDER by ?name ?id");

    mapQueries.put ("DistIEEE1547Used",
      "SELECT DISTINCT ?name ?id ?pecid ?enabled ?cat ?acVnom ?acVmin ?acVmax ?sMax ?pMax ?pMaxOverPF ?overPF ?pMaxUnderPF ?underPF ?qMaxInj ?qMaxAbs ?pMaxCharge ?apparentPowerChargeMax ?fdrid"+
      " ?vvEnabled ?vvV1 ?vvV2 ?vvV3 ?vvV4 ?vvQ1 ?vvQ2 ?vvQ3 ?vvQ4 ?vvRef ?vvRefAuto ?vvRefOlrt ?vvOlrt"+
      " ?wvEnabled ?wvP1gen ?wvP2gen ?wvP3gen ?wvQ1gen ?wvQ2gen ?wvQ3gen ?wvP1load ?wvP2load ?wvP3load ?wvQ1load ?wvQ2load ?wvQ3load"+
      " ?pfEnabled ?powerFactor ?pfKind"+
      " ?cqEnabled ?reactivePower"+
      " ?vwEnabled ?vwV1 ?vwP1 ?vwV2 ?vwP2gen ?vwP2load ?vwOlrt "+
      " ?hasConstPF ?hasConstQ ?hasPV ?hasQV ?hasQP ?hasPF ?usePG ?usePN ?usePP "+
      "WHERE {"+
      " ?pec c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s r:type c:DERIEEEType1."+
      " ?s c:DERDynamics.PowerElectronicsConnection ?pec."+
      " ?s c:DERIEEEType1.phaseToGroundApplicable ?usePG."+
      " ?s c:DERIEEEType1.phaseToNeutralApplicable ?usePN."+
      " ?s c:DERIEEEType1.phaseToPhaseApplicable ?usePP."+
      " ?pec c:IdentifiedObject.mRID ?pecid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?s c:DynamicsFunctionBlock.enabled ?enabled."+
      " ?nd c:DERNameplateData.DERIEEEType1 ?s."+
      " ?nd c:DERNameplateData.acVmin ?acVmin."+
      " ?nd c:DERNameplateData.acVmax ?acVmax."+
      " ?nd c:DERNameplateData.normalOPcatKind ?catraw. bind(strafter(str(?catraw),\"NormalOPcatKind.\") as ?cat)"+
      " ?nd c:DERNameplateData.supportsConstPFmode ?hasConstPF."+
      " ?nd c:DERNameplateData.supportsConstQmode ?hasConstQ."+
      " ?nd c:DERNameplateData.supportsPVmode ?hasPV."+
      " ?nd c:DERNameplateData.supportsQVmode ?hasQV."+
      " ?nd c:DERNameplateData.supportsQPmode ?hasQP."+
      " ?nd c:DERNameplateData.supportsPFmode ?hasPF."+
      " ?ad c:DERNameplateDataApplied.DERNameplateData ?nd."+
      " ?ad c:DERNameplateDataApplied.acVnom ?acVnom."+
      " ?ad c:DERNameplateDataApplied.sMax ?sMax."+
      " ?ad c:DERNameplateDataApplied.pMax ?pMax."+
      " ?ad c:DERNameplateDataApplied.pMaxOverPF ?pMaxOverPF."+
      " ?ad c:DERNameplateDataApplied.overPF ?overPF."+
      " ?ad c:DERNameplateDataApplied.pMaxUnderPF ?pMaxUnderPF."+
      " ?ad c:DERNameplateDataApplied.underPF ?underPF."+
      " ?ad c:DERNameplateDataApplied.qMaxInj ?qMaxInj."+
      " ?ad c:DERNameplateDataApplied.qMaxAbs ?qMaxAbs."+
      " ?ad c:DERNameplateDataApplied.pMaxCharge ?pMaxCharge."+
      " ?ad c:DERNameplateDataApplied.apparentPowerChargeMax ?apparentPowerChargeMax."+
      " ?vv c:VoltVarSettings.DERIEEEType1 ?s."+
      " ?vv c:VoltVarSettings.enabled ?vvEnabled."+
      " ?vv c:VoltVarSettings.vRef ?vvRef."+
      " ?vv c:VoltVarSettings.vRefAutoModeEnabled ?vvRefAuto."+
      " ?vv c:VoltVarSettings.vRefOlrt ?vvRefOlrt."+
      " ?vv c:VoltVarSettings.curveV1 ?vvV1."+
      " ?vv c:VoltVarSettings.curveV2 ?vvV2."+
      " ?vv c:VoltVarSettings.curveV3 ?vvV3."+
      " ?vv c:VoltVarSettings.curveV4 ?vvV4."+
      " ?vv c:VoltVarSettings.curveQ1 ?vvQ1."+
      " ?vv c:VoltVarSettings.curveQ2 ?vvQ2."+
      " ?vv c:VoltVarSettings.curveQ3 ?vvQ3."+
      " ?vv c:VoltVarSettings.curveQ4 ?vvQ4."+
      " ?vv c:VoltVarSettings.olrt ?vvOlrt."+
      " ?wv c:WattVarSettings.DERIEEEType1 ?s."+
      " ?wv c:WattVarSettings.enabled ?wvEnabled."+
      " ?wv c:WattVarSettings.curveP1gen ?wvP1gen."+
      " ?wv c:WattVarSettings.curveP1load ?wvP1load."+
      " ?wv c:WattVarSettings.curveP2gen ?wvP2gen."+
      " ?wv c:WattVarSettings.curveP2load ?wvP2load."+
      " ?wv c:WattVarSettings.curveP3gen ?wvP3gen."+
      " ?wv c:WattVarSettings.curveP3load ?wvP3load."+
      " ?wv c:WattVarSettings.curveQ1gen ?wvQ1gen."+
      " ?wv c:WattVarSettings.curveQ1load ?wvQ1load."+
      " ?wv c:WattVarSettings.curveQ2gen ?wvQ2gen."+
      " ?wv c:WattVarSettings.curveQ2load ?wvQ2load."+
      " ?wv c:WattVarSettings.curveQ3gen ?wvQ3gen."+
      " ?wv c:WattVarSettings.curveQ3load ?wvQ3load."+
      " ?vw c:VoltWattSettings.DERIEEEType1 ?s."+
      " ?vw c:VoltWattSettings.enabled ?vwEnabled."+
      " ?vw c:VoltWattSettings.curveV1 ?vwV1."+
      " ?vw c:VoltWattSettings.curveP1 ?vwP1."+
      " ?vw c:VoltWattSettings.curveV2 ?vwV2."+
      " ?vw c:VoltWattSettings.curveP2gen ?vwP2gen."+
      " ?vw c:VoltWattSettings.curveP2load ?vwP2load."+
      " ?vw c:VoltWattSettings.olrt ?vwOlrt."+
      " ?pf c:ConstantPowerFactorSettings.DERIEEEType1 ?s."+
      " ?pf c:ConstantPowerFactorSettings.enabled ?pfEnabled."+
      " ?pf c:ConstantPowerFactorSettings.powerFactor ?powerFactor."+
      " ?pf c:ConstantPowerFactorSettings.constantPowerFactorExcitationKind ?pfraw. bind(strafter(str(?pfraw),\"ConstantPowerFactorSettingKind.\") as ?pfKind)"+
      " ?cq c:ConstantReactivePowerSettings.DERIEEEType1 ?s."+
      " ?cq c:ConstantReactivePowerSettings.enabled ?cqEnabled."+
      " ?cq c:ConstantReactivePowerSettings.reactivePower ?reactivePower."+
      "} "+
      "ORDER by ?name ?id");

    mapQueries.put ("DistTapeShieldCable",
      "SELECT DISTINCT ?name ?rad ?corerad ?gmr ?rdc ?r25 ?r50 ?r75 ?amps ?ins ?insmat"+
      " ?insthick ?diacore ?diains ?diascreen ?diajacket ?sheathneutral ?epsr"+
      " ?tapelap ?tapethickness ?id WHERE {"+
      " ?eq r:type c:ACLineSegment."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?acp c:ACLineSegmentPhase.ACLineSegment ?eq."+
      " ?acp c:ACLineSegmentPhase.WireInfo ?w."+
      " ?w r:type c:TapeShieldCableInfo."+
      " ?w c:IdentifiedObject.name ?name."+
      " ?w c:IdentifiedObject.mRID ?id."+
      " ?w c:WireInfo.radius ?rad."+
      " ?w c:WireInfo.gmr ?gmr."+
      " OPTIONAL {?w c:WireInfo.rDC20 ?rdc.}"+
      " OPTIONAL {?w c:WireInfo.rAC25 ?r25.}"+
      " OPTIONAL {?w c:WireInfo.rAC50 ?r50.}"+
      " OPTIONAL {?w c:WireInfo.rAC75 ?r75.}"+
      " OPTIONAL {?w c:WireInfo.coreRadius ?corerad.}"+
      " OPTIONAL {?w c:WireInfo.ratedCurrent ?amps.}"+
      " OPTIONAL {?w c:WireInfo.insulationMaterial ?insraw."+
      "       bind(strafter(str(?insraw),\"WireInsulationKind.\") as ?insmat)}"+
      " OPTIONAL {?w c:WireInfo.insulated ?ins.}"+
      " OPTIONAL {?w c:WireInfo.insulationThickness ?insthick.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverCore ?diacore.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverJacket ?diajacket.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverInsulation ?diains.}"+
      " OPTIONAL {?w c:CableInfo.diameterOverScreen ?diascreen.}"+
      " OPTIONAL {?w c:CableInfo.sheathAsNeutral ?sheathneutral.}"+
      " OPTIONAL {?w c:CableInfo.relativePermittivity ?epsr.}"+
      " OPTIONAL {?w c:TapeShieldCableInfo.tapeLap ?tapelap.}"+
      " OPTIONAL {?w c:TapeShieldCableInfo.tapeThickness ?tapethickness.}"+
      "} ORDER BY ?name");

    mapQueries.put ("DistThermostat",
      "SELECT ?name ?aggregatorName ?baseSetpoint ?controlMode ?priceCap ?rampHigh ?rampLow ?rangeHigh ?rangeLow ?useOverride ?usePredictive ?id ?fdrid "+
      "WHERE {"+
      " ?s r:type c:EnergyConsumer."+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:IdentifiedObject.name ?name."+
      " ?s c:IdentifiedObject.mRID ?id."+
      " ?s c:Thermostat.aggregatorName ?aggregatorName."+
      " ?bv c:Thermostat.baseSetpoint ?baseSetpoint."+
      " ?s c:Thermostat.controlMode ?controlMode."+
      " ?s c:Thermostat.priceCap ?priceCap."+
      " ?s c:Thermostat.rampHigh ?rampHigh."+
      " ?s c:Thermostat.rampLow ?rampLow."+
      " ?lr c:Thermostat.rangeHigh ?rangeHigh."+
      " ?lr c:Thermostat.rangeLow ?rangeLow."+
      " ?lr c:Thermostat.useOverride ?useOverride."+
      " ?lr c:Thermostat.usePredictive ?usePredictive."+
      " ?lr c:LoadResponseCharacteristic.pConstantPower ?pp."+
      " ?lr c:LoadResponseCharacteristic.qConstantPower ?qp."+
      " ?lr c:LoadResponseCharacteristic.pVoltageExponent ?pe."+
      " ?lr c:LoadResponseCharacteristic.qVoltageExponent ?qe."+
      " OPTIONAL {?ecp c:EnergyConsumerPhase.EnergyConsumer ?s"+
      "} "+
      "GROUP BY ?name ?aggregatorName ?baseSetpoint ?controlMode ?priceCap ?rampHigh ?rampLow ?rangeHigh ?rangeLow ?useOverride ?usePredictive ?id ?fdrid "+
      "ORDER BY ?name");

    mapQueries.put ("DistXfmrBank",
      "SELECT ?name ?id ?vgrp ?tid ?fdrid WHERE {"+
      " ?p r:type c:PowerTransformer."+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p c:IdentifiedObject.name ?name."+
      " ?p c:IdentifiedObject.mRID ?id."+
      " ?p c:PowerTransformer.vectorGroup ?vgrp."+
      " ?t c:TransformerTank.PowerTransformer ?p."+
      " ?t c:IdentifiedObject.mRID ?tid"+
      "} ORDER BY ?name");

    mapQueries.put ("DistXfmrCodeNLTest",
      "SELECT DISTINCT ?tid ?nll ?iexc ?base WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?xft c:TransformerTank.PowerTransformer ?eq."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?xft c:TransformerTank.TransformerTankInfo ?t."+
      " ?t c:IdentifiedObject.mRID ?tid."+
      " ?e c:TransformerEndInfo.TransformerTankInfo ?t."+
      " ?nlt c:NoLoadTest.EnergisedEnd ?e."+
      " ?nlt c:NoLoadTest.loss ?nll."+
      " ?nlt c:NoLoadTest.excitingCurrent ?iexc."+
      " ?nlt c:TransformerTest.basePower ?base."+
      "} ORDER BY ?tid");

    mapQueries.put ("DistXfmrCodeRating",
      "SELECT DISTINCT ?id ?name ?enum ?ratedS ?ratedU ?conn ?ang ?res ?eid WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?xft c:TransformerTank.PowerTransformer ?eq."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?xft c:TransformerTank.TransformerTankInfo ?t."+
      " ?e c:TransformerEndInfo.TransformerTankInfo ?t."+
      " ?e c:IdentifiedObject.mRID ?eid."+
      " ?t c:IdentifiedObject.mRID ?id."+
      " ?t c:IdentifiedObject.name ?name."+
      " ?e c:TransformerEndInfo.endNumber ?enum."+
      " ?e c:TransformerEndInfo.ratedS ?ratedS."+
      " ?e c:TransformerEndInfo.ratedU ?ratedU."+
      " ?e c:TransformerEndInfo.r ?res."+
      " ?e c:TransformerEndInfo.phaseAngleClock ?ang."+
      " ?e c:TransformerEndInfo.connectionKind ?connraw."+
      "         bind(strafter(str(?connraw),\"WindingConnection.\") as ?conn)"+
      "} ORDER BY ?id ?enum");

    mapQueries.put ("DistXfmrCodeSCTest",
      "SELECT DISTINCT ?tid ?enum ?gnum ?z ?ll ?base WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?xft c:TransformerTank.PowerTransformer ?eq."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?xft c:TransformerTank.TransformerTankInfo ?t."+
      " ?t c:IdentifiedObject.mRID ?tid."+
      " ?e c:TransformerEndInfo.TransformerTankInfo ?t."+
      " ?e c:TransformerEndInfo.endNumber ?enum."+
      " ?sct c:ShortCircuitTest.EnergisedEnd ?e."+
      " ?sct c:ShortCircuitTest.leakageImpedance ?z."+
      " ?sct c:ShortCircuitTest.loss ?ll."+
      " ?sct c:ShortCircuitTest.GroundedEnds ?grnd."+
      " ?grnd c:TransformerEndInfo.endNumber ?gnum."+
      " ?sct c:TransformerTest.basePower ?base."+
      "} ORDER BY ?tid ?enum ?gnum");

    mapQueries.put ("DistXfmrTank",
      "SELECT ?pid ?name ?vgrp ?enum ?bus ?basev ?orderedPhases ?reversed ?grounded ?rground ?xground ?id ?infoid ?fdrid ?eid ?t1id WHERE {"+
      " ?p r:type c:PowerTransformer."+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p c:IdentifiedObject.mRID ?pid."+
      " ?p c:PowerTransformer.vectorGroup ?vgrp."+
      " ?t c:TransformerTank.PowerTransformer ?p."+
      " ?t c:IdentifiedObject.name ?name."+
      " ?t c:TransformerTank.TransformerTankInfo ?inf."+
      " ?inf c:IdentifiedObject.mRID ?infoid."+
      " ?end c:TransformerTankEnd.TransformerTank ?t."+
      " ?end c:TransformerTankEnd.orderedPhases ?phsraw."+
      "  bind(strafter(str(?phsraw),\"OrderedPhaseCodeKind.\") as ?orderedPhases)"+
      " ?end c:TransformerEnd.endNumber ?enum."+
      " ?end c:TransformerEnd.grounded ?grounded."+
      " ?end c:IdentifiedObject.mRID ?eid."+
      " OPTIONAL {?end c:TransformerEnd.rground ?rground.}"+
      " OPTIONAL {?end c:TransformerEnd.xground ?xground.}"+
      " ?end c:TransformerEnd.Terminal ?trm."+
      " ?trm c:Terminal.ConnectivityNode ?cn."+ 
      " ?trm c:IdentifiedObject.mRID ?t1id."+
      " ?cn c:IdentifiedObject.mRID ?bus."+
      " ?t c:IdentifiedObject.mRID ?id."+
      " ?end c:TransformerEnd.BaseVoltage ?bv."+
      " ?bv c:BaseVoltage.nominalVoltage ?basev"+
      "}"+
      " ORDER BY ?pid ?id ?enum");

    mapQueries.put ("CountLinePhases",
      "SELECT ?key (count(?phs) as ?count) WHERE {"+
      " SELECT DISTINCT ?key ?phs WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?s c:Equipment.EquipmentContainer ?fdr."+
      " ?s r:type c:ACLineSegment."+
      " ?s c:IdentifiedObject.mRID ?key."+
      " OPTIONAL {?acp c:ACLineSegmentPhase.ACLineSegment ?s."+
      " ?acp c:ACLineSegmentPhase.phase ?phsraw."+
      " bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs)}"+
      "}} GROUP BY ?key ORDER BY ?key");

    mapQueries.put ("CountSpacingXY",
      "SELECT ?key (count(?seq) as ?count) WHERE {"+
      " SELECT DISTINCT ?key ?seq WHERE {"+
      " ?eq r:type c:ACLineSegment."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?eq c:ACLineSegment.WireSpacingInfo ?w."+
      " ?w c:IdentifiedObject.mRID ?key."+
      " ?pos c:WirePosition.WireSpacingInfo ?w."+
      " ?pos c:WirePosition.sequenceNumber ?seq."+
      "}} GROUP BY ?key ORDER BY ?key");

    mapQueries.put ("CountBankTanks",
      "SELECT ?key (count(?tank) as ?count) WHERE {"+
      " ?pxf c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?tank c:TransformerTank.PowerTransformer ?pxf."+
      " ?pxf c:IdentifiedObject.mRID ?key"+
      "} GROUP BY ?key ORDER BY ?key");

    mapQueries.put ("CountTankEnds",
      "SELECT ?key (count(?end) as ?count) WHERE {"+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p r:type c:PowerTransformer."+
      " ?t c:TransformerTank.PowerTransformer ?p."+
      " ?t c:IdentifiedObject.mRID ?key."+
      " ?end c:TransformerTankEnd.TransformerTank ?t"+
      "} GROUP BY ?key ORDER BY ?key");

    mapQueries.put ("CountXfmrMeshes",
      "SELECT ?key (count(?imp) as ?count) WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p r:type c:PowerTransformer."+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?p c:IdentifiedObject.mRID ?key."+
      " ?from c:PowerTransformerEnd.PowerTransformer ?p."+
      " ?imp c:TransformerMeshImpedance.FromTransformerEnd ?from."+
      "} GROUP BY ?key ORDER BY ?key");

    mapQueries.put ("CountXfmrWindings",
      "SELECT ?key (count(?p) as ?count) WHERE {"+
      " ?p r:type c:PowerTransformer."+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?p c:Equipment.EquipmentContainer ?fdr."+
      " ?p c:IdentifiedObject.mRID ?key."+
      " ?end c:PowerTransformerEnd.PowerTransformer ?p."+
      "} GROUP BY ?key ORDER BY ?key");

    mapQueries.put ("CountXfmrCodeRatings",
      "SELECT ?key (count(?enum) as ?count) WHERE {"+
      " SELECT DISTINCT ?key ?enum WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?xft c:TransformerTank.PowerTransformer ?eq."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?xft c:TransformerTank.TransformerTankInfo ?t."+
      " ?t c:IdentifiedObject.mRID ?key."+
      " ?e c:TransformerEndInfo.TransformerTankInfo ?t."+
      " ?e c:TransformerEndInfo.endNumber ?enum."+
      "}} GROUP BY ?key ORDER BY ?key");

    mapQueries.put ("CountXfmrCodeSCTests",
      "SELECT ?key (count(?sct) as ?count) WHERE {"+
      " SELECT DISTINCT ?key ?sct WHERE {"+
      " ?fdr c:IdentifiedObject.mRID ?fdrid."+
      " ?xft c:TransformerTank.PowerTransformer ?eq."+
      " ?eq c:Equipment.EquipmentContainer ?fdr."+
      " ?xft c:TransformerTank.TransformerTankInfo ?t."+
      " ?t c:IdentifiedObject.mRID ?key."+
      " ?e c:TransformerEndInfo.TransformerTankInfo ?t."+
      " ?sct c:ShortCircuitTest.EnergisedEnd ?e."+
      "}} GROUP BY ?key ORDER BY ?key");

    System.out.println ("Created Default SPARQL for: " + mapQueries.keySet());
  }
//  public static final String szQUERY = szSELECT + " ?s r:type c:LoadBreakSwitch." + szWHERE;



  public String getSelectionQuery (String id) {
    if (mapSwitchClasses.containsKey (id)) {
      return mapQueries.get("DistSwitchSelect") + " ?s r:type c:" + 
        mapSwitchClasses.get(id) + ". " + mapQueries.get("DistSwitchWhere");
    } else if (mapQueries.containsKey(id)) {
      return mapQueries.get(id);
    }
    return "***:" + id + ": not found ***";
  }

  String obj = "";
  StringBuilder buf = new StringBuilder("");
  String delims = "[ ]+";

  private boolean wantThisLine (String ln) {
    if (ln.length() < 0) return false;
    if (ln.contains("PREFIX")) return false;
    if (ln.startsWith("#")) return false;
    return true;
  }

  private String getCharacterDataFromElement(Element e) {
    NodeList list = e.getChildNodes();
    String data;
    for(int index = 0; index < list.getLength(); index++) {
      if(list.item(index) instanceof CharacterData) {
        CharacterData child = (CharacterData) list.item(index);
        data = child.getData();
        if (data != null && data.trim().length() > 0) {
          return child.getData();
        }
      }
    }
    return "";
  }

  private String condenseQuery (String root) {
    String lines[] = root.split("\\r?\\n");
    buf = new StringBuilder("");
    for (String ln : lines) {
      if (wantThisLine (ln)) buf.append (ln);
    }
    return buf.toString();
  }

  public void setQueriesFromXMLFile (String fname) {
    System.out.println ("Reading queries from XML file " + fname);
    try {
      DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
      DocumentBuilder db = dbf.newDocumentBuilder();
      Document doc = db.parse (new File (fname));
      Element elm = doc.getDocumentElement();

      NodeList namespaces = elm.getElementsByTagName ("nsCIM");
      for (int i = 0; i < namespaces.getLength(); i++) {
        Element nsElm = (Element) namespaces.item(i);
        String val = condenseQuery (getCharacterDataFromElement (nsElm));
        System.out.println ("nsCIM:" + val);
        DistComponent.nsCIM = val;
      }

      NodeList queries = elm.getElementsByTagName ("query");
      for (int i = 0; i < queries.getLength(); i++) {
        Element elmId = (Element) ((Element) queries.item(i)).getElementsByTagName("id").item(0);
        String id = getCharacterDataFromElement (elmId);
        Element elmVal = (Element) ((Element) queries.item(i)).getElementsByTagName("value").item(0);
        String val = condenseQuery (getCharacterDataFromElement (elmVal));
        boolean used = mapNewQuery (id, val);
        if (!used) {
          System.out.println(id + ":not matched");
        }
      }
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

  private boolean mapNewQuery (String id, String val) {
    if (mapQueries.containsKey (id)) {
      mapQueries.replace (id, val);
      return true;
    }
    return false;
  }
}

