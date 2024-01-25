package gov.pnnl.gridappsd.cimhub;
// ----------------------------------------------------------
// Copyright (c) 2017-2022, Battelle Memorial Institute
// All rights reserved.
// ----------------------------------------------------------

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.SortedSet;
import java.util.TreeSet;

import org.apache.jena.query.QuerySolution;
import org.apache.jena.query.ResultSet;
import org.apache.jena.query.ResultSetCloseable;

import gov.pnnl.gridappsd.cimhub.CIMQuerySetter;
import gov.pnnl.gridappsd.cimhub.components.DistBaseVoltage;
import gov.pnnl.gridappsd.cimhub.components.DistBreaker;
import gov.pnnl.gridappsd.cimhub.components.DistBus;
import gov.pnnl.gridappsd.cimhub.components.DistCapacitor;
import gov.pnnl.gridappsd.cimhub.components.DistComponent;
import gov.pnnl.gridappsd.cimhub.components.DistConcentricNeutralCable;
import gov.pnnl.gridappsd.cimhub.components.DistCoordinates;
import gov.pnnl.gridappsd.cimhub.components.DistDisconnector;
import gov.pnnl.gridappsd.cimhub.components.DistEnergyConnectionProfile;
import gov.pnnl.gridappsd.cimhub.components.DistEquipment;
import gov.pnnl.gridappsd.cimhub.components.DistFeeder;
import gov.pnnl.gridappsd.cimhub.components.DistFuse;
import gov.pnnl.gridappsd.cimhub.components.DistGroundDisconnector;
import gov.pnnl.gridappsd.cimhub.components.DistHouse;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Connection;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Signal;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Used;
import gov.pnnl.gridappsd.cimhub.components.DistJumper;
import gov.pnnl.gridappsd.cimhub.components.DistLineSegment;
import gov.pnnl.gridappsd.cimhub.components.DistLineSpacing;
import gov.pnnl.gridappsd.cimhub.components.DistLinesCodeZ;
import gov.pnnl.gridappsd.cimhub.components.DistLinesInstanceZ;
import gov.pnnl.gridappsd.cimhub.components.DistLinesSpacingZ;
import gov.pnnl.gridappsd.cimhub.components.DistLoad;
import gov.pnnl.gridappsd.cimhub.components.DistLoadBreakSwitch;
import gov.pnnl.gridappsd.cimhub.components.DistMeasurement;
import gov.pnnl.gridappsd.cimhub.components.DistOverheadWire;
import gov.pnnl.gridappsd.cimhub.components.DistPhaseMatrix;
import gov.pnnl.gridappsd.cimhub.components.DistPowerXfmrCore;
import gov.pnnl.gridappsd.cimhub.components.DistPowerXfmrMesh;
import gov.pnnl.gridappsd.cimhub.components.DistPowerXfmrWinding;
import gov.pnnl.gridappsd.cimhub.components.DistRecloser;
import gov.pnnl.gridappsd.cimhub.components.DistRegulator;
import gov.pnnl.gridappsd.cimhub.components.DistSectionaliser;
import gov.pnnl.gridappsd.cimhub.components.DistSequenceMatrix;
import gov.pnnl.gridappsd.cimhub.components.DistSeriesCompensator;
import gov.pnnl.gridappsd.cimhub.components.DistSolar;
import gov.pnnl.gridappsd.cimhub.components.DistStorage;
import gov.pnnl.gridappsd.cimhub.components.DistSubstation;
import gov.pnnl.gridappsd.cimhub.components.DistSwitch;
import gov.pnnl.gridappsd.cimhub.components.DistSyncMachine;
import gov.pnnl.gridappsd.cimhub.components.DistTapeShieldCable;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrBank;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeNLTest;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeRating;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeSCTest;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrTank;
import gov.pnnl.gridappsd.cimhub.dto.ModelState;
import gov.pnnl.gridappsd.cimhub.dto.Switch;
import gov.pnnl.gridappsd.cimhub.dto.SyncMachine;
import gov.pnnl.gridappsd.cimhub.queryhandler.QueryHandler;
import gov.pnnl.gridappsd.cimhub.queryhandler.impl.HTTPBlazegraphQueryHandler;
import gov.pnnl.gridappsd.cimhub.components.ExportNameMode;

/**
 * <p>This class builds a GridLAB-D or OpenDSS model by running
 * SQARQL queries against Blazegraph
 * triple-store</p>
 *
 * <p>Invoke as a console-mode program</p>
 *
 * @see CIMImporter#main
 *
 * @author Tom McDermott
 * @version 1.0
 *
 */

public class CIMImporter extends Object {
  QueryHandler queryHandler;
  CIMQuerySetter querySetter;
  OperationalLimits oLimits;

  HashMap<String,CIMTerminal> mapTerminals = new HashMap<>();

  HashMap<String,GldNode> mapNodes = new HashMap<>();
  HashMap<String,GldLineConfig> mapLineConfigs = new HashMap<>();

  HashMap<String,Integer> mapCountMesh = new HashMap<>();
  HashMap<String,Integer> mapCountWinding = new HashMap<>();
  HashMap<String,Integer> mapCountCodeRating = new HashMap<>();
  HashMap<String,Integer> mapCountCodeSCTest = new HashMap<>();
  HashMap<String,Integer> mapCountTank = new HashMap<>();
  HashMap<String,Integer> mapCountBank = new HashMap<>();
  HashMap<String,Integer> mapCountLinePhases = new HashMap<>();
  HashMap<String,Integer> mapCountSpacingXY = new HashMap<>();

  HashMap<String,DistBaseVoltage> mapBaseVoltages = new HashMap<>();
  HashMap<String,DistBreaker> mapBreakers = new HashMap<>();
  HashMap<String,DistCapacitor> mapCapacitors = new HashMap<>();
  HashMap<String,DistConcentricNeutralCable> mapCNCables = new HashMap<>();
  HashMap<String,DistCoordinates> mapCoordinates = new HashMap<>();
  HashMap<String,DistDisconnector> mapDisconnectors = new HashMap<>();
  HashMap<String,DistEnergyConnectionProfile> mapDssProfiles = new HashMap<>();
  HashMap<String,DistEnergyConnectionProfile> mapGlmProfiles = new HashMap<>();
  HashMap<String,DistFeeder> mapFeeders = new HashMap<>();
  HashMap<String,DistFuse> mapFuses = new HashMap<>();
  HashMap<String,DistGroundDisconnector> mapGroundDisconnectors = new HashMap<>();
  HashMap<String,DistIEEE1547Connection> mapIEEE1547Connections = new HashMap<>();
  HashMap<String,DistIEEE1547Signal> mapIEEE1547Signals = new HashMap<>();
  HashMap<String,DistIEEE1547Used> mapIEEE1547Used = new HashMap<>();
  HashMap<String,DistJumper> mapJumpers = new HashMap<>();
  HashMap<String,DistLinesCodeZ> mapLinesCodeZ = new HashMap<>();
  HashMap<String,DistLinesInstanceZ> mapLinesInstanceZ = new HashMap<>();
  HashMap<String,DistLineSpacing> mapSpacings = new HashMap<>();
  HashMap<String,DistLinesSpacingZ> mapLinesSpacingZ = new HashMap<>();
  HashMap<String,DistLoad> mapLoads = new HashMap<>();
  HashMap<String,DistLoadBreakSwitch> mapLoadBreakSwitches = new HashMap<>();
  HashMap<String,DistOverheadWire> mapWires = new HashMap<>();
  HashMap<String,DistPhaseMatrix> mapPhaseMatrices = new HashMap<>();
  HashMap<String,DistPowerXfmrCore> mapXfmrCores = new HashMap<>();
  HashMap<String,DistPowerXfmrMesh> mapXfmrMeshes = new HashMap<>();
  HashMap<String,DistPowerXfmrWinding> mapXfmrWindings = new HashMap<>();
  HashMap<String,DistRecloser> mapReclosers = new HashMap<>();
  HashMap<String,DistRegulator> mapRegulators = new HashMap<>();
  HashMap<String,DistSectionaliser> mapSectionalisers = new HashMap<>();
  HashMap<String,DistSequenceMatrix> mapSequenceMatrices = new HashMap<>();
  HashMap<String,DistSeriesCompensator> mapSeriesCompensators = new HashMap<>();
  HashMap<String,DistSolar> mapSolars = new HashMap<>();
  HashMap<String,DistStorage> mapStorages = new HashMap<>();
  HashMap<String,DistSubstation> mapSubstations = new HashMap<>();
  HashMap<String,DistSyncMachine> mapSyncMachines = new HashMap<>();
  HashMap<String,DistTapeShieldCable> mapTSCables = new HashMap<>();
  HashMap<String,DistXfmrCodeNLTest> mapCodeNLTests = new HashMap<>();
  HashMap<String,DistXfmrCodeRating> mapCodeRatings = new HashMap<>();
  HashMap<String,DistXfmrCodeSCTest> mapCodeSCTests = new HashMap<>();
  HashMap<String,DistXfmrTank> mapTanks = new HashMap<>();
  HashMap<String,DistXfmrBank> mapBanks = new HashMap<>();
  HashMap<String,DistMeasurement> mapMeasurements = new HashMap<>();
  HashMap<String,DistHouse> mapHouses = new HashMap<>();

  HashMap<String,DistSwitch> mapSwitches = new HashMap<>(); // polymorphic
  HashMap<String,DistLineSegment> mapLines = new HashMap<>(); // polymorphic

  boolean allMapsLoaded = false;

  void LoadOneCountMap (HashMap<String,Integer> map, String szTag) {
    String szQuery = querySetter.getSelectionQuery (szTag);
    ResultSet results = queryHandler.query (szQuery, szTag);
    while (results.hasNext()) {
      QuerySolution soln = results.next();
      String key = DistComponent.SafeName (soln.get("?key").toString());
      int count = soln.getLiteral("?count").getInt();
      map.put (key, count);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadCountMaps() {
    LoadOneCountMap (mapCountBank, "CountBankTanks");
    LoadOneCountMap (mapCountTank, "CountTankEnds");
    LoadOneCountMap (mapCountMesh, "CountXfmrMeshes");
    LoadOneCountMap (mapCountWinding, "CountXfmrWindings");
    LoadOneCountMap (mapCountCodeRating, "CountXfmrCodeRatings");
    LoadOneCountMap (mapCountCodeSCTest, "CountXfmrCodeSCTests");
    LoadOneCountMap (mapCountLinePhases, "CountLinePhases");
    LoadOneCountMap (mapCountSpacingXY, "CountSpacingXY");
  //  PrintAllCountMaps ();
  }

  void LoadBaseVoltages() {
    boolean b208 = false;
    boolean b240 = false;
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistBaseVoltage"), "BaseVoltage");
    while (results.hasNext()) {
      DistBaseVoltage obj = new DistBaseVoltage (results);
      mapBaseVoltages.put (obj.GetKey(), obj);
      if (Math.abs(obj.vnom - 208.0) < 0.1) b208 = true;
      if (Math.abs(obj.vnom - 240.0) < 0.1) b240 = true;
    }
    ((ResultSetCloseable)results).close();
    // if 240V is a base voltage for split-phase, make sure 208V is also a voltage base for pu reporting
    if (b240 && !b208) {
      DistBaseVoltage bvCust = new DistBaseVoltage("208", 208.0);
      mapBaseVoltages.put(bvCust.GetKey(), bvCust);
    }
  }

  void LoadBusNames() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistBus"), "BusName");
    while (results.hasNext()) {
      DistBus obj = new DistBus (results);
      DistComponent.mapBusNames.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }
/*
  void LoadEquipmentNames() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistEquipment"), "EquipmentName");
    while (results.hasNext()) {
      DistEquipment obj = new DistEquipment (results);
      mapEquipmentNames.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }
*/
  void LoadSubstations() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistSubstation"), "Substation");
    while (results.hasNext()) {
      DistSubstation obj = new DistSubstation (results);
      mapSubstations.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadEnergyConnectionProfiles() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistEnergyConnectionProfile"), "EnergyConnectionProfile");
    while (results.hasNext()) {
      DistEnergyConnectionProfile obj = new DistEnergyConnectionProfile (results);
      if (obj.ForDSS()) mapDssProfiles.put (obj.GetKey(), obj);
      if (obj.ForGLM()) mapGlmProfiles.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadSolars() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistSolar"), "Solar");
    while (results.hasNext()) {
      DistSolar obj = new DistSolar (results);
      mapSolars.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadMeasurements(boolean useHouses) {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistMeasurement"), "Measurement");
    while (results.hasNext()) {
      DistMeasurement obj = new DistMeasurement (results, useHouses);
      mapMeasurements.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadStorages() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistStorage"), "Storage");
    while (results.hasNext()) {
      DistStorage obj = new DistStorage (results);
      mapStorages.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadCapacitors() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistCapacitor"), "Capacitor");
    while (results.hasNext()) {
      DistCapacitor obj = new DistCapacitor (results);
      mapCapacitors.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadLoads() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistLoad"), "Load");
    while (results.hasNext()) {
      DistLoad obj = new DistLoad (results);
      mapLoads.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadPhaseMatrices() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistPhaseMatrix"), "PhaseMatrix");
    while (results.hasNext()) {
      DistPhaseMatrix obj = new DistPhaseMatrix (results);
      mapPhaseMatrices.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadSequenceMatrices() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistSequenceMatrix"), "SequenceMatrix");
    while (results.hasNext()) {
      DistSequenceMatrix obj = new DistSequenceMatrix (results);
      mapSequenceMatrices.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadXfmrCodeRatings() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistXfmrCodeRating"), "XfmrCodeRating");
    while (results.hasNext()) {
      DistXfmrCodeRating obj = new DistXfmrCodeRating (results, mapCountCodeRating);
      mapCodeRatings.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadXfmrCodeNLTests() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistXfmrCodeNLTest"), "XfmrCodeNLTest");
    while (results.hasNext()) {
      DistXfmrCodeNLTest obj = new DistXfmrCodeNLTest (results);
      mapCodeNLTests.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadXfmrCodeSCTests() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistXfmrCodeSCTest"), "XfmrCodeSCTest");
    while (results.hasNext()) {
      DistXfmrCodeSCTest obj = new DistXfmrCodeSCTest (results, mapCountCodeSCTest);
      mapCodeSCTests.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadPowerXfmrCore() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistPowerXfmrCore"), "PowerXfmrCore");
    while (results.hasNext()) {
      DistPowerXfmrCore obj = new DistPowerXfmrCore (results);
      mapXfmrCores.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadPowerXfmrMesh() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistPowerXfmrMesh"), "PowerXfmrMesh");
    while (results.hasNext()) {
      DistPowerXfmrMesh obj = new DistPowerXfmrMesh (results, mapCountMesh);
      mapXfmrMeshes.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadOverheadWires() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistOverheadWire"), "OverheadWire");
    while (results.hasNext()) {
      DistOverheadWire obj = new DistOverheadWire (results);
      mapWires.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadTapeShieldCables() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistTapeShieldCable"), "TSCable");
    while (results.hasNext()) {
      DistTapeShieldCable obj = new DistTapeShieldCable (results);
      mapTSCables.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadConcentricNeutralCables() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistConcentricNeutralCable"), "CNCable");
    while (results.hasNext()) {
      DistConcentricNeutralCable obj = new DistConcentricNeutralCable (results);
      mapCNCables.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadLineSpacings() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistLineSpacing"), "LineSpacing");
    while (results.hasNext()) {
      DistLineSpacing obj = new DistLineSpacing (results, mapCountSpacingXY);
      mapSpacings.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadLoadBreakSwitches() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistLoadBreakSwitch"), "LoadBreakSwitch");
    while (results.hasNext()) {
      DistLoadBreakSwitch obj = new DistLoadBreakSwitch (results);
      mapLoadBreakSwitches.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadFuses() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistFuse"), "Fuse");
    while (results.hasNext()) {
      DistFuse obj = new DistFuse (results);
      mapFuses.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadDisconnectors() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistDisconnector"), "Disconnector");
    while (results.hasNext()) {
      DistDisconnector obj = new DistDisconnector (results);
      mapDisconnectors.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadGroundDisconnectors() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistGroundDisconnector"), "GroundDisconnector");
    while (results.hasNext()) {
      DistGroundDisconnector obj = new DistGroundDisconnector (results);
      mapGroundDisconnectors.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadJumpers() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistJumper"), "Jumper");
    while (results.hasNext()) {
      DistJumper obj = new DistJumper (results);
      mapJumpers.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadBreakers() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistBreaker"), "Breaker");
    while (results.hasNext()) {
      DistBreaker obj = new DistBreaker (results);
      mapBreakers.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadReclosers() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistRecloser"), "Recloser");
    while (results.hasNext()) {
      DistRecloser obj = new DistRecloser (results);
      mapReclosers.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadSectionalisers() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistSectionaliser"), "Sectionaliser");
    while (results.hasNext()) {
      DistSectionaliser obj = new DistSectionaliser (results);
      mapSectionalisers.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadSeriesCompensators() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistSeriesCompensator"), "SeriesCompensator");
    while (results.hasNext()) {
      DistSeriesCompensator obj = new DistSeriesCompensator (results);
      mapSeriesCompensators.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadLinesInstanceZ() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistLinesInstanceZ"), "LinesInstanceZ");
    while (results.hasNext()) {
      DistLinesInstanceZ obj = new DistLinesInstanceZ (results, mapCountLinePhases);
      mapLinesInstanceZ.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadLinesCodeZ() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistLinesCodeZ"), "LinesCodeZ");
    while (results.hasNext()) {
      DistLinesCodeZ obj = new DistLinesCodeZ (results, mapCountLinePhases);
      mapLinesCodeZ.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadLinesSpacingZ() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistLinesSpacingZ"), "LinesSpacingZ");
    while (results.hasNext()) {
      DistLinesSpacingZ obj = new DistLinesSpacingZ (results, mapCountLinePhases);
      mapLinesSpacingZ.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadRegulators() {
    String szQuery = querySetter.getSelectionQuery ("DistRegulatorPrefix") +
      querySetter.getSelectionQuery ("DistRegulatorBanked") + querySetter.getSelectionQuery ("DistRegulatorSuffix");
    ResultSet results = queryHandler.query (szQuery, "DistRegulatorBanked");
    while (results.hasNext()) {
      DistRegulator obj = new DistRegulator (results, queryHandler);
      mapRegulators.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  //  System.out.format ("%d Banked Regulators\n", mapRegulators.size());

    szQuery = querySetter.getSelectionQuery ("DistRegulatorPrefix") +
      querySetter.getSelectionQuery ("DistRegulatorTanked") + querySetter.getSelectionQuery ("DistRegulatorSuffix");
    results = queryHandler.query (szQuery, "DistRegulatorTanked");
    while (results.hasNext()) {
      DistRegulator obj = new DistRegulator (results, queryHandler);
      mapRegulators.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  //  System.out.format ("%d Banked plus By-phase Regulators\n", mapRegulators.size());
  }

  void LoadXfmrTanks() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistXfmrTank"), "XfmrTank");
    while (results.hasNext()) {
      DistXfmrTank obj = new DistXfmrTank (results, mapCountTank);
      mapTanks.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadXfmrBanks() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistXfmrBank"), "XfmrBank");
    while (results.hasNext()) {
      DistXfmrBank obj = new DistXfmrBank (results, mapCountBank);
      mapBanks.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadPowerXfmrWindings() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistPowerXfmrWinding"), "PowerXfmrWinding");
    while (results.hasNext()) {
      DistPowerXfmrWinding obj = new DistPowerXfmrWinding (results, mapCountWinding);
      mapXfmrWindings.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadCoordinates() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistCoordinates"), "Coordinate");
    while (results.hasNext()) {
      DistCoordinates obj = new DistCoordinates (results);
      mapCoordinates.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadFeeders() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistFeeder"), "Feeder");
    while (results.hasNext()) {
      DistFeeder obj = new DistFeeder (results);
      mapFeeders.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadHouses() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistHouse"), "House");
    while (results.hasNext()) {
      DistHouse obj = new DistHouse (results);
      mapHouses.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadSyncMachines() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistSyncMachine"), "SyncMach");
    while (results.hasNext()) {
      DistSyncMachine obj = new DistSyncMachine (results);
      mapSyncMachines.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadIEEE1547Connections() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistIEEE1547Connection"), "I1547Conn");
    while (results.hasNext()) {
      DistIEEE1547Connection obj = new DistIEEE1547Connection (results);
      mapIEEE1547Connections.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadIEEE1547Signals() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistIEEE1547Signal"), "I1547Sig");
    while (results.hasNext()) {
      DistIEEE1547Signal obj = new DistIEEE1547Signal (results);
      mapIEEE1547Signals.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  void LoadIEEE1547Used() {
    ResultSet results = queryHandler.query (querySetter.getSelectionQuery ("DistIEEE1547Used"), "I1547Used");
    while (results.hasNext()) {
      DistIEEE1547Used obj = new DistIEEE1547Used (results);
      mapIEEE1547Used.put (obj.GetKey(), obj);
    }
    ((ResultSetCloseable)results).close();
  }

  public void PrintOneMap(HashMap<String,? extends DistComponent> map, String label) {
    System.out.println(label);
    SortedSet<String> keys = new TreeSet<String>(map.keySet());
    for (String key : keys) {
      System.out.println (map.get(key).DisplayString());
    }
  }

  public void PrintOneCountMap(HashMap<String,Integer> map, String label) {
    System.out.println(label);
    SortedSet<String> keys = new TreeSet<String>(map.keySet());
    for (String key : keys) {
      System.out.println (key + ":" + Integer.toString (map.get(key)));
    }
  }

  public void PrintGldNodeMap(HashMap<String,GldNode> map, String label) {
    System.out.println(label);
    SortedSet<String> keys = new TreeSet<String>(map.keySet());
    for (String key : keys) {
      System.out.println (map.get(key).DisplayString());
    }
  }

  public void PrintTerminalMap(HashMap<String,CIMTerminal> map, String label) {
    System.out.println(label);
    SortedSet<String> keys = new TreeSet<String>(map.keySet());
    for (String key : keys) {
      System.out.println (map.get(key).DisplayString());
    }
  }

  public void PrintAllCountMaps () {
    PrintOneCountMap (mapCountBank, "Count of Bank Tanks");
    PrintOneCountMap (mapCountTank, "Count of Tank Ends");
    PrintOneCountMap (mapCountMesh, "Count of Xfmr Meshes");
    PrintOneCountMap (mapCountWinding, "Count of Xfmr Windings");
    PrintOneCountMap (mapCountCodeRating, "Count of XfmrCode Ratings");
    PrintOneCountMap (mapCountCodeSCTest, "Count of XfmrCode SCTests");
    PrintOneCountMap (mapCountLinePhases, "Count of Line Phases");
    PrintOneCountMap (mapCountSpacingXY, "Count of Spacing XY Positions");
  }

  public void PrintAllMaps() {
    PrintOneMap (mapBaseVoltages, "** BASE VOLTAGES");
    PrintOneMap (mapCapacitors, "** CAPACITORS");
    PrintOneMap (mapCNCables, "** CN CABLES");
    PrintOneMap (mapCoordinates, "** COMPONENT XY COORDINATES");
    PrintOneMap (mapLinesCodeZ, "** LINES REFERENCING MATRICES");
    PrintOneMap (mapLinesInstanceZ, "** LINES WITH IMPEDANCE ATTRIBUTES");
    PrintOneMap (mapSeriesCompensators, "** SERIES COMPENSATORS (Reactors only)");
    PrintOneMap (mapSpacings, "** LINE SPACINGS");
    PrintOneMap (mapLinesSpacingZ, "** LINES REFERENCING SPACINGS");
    PrintOneMap (mapBreakers, "** BREAKERS");
    PrintOneMap (mapReclosers, "** RECLOSERS");
    PrintOneMap (mapFuses, "** FUSES");
    PrintOneMap (mapLoadBreakSwitches, "** LOADBREAK SWITCHES");
    PrintOneMap (mapSectionalisers, "** SECTIONALISERS");
    PrintOneMap (mapJumpers, "** JUMPERS");
    PrintOneMap (mapDisconnectors, "** DISCONNECTORS");
    PrintOneMap (mapGroundDisconnectors, "** GROUND DISCONNECTORS");
    PrintOneMap (mapLoads, "** LOADS");
    PrintOneMap (mapWires, "** OVERHEAD WIRES");
    PrintOneMap (mapPhaseMatrices, "** PHASE IMPEDANCE MATRICES");
    PrintOneMap (mapXfmrCores, "** POWER XFMR CORE ADMITTANCES");
    PrintOneMap (mapXfmrMeshes, "** POWER XFMR MESH IMPEDANCES");
    PrintOneMap (mapXfmrWindings, "** POWER XFMR WINDINGS");
    PrintOneMap (mapRegulators, "** REGULATORS");
    PrintOneMap (mapSequenceMatrices, "** SEQUENCE IMPEDANCE MATRICES");
    PrintOneMap (mapSolars, "** SOLAR PV SOURCES");
    PrintOneMap (mapStorages, "** STORAGE SOURCES");
    PrintOneMap (mapSubstations, "** SUBSTATION SOURCES");
    PrintOneMap (mapTSCables, "** TS CABLES");
    PrintOneMap (mapCodeNLTests, "** XFMR CODE OC TESTS");
    PrintOneMap (mapCodeRatings, "** XFMR CODE WINDING RATINGS");
    PrintOneMap (mapCodeSCTests, "** XFMR CODE SC TESTS");
    PrintOneMap (mapBanks, "** XFMR BANKS");
    PrintOneMap (mapTanks, "** XFMR TANKS");
    PrintOneMap (mapHouses, "** HOUSES");
    PrintOneMap (mapSyncMachines, "** SYNC MACHINES");
    PrintOneMap (mapIEEE1547Connections, "** IEEE 1547 CONNECTIONS");
    PrintOneMap (mapIEEE1547Signals, "** IEEE 1547 SIGNALS");
    PrintOneMap (mapIEEE1547Used, "** IEEE 1547 USED");
    PrintOneMap (mapDssProfiles, "** ENERGY CONNECTION PROFILES (DSS)");
    PrintOneMap (mapGlmProfiles, "** ENERGY CONNECTION PROFILES (GLM)");
    PrintOneMap (DistComponent.mapBusNames, "** BUS NAMES");
    PrintOneMap (DistComponent.mapEquipmentNames, "** CONDUCTING EQUIPMENT NAMES");
  }

  public void LoadAllMaps() {
    boolean useHouses = false;
    LoadAllMaps(useHouses);
  }

  public void LoadAllMaps(boolean useHouses) {
    LoadCountMaps();
    LoadBusNames();
    // PrintOneMap (DistComponent.mapBusNames, "** Bus (ConnectivityNode) names");

    LoadBaseVoltages();
    LoadBreakers();
    LoadCapacitors();
    LoadConcentricNeutralCables();
    LoadCoordinates();
    LoadDisconnectors();
    LoadFuses();
    LoadJumpers();
    LoadSeriesCompensators();
    LoadLinesCodeZ();
    LoadLinesInstanceZ();
    LoadLineSpacings();
    LoadLinesSpacingZ();
    LoadLoadBreakSwitches();
    LoadLoads();
    LoadMeasurements(useHouses);
    LoadOverheadWires();
    LoadPhaseMatrices();
    LoadPowerXfmrCore();
    LoadPowerXfmrMesh();
    LoadPowerXfmrWindings();
    LoadReclosers();
    LoadRegulators();
    LoadSectionalisers();
    LoadSequenceMatrices();
    LoadSolars();
    LoadStorages();
    LoadSubstations();
    LoadTapeShieldCables();
    LoadXfmrCodeNLTests();
    LoadXfmrCodeRatings();
    LoadXfmrCodeSCTests();
    LoadXfmrTanks();
    LoadXfmrBanks();
    LoadFeeders();
    LoadHouses();
    LoadSyncMachines();
    LoadIEEE1547Connections();
    LoadIEEE1547Signals();
    LoadIEEE1547Used();
    LoadEnergyConnectionProfiles();

    MakeSwitchMap();
    MakeLineMap();

    oLimits = new OperationalLimits();
    oLimits.BuildLimitMaps (this, queryHandler, mapCoordinates);
    allMapsLoaded = true;
    //PrintOneMap (DistComponent.mapBusNames, "** Bus (ConnectivityNode) names");
    //PrintOneMap (DistComponent.mapEquipmentNames, "** ConductingEquipment names");
  }

  public void PrepMapsForExport() { // apply ExportNameMode
    for (HashMap.Entry<String, DistCapacitor> pair: mapCapacitors.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistEnergyConnectionProfile> pair: mapDssProfiles.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistEnergyConnectionProfile> pair: mapGlmProfiles.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistHouse> pair: mapHouses.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistLinesCodeZ> pair: mapLinesCodeZ.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistLinesSpacingZ> pair: mapLinesSpacingZ.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistMeasurement> pair: mapMeasurements.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistRegulator> pair: mapRegulators.entrySet()) pair.getValue().PrepForExport();
    for (HashMap.Entry<String, DistXfmrTank> pair: mapTanks.entrySet()) pair.getValue().PrepForExport();
  }

  public boolean CheckMaps() {
    int nLinks, nNodes;
  /*  CIMPatching patch = new CIMPatching();
    patch.FixLoads (mapLoads);
    patch.FixOverheadWires (mapWires);
    patch.FixCapacitors (mapCapacitors);
    patch.FixLineSpacings (mapSpacings);
    patch.FixLinesSpacingZ (mapLinesSpacingZ);
    patch.FixTransformerKVA (mapCodeRatings);
    patch.FixShortCircuitTests (mapCodeSCTests, mapCodeRatings);  // must do this after FixTransformerKVA
  */
    if (mapSubstations.size() < 1) {
      throw new RuntimeException ("no substation source");
    }
    nLinks = mapLoadBreakSwitches.size() + mapLinesCodeZ.size() + mapLinesSpacingZ.size() + mapLinesInstanceZ.size() +
      mapXfmrWindings.size() + mapTanks.size() + mapFuses.size() + mapDisconnectors.size() + mapBreakers.size() +
      mapReclosers.size() + mapSectionalisers.size() + mapJumpers.size() + mapSeriesCompensators.size(); // standalone regulators not allowed in CIM
    if (nLinks < 1) {
      throw new RuntimeException ("no lines, reactors, transformers or switches");
    }
    nNodes = mapLoads.size() + mapCapacitors.size() + mapSolars.size() + mapStorages.size() + mapSyncMachines.size();
    if (nNodes < 1) {
      throw new RuntimeException ("no loads, capacitors, synchronous machines, solar PV or batteries");
    }
    return true;
  }

  public boolean ApplyCurrentLimits() {
    // apply available current limits to a polymorphic map of line segments
    HashMap<String,DistLineSegment> mapSegments = new HashMap<>();
    mapSegments.putAll (mapLinesInstanceZ);
    mapSegments.putAll (mapLinesCodeZ);
    mapSegments.putAll (mapLinesSpacingZ);
    for (HashMap.Entry<String,DistLineSegment> pair : mapSegments.entrySet()) {
      DistLineSegment obj = pair.getValue();
      if (oLimits.mapCurrentLimits.containsKey (obj.id)) {
        double[] vals = oLimits.mapCurrentLimits.get(obj.id);
        obj.normalCurrentLimit = vals[0];
        obj.emergencyCurrentLimit = vals[1];
      }
    }

    // ... to a polymorphic map of switches
    for (HashMap.Entry<String,DistSwitch> pair : mapSwitches.entrySet()) {
      DistSwitch obj = pair.getValue();
      if (oLimits.mapCurrentLimits.containsKey (obj.id)) {
        double[] vals = oLimits.mapCurrentLimits.get(obj.id);
        obj.normalCurrentLimit = vals[0];
        obj.emergencyCurrentLimit = vals[1];
      }
    }

    // to transformers and tanks
    for (HashMap.Entry<String,DistPowerXfmrWinding> pair : mapXfmrWindings.entrySet()) {
      DistPowerXfmrWinding obj = pair.getValue();
      if (oLimits.mapCurrentLimits.containsKey (obj.id)) {
        double[] vals = oLimits.mapCurrentLimits.get(obj.id);
        obj.normalCurrentLimit = vals[0];
        obj.emergencyCurrentLimit = vals[1];
      }
    }
    for (HashMap.Entry<String,DistXfmrTank> pair : mapTanks.entrySet()) {
      DistXfmrTank obj = pair.getValue();
      if (oLimits.mapCurrentLimits.containsKey (obj.id)) {
        double[] vals = oLimits.mapCurrentLimits.get(obj.id);
        obj.normalCurrentLimit = vals[0];
        obj.emergencyCurrentLimit = vals[1];
      }
    }

    // to regulators, for GridLAB-D (ratings for OpenDSS regulators are already on the transformer)
    // TODO: we can also use the CT primary ratings if pxfid fails to work in some cases
    for (HashMap.Entry<String,DistRegulator> pair : mapRegulators.entrySet()) {
      DistRegulator obj = pair.getValue();
      if (oLimits.mapCurrentLimits.containsKey (obj.pid)) {
        double[] vals = oLimits.mapCurrentLimits.get(obj.pid);
        obj.normalCurrentLimit = vals[0];
        obj.emergencyCurrentLimit = vals[1];
      }
    }

    // to series compensators
    for (HashMap.Entry<String,DistSeriesCompensator> pair : mapSeriesCompensators.entrySet()) {
      DistSeriesCompensator obj = pair.getValue();
      if (oLimits.mapCurrentLimits.containsKey (obj.id)) {
        double[] vals = oLimits.mapCurrentLimits.get(obj.id);
        obj.normalCurrentLimit = vals[0];
        obj.emergencyCurrentLimit = vals[1];
      }
    }

    return true;
  }

  public void WriteMapDictionary (HashMap<String,? extends DistComponent> map, String label, boolean bLast, PrintWriter out){
    WriteMapDictionary(map, label, bLast, out, -1);
  }

  public void WriteMapDictionary (HashMap<String,? extends DistComponent> map, String label, boolean bLast, PrintWriter out, int maxMeasurements) {
    int count = 1, last = map.size();
    out.println ("\"" + label + "\":[");

    SortedSet<String> keys = new TreeSet<String>(map.keySet());
    //If we only want a limited number of measurements restrict them
    if(maxMeasurements>=0 && keys.size()>maxMeasurements){
      List<String> tmp = new ArrayList<String>();
      tmp.addAll(keys);
      keys = new TreeSet<String>(tmp.subList(0, maxMeasurements));
    }
    for (String key : keys) {
      out.print (map.get(key).GetJSONEntry ());
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
    }
    if (bLast) {
      out.println("]");
    } else {
      out.println("],");
    }
  }

  public void WriteLimitsFile (PrintWriter out) {
    out.println("{\"limits\":{");
    out.println("\"voltages\":[");
    oLimits.VoltageMapToJSON (out);
    out.println("],");
    out.println("\"currents\":[");
    oLimits.CurrentMapToJSON (out);
    out.println("]");
    out.println("}}");
    out.close();
  }

  public void WriteDictionaryFile (PrintWriter out, int maxMeasurements) {
    out.println("{\"exportNameMode\":\"" + DistComponent.gExportNames + "\",");
    out.println("\"feeders\":[");
    for (HashMap.Entry<String,DistFeeder> pair : mapFeeders.entrySet()) {
      DistFeeder fdr = pair.getValue();
      if (fdr.feederID.equals (queryHandler.getFeederSelection())) {
        out.println("{\"name\":\"" + fdr.feederName + "\",");
        out.println("\"mRID\":\"" + fdr.feederID + "\",");
        out.println("\"substation\":\"" + fdr.substationName + "\",");
        out.println("\"substationID\":\"" + fdr.substationID + "\",");
        out.println("\"subregion\":\"" + fdr.subregionName + "\",");
        out.println("\"subregionID\":\"" + fdr.subregionID + "\",");
        out.println("\"region\":\"" + fdr.regionName + "\",");
        out.println("\"regionID\":\"" + fdr.regionID + "\",");
      }
    }
    WriteMapDictionary (DistComponent.mapBusNames, "busnames", false, out);
    WriteMapDictionary (DistComponent.mapEquipmentNames, "equipmentnames", false, out);
    WriteMapDictionary (mapSyncMachines, "synchronousmachines", false, out);
    WriteMapDictionary (mapCapacitors, "capacitors", false, out);
    WriteMapDictionary (mapRegulators, "regulators", false, out);
    WriteMapDictionary (mapSolars, "solarpanels", false, out);
    WriteMapDictionary (mapStorages, "batteries", false, out);
    WriteMapDictionary (mapLoadBreakSwitches, "switches", false, out);
    WriteMapDictionary (mapFuses, "fuses", false, out);
    WriteMapDictionary (mapJumpers, "jumpers", false, out);
    WriteMapDictionary (mapSectionalisers, "sectionalisers", false, out);
    WriteMapDictionary (mapBreakers, "breakers", false, out);
    WriteMapDictionary (mapReclosers, "reclosers", false, out);
    WriteMapDictionary (mapSeriesCompensators, "reactors", false, out);
    WriteMapDictionary (mapDisconnectors, "disconnectors", false, out);
    WriteMapDictionary (mapLoads, "energyconsumers", false, out);
    WriteMapDictionary (mapMeasurements, "measurements", true, out, maxMeasurements);
    out.println("}]}");
    out.close();
  }

  public void WriteMapSymbols (HashMap<String,? extends DistComponent> map, String label,
    boolean bLast, PrintWriter out) {
    int count = 1, last = map.size();
    out.println ("\"" + label + "\":[");

    SortedSet<String> keys = new TreeSet<String>(map.keySet());
    for (String key : keys) {
      out.print(map.get(key).GetJSONSymbols(mapCoordinates));
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
    }
    if (bLast) {
      out.println("]");
    } else {
      out.println("],");
    }
  }

  public void WriteRegulatorMapSymbols (boolean bLast, PrintWriter out) {
    int count = 1, last = mapRegulators.size();
    out.println ("\"regulators\":[");

    for (HashMap.Entry<String,DistRegulator> pair : mapRegulators.entrySet()) {
      DistRegulator reg = pair.getValue();
      out.print(reg.GetJSONSymbols(mapCoordinates, mapTanks, mapXfmrWindings));
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
    }
    if (bLast) {
      out.println("]");
    } else {
      out.println("],");
    }
  }

  public void WriteJSONSymbolFile (PrintWriter out)  {

    int count, last;

    out.println("{\"feeders\":[");
    for (HashMap.Entry<String,DistFeeder> pair : mapFeeders.entrySet()) {
      DistFeeder fdr = pair.getValue();
      if (fdr.feederID.equals (queryHandler.getFeederSelection())) {
        out.println("{\"name\":\"" + fdr.feederName + "\",");
        out.println("\"mRID\":\"" + fdr.feederID + "\",");
        out.println("\"substation\":\"" + fdr.substationName + "\",");
        out.println("\"substationID\":\"" + fdr.substationID + "\",");
        out.println("\"subregion\":\"" + fdr.subregionName + "\",");
        out.println("\"subregionID\":\"" + fdr.subregionID + "\",");
        out.println("\"region\":\"" + fdr.regionName + "\",");
        out.println("\"regionID\":\"" + fdr.regionID + "\",");
      }
    }

    WriteMapSymbols (mapSubstations, "swing_nodes", false, out);
    WriteMapSymbols (mapSyncMachines, "synchronousmachines", false, out);
    WriteMapSymbols (mapCapacitors, "capacitors", false, out);
    WriteMapSymbols (mapSolars, "solarpanels", false, out);
    WriteMapSymbols (mapStorages, "batteries", false, out);

    out.println("\"overhead_lines\":[");
    count = 1;
    last = mapLinesCodeZ.size() + mapLinesInstanceZ.size() + mapLinesSpacingZ.size();
    for (HashMap.Entry<String,DistLinesCodeZ> pair : mapLinesCodeZ.entrySet()) {
      out.print (pair.getValue().GetJSONSymbols(mapCoordinates));
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
    }
    for (HashMap.Entry<String,DistLinesInstanceZ> pair : mapLinesInstanceZ.entrySet()) {
      out.print (pair.getValue().GetJSONSymbols(mapCoordinates));
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
    }
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLinesSpacingZ.entrySet()) {
      out.print (pair.getValue().GetJSONSymbols(mapCoordinates));
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
    }
    out.println("],");

    WriteMapSymbols (mapLoadBreakSwitches, "switches", false, out);
    WriteMapSymbols (mapFuses, "fuses", false, out);
    WriteMapSymbols (mapJumpers, "jumpers", false, out);
    WriteMapSymbols (mapBreakers, "breakers", false, out);
    WriteMapSymbols (mapReclosers, "reclosers", false, out);
    WriteMapSymbols (mapSectionalisers, "sectionalisers", false, out);
    WriteMapSymbols (mapDisconnectors, "disconnectors", false, out);
    WriteMapSymbols (mapSeriesCompensators, "reactors", false, out);

    out.println("\"transformers\":[");
    count = 1;
    last =  mapXfmrWindings.size();
    for (HashMap.Entry<String,DistXfmrTank> pair : mapTanks.entrySet()) {
      if (pair.getValue().glmUsed) {
        last += 1;
      }
    }
    for (HashMap.Entry<String,DistPowerXfmrWinding> pair : mapXfmrWindings.entrySet()) {
      out.print (pair.getValue().GetJSONSymbols(mapCoordinates));
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
    }
    for (HashMap.Entry<String,DistXfmrTank> pair : mapTanks.entrySet()) {
      DistXfmrTank obj = pair.getValue();
      if (obj.glmUsed) {
      out.print(obj.GetJSONSymbols(mapCoordinates));
      if (count++ < last) {
        out.println (",");
      } else {
        out.println ("");
      }
      }
    }
    out.println("],");

    WriteRegulatorMapSymbols (true, out);

    out.println("}]}");
    out.close();
  }

  private String GetGLMLineConfiguration (DistLinesSpacingZ ln) {
    String match_A = "";
    String match_B = "";
    String match_C = "";
    String match_N = "";
    String config_name;
    boolean bCable = false;
    StringBuilder buf = new StringBuilder (DistComponent.GLMObjectPrefix ("spc_") + ln.spacing + "_");

    // what are we looking for?
    for (int i = 0; i < ln.nwires; i++) {
      if (ln.wire_classes[i].equals ("ConcentricNeutralCableInfo")) {
        bCable = true;
        break;
      }
      if (ln.wire_classes[i].equals ("TapeShieldCableInfo")) {
        bCable = true;
        break;
      }
    }
    for (int i = 0; i < ln.nwires; i++) {
      if (ln.wire_phases[i].equals ("A")) {
        match_A = GldLineConfig.GetMatchWire (ln.wire_classes[i], ln.wire_names[i], bCable);
        buf.append ("A");
      }
      if (ln.wire_phases[i].equals ("B")) {
        match_B = GldLineConfig.GetMatchWire (ln.wire_classes[i], ln.wire_names[i], bCable);
        buf.append ("B");
      }
      if (ln.wire_phases[i].equals ("C")) {
        match_C = GldLineConfig.GetMatchWire (ln.wire_classes[i], ln.wire_names[i], bCable);
        buf.append ("C");
      }
      if (ln.wire_phases[i].equals ("N")) {
        match_N = GldLineConfig.GetMatchWire(ln.wire_classes[i], ln.wire_names[i], bCable);
        // we may need to write this as an unshielded underground line conductor
        if (bCable && ln.wire_classes[i].equals ("OverheadWireInfo")) {
          DistOverheadWire oh_wire = mapWires.get (ln.wire_ids[i]);
          oh_wire.canBury = true;
        }
        buf.append ("N");
      }
    }
    String match_SPC = buf.toString();

    // search for an existing one
    for (HashMap.Entry<String, GldLineConfig> pair: mapLineConfigs.entrySet()) {
      GldLineConfig cfg = pair.getValue();
      config_name = pair.getKey();
      if (cfg.spacing.equals (match_SPC)) {
        if (cfg.conductor_A.equals (match_A)) {
          if (cfg.conductor_B.equals (match_B)) {
            if (cfg.conductor_C.equals (match_C)) {
              if (cfg.conductor_N.equals (match_N)) {
                return config_name;
              }
            }
          }
        }
      }
    }

    // need to make a new one
    config_name = "lcon_" + ln.spacing + "_" + Integer.toString(mapLineConfigs.size());
    GldLineConfig cfg = new GldLineConfig (config_name);
    cfg.spacing = match_SPC;
    cfg.conductor_A = match_A;
    cfg.conductor_B = match_B;
    cfg.conductor_C = match_C;
    cfg.conductor_N = match_N;
    mapLineConfigs.put (config_name, cfg);
    return config_name;
  }

  protected void MakeSwitchMap () {
    // build a polymorphic map of switches
    mapSwitches.putAll (mapLoadBreakSwitches);
    mapSwitches.putAll (mapFuses);
    mapSwitches.putAll (mapJumpers);
    mapSwitches.putAll (mapBreakers);
    mapSwitches.putAll (mapReclosers);
    mapSwitches.putAll (mapSectionalisers);
    mapSwitches.putAll (mapDisconnectors);
    mapSwitches.putAll (mapGroundDisconnectors);
  }

  protected void MakeLineMap () {
    // build a polymorphic map of line segments
    mapLines.putAll (mapLinesCodeZ);
    mapLines.putAll (mapLinesInstanceZ);
    mapLines.putAll (mapLinesSpacingZ);
  }

  protected void MakeTerminalMap () {
    for (HashMap.Entry<String, DistLineSegment> pair: mapLines.entrySet()) {
      DistLineSegment obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus1, obj.phases, obj.basev, "ACLineSegment");
      mapTerminals.put (obj.t1id, trm1);
      CIMTerminal trm2 = new CIMTerminal (obj.t2id, obj.bus2, obj.phases, obj.basev, "ACLineSegment");
      mapTerminals.put (obj.t2id, trm2);
    }
    for (HashMap.Entry<String, DistSeriesCompensator> pair: mapSeriesCompensators.entrySet()) {
      DistSeriesCompensator obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus1, obj.phases, obj.basev, "SeriesCompensator");
      mapTerminals.put (obj.t1id, trm1);
      CIMTerminal trm2 = new CIMTerminal (obj.t2id, obj.bus2, obj.phases, obj.basev, "SeriesCompensator");
      mapTerminals.put (obj.t2id, trm2);
    }
    for (HashMap.Entry<String, DistSwitch> pair: mapSwitches.entrySet()) {
      DistSwitch obj = pair.getValue();
      String eq = obj.CIMClass();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus1, obj.phases, obj.basev, eq);
      mapTerminals.put (obj.t1id, trm1);
      CIMTerminal trm2 = new CIMTerminal (obj.t2id, obj.bus2, obj.phases, obj.basev, eq);
      mapTerminals.put (obj.t2id, trm2);
    }
    for (HashMap.Entry<String, DistCapacitor> pair: mapCapacitors.entrySet()) {
      DistCapacitor obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus, obj.phs, obj.basev, "LinearShuntCompensator");
      mapTerminals.put (obj.t1id, trm1);
    }
    for (HashMap.Entry<String, DistLoad> pair: mapLoads.entrySet()) {
      DistLoad obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus, obj.phases, obj.basev, "EnergyConsumer");
      mapTerminals.put (obj.t1id, trm1);
    }
    for (HashMap.Entry<String, DistSyncMachine> pair: mapSyncMachines.entrySet()) {
      DistSyncMachine obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus, obj.phases, obj.ratedU, "SynchronousMachine");
      mapTerminals.put (obj.t1id, trm1);
    }
    for (HashMap.Entry<String, DistSolar> pair: mapSolars.entrySet()) {
      DistSolar obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus, obj.phases, obj.ratedU, "PhotovoltaicUnit");
      mapTerminals.put (obj.t1id, trm1);
    }
    for (HashMap.Entry<String, DistStorage> pair: mapStorages.entrySet()) {
      DistStorage obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus, obj.phases, obj.ratedU, "StorageUnit");
      mapTerminals.put (obj.t1id, trm1);
    }
    for (HashMap.Entry<String, DistSubstation> pair: mapSubstations.entrySet()) {
      DistSubstation obj = pair.getValue();
      CIMTerminal trm1 = new CIMTerminal (obj.t1id, obj.bus, "ABC", obj.basev, "EnergySource");
      mapTerminals.put (obj.t1id, trm1);
    }
    for (HashMap.Entry<String, DistXfmrTank> pair: mapTanks.entrySet()) {
      DistXfmrTank obj = pair.getValue();
      for (int i = 0; i < obj.size; i++) {
        CIMTerminal trm1 = new CIMTerminal(obj.t1id[i], obj.bus[i], DistComponent.PhaseCodeFromOrderedPhases(obj.orderedPhases[i]), obj.basev[i], "TransformerTank");
        mapTerminals.put (obj.t1id[i], trm1);
      }
    }
    for (HashMap.Entry<String, DistPowerXfmrWinding> pair: mapXfmrWindings.entrySet()) {
      DistPowerXfmrWinding obj = pair.getValue();
      for (int i = 0; i < obj.size; i++) {
        CIMTerminal trm1 = new CIMTerminal(obj.t1id[i], obj.bus[i], "ABC", obj.basev[i], "PowerTransformer");
        mapTerminals.put (obj.t1id[i], trm1);
      }
    }
  //  PrintTerminalMap (mapTerminals, "*** Map Terminals");
  }

  protected void WriteGLMFile (PrintWriter out, double load_scale, boolean bWantSched, String fSched,
      boolean bWantZIP, boolean randomZIP, boolean useHouses, double Zcoeff, double Icoeff, double Pcoeff, 
      boolean bHaveEventGen, boolean bUseProfiles, String fInclude1, String fInclude2, List<String> separateLoads) {

    DistEnergyConnectionProfile prf = null;
    HashMap<String,String> mapUsedProfiles = new HashMap<>(); // name, and one of the keys that uses it
    boolean bIncludeFile1Referenced = false;

    // reference the prefix include file by a local name
    if ((fInclude1 != null) && !fInclude1.isEmpty()) {
      File fIncludeFile1 = new File(fInclude1);
      out.println ("#include \"" + fIncludeFile1.getName() + "\"");
      bIncludeFile1Referenced = true;
    }
    // preparatory steps to build the list of nodes
    ResultSet results = queryHandler.query (
        "SELECT ?id WHERE {"+
            " ?fdr c:IdentifiedObject.mRID ?fdrid."+
            " ?s c:ConnectivityNode.ConnectivityNodeContainer ?fdr."+
            " ?s r:type c:ConnectivityNode."+
            " ?s c:IdentifiedObject.mRID ?id."+
        "} ORDER by ?id", "list nodes");
    if (!results.hasNext()) {
      System.out.println ("== no ConnectivityNodes found in a ConnectivityNodeContainer for GridLAB-D; trying a less restrictive query");
      results = queryHandler.query (
          "SELECT ?id WHERE {"+
              " ?s r:type c:ConnectivityNode."+
              " ?s c:IdentifiedObject.mRID ?id."+
          "} ORDER by ?id", "list nodes");
    }
    while (results.hasNext()) {
      QuerySolution soln = results.next();
      String id = soln.get ("?id").toString();
      String bus = DistComponent.GetBusExportName (id);
      mapNodes.put (bus, new GldNode(bus));
    }
    // PrintGldNodeMap (mapNodes, "*** GldNode Map Before Accumulation");
    for (HashMap.Entry<String,DistSubstation> pair : mapSubstations.entrySet()) {
      DistSubstation obj = pair.getValue();
      GldNode nd = mapNodes.get (obj.bus);
      nd.bSwing = true;
      nd.nomvln = obj.basev / Math.sqrt(3.0);
      nd.phases = "ABC";
    }
    // do the Tanks first, because they assign primary and secondary phasings
    for (HashMap.Entry<String,DistXfmrTank> pair : mapTanks.entrySet()) {
      DistXfmrTank obj = pair.getValue();
      DistXfmrCodeRating code = mapCodeRatings.get (obj.infoid);
      code.glmUsed = true;
      boolean bServiceTransformer = false;
      String primaryPhase = "";
      for (int i = 0; i < obj.size; i++) {
        GldNode nd = mapNodes.get(obj.bus[i]);
        nd.nomvln = obj.basev[i] / Math.sqrt(3.0);
        nd.AddPhases (obj.orderedPhases[i]); // TODO
        if (nd.bSecondary) {
          bServiceTransformer = true;
        } else {
          primaryPhase = obj.orderedPhases[i]; // TODO
          code.AddGldPrimaryPhase (primaryPhase);
          if (i > 1) {
            nd.bTertiaryWinding = true; // unsupported primary node in GridLAB-D - TODO: throw some kind of warning
          }
        }
      }
      if (bServiceTransformer) {
        for (int i = 0; i < obj.size; i++) {
          GldNode nd = mapNodes.get(obj.bus[i]);
          if (nd.bSecondary) {
            nd.AddPhases (primaryPhase);
            DistCoordinates pt1 = mapCoordinates.get("PowerTransformer:" + obj.pid + ":1");
            DistCoordinates pt2 = mapCoordinates.get("PowerTransformer:" + obj.pid + ":2");
            if (pt2 == null) {
              pt2 = pt1;
            } else if (pt1 == null) {
              pt1 = pt2;
            }
            if (pt1.x == 0.0 && pt1.y == 0.0) {
              if (pt2.x != 0.0 || pt2.y != 0.0) {
                pt1.x = pt2.x + 3.0;
                pt1.y = pt2.y + 0.0;
              }
            } else if (pt2.x == 0.0 && pt2.y == 0.0) {
              if (pt1.x != 0.0 || pt1.y != 0.0) {
                pt2.x = pt1.x + 3.0;
                pt2.y = pt1.y + 0.0;
              }
            }
          }
        }
      }
    }
    for (HashMap.Entry<String,DistLoad> pair : mapLoads.entrySet()) {
      DistLoad obj = pair.getValue();
      if (bUseProfiles) prf = mapGlmProfiles.get(obj.id);
      GldNode nd = mapNodes.get (obj.bus);
      nd.nomvln = obj.basev / Math.sqrt(3.0);
      nd.AccumulateLoads (obj.name, obj.phases, obj.conn, obj.p, obj.q, obj.pe, obj.qe, obj.pz, obj.pi, obj.pp, obj.qz, obj.qi, obj.qp, randomZIP);
      if (prf != null) {
        nd.AccumulateProfiles (prf.gldPlayer, prf.gldSchedule);
        mapUsedProfiles.put(prf.name, prf.GetKey());
      }
    }
    for (HashMap.Entry<String,DistCapacitor> pair : mapCapacitors.entrySet()) {
      DistCapacitor obj = pair.getValue();
      GldNode nd = mapNodes.get (obj.bus);
      nd.nomvln = obj.basev / Math.sqrt(3.0);
      nd.AddPhases (obj.phs);
    }
    for (HashMap.Entry<String, DistSeriesCompensator> pair: mapSeriesCompensators.entrySet()) {
      DistSeriesCompensator obj = pair.getValue();
      GldNode nd1 = mapNodes.get (obj.bus1);
      nd1.nomvln = obj.basev / Math.sqrt(3.0);
      nd1.AddPhases (obj.phases);
      GldNode nd2 = mapNodes.get (obj.bus2);
      nd2.nomvln = nd1.nomvln;
      nd2.AddPhases (obj.phases);
    }
    for (HashMap.Entry<String, DistLinesInstanceZ> pair: mapLinesInstanceZ.entrySet()) {
      DistLinesInstanceZ obj = pair.getValue();
      GldNode nd1 = mapNodes.get (obj.bus1);
      nd1.nomvln = obj.basev / Math.sqrt(3.0);
      nd1.AddPhases (obj.phases);
      GldNode nd2 = mapNodes.get (obj.bus2);
      nd2.nomvln = nd1.nomvln;
      nd2.AddPhases (obj.phases);
    }
    for (HashMap.Entry<String,DistLinesCodeZ> pair : mapLinesCodeZ.entrySet()) {
      DistLinesCodeZ obj = pair.getValue();
      DistPhaseMatrix zmat = mapPhaseMatrices.get (obj.codeid);
      if (zmat != null) {
        zmat.MarkGLMPermutationsUsed(obj.phases);
      } else {
        DistSequenceMatrix zseq = mapSequenceMatrices.get (obj.codeid);
        if (zseq != null) {
          //          System.out.println ("Sequence Z " + zseq.name + " using " + obj.phases + " for " + obj.name);
        }
      }
      GldNode nd1 = mapNodes.get (obj.bus1);
      nd1.nomvln = obj.basev / Math.sqrt(3.0);
      GldNode nd2 = mapNodes.get (obj.bus2);
      nd2.nomvln = nd1.nomvln;
      if (obj.phases.contains("s")) {  // add primary phase to this triplex
        nd1.bSecondary = true;
        nd2.bSecondary = true;
        if (nd2.phases.length() > 0) {
          nd1.AddPhases (nd2.phases);
          obj.phases = obj.phases + ":" + nd2.phases;
        } else if (nd1.phases.length() > 0) {
          nd2.AddPhases (nd1.phases);
          obj.phases = obj.phases + ":" + nd1.phases;
        }
        DistCoordinates pt1 = mapCoordinates.get("ACLineSegment:" + obj.id + ":1");
        DistCoordinates pt2 = mapCoordinates.get("ACLineSegment:" + obj.id + ":2");
        if (pt1.x == 0.0 && pt1.y == 0.0) {
          if (pt2.x != 0.0 || pt2.y != 0.0) {
            pt1.x = pt2.x + 3.0;
            pt1.y = pt2.y + 0.0;
          }
        } else if (pt2.x == 0.0 && pt2.y == 0.0) {
          if (pt1.x != 0.0 || pt1.y != 0.0) {
            pt2.x = pt1.x + 3.0;
            pt2.y = pt1.y + 0.0;
          }
        }
      } else {
        nd1.AddPhases (obj.phases);
        nd2.AddPhases (obj.phases);
      }
    }
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLinesSpacingZ.entrySet()) {
      DistLinesSpacingZ obj = pair.getValue();
      // TODO - make line configurations on the fly, mark the wires and spacings used
      obj.glm_config = GetGLMLineConfiguration (obj);
      DistLineSpacing spc = mapSpacings.get (obj.spcid);
      if (spc != null) {
        spc.MarkPermutationsUsed(obj.phases);
      }
      GldNode nd1 = mapNodes.get (obj.bus1);
      nd1.nomvln = obj.basev / Math.sqrt(3.0);
      nd1.AddPhases (obj.phases);
      GldNode nd2 = mapNodes.get (obj.bus2);
      nd2.nomvln = nd1.nomvln;
      nd2.AddPhases (obj.phases);
    }
    for (HashMap.Entry<String,DistSwitch> pair : mapSwitches.entrySet()) {
      DistSwitch obj = pair.getValue();
      GldNode nd1 = mapNodes.get (obj.bus1);
      GldNode nd2 = mapNodes.get (obj.bus2);
      if (obj.glm_phases.equals("S")) {  // TODO - we should be using a graph component like networkx (but for Java) to assign phasing
        String phs1 = nd1.GetPhases(false);
        String phs2 = nd2.GetPhases(false);
        if (phs1.length() > 1 && phs1.contains ("S")) {
          obj.glm_phases = nd1.GetPhases(false);
          nd2.ResetPhases (phs1);
        } else if (phs2.length() > 1 && phs2.contains ("S")) {
          obj.glm_phases = nd2.GetPhases(false);
          nd1.ResetPhases (phs2);
        }
      } else {
        nd1.nomvln = obj.basev / Math.sqrt(3.0);
        nd1.AddPhases (obj.phases);
        nd2.nomvln = nd1.nomvln;
        nd2.AddPhases (obj.phases);
      }
    }
    for (HashMap.Entry<String,DistPowerXfmrWinding> pair : mapXfmrWindings.entrySet()) {
      DistPowerXfmrWinding obj = pair.getValue();
      for (int i = 0; i < obj.size; i++) {
        GldNode nd = mapNodes.get(obj.bus[i]);
        nd.nomvln = obj.basev[i] / Math.sqrt(3.0);
        nd.AddPhases ("ABC");
        if (i > 1) {
          nd.bTertiaryWinding = true; // unsupported node in GridLAB-D - TODO: throw some kind of warning
        }
      }
    }
    for (HashMap.Entry<String,DistSolar> pair : mapSolars.entrySet()) {
      DistSolar obj = pair.getValue();
      if (bUseProfiles) prf = mapGlmProfiles.get(obj.pecid);
      if (prf != null) mapUsedProfiles.put(prf.name, prf.GetKey());
      GldNode nd = mapNodes.get (obj.bus);
      nd.bSolarInverters = true;
      if (nd.nomvln < 0.0) {
        if (obj.phases.equals("ABC") || obj.phases.equals("AB") || obj.phases.equals("AC") || obj.phases.equals("BC")) {
          nd.nomvln = obj.ratedU / Math.sqrt(3.0);
        } else {
          nd.nomvln = obj.ratedU;
        }
      }
      nd.AddPhases (obj.phases);
      if (nd.bSecondary) {
        obj.phases = nd.GetPhases(false);
      }
    }
    for (HashMap.Entry<String,DistStorage> pair : mapStorages.entrySet()) {
      DistStorage obj = pair.getValue();
      if (bUseProfiles) prf = mapGlmProfiles.get(obj.pecid);
      if (prf != null) mapUsedProfiles.put(prf.name, prf.GetKey());
      GldNode nd = mapNodes.get (obj.bus);
      nd.bStorageInverters = true;
      if (nd.nomvln < 0.0) {
        if (obj.phases.equals("ABC") || obj.phases.equals("AB") || obj.phases.equals("AC") || obj.phases.equals("BC")) {
          nd.nomvln = obj.ratedU / Math.sqrt(3.0);
        } else {
          nd.nomvln = obj.ratedU;
        }
      }
      nd.AddPhases (obj.phases);
      if (nd.bSecondary) {
        obj.phases = nd.GetPhases(false);
      }
    }
    for (HashMap.Entry<String,DistSyncMachine> pair : mapSyncMachines.entrySet()) { // TODO: GridLAB-D doesn't actually support 1-phase generators
      DistSyncMachine obj = pair.getValue();
      GldNode nd = mapNodes.get (obj.bus);
      if (bUseProfiles) prf = mapGlmProfiles.get(obj.id);
      if (prf != null) mapUsedProfiles.put(prf.name, prf.GetKey());
      nd.bSyncMachines = true;
      if (nd.nomvln < 0.0) {
        if (obj.phases.equals("ABC") || obj.phases.equals("AB") || obj.phases.equals("AC") || obj.phases.equals("BC")) {
          nd.nomvln = obj.ratedU / Math.sqrt(3.0);
        } else {
          nd.nomvln = obj.ratedU;
        }
      }
      nd.AddPhases (obj.phases);
      if (nd.bSecondary) {
        obj.phases = nd.GetPhases(false);
      }
    }
    for (HashMap.Entry<String,DistRegulator> pair : mapRegulators.entrySet()) {
      DistRegulator reg = pair.getValue();
      if (reg.hasTanks) {
        DistXfmrTank tank = mapTanks.get(reg.tid[0]); // TODO: revisit if GridLAB-D can model un-banked regulator tanks
        DistXfmrCodeRating code = mapCodeRatings.get (tank.infoid);
        out.print (reg.GetTankedGLM (tank));
        code.glmUsed = false;
        tank.glmUsed = false;
        for (int i = 1; i < reg.size; i++) {
          tank = mapTanks.get (reg.tid[i]);
          code = mapCodeRatings.get (tank.infoid);
          code.glmUsed = false;
          tank.glmUsed = false;
        }
      } else {
        DistPowerXfmrWinding xfmr = mapXfmrWindings.get(reg.pid);
        out.print (reg.GetGangedGLM (xfmr));
        xfmr.glmUsed = false;
      }
    }
    //PrintGldNodeMap (mapNodes, "*** GldNode Map After Accumulation");

    // GLM configurations
    for (HashMap.Entry<String,DistOverheadWire> pair : mapWires.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistConcentricNeutralCable> pair : mapCNCables.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistTapeShieldCable> pair : mapTSCables.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistLineSpacing> pair : mapSpacings.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,GldLineConfig> pair : mapLineConfigs.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistPhaseMatrix> pair : mapPhaseMatrices.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistSequenceMatrix> pair : mapSequenceMatrices.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistXfmrCodeRating> pair : mapCodeRatings.entrySet()) {
      DistXfmrCodeRating code = pair.getValue();
      if (code.glmUsed) {
        DistXfmrCodeSCTest sct = mapCodeSCTests.get (code.id);
        DistXfmrCodeNLTest oct = mapCodeNLTests.get (code.id);
        out.print (code.GetGLM(sct, oct));
      }
    }

    // GLM circuit components
    for (HashMap.Entry<String,DistCapacitor> pair : mapCapacitors.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistSolar> pair : mapSolars.entrySet()) {
      if (bUseProfiles) prf = mapGlmProfiles.get(pair.getValue().pecid);
      out.print (pair.getValue().GetGLM(mapIEEE1547Connections, mapIEEE1547Used, prf));
    }
    for (HashMap.Entry<String,DistStorage> pair : mapStorages.entrySet()) {
      if (bUseProfiles) prf = mapGlmProfiles.get(pair.getValue().pecid);
      out.print (pair.getValue().GetGLM(mapIEEE1547Connections, mapIEEE1547Used, prf));
    }
    for (HashMap.Entry<String,DistSyncMachine> pair : mapSyncMachines.entrySet()) {
      if (bUseProfiles) prf = mapGlmProfiles.get(pair.getValue().id);
      out.print (pair.getValue().GetGLM(prf));
    }
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLinesSpacingZ.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistLinesCodeZ> pair : mapLinesCodeZ.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistLinesInstanceZ> pair : mapLinesInstanceZ.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistSeriesCompensator> pair : mapSeriesCompensators.entrySet()) {
      out.print (pair.getValue().GetGLM());
    }
    for (HashMap.Entry<String,DistSwitch> pair : mapSwitches.entrySet()) {
      DistSwitch obj = pair.getValue();
      if (obj.glm_phases.contains ("S")) { // TODO: this is hard-wired to PNNL taxonomy, needing to parent the nodes instead of writing a switch.
        GldNode nd1 = mapNodes.get (obj.bus1);
        GldNode nd2 = mapNodes.get (obj.bus2);
        if (nd1.name.contains ("_tn_") && nd2.name.contains ("_tm_")) {
          nd2.CopyLoad (nd1);
          mapNodes.remove (obj.bus1);
        } else if (nd1.name.contains ("_tn_") && nd2.name.contains ("_tm_")) {
          nd1.CopyLoad (nd2);
          mapNodes.remove (obj.bus2);
        } else { // TODO: doesn't seem to be a taxonomy feeder, so write the secondary switch as-is, although GridLAB-D will not solve it.
          out.print(obj.GetGLM());
          System.out.println ("** secondary switch: " + obj.name + " is not supported in GridLAB-D");
        }
      } else {
        out.print(obj.GetGLM());
      }
    }
    for (HashMap.Entry<String,DistPowerXfmrWinding> pair : mapXfmrWindings.entrySet()) {
      DistPowerXfmrWinding obj = pair.getValue();
      if (obj.glmUsed) {
        DistPowerXfmrMesh mesh = mapXfmrMeshes.get (obj.id);
        DistPowerXfmrCore core = mapXfmrCores.get (obj.id);
        out.print (pair.getValue().GetGLM(mesh, core));
      }
    }
    for (HashMap.Entry<String,DistXfmrTank> pair : mapTanks.entrySet()) {
      DistXfmrTank obj = pair.getValue();
      if (obj.glmUsed) {
        out.print (obj.GetGLM());
      }
    }

    // GLM nodes and loads
    boolean bWroteEventGen = bHaveEventGen;
    for (HashMap.Entry<String,GldNode> pair : mapNodes.entrySet()) {
      GldNode nd = pair.getValue();
      out.print (pair.getValue().GetGLM (load_scale, bWantSched, fSched, bWantZIP, useHouses, Zcoeff, Icoeff, Pcoeff, separateLoads));
      if (!bWroteEventGen && nd.bSwingPQ) {
        // we can't have two fault_check objects, and there may already be one for external event scripting
        bWroteEventGen = true;
        out.print ("object fault_check {\n");
        out.print ("  name base_fault_check_object;\n");
        out.print ("  check_mode ONCHANGE;\n");
        out.print ("  strictly_radial false;\n");
        out.print ("  eventgen_object testgendev;\n");
        out.print ("  grid_association true;\n");
        out.print ("}\n");
        out.print ("object eventgen {\n");
        out.print ("  name testgendev;\n");
        out.print ("  fault_type \"DLG-X\";\n");
        out.print ("  manual_outages \"" + nd.name + ",2100-01-01 00:00:05,2100-01-01 00:00:30\";\n");
        out.print ("}\n");
      }
    }

    // GLM houses
    if (useHouses) {
      Random r = new Random();
      r.setSeed(10);
      for (HashMap.Entry<String, DistHouse> pair : mapHouses.entrySet()) {
        int seed = r.nextInt();
        out.print((pair.getValue().GetGLM(r)));
      }
    }

    // reference the suffix include file by a local name
    if ((fInclude2 != null) && !fInclude2.isEmpty()) {
      File fIncludeFile2 = new File(fInclude2);
      out.println ("#include \"" + fIncludeFile2.getName() + "\"");
    }

    // try to link all CIM measurements to the GridLAB-D objects
    // PrintGldNodeMap (mapNodes, "*** GldNode Map for Measurements");
    HashMap<String,GldNode> mapLoadNodes = new HashMap<>();
    for (HashMap.Entry<String,GldNode> pair : mapNodes.entrySet()) {
      GldNode nd = pair.getValue();
      if (nd.loadname.length() > 0) {
        mapLoadNodes.put(nd.loadname, nd);
      }
    }
    // PrintGldNodeMap (mapLoadNodes, "*** GldLoadNode Map for Measurements");
    int measurements_not_linked = 0;
    int measurements_no_bus = 0;
    for (HashMap.Entry<String,DistMeasurement> pair : mapMeasurements.entrySet()) {
      DistMeasurement obj = pair.getValue();
      GldNode nd = mapNodes.get (obj.bus);
      if (nd == null) {
        nd = mapLoadNodes.get (obj.GetGldLoadName());
      }
      if (nd != null) {
        obj.FindSimObject (nd.loadname, nd.phases, nd.bStorageInverters, nd.bSolarInverters, nd.bSyncMachines);
        if (!obj.LinkedToSimulatorObject()) {
          measurements_not_linked += 1;
          System.out.println ("  unlinked " + obj.DisplayString());
        }
      } else {
        measurements_no_bus += 1;
        System.out.println ("  no GldNode for " + obj.DisplayString());
      }
    }
    if ((measurements_not_linked+measurements_no_bus) > 0) {
      System.out.println ("*** Could not FindSimObject for " + Integer.toString (measurements_not_linked) +
                " or bus for " + Integer.toString (measurements_no_bus) + 
                " out of " + Integer.toString(mapMeasurements.size()) + " Measurements");
    }

    if (mapUsedProfiles.size() > 0) {
      out.print ("// referenced EnergyConnectionProfiles that must be defined\n");
      if (!bIncludeFile1Referenced) {
        out.print ("// (consider re-exporting with -m=1 (or 3) option to reference an include file)\n");
      }
      for (HashMap.Entry<String,String> pair : mapUsedProfiles.entrySet()) {
        out.print (mapGlmProfiles.get(pair.getValue()).GetGLM());
      }
    }

    out.close();
  }

  protected void WriteDSSCoordinates (PrintWriter out)  {
    String bus;
    DistCoordinates pt1, pt2;
    HashMap<String,Double[]> mapBusXY = new HashMap<String,Double[]>();

    // loads, capacitors, transformers and energy sources have a single bus location, assumed to be correct
    for (HashMap.Entry<String,DistCoordinates> pair : mapCoordinates.entrySet()) {
      DistCoordinates obj = pair.getValue();
      if ((obj.x != 0) || (obj.y != 0)) {
        if (obj.cname.equals("EnergyConsumer")) {
          bus = mapLoads.get(obj.id).bus;
          mapBusXY.put(bus, new Double[] {obj.x, obj.y});
        } else if (obj.cname.equals("LinearShuntCompensator")) {
          bus = mapCapacitors.get(obj.id).bus;
          mapBusXY.put(bus, new Double[] {obj.x, obj.y});
        } else if (obj.cname.equals("EnergySource")) {
          bus = mapSubstations.get(obj.id).bus;
          mapBusXY.put(bus, new Double[] {obj.x, obj.y});
        } else if (obj.cname.equals("BatteryUnit")) {
          bus = mapStorages.get(obj.id).bus;
          mapBusXY.put(bus, new Double[] {obj.x, obj.y});
        } else if (obj.cname.equals("PhotovoltaicUnit")) {
          bus = mapSolars.get(obj.id).bus;
          mapBusXY.put(bus, new Double[] {obj.x, obj.y});
        } else if (obj.cname.equals("SynchronousMachine")) {
          bus = mapSyncMachines.get(obj.id).bus;
          mapBusXY.put(bus, new Double[] {obj.x, obj.y});
        } else if (obj.cname.equals("PowerTransformer")) {
          DistXfmrTank tnk = mapTanks.get(obj.id);
          if (tnk != null) {
            for (int i = 0; i < tnk.size; i++) {
              mapBusXY.put(tnk.bus[i], new Double[] { obj.x, obj.y });
            }
          } else {
            DistPowerXfmrWinding wdg = mapXfmrWindings.get(obj.id);
            if (wdg != null) {
              mapBusXY.put(wdg.bus[obj.seq - 1], new Double[] { obj.x, obj.y });
            }
          }
        }
      }
    }

    // switches and lines have bus locations; should be in correct order using ACDCTerminal.sequenceNumber
    for (HashMap.Entry<String,DistLinesCodeZ> pair : mapLinesCodeZ.entrySet()) {
      DistLineSegment obj = pair.getValue();
      pt1 = mapCoordinates.get("ACLineSegment:" + obj.name + ":1");
      pt2 = mapCoordinates.get("ACLineSegment:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
      //    setSegXY.add(new DSSSegmentXY (obj.bus1, pt1.x, pt1.y, obj.bus2, pt2.x, pt2.y));
    }
    for (HashMap.Entry<String,DistLinesInstanceZ> pair : mapLinesInstanceZ.entrySet()) {
      DistLineSegment obj = pair.getValue();
      pt1 = mapCoordinates.get("ACLineSegment:" + obj.name + ":1");
      pt2 = mapCoordinates.get("ACLineSegment:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistSeriesCompensator> pair : mapSeriesCompensators.entrySet()) {
      DistSeriesCompensator obj = pair.getValue();
      pt1 = mapCoordinates.get("SeriesCompensator:" + obj.name + ":1");
      pt2 = mapCoordinates.get("SeriesCompensator:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLinesSpacingZ.entrySet()) {
      DistLineSegment obj = pair.getValue();
      pt1 = mapCoordinates.get("ACLineSegment:" + obj.name + ":1");
      pt2 = mapCoordinates.get("ACLineSegment:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistLoadBreakSwitch> pair : mapLoadBreakSwitches.entrySet()) {
      DistLoadBreakSwitch obj = pair.getValue();
      pt1 = mapCoordinates.get("LoadBreakSwitch:" + obj.name + ":1");
      pt2 = mapCoordinates.get("LoadBreakSwitch:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistFuse> pair : mapFuses.entrySet()) { // TODO - polymorphic switch maps
      DistFuse obj = pair.getValue();
      pt1 = mapCoordinates.get("Fuse:" + obj.name + ":1");
      pt2 = mapCoordinates.get("Fuse:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistJumper> pair : mapJumpers.entrySet()) {
      DistJumper obj = pair.getValue();
      pt1 = mapCoordinates.get("Jumper:" + obj.name + ":1");
      pt2 = mapCoordinates.get("Jumper:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistRecloser> pair : mapReclosers.entrySet()) {
      DistRecloser obj = pair.getValue();
      pt1 = mapCoordinates.get("Recloser:" + obj.name + ":1");
      pt2 = mapCoordinates.get("Recloser:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistBreaker> pair : mapBreakers.entrySet()) {
      DistBreaker obj = pair.getValue();
      pt1 = mapCoordinates.get("Breaker:" + obj.name + ":1");
      pt2 = mapCoordinates.get("Breaker:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistSectionaliser> pair : mapSectionalisers.entrySet()) {
      DistSectionaliser obj = pair.getValue();
      pt1 = mapCoordinates.get("Sectionaliser:" + obj.name + ":1");
      pt2 = mapCoordinates.get("Sectionaliser:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }
    for (HashMap.Entry<String,DistDisconnector> pair : mapDisconnectors.entrySet()) {
      DistDisconnector obj = pair.getValue();
      pt1 = mapCoordinates.get("Disconnector:" + obj.name + ":1");
      pt2 = mapCoordinates.get("Disconnector:" + obj.name + ":2");
      if (pt1 != null) mapBusXY.put (obj.bus1, new Double [] {pt1.x, pt1.y});
      if (pt2 != null) mapBusXY.put (obj.bus2, new Double [] {pt2.x, pt2.y});
    }

    // The bus locations in mapBusXY should now be unique, and topologically consistent, so write them.
    for (HashMap.Entry<String,Double[]> pair : mapBusXY.entrySet()) {
      Double[] xy = pair.getValue();
      bus = pair.getKey();
      out.println(bus + "," + Double.toString(xy[0]) + "," + Double.toString(xy[1]));
    }

    out.close();
  }

  protected String UUIDfromCIMmRID (String id) {
    int idx = id.indexOf ("_");
    if (idx >= 0) {
      return id.substring(idx+1);
    }
    return id;
  }

  protected void WriteDSSFile (PrintWriter out, PrintWriter outID, String fXY, String fID, double load_scale,
      boolean bWantSched, String fSched, boolean bWantZIP, double Zcoeff, double Icoeff, double Pcoeff, String fEarth,
      boolean bUseProfiles, String fInclude1, String fInclude2)  {


    DistEnergyConnectionProfile prf = null;
    HashMap<String,String> mapUsedProfiles = new HashMap<>(); // name, and one of the keys that uses it
    boolean bIncludeFile1Referenced = false;

    out.println ("clear");
    out.println ("set defaultbasefrequency=" + String.valueOf (DistComponent.GetSystemFrequency()));

    for (HashMap.Entry<String,DistSubstation> pair : mapSubstations.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Circuit." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    out.println ("set earthmodel=" + fEarth);

    // reference the prefix include file by a local name
    if ((fInclude1 != null) && !fInclude1.isEmpty()) {
      File fIncludeFile1 = new File(fInclude1);
      out.println ("redirect " + fIncludeFile1.getName());
      bIncludeFile1Referenced = true;
    }

    if (mapWires.size() > 0) out.println();
    for (HashMap.Entry<String,DistOverheadWire> pair : mapWires.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Wiredata." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapCNCables.size() > 0) out.println();
    for (HashMap.Entry<String,DistConcentricNeutralCable> pair : mapCNCables.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("CNData." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapTSCables.size() > 0) out.println();
    for (HashMap.Entry<String,DistTapeShieldCable> pair : mapTSCables.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("TSData." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapLinesSpacingZ.size() > 0) out.println();
    // DistLineSpacing can be transposed, so mark the permutations (i.e. transpositions) actually neede
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLinesSpacingZ.entrySet()) {
      DistLinesSpacingZ obj = pair.getValue();
      DistLineSpacing spc = mapSpacings.get (obj.spcid);
      if (spc != null) {
        spc.MarkPermutationsUsed(obj.phases);
      }
    }
    for (HashMap.Entry<String,DistLineSpacing> pair : mapSpacings.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("LineSpacing." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapPhaseMatrices.size() > 0) out.println();
    for (HashMap.Entry<String,DistPhaseMatrix> pair : mapPhaseMatrices.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Linecode." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapSequenceMatrices.size() > 0) out.println();
    for (HashMap.Entry<String,DistSequenceMatrix> pair : mapSequenceMatrices.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Linecode." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapCodeRatings.size() > 0) out.println();
    for (HashMap.Entry<String,DistXfmrCodeRating> pair : mapCodeRatings.entrySet()) {
      DistXfmrCodeRating obj = pair.getValue();
      DistXfmrCodeSCTest sct = mapCodeSCTests.get (obj.id);
      DistXfmrCodeNLTest oct = mapCodeNLTests.get (obj.id);
      out.print (obj.GetDSS(sct, oct));
      outID.println ("Xfmrcode." + obj.name + "\t" + UUIDfromCIMmRID (obj.id));
    }

    if (mapSolars.size() > 0) out.println();
    for (HashMap.Entry<String,DistSolar> pair : mapSolars.entrySet()) {
      if (bUseProfiles) {
        prf = mapDssProfiles.get(pair.getValue().pecid);
        if (prf != null) {
          mapUsedProfiles.put(prf.name, prf.GetKey());
        }
      }
      out.print (pair.getValue().GetDSS(prf));
      outID.println ("PVSystem." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapStorages.size() > 0) out.println();
    for (HashMap.Entry<String,DistStorage> pair : mapStorages.entrySet()) {
      if (bUseProfiles) {
        prf = mapDssProfiles.get(pair.getValue().pecid);
        if (prf != null) {
          mapUsedProfiles.put(prf.name, prf.GetKey());
        }
      }
      out.print (pair.getValue().GetDSS(prf));
      outID.println ("Storage." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapSyncMachines.size() > 0) out.println();
    for (HashMap.Entry<String,DistSyncMachine> pair : mapSyncMachines.entrySet()) {
      if (bUseProfiles) {
        prf = mapDssProfiles.get(pair.getValue().id);
        if (prf != null) {
          mapUsedProfiles.put(prf.name, prf.GetKey());
        }
      }
      out.print (pair.getValue().GetDSS(prf));
      outID.println ("Generator." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapLoads.size() > 0) out.println();
    for (HashMap.Entry<String,DistLoad> pair : mapLoads.entrySet()) {
      if (bUseProfiles) {
        prf = mapDssProfiles.get(pair.getValue().id);
        if (prf != null) {
          mapUsedProfiles.put(prf.name, prf.GetKey());
        }
      }
      out.print (pair.getValue().GetDSS(prf));
      outID.println ("Load." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapLoadBreakSwitches.size() > 0) out.println();
    for (HashMap.Entry<String,DistLoadBreakSwitch> pair : mapLoadBreakSwitches.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapFuses.size() > 0) out.println();
    for (HashMap.Entry<String,DistFuse> pair : mapFuses.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapReclosers.size() > 0) out.println();
    for (HashMap.Entry<String,DistRecloser> pair : mapReclosers.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapSectionalisers.size() > 0) out.println();
    for (HashMap.Entry<String,DistSectionaliser> pair : mapSectionalisers.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapBreakers.size() > 0) out.println();
    for (HashMap.Entry<String,DistBreaker> pair : mapBreakers.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapDisconnectors.size() > 0) out.println();
    for (HashMap.Entry<String,DistDisconnector> pair : mapDisconnectors.entrySet()) { // TODO: use mapSwitches?
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapJumpers.size() > 0) out.println();
    for (HashMap.Entry<String,DistJumper> pair : mapJumpers.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapLinesCodeZ.size() > 0) out.println();
    for (HashMap.Entry<String,DistLinesCodeZ> pair : mapLinesCodeZ.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapLinesSpacingZ.size() > 0) out.println();
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLinesSpacingZ.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapLinesInstanceZ.size() > 0) out.println();
    for (HashMap.Entry<String,DistLinesInstanceZ> pair : mapLinesInstanceZ.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Line." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapSeriesCompensators.size() > 0) out.println();
    for (HashMap.Entry<String,DistSeriesCompensator> pair : mapSeriesCompensators.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Reactor." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapXfmrWindings.size() > 0) out.println();
    for (HashMap.Entry<String,DistPowerXfmrWinding> pair : mapXfmrWindings.entrySet()) {
      DistPowerXfmrWinding obj = pair.getValue();
      DistPowerXfmrMesh mesh = mapXfmrMeshes.get (obj.id);
      DistPowerXfmrCore core = mapXfmrCores.get (obj.id);
      out.print (obj.GetDSS(mesh, core));
      outID.println ("Transformer." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapTanks.size() > 0) out.println();
    for (HashMap.Entry<String,DistXfmrTank> pair : mapTanks.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Transformer." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapRegulators.size() > 0) out.println();
    for (HashMap.Entry<String,DistRegulator> pair : mapRegulators.entrySet()) {
      DistRegulator obj = pair.getValue();
      out.print(obj.GetDSS());
      for (int i = 0; i < obj.size; i++) {
        outID.println("RegControl." + obj.name[i] + "\t" + UUIDfromCIMmRID (obj.id[i]));
      }
    }
    if (mapCapacitors.size() > 0) out.println(); // capacitors last in case the capcontrols reference a preceeding element
    for (HashMap.Entry<String,DistCapacitor> pair : mapCapacitors.entrySet()) {
      out.print (pair.getValue().GetDSS());
      outID.println ("Capacitor." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));
    }
    if (mapIEEE1547Connections.size() > 0) {
      MakeTerminalMap();
      out.println();
    } else {
      MakeTerminalMap();
    }
    for (HashMap.Entry<String,DistIEEE1547Connection> pair : mapIEEE1547Connections.entrySet()) {
      out.print (pair.getValue().GetDSS(mapSolars, mapStorages, mapIEEE1547Used, mapIEEE1547Signals, mapTerminals));
      outID.println ("InvControl." + pair.getValue().name + "\t" + UUIDfromCIMmRID (pair.getValue().id));  // TODO: what if ExpControl?
    }
    if (mapBaseVoltages.size() > 0) out.println();
    out.print ("set voltagebases=[");
    for (HashMap.Entry<String,DistBaseVoltage> pair : mapBaseVoltages.entrySet()) {
      out.print (pair.getValue().GetDSS());
    }
    out.println ("]");
    out.println();
    out.println ("calcv");

    // capture the time sequence of phase voltage and current magnitudes at the feeder head

    //  out.println ("New Monitor.fdr element=line.sw1 mode=32 // mode=48 for sequence magnitudes ");

    // import the "player file" and assign to all loads

    // this is the player file, with header, first column, and semicolons removed
    //new loadshape.player npts=1440 sinterval=60 mult=(file=ieeeziploadshape.dss) action=normalize
    // this command works with the original player file, if the semicolons are removed from about line 1380 onward
    if (bWantSched) {
      out.println("new loadshape.player npts=1440 sinterval=60 mult=(file=" + fSched + ".player,col=2,header=yes) action=normalize");
      out.println ("batchedit load..* duty=player daily=player");
    }

    out.println ("set loadmult = " + Double.toString(load_scale));

    // removed the local Docker paths, relying on cwd instead

    //  buscoords model_busxy.dss
    //  uuids model_uuid.dss

    //Only use local names for fXY and FID
    File fXYFile = new File(fXY);
    File fIDFile = new File(fID);

    out.println ("buscoords " + fXYFile.getName());
    out.println ("uuids " + fIDFile.getName());

    // reference the suffix include file by a local name
    if ((fInclude2 != null) && !fInclude2.isEmpty()) {
      File fIncludeFile2 = new File(fInclude2);
      out.println ("redirect " + fIncludeFile2.getName());
    }

    if (mapUsedProfiles.size() > 0) {
      out.print ("// referenced EnergyConnectionProfiles that must be defined\n");
      if (!bIncludeFile1Referenced) {
        out.print ("// (consider re-exporting with -m=1 (or 3) option to reference an include file)\n");
      }
      for (HashMap.Entry<String,String> pair : mapUsedProfiles.entrySet()) {
        out.print (mapDssProfiles.get(pair.getValue()).GetDSS());
      }
    }

    out.println();

    out.close();
    outID.close();
  }

  protected void WriteIndexFile (PrintWriter out)  {
    LoadFeeders ();
    PrintOneMap (mapFeeders, "*** FEEDERS ***");

    out.println("{\"feeders\":[");

    int count = 1, last = mapFeeders.size();

    for (HashMap.Entry<String,DistFeeder> pair : mapFeeders.entrySet()) {
      out.print (pair.getValue().GetJSONEntry());
      if (count++ < last) {
      out.println (",");
      } else {
      out.println ("");
      }
    }
    out.println("]}");
    out.close();
  }

  protected void WriteCsvFiles (String fRoot) throws FileNotFoundException {
    PrintWriter out =  new PrintWriter(fRoot + "_Buscoords.csv");
    out.println(DistCoordinates.szCSVHeader);
    WriteDSSCoordinates (out);  // this function closes out

    out =  new PrintWriter(fRoot + "_Capacitors.csv");
    out.println(DistCapacitor.szCSVCapHeader);
    for (HashMap.Entry<String,DistCapacitor> pair : mapCapacitors.entrySet()) {
      out.print (pair.getValue().GetCapCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_CapControls.csv");
    out.println(DistCapacitor.szCSVCapControlHeader);
    for (HashMap.Entry<String,DistCapacitor> pair : mapCapacitors.entrySet()) {
      if (pair.getValue().ctrl.equals("true")) out.print (pair.getValue().GetCapControlCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_LinesCodeZ.csv");
    out.println(DistLinesCodeZ.szCSVHeader);
    for (HashMap.Entry<String,DistLinesCodeZ> pair : mapLinesCodeZ.entrySet()) {
      if (!pair.getValue().phases.contains("s")) out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_LinesInstanceZ.csv");
    out.println(DistLinesInstanceZ.szCSVHeader);
    for (HashMap.Entry<String,DistLinesInstanceZ> pair : mapLinesInstanceZ.entrySet()) {
      if (!pair.getValue().phases.contains("s")) out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_SeriesCompensator.csv");
    out.println(DistSeriesCompensator.szCSVHeader);
    for (HashMap.Entry<String,DistSeriesCompensator> pair : mapSeriesCompensators.entrySet()) {
      if (!pair.getValue().phases.contains("s")) out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_LinesSpacingZ.csv");
    out.println(DistLinesSpacingZ.szCSVHeader);
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLinesSpacingZ.entrySet()) {
      DistLinesSpacingZ obj = pair.getValue();
      DistLineSpacing spc = mapSpacings.get (obj.spcid);
      if (spc != null) {
        spc.MarkPermutationsUsed(obj.phases);
      }
      if (!obj.phases.contains("s")) out.print (obj.GetCSV());
    }
    out.close();
    out =  new PrintWriter(fRoot + "_Spacings.csv");
    out.println(DistLineSpacing.szCSVHeader);
    for (HashMap.Entry<String,DistLineSpacing> pair : mapSpacings.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Loads.csv");
    out.println(DistLoad.szCSVHeader);
    for (HashMap.Entry<String,DistLoad> pair : mapLoads.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Regulators.csv");
    out.println(DistRegulator.szCSVHeader);
    for (HashMap.Entry<String,DistRegulator> pair : mapRegulators.entrySet()) {
      DistRegulator reg = pair.getValue();
      if (reg.hasTanks) {
        DistXfmrTank tank = mapTanks.get(reg.tid[0]); // TODO: revisit if GridLAB-D can model un-banked regulator tanks
        out.print (pair.getValue().GetCSV(tank.bus[0], tank.orderedPhases[0], tank.bus[1], tank.orderedPhases[1]));
        tank.glmUsed = false;  // don't write these as separate transformers to CSV
      } else {
        DistPowerXfmrWinding xfmr = mapXfmrWindings.get(reg.pid);
        out.print (pair.getValue().GetCSV(xfmr.bus[0], "ABC", xfmr.bus[1], "ABC"));
        xfmr.glmUsed = false;  // don't write these as separate transformers to CSV
      }
    }
    out.close();

    out =  new PrintWriter(fRoot + "_XfmrCodes.csv");
    out.println(DistXfmrCodeRating.szCSVHeader);
    for (HashMap.Entry<String,DistXfmrCodeRating> pair : mapCodeRatings.entrySet()) {
      DistXfmrCodeRating obj = pair.getValue();
      DistXfmrCodeSCTest sct = mapCodeSCTests.get (obj.id);
      DistXfmrCodeNLTest oct = mapCodeNLTests.get (obj.id);
      out.print (obj.GetCSV(sct, oct));
    }
    out.close();

    out =  new PrintWriter(fRoot + "_XfmrTanks.csv");
    out.println(DistXfmrTank.szCSVHeader);
    for (HashMap.Entry<String,DistXfmrTank> pair : mapTanks.entrySet()) {
      DistXfmrTank obj = pair.getValue();
      if (obj.glmUsed) {
        out.print (obj.GetCSV());
      }
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Transformers.csv");
    out.println(DistPowerXfmrWinding.szCSVHeader);
    for (HashMap.Entry<String,DistPowerXfmrWinding> pair : mapXfmrWindings.entrySet()) {
      DistPowerXfmrWinding obj = pair.getValue();
      if (obj.glmUsed) {
        DistPowerXfmrMesh mesh = mapXfmrMeshes.get(obj.id);
        DistPowerXfmrCore core = mapXfmrCores.get (obj.id);
        out.print (obj.GetCSV(mesh, core));
      }
    }
    out.close();

    out =  new PrintWriter(fRoot + "_TriplexLines.csv");
    out.println(DistLinesCodeZ.szCSVHeader);
    for (HashMap.Entry<String,DistLinesCodeZ> pair : mapLinesCodeZ.entrySet()) {
      if (pair.getValue().phases.contains("s")) out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_PhaseLineCodes.csv");
    out.println(DistPhaseMatrix.szCSVHeader);
    for (HashMap.Entry<String,DistPhaseMatrix> pair : mapPhaseMatrices.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_SequenceLineCodes.csv");
    out.println(DistSequenceMatrix.szCSVHeader);
    for (HashMap.Entry<String,DistSequenceMatrix> pair : mapSequenceMatrices.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Wires.csv");
    out.println(DistOverheadWire.szCSVHeader);
    for (HashMap.Entry<String,DistOverheadWire> pair : mapWires.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_CNCables.csv");
    out.println(DistConcentricNeutralCable.szCSVHeader);
    for (HashMap.Entry<String,DistConcentricNeutralCable> pair : mapCNCables.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_TSCables.csv");
    out.println(DistTapeShieldCable.szCSVHeader);
    for (HashMap.Entry<String,DistTapeShieldCable> pair : mapTSCables.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Switches.csv");
    out.println(DistSwitch.szCSVHeader);
    for (HashMap.Entry<String,DistSwitch> pair : mapSwitches.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    for (HashMap.Entry<String,DistFuse> pair : mapFuses.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    for (HashMap.Entry<String,DistRecloser> pair : mapReclosers.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    for (HashMap.Entry<String,DistBreaker> pair : mapBreakers.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    for (HashMap.Entry<String,DistSectionaliser> pair : mapSectionalisers.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    for (HashMap.Entry<String,DistJumper> pair : mapJumpers.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    for (HashMap.Entry<String,DistDisconnector> pair : mapDisconnectors.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Solar.csv");
    out.println(DistSolar.szCSVHeader);
    for (HashMap.Entry<String,DistSolar> pair : mapSolars.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Storage.csv");
    out.println(DistStorage.szCSVHeader);
    for (HashMap.Entry<String,DistStorage> pair : mapStorages.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_SyncGen.csv");
    out.println(DistSyncMachine.szCSVHeader);
    for (HashMap.Entry<String,DistSyncMachine> pair : mapSyncMachines.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_I1547Conn.csv");
    out.println(DistIEEE1547Connection.szCSVHeader);
    for (HashMap.Entry<String,DistIEEE1547Connection> pair : mapIEEE1547Connections.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_I1547Sig.csv");
    out.println(DistIEEE1547Signal.szCSVHeader);
    if (mapIEEE1547Connections.size() > 0) {
      MakeTerminalMap();
    }
    for (HashMap.Entry<String,DistIEEE1547Signal> pair : mapIEEE1547Signals.entrySet()) {
      out.print (pair.getValue().GetCSV(mapTerminals));
    }
    out.close();

    out =  new PrintWriter(fRoot + "_I1547Used.csv");
    out.println(DistIEEE1547Used.szCSVHeader);
    for (HashMap.Entry<String,DistIEEE1547Used> pair : mapIEEE1547Used.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Profile.csv");
    out.println(DistEnergyConnectionProfile.szCSVHeader);
    for (HashMap.Entry<String,DistEnergyConnectionProfile> pair : mapDssProfiles.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    for (HashMap.Entry<String,DistEnergyConnectionProfile> pair : mapGlmProfiles.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();

    out =  new PrintWriter(fRoot + "_Source.csv");
    out.println(DistSubstation.szCSVHeader);
    for (HashMap.Entry<String,DistSubstation> pair : mapSubstations.entrySet()) {
      out.print (pair.getValue().GetCSV());
    }
    out.close();
  }

  public void start(QueryHandler queryHandler, CIMQuerySetter querySetter, String fTarget, String fRoot, 
      String fSched, double load_scale, boolean bWantSched, boolean bWantZIP, boolean randomZIP, 
      boolean useHouses, double Zcoeff, double Icoeff, double Pcoeff, boolean bHaveEventGen, ModelState ms, 
      boolean bTiming, String fEarth, int iManualFile, boolean bUseProfiles) throws FileNotFoundException{
    start(queryHandler, querySetter, fTarget, fRoot, fSched, load_scale, bWantSched, bWantZIP, randomZIP, useHouses,
        Zcoeff, Icoeff, Pcoeff, -1, bHaveEventGen, ms, bTiming, fEarth, iManualFile, bUseProfiles, new ArrayList<String>());
  }


  /**
   * @param queryHandler sends queries to Blazegraph and gets 
   *           results
   * @param querySetter manages the SPARQL for model components 
   * @param fTarget glm, dss, both(glm+dss), csv, idx, cim
   * @param fRoot root name for model output files
   * @param fSched name of a GridLAB-D schedule file for loads
   * @param load_scale multiplier on the nominal or peak loads
   * @param bWantSched true to use a time schedule for GridLAB-D
   *           loads
   * @param bWantZIP true if using Zcoeff, Icoeff, Pcoeff
   * @param randomZIP true to randomize Zcoeff, Icoeff, Pcoeff
   * @param useHouses true for houses to replace triplex loads
   * @param Zcoeff fixed portion of constant-impedance load
   * @param Icoeff fixed portion of constant-current load
   * @param Pcoeff fixed portion of constant-power load
   * @param maxMeasurements postive number to limit the number of
   *            measurements created
   * @param bHaveEventGen true if the GridLAB-D export won't need
   *            it's own fault_check and eventgen
   *            objects for electrical islands
   * @param ms used only for testing switch operations
   * @param bTiming true for logging SPARQL query times
   * @param fEarth Deri, Carson, FullCarson for OpenDSS
   * @param iManualFile 1 to reference manual pre-edits, 2 for 
   *                    post-edits, 3 for both edits in exported
   *                    OpenDSS / GridLAB-D
   * @param bUseProfiles true to use players, schedules and shapes 
   * @throws FileNotFoundException may occur if a file cannot be 
   *                 opened in the specified
   *                 directory for writing
   */
  public void start(QueryHandler queryHandler, CIMQuerySetter querySetter, String fTarget, String fRoot, String fSched,
      double load_scale, boolean bWantSched, boolean bWantZIP, boolean randomZIP,
      boolean useHouses, double Zcoeff, double Icoeff, double Pcoeff, int maxMeasurements, boolean bHaveEventGen, 
      ModelState ms, boolean bTiming, String fEarth, int iManualFile, boolean bUseProfiles, List<String> separateLoads) throws FileNotFoundException{

    this.queryHandler = queryHandler;
    this.querySetter = querySetter;
    String fOut, fXY, fID, fDict, fInclude1, fInclude2;
    fInclude1 = "";
    fInclude2 = "";

    if (fTarget.equals("glm")) {
      LoadAllMaps(useHouses);
      PrepMapsForExport();
      CheckMaps();
      UpdateModelState(ms);
      ApplyCurrentLimits();
      // PrintAllMaps();
      fDict = fRoot + "_dict.json";
      fOut = fRoot + "_base.glm";
      fXY = fRoot + "_symbols.json";
      if ((iManualFile & 1) > 0) {
        fInclude1 = fRoot + "_edits.glm";
      }
      if ((iManualFile & 2) > 0) {
        fInclude2 = fRoot + "_edits2.glm";
      }
      PrintWriter pOut = new PrintWriter(fOut);
      WriteGLMFile(pOut, load_scale, bWantSched, fSched, bWantZIP, randomZIP, useHouses, Zcoeff, Icoeff, Pcoeff, 
                   bHaveEventGen, bUseProfiles, fInclude1, fInclude2, separateLoads);
      PrintWriter pXY = new PrintWriter(fXY);
      WriteJSONSymbolFile (pXY);
      PrintWriter pDict = new PrintWriter(fDict);
      WriteDictionaryFile (pDict, maxMeasurements);
      PrintWriter pLimits = new PrintWriter(fRoot + "_limits.json");
      WriteLimitsFile (pLimits);
    } else if (fTarget.equals("dss")) {
      LoadAllMaps();
      PrepMapsForExport();
      CheckMaps();
      UpdateModelState(ms);
      ApplyCurrentLimits();
      // PrintAllMaps();
      // PrintOneMap (mapCoordinates, "** XY COORDINATES");
      fDict = fRoot + "_dict.json";
      fOut = fRoot + "_base.dss";
      fXY = fRoot + "_busxy.dss";
      fID = fRoot + "_uuid.dss";
      if ((iManualFile & 1) > 0) {
        fInclude1 = fRoot + "_edits.dss";
      }
      if ((iManualFile & 2) > 0) {
        fInclude2 = fRoot + "_edits2.dss";
      }
      PrintWriter pOut = new PrintWriter(fOut);
      PrintWriter pID = new PrintWriter(fID);
      WriteDSSFile (pOut, pID, fXY, fID, load_scale, bWantSched, fSched, bWantZIP, Zcoeff, 
                    Icoeff, Pcoeff, fEarth, bUseProfiles, fInclude1, fInclude2);
      PrintWriter pXY = new PrintWriter(fXY);
      WriteDSSCoordinates (pXY);
      PrintWriter pSym = new PrintWriter (fRoot + "_symbols.json");
      WriteJSONSymbolFile (pSym);
      PrintWriter pDict = new PrintWriter(fDict);
      WriteDictionaryFile (pDict, maxMeasurements);
      PrintWriter pLimits = new PrintWriter(fRoot + "_limits.json");
      WriteLimitsFile (pLimits);
    } else if (fTarget.equals("both")) {
      long t1 = System.nanoTime();
      LoadAllMaps(useHouses);
      long t2 = System.nanoTime();
      PrepMapsForExport();
      long t3 = System.nanoTime();
      CheckMaps();
      long t4 = System.nanoTime();
      UpdateModelState(ms);
      long t5 = System.nanoTime();
      ApplyCurrentLimits();
      long t6 = System.nanoTime();
      // write OpenDSS first, before GridLAB-D can modify the phases
      fXY = fRoot + "_busxy.dss";
      fID = fRoot + "_uuid.dss";
      if ((iManualFile & 1) > 0) {
        fInclude1 = fRoot + "_edits.dss";
      }
      if ((iManualFile & 2) > 0) {
        fInclude2 = fRoot + "_edits2.dss";
      }
      PrintWriter pDss = new PrintWriter(fRoot + "_base.dss");
      PrintWriter pID = new PrintWriter(fID);
      WriteDSSFile (pDss, pID, fXY, fID, load_scale, bWantSched, fSched, bWantZIP, Zcoeff, Icoeff, Pcoeff, 
                    fEarth, bUseProfiles, fInclude1, fInclude2);
      long t7 = System.nanoTime();
      PrintWriter pXY = new PrintWriter(fXY);
      WriteDSSCoordinates (pXY);
      long t8 = System.nanoTime();
      // write GridLAB-D and the dictionaries to match GridLAB-D
      PrintWriter pGld = new PrintWriter(fRoot + "_base.glm");
      if ((iManualFile & 1) > 0) {
        fInclude1 = fRoot + "_edits.glm";
      }
      if ((iManualFile & 2) > 0) {
        fInclude2 = fRoot + "_edits2.glm";
      }
      WriteGLMFile(pGld, load_scale, bWantSched, fSched, bWantZIP, randomZIP, useHouses, Zcoeff, 
                   Icoeff, Pcoeff, bHaveEventGen, bUseProfiles, fInclude1, fInclude2, separateLoads);
      long t9 = System.nanoTime();
      PrintWriter pSym = new PrintWriter(fRoot + "_symbols.json");
      WriteJSONSymbolFile (pSym);
      long t10 = System.nanoTime();
      PrintWriter pDict = new PrintWriter(fRoot + "_dict.json");
      WriteDictionaryFile (pDict, maxMeasurements);
      long t11 = System.nanoTime();
      PrintWriter pLimits = new PrintWriter(fRoot + "_limits.json");
      WriteLimitsFile (pLimits);
      long t12 = System.nanoTime();
      if (bTiming) {
        System.out.format ("LoadAllMaps:         %7.4f\n", (double) (t2 - t1) / 1.0e9);
        System.out.format ("PrepMapsForExport:   %7.4f\n", (double) (t3 - t2) / 1.0e9);
        System.out.format ("CheckMaps:           %7.4f\n", (double) (t4 - t3) / 1.0e9);
        System.out.format ("UpdateModelState:    %7.4f\n", (double) (t5 - t4) / 1.0e9);
        System.out.format ("ApplyCurrentLimits:  %7.4f\n", (double) (t6 - t5) / 1.0e9);
        System.out.format ("WriteDSSFile:        %7.4f\n", (double) (t7 - t6) / 1.0e9);
        System.out.format ("WriteDSSCoordinates: %7.4f\n", (double) (t8 - t7) / 1.0e9);
        System.out.format ("WriteGLMFile:        %7.4f\n", (double) (t9 - t8) / 1.0e9);
        System.out.format ("WriteJSONSymbolFile: %7.4f\n", (double) (t10 - t9) / 1.0e9);
        System.out.format ("WriteDictionaryFile: %7.4f\n", (double) (t11 - t10) / 1.0e9);
        System.out.format ("WriteLimitsFile:     %7.4f\n", (double) (t12 - t11) / 1.0e9);
      }
    } else if (fTarget.equals("csv")) {
      LoadAllMaps();
      PrepMapsForExport();
      CheckMaps();
      UpdateModelState(ms);
      ApplyCurrentLimits();
      WriteCsvFiles (fRoot);
    } else if (fTarget.equals("idx")) {
      fOut = fRoot + "_feeder_index.json";
      PrintWriter pOut = new PrintWriter(fOut);
      WriteIndexFile (pOut);
    } else if (fTarget.equals("cim")) {
      LoadAllMaps();
      PrepMapsForExport();
      CheckMaps();
      fOut = fRoot + ".xml";
      PrintWriter pOut = new PrintWriter(fOut);
      new CIMWriter().WriteCIMFile (this, queryHandler, pOut);
    }
  }


  protected void UpdateModelState(ModelState ms){
    List<SyncMachine> machinesToUpdate = ms.getSynchronousmachines();
    List<Switch> switchesToUpdate = ms.getSwitches();
    //  System.out.println("Generators");
    //  for(String key: mapSyncMachines.keySet()){
    //    DistSyncMachine gen = mapSyncMachines.get(key);
    //    System.out.println(key+"  "+gen.p+"  "+gen.q);
    //  }

    for (SyncMachine machine : machinesToUpdate) {
      DistSyncMachine toUpdate = mapSyncMachines.get(machine.name);
      if(toUpdate!=null){
        toUpdate.p = machine.p;
        toUpdate.q = machine.q;
      }
    }

    HashMap<String,DistSwitch> mapSwitches = new HashMap<>();
    mapSwitches.putAll (mapLoadBreakSwitches);
    mapSwitches.putAll (mapFuses);
    mapSwitches.putAll (mapJumpers);
    mapSwitches.putAll (mapBreakers);
    mapSwitches.putAll (mapReclosers);
    mapSwitches.putAll (mapSectionalisers);
    mapSwitches.putAll (mapDisconnectors);
    mapSwitches.putAll (mapJumpers);
    mapSwitches.putAll (mapGroundDisconnectors);

    for (Switch sw : switchesToUpdate) {
      DistSwitch toUpdate = mapSwitches.get(sw.name);
      if(toUpdate!=null){
        toUpdate.open = sw.open;
      }
    }

    //  for(DistSwitch s: switchesToUpdate){
    //    DistSwitch toUpdate = mapLoadBreakSwitches.get(s.name);
    //    if(toUpdate!=null){
    //    toUpdate.open = s.open;
    //    }
    //    //mapLoadBreakSwitches.put(s.name, (DistLoadBreakSwitch) toUpdate);
    //  }
    //  for(DistSwitch s: switchesToUpdate){
    //    DistSwitch toUpdate = mapFuses.get(s.name);
    //    if(toUpdate!=null){
    //    toUpdate.open = s.open;
    //    }
    //    //mapFuses.put(s.name, (DistFuse)toUpdate);
    //  }
    //  for(DistSwitch s: switchesToUpdate){
    //    DistSwitch toUpdate = mapBreakers.get(s.name);
    //    if(toUpdate!=null){
    //    toUpdate.open = s.open;
    //    }
    //    //mapBreakers.put(s.name, (DistBreaker) toUpdate);
    //  }
    //  for(DistSwitch s: switchesToUpdate){
    //    DistSwitch toUpdate = mapReclosers.get(s.name);
    //    if(toUpdate!=null){
    //    toUpdate.open = s.open;
    //    }
    //    //mapReclosers.put(s.name, (DistRecloser) toUpdate);
    //  }
    //  for(DistSwitch s: switchesToUpdate){
    //    DistSwitch toUpdate = mapSectionalisers.get(s.name);
    //    if(toUpdate!=null){
    //    toUpdate.open = s.open;
    //    }
    //    //mapSectionalisers.put(s.name, (DistSectionaliser) toUpdate);
    //  }
    //  for(DistSwitch s: switchesToUpdate){
    //    DistSwitch toUpdate = mapDisconnectors.get(s.name);
    //    if(toUpdate!=null){
    //    toUpdate.open = s.open;
    //    }
    //    //mapDisconnectors.put(s.name,  (DistDisconnector) toUpdate);
    //  }
    //
    //  System.out.println("Switches");
    //  for(String key: mapSwitches.keySet()){
    //    DistSwitch gen = mapSwitches.get(key);
    //    System.out.println(key+"  "+gen.open);
    //  }

  }
  /**
   *
   * @param queryHandler sends queries to Blazegraph and gets 
   *           results
   * @param out for file output streaming
   * @param querySetter manages the SPARQL for model components 
   * @param fSched name of a GridLAB-D schedule file for loads
   * @param load_scale multiplier on the nominal or peak loads
   * @param bWantSched true to use a time schedule for GridLAB-D
   *           loads
   * @param bWantZIP true if using Zcoeff, Icoeff, Pcoeff
   * @param randomZIP true to randomize Zcoeff, Icoeff, Pcoeff
   * @param useHouses true for houses to replace triplex loads
   * @param Zcoeff fixed portion of constant-impedance load
   * @param Icoeff fixed portion of constant-current load
   * @param Pcoeff fixed portion of constant-power load
   * @param bHaveEventGen true if the GridLAB-D export won't need
   *            it's own fault_check and eventgen
   *            objects for electrical islands
   * @param iManualFile 1 to include reference to an include file
   *                    of manual pre-edits in OpenDSS/GridLAB-D,
   *                    2 for post-edits and 3 for both edits
   * @param bUseProfiles true to use players, schedules and shapes 
   */
  public void generateGLMFile(QueryHandler queryHandler, CIMQuerySetter querySetter, 
      PrintWriter out, String fSched,
      double load_scale, boolean bWantSched, boolean bWantZIP,
      boolean randomZIP, boolean useHouses, double Zcoeff,
      double Icoeff, double Pcoeff, boolean bHaveEventGen,
      boolean bUseProfiles) {
    this.queryHandler = queryHandler;
    if(this.querySetter==null) {
      this.querySetter = querySetter;
    }
    if(!allMapsLoaded){
      LoadAllMaps();
      PrepMapsForExport();
    }
    CheckMaps();
    ApplyCurrentLimits();
    String fInclude1 = "";
    String fInclude2 = "";
    WriteGLMFile (out, load_scale, bWantSched, fSched, bWantZIP, randomZIP, useHouses, 
                  Zcoeff, Icoeff, Pcoeff, bHaveEventGen, bUseProfiles, fInclude1, fInclude2, new ArrayList<String>());
  }

  /**
   *
   * @param queryHandler sends queries to Blazegraph and gets 
   *           results
   * @param out stream for the OpenDSS components
   */
  public void generateJSONSymbolFile(QueryHandler queryHandler, PrintWriter out){
    this.queryHandler = queryHandler;
    if(this.querySetter==null) {
      this.querySetter=new CIMQuerySetter();
    }
    if(!allMapsLoaded){
      LoadAllMaps();
      PrepMapsForExport();
    }
    CheckMaps();
    WriteJSONSymbolFile(out);
  }


  public void generateDictionaryFile(QueryHandler queryHandler, PrintWriter out, boolean useHouses, ModelState modelState){
    generateDictionaryFile(queryHandler, out, -1, useHouses, modelState);
  }
  /**
   *
   * @param queryHandler sends queries to Blazegraph and gets 
   *           results
   * @param out stream for the OpenDSS components
   * @param useHouses true for houses to replace triplex loads
   * @param maxMeasurements postive number to limit the number of
   *            measurements created
   * @param ms used only for testing switch operations
   */
  public void generateDictionaryFile(QueryHandler queryHandler, PrintWriter out, int maxMeasurements, boolean useHouses,ModelState ms){
    this.queryHandler = queryHandler;
    if(this.querySetter==null) {
      this.querySetter=new CIMQuerySetter();
    }
    if(!allMapsLoaded){
      LoadAllMaps(useHouses);
      PrepMapsForExport();
    }
    CheckMaps();
    UpdateModelState(ms);
    WriteDictionaryFile(out, maxMeasurements);
  }

  /**
   * @param queryHandler sends queries to Blazegraph and gets 
   *           results
   * @param out stream for the OpenDSS components
   * @param outID stream for the OpenDSS UUID values
   * @param fXY name of output file for XY coordinates, to call 
   *      from master OpenDSS file
   * @param fID name of output file for UUID / mRID values, to 
   *      call from the master OpenDSS file
   * @param fSched name of a GridLAB-D schedule file for loads 
   *         (not implemented for OpenDSS?)
   * @param load_scale multiplier on the nominal or peak loads
   * @param bWantSched true to use a time schedule for GridLAB-D
   *           loads (not implemented for OpenDSS?)
   * @param bWantZIP true if using Zcoeff, Icoeff, Pcoeff
   * @param Zcoeff fixed portion of constant-impedance load
   * @param Icoeff fixed portion of constant-current load
   * @param Pcoeff fixed portion of constant-power load
   * @param fEarth Deri, Carson, FullCarson for OpenDSS 
   * @param bUseProfiles true to use players, schedules and shapes 
   */
  public void generateDSSFile(QueryHandler queryHandler, PrintWriter out, PrintWriter outID, String fXY, String fID,
      double load_scale, boolean bWantSched, String fSched, boolean bWantZIP, double Zcoeff, double Icoeff, double Pcoeff, 
      String fEarth, boolean bUseProfiles){
    this.queryHandler = queryHandler;
    if(this.querySetter==null) {
      this.querySetter=new CIMQuerySetter();
    }
    if(!allMapsLoaded){
      LoadAllMaps();
      PrepMapsForExport();
    }
    CheckMaps();
    ApplyCurrentLimits();
    String fInclude1 = "";
    String fInclude2 = "";
    WriteDSSFile(out, outID, fXY, fID, load_scale, bWantSched, fSched, bWantZIP, Zcoeff, Icoeff, Pcoeff, 
                 fEarth, bUseProfiles, fInclude1, fInclude2);
  }

  /**
   *
  * @param queryHandler sends queries to Blazegraph and gets 
  *           results
  * @param out stream for the OpenDSS components
   */
  public void generateDSSCoordinates(QueryHandler queryHandler, PrintWriter out){
    this.queryHandler = queryHandler;
    if(this.querySetter==null) {
      this.querySetter=new CIMQuerySetter();
    }
    if(!allMapsLoaded){
      LoadAllMaps();
      PrepMapsForExport();
    }
    CheckMaps();

    WriteDSSCoordinates(out);
  }

  /**
   *
  * @param queryHandler sends queries to Blazegraph and gets 
  *           results
  * @param out stream for the OpenDSS components
   */
  public void generateFeederIndexFile(QueryHandler queryHandler, PrintWriter out){
    this.queryHandler = queryHandler;
    if(this.querySetter==null) {
      this.querySetter=new CIMQuerySetter();
    }
    WriteIndexFile(out);
  }

  public static void main (String args[]) throws FileNotFoundException {
    String fRoot = "";
    double freq = 60.0, load_scale = 1.0;
    boolean bWantSched = false, bWantZIP = false, bSelectFeeder = false, randomZIP = false, useHouses = false;
    boolean bHaveEventGen = false;
    boolean bTiming = false;
    boolean bReadSPARQL = false;
    int iManualFile = 0;
    boolean bUseProfiles = false;
    String fSched = "";
    String fTarget = "dss";
    String feeder_mRID = "";
    double Zcoeff = 0.0, Icoeff = 0.0, Pcoeff = 0.0;
    String blazegraphURI = "http://localhost:8889/bigdata/namespace/kb/sparql";
    String fSPARQL = "";
    String fEarth = "deri";
    if (args.length < 1) {
      System.out.println ("Usage: java CIMImporter [options] output_root");
      System.out.println ("       -q={queries_file}  // optional file with CIM namespace and component queries (defaults to CIM100x)");
      System.out.println ("       -s={mRID}          // select one feeder by CIM mRID; selects all feeders if not specified");
      System.out.println ("       -o={glm|dss|both|idx|cim|csv} // output format; defaults to glm");
      System.out.println ("       -l={0..1}          // load scaling factor; defaults to 1");
      System.out.println ("       -f={50|60}         // system frequency; defaults to 60");
      System.out.println ("       -e={Deri|Carson|FullCarson} // earth model for OpenDSS, defaults to Deri but GridLAB-D supports only Carson");
      System.out.println ("       -n={schedule_name} // root filename for scheduled ZIP loads (defaults to none)");
      System.out.println ("       -m={0, 1, 2, 3}    // include references to manual edits (none, prefix, suffix, both) in OpenDSS or GridLAB-D exports (defaults to 0)");
      System.out.println ("       -z={0..1}          // constant Z portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)");
      System.out.println ("       -i={0..1}          // constant I portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)");
      System.out.println ("       -p={0..1}          // constant P portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)");
      System.out.println ("       -r={0, 1}          // determine ZIP load fraction based on given xml file or randomized fractions");
      System.out.println ("       -h={0, 1}          // determine if house load objects should be added to the model or not");
      System.out.println ("       -x={0, 1}          // indicate whether for glm, the model will be called with a fault_check already created");
      System.out.println ("       -t={0, 1}          // request timing of top-level methods and SPARQL queries, requires -o=both for methods");
      System.out.println ("       -a={0, 1}          // use of EnergyConnectionProfile class (default 0)");
      System.out.println ("       -d={0, 1, 2}       // use of safe name, name, or mRID to identify simulator objects; defaults to safe name");
      System.out.println ("                          // safe name replaces characters from the set \" .=+^$*|[]{}\" with \"_\"");
      System.out.println ("       -u={http://localhost:8889/bigdata/namespace/kb/sparql} // blazegraph uri (if connecting over HTTP); defaults to http://localhost:8889/bigdata/namespace/kb/sparql");

      System.out.println ("Example 1: java CIMImporter -l=1 -i=1 -n=zipload_schedule ieee8500");
      System.out.println ("   assuming Jena and Commons-Math are in Java's classpath, this will produce two output files");
      System.out.println ("   1) ieee8500_base.glm with GridLAB-D components for a constant-current model at peak load,");
      System.out.println ("      where each load's base_power attributes reference zipload_schedule.player");
      System.out.println ("      This file includes an adjustable source voltage, and manual capacitor/tap changer states.");
      System.out.println ("      It should be invoked from a separate GridLAB-D file that sets up the clock, solver, recorders, etc.");
      System.out.println ("      For example, these two GridLAB-D input lines set up 1.05 per-unit source voltage on a 115-kV system:");
      System.out.println ("          #define VSOURCE=69715.065 // 66395.3 * 1.05");
      System.out.println ("          #include \"ieee8500_base.glm\"");
      System.out.println ("      If there were capacitor/tap changer controls in the CIM input file, that data was written to");
      System.out.println ("          ieee8500_base.glm as comments, which can be recovered through manual edits.");
      System.out.println ("   2) ieee8500_symbols.json with component labels and geographic coordinates, used in GridAPPS-D but not GridLAB-D");
      System.out.println ("Example 2: java CIMImporter -o=dss ieee8500");
      System.out.println ("   assuming Jena and Commons-Math are in Java's classpath, this will produce three output files");
      System.out.println ("   1) ieee8500_base.dss with OpenDSS components for the CIM LoadResponseCharacteristic at peak load");
      System.out.println ("      It should be invoked from a separate OpenDSS file that sets up the solution and options.");
      System.out.println ("   2) ieee8500_busxy.dss with node xy coordinates");
      System.out.println ("   3) ieee8500_uuid.dss with CIM mRID values for the components");
      System.exit (0);
    }

    int i = 0;
    while (i < args.length) {
      if (args[i].charAt(0) == '-') {
        char opt = args[i].charAt(1);
        String optVal = args[i].substring(3);
        if (opt == 'l') {
          load_scale = Double.parseDouble(optVal);
        } else if (opt == 'o') {
          fTarget = optVal;
        } else if (opt == 'f') {
          freq = Double.parseDouble(optVal);
          DistComponent.SetSystemFrequency (freq);
        } else if (opt == 'n') {
          fSched = optVal;
          bWantSched = true;
        } else if (opt == 'z') {
          Zcoeff = Double.parseDouble(optVal);
          bWantZIP = true;
        } else if (opt == 'i') {
          Icoeff = Double.parseDouble(optVal);
          bWantZIP = true;
        } else if (opt == 'p') {
          Pcoeff = Double.parseDouble(optVal);
          bWantZIP = true;
        } else if (opt == 'r' && Integer.parseInt(optVal) == 1) {
          randomZIP = true;
        } else if (opt == 'h' && Integer.parseInt(optVal) == 1) {
          useHouses = true;
        } else if (opt == 'm') {
          iManualFile = Integer.parseInt(optVal);
        } else if (opt == 'x' && Integer.parseInt(optVal) == 1) {
          bHaveEventGen = true;
        } else if (opt == 't' && Integer.parseInt(optVal) == 1) {
          bTiming = true;
        } else if (opt == 's') {
          feeder_mRID = optVal;
          bSelectFeeder = true;
        } else if (opt == 'u') {
          blazegraphURI = optVal;
        } else if (opt == 'q') {
          fSPARQL = optVal;
          bReadSPARQL = true;
        } else if (opt == 'e') {
          fEarth = optVal.toLowerCase();
        } else if (opt == 'a' && Integer.parseInt(optVal) == 1) {
          bUseProfiles = true;
        } else if (opt == 'd') {
          int choice = Integer.parseInt(optVal);
          if (choice == 1) {
            DistComponent.SetExportNames (ExportNameMode.NAME);
          } else if (choice == 2) {
            DistComponent.SetExportNames (ExportNameMode.MRID);
          } else {
            DistComponent.SetExportNames (ExportNameMode.SAFENAME);
          }
        }
      } else {
        if (fTarget.equals("glm")) {
          fRoot = args[i];
        } else if (fTarget.equals("dss")) {
          fRoot = args[i];
        } else if (fTarget.equals("idx")) {
          fRoot = args[i];
        } else if (fTarget.equals("cim")) {
          fRoot = args[i];
        } else if (fTarget.equals("both")) {
          fRoot = args[i];
        } else if (fTarget.equals("csv")) {
          fRoot = args[i];
        } else {
          System.out.println ("Unknown target type " + fTarget);
          System.exit(0);
        }
      }
      ++i;
    }

    try {
      org.apache.jena.query.ARQ.init();
      HTTPBlazegraphQueryHandler qh = new HTTPBlazegraphQueryHandler(blazegraphURI);
      CIMQuerySetter qs = new CIMQuerySetter();
      if (bReadSPARQL) {
        qs.setQueriesFromXMLFile (fSPARQL);
      }
      if (bSelectFeeder) {
        qh.addFeederSelection (feeder_mRID);
      }
      qh.setTiming (bTiming);

      List<SyncMachine> machinesToUpdate = new ArrayList<>();
      List<Switch> switchesToUpdate = new ArrayList<>();
      ModelState ms = new ModelState(machinesToUpdate, switchesToUpdate);

      new CIMImporter().start(qh, qs, fTarget, fRoot, fSched, load_scale,
            bWantSched, bWantZIP, randomZIP, useHouses,
            Zcoeff, Icoeff, Pcoeff, bHaveEventGen, ms, bTiming, fEarth, iManualFile,
            bUseProfiles);
    } catch (RuntimeException e) {
      System.out.println ("Can not produce a model: " + e.getMessage());
      e.printStackTrace();
    }
  }
}

