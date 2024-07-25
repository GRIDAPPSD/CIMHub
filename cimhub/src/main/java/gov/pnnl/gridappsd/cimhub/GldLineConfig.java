package gov.pnnl.gridappsd.cimhub;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import gov.pnnl.gridappsd.cimhub.components.DistComponent;

/** 
 Helper class to accumulate spacings and conductors. 
*/
public class GldLineConfig {
  public final String name;
  public String spacing;
  public String conductor_A;
  public String conductor_B;
  public String conductor_C;
  public String conductor_N;

  public GldLineConfig (String name) {
    this.name = name;
    spacing = "";
    conductor_A = "";
    conductor_B = "";
    conductor_C = "";
    conductor_N = "";
  }

  static String GetMatchWire (String wclass, String name, boolean buried) {
    if (wclass.equals("OverheadWireInfo")) {
      if (buried) {
        return DistComponent.GLMObjectPrefix ("ugwire_", true) + name;
      } else {
        return DistComponent.GLMObjectPrefix ("wire_") + name;
      }
    } else if (wclass.equals("ConcentricNeutralCableInfo")) {
      return DistComponent.GLMObjectPrefix ("cncab_") + name;
    } else if (wclass.equals("TapeShieldCableInfo")) {
      return DistComponent.GLMObjectPrefix ("tscab_") + name;
    }
    return "unknown_" + name;
  }

  public String GetGLM () {
    StringBuilder buf = new StringBuilder ();
    buf.append ("object line_configuration {\n");
    buf.append ("  name \"" + name + "\";\n");
    buf.append ("  spacing \"" + spacing + "\";\n");
    if (conductor_A.length() > 0) {
      buf.append ("  conductor_A \"" + conductor_A + "\";\n");
    }
    if (conductor_B.length() > 0) {
      buf.append ("  conductor_B \"" + conductor_B + "\";\n");
    }
    if (conductor_C.length() > 0) {
      buf.append ("  conductor_C \"" + conductor_C + "\";\n");
    }
    if (conductor_N.length() > 0) {
      buf.append ("  conductor_N \"" + conductor_N + "\";\n");
    }
    buf.append("}\n");
    return buf.toString();
  }
}

