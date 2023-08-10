package gov.pnnl.gridappsd.cimhub;
// ----------------------------------------------------------
// Copyright (c) 2017-2022, Battelle Memorial Institute
// All rights reserved.
// ----------------------------------------------------------

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.SortedSet;
import java.util.TreeSet;

import gov.pnnl.gridappsd.cimhub.components.DistComponent;

import gov.pnnl.gridappsd.cimhub.components.DistCapacitor;
import gov.pnnl.gridappsd.cimhub.components.DistLineSpacing;
import gov.pnnl.gridappsd.cimhub.components.DistLinesSpacingZ;
import gov.pnnl.gridappsd.cimhub.components.DistLoad;
import gov.pnnl.gridappsd.cimhub.components.DistOverheadWire;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeRating;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeSCTest;

public class CIMPatching extends Object {
  private static double sqrt3 = Math.sqrt(3.0);

  public void FixLoads (HashMap<String,DistLoad> mapLoads) { // street light loads
    for (HashMap.Entry<String,DistLoad> pair : mapLoads.entrySet()) {
      DistLoad obj = pair.getValue();
      if (obj.p < 0.001 && obj.q < 0.001) {
        obj.p = 0.2; // kW
      }
    }
  }

  public void FixShortCircuitTests (HashMap<String,DistXfmrCodeSCTest> mapCodeSCTests,
                                    HashMap<String,DistXfmrCodeRating> mapCodeRatings) {
    double vbase, sbase, zbase;
    int fwdg, twdg;

    for (HashMap.Entry<String,DistXfmrCodeSCTest> pair : mapCodeSCTests.entrySet()) {
      DistXfmrCodeSCTest obj = pair.getValue();
      if (obj.z[0] <= 0.0) {
        DistXfmrCodeRating rat = mapCodeRatings.get (obj.id);
        for (int i = 0; i < obj.size; i++) {
          fwdg = obj.fwdg[i];
          twdg = obj.twdg[i];
          vbase = rat.ratedU[fwdg-1];
          sbase = rat.ratedS[fwdg-1];
          zbase = vbase * vbase / sbase;
          if (rat.r[0] <= 0.0) { // put the load loss of 0.5% into first winding resistance
            rat.r[0] = 0.005 * zbase;
            if (obj.size == 3) {
              rat.r[0] *= 2.0;
            }
          }
          if (obj.size == 1) { // for a two-winding transformer, use 3.5% Z and 0.5% load loss
            obj.z[0] = 0.035 * zbase;
            obj.ll[0] = 0.005 * sbase;
          } else if (obj.size == 3) { // assume center-tapped secondary service transformer
            // interlaced, Z1 = 0.5R + j0.8X and Z2 = Z3 = R + j0.4X
            // short-circuit tests, Z23 = 2R + j0.8 and Z12 = Z23 = 1.5R + j1.2X
            // if you parallel both secondary windings then ZHL = R + jX as expected
            // let ZHL = 1 + j2 in percent; note that obj.ll not actually used in model export
            if (fwdg == 1) {  // high side to a low-voltage winding
              obj.z[i] = 0.02 * 1.2 * zbase;
              obj.ll[i] = 0.01 * 1.5 * sbase;
            } else {  // between low-voltage windings
              obj.z[i] = 0.02 * 0.8 * zbase;
              obj.ll[i] = 0.01 * 2.0 * sbase;
            }
          } else {
            System.out.println ("*** Trying to patch the short-circuit tests on a transformer with more than 3 windings:" + obj.id);
          }
        }
      }
    }
  }

  public void FixTransformerKVA (HashMap<String,DistXfmrCodeRating> mapCodeRatings) {
    for (HashMap.Entry<String,DistXfmrCodeRating> pair : mapCodeRatings.entrySet()) {
      DistXfmrCodeRating obj = pair.getValue();
      if (obj.name.contains("kVA") && obj.ratedS[0] < 1501.0) { // TODO, tname used to be pname
        for (int i = 0; i < obj.size; i++) {
          obj.ratedS[i] *= 1000.0;
        }
      }
    }
  }

  public void FixCapacitors (HashMap<String,DistCapacitor> mapCapacitors) { // delta ==> wye
    for (HashMap.Entry<String,DistCapacitor> pair : mapCapacitors.entrySet()) {
      DistCapacitor obj = pair.getValue();
      obj.conn = "Y";
      obj.nomu *= sqrt3;
      obj.SetDerivedParameters();
    }
  }

  public void FixOverheadWires (HashMap<String,DistOverheadWire> mapWires) {
    for (HashMap.Entry<String,DistOverheadWire> pair : mapWires.entrySet()) {
      DistOverheadWire obj = pair.getValue();
      if (obj.name.equals("6A")) { // manual correction we just happened to notice
        obj.gmr = 0.0014097;
      }
      if (obj.rad <= 0.0) {
        if (obj.name.contains("2/0")) {
          obj.amps = 255;
          obj.rad = 0.004775;
          obj.gmr = 0.00353568;
          obj.rdc = obj.r25 = obj.r50 = obj.r75 = 0.000433727;
        } else if (obj.name.contains("4/0")) {
          obj.amps = 380;
          obj.rad = 0.0066294;
          obj.gmr = 0.00481584;
          obj.rdc = obj.r25 = obj.r50 = obj.r75 = 0.00027395;
        } else if (obj.name.contains("350")) {
          obj.amps = 399;
          obj.rad = 0.008623;
          obj.gmr = 0.006523;
          obj.rdc = obj.r25 = obj.r50 = obj.r75 = 0.000185;
        } else if (obj.name.contains("2")) {
          obj.amps = 240;
          obj.rad = 0.0037084;
          obj.gmr = 0.002691384;
          obj.rdc = obj.r25 = obj.r50 = obj.r75 = 0.000548049;
        } else if (obj.name.contains("4")) {  // from 4CU
          obj.amps = 170;
          obj.rad = 0.0025908;
          obj.gmr = 0.002020824;
          obj.rdc = obj.r25 = obj.r50 = obj.r75 = 0.000866813;
        } else if (obj.name.contains("6")) {  // from 6A
          obj.amps = 105;
          obj.rad = 0.00233684;
          obj.gmr = 0.0014097;  // CIM XML has 3 leading zeros for 6A
          obj.rdc = obj.r25 = obj.r50 = obj.r75 = 0.002208005;
        }
      }
    }
  }

  public void FixLineSpacings (HashMap<String,DistLineSpacing> mapSpacings) {
    for (HashMap.Entry<String,DistLineSpacing> pair : mapSpacings.entrySet()) {
      DistLineSpacing obj = pair.getValue();
      if (obj.name.equals("SVC_OH_Wire_Spacing")) {
        obj.xarray[0] = 0.05;
        obj.xarray[1] = 0.00;
        obj.yarray[0] = obj.yarray[1] = 9.144;
      } else if (obj.name.equals("UG_Wire_Spacing")) {
        obj.xarray[0] = -0.1651;
        obj.xarray[1] = 0.00;
        obj.xarray[2] = 0.1651;
        obj.yarray[0] = obj.yarray[1] = obj.yarray[2] = 0.762; // these are really depths
      }
    }
  }

  public void FixLinesSpacingZ (HashMap<String,DistLinesSpacingZ> mapLines) {
    for (HashMap.Entry<String,DistLinesSpacingZ> pair : mapLines.entrySet()) {
      DistLinesSpacingZ obj = pair.getValue();
      if (obj.spacing.equals("OH_Wire_Spacing") && obj.phases.equals("ABC") && obj.nwires < 4) { // needs a neutral conductor
        obj.nwires = 4;
        String wire_phase = obj.wire_phases[0];
        String wire_name = obj.wire_names[0];
        String wire_class = obj.wire_classes[0];
        System.out.println ("Adding neutral to " + obj.name);
        obj.wire_phases = new String[obj.nwires];
        obj.wire_names = new String[obj.nwires];
        obj.wire_classes = new String[obj.nwires];
        for (int i = 0; i < obj.nwires; i++) {
          obj.wire_phases[i] = wire_phase;
          obj.wire_names[i] = wire_name;
          obj.wire_classes[i] = wire_class;
        }
      }
    }
  }
}

