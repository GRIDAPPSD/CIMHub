package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import java.io.*;
import java.util.HashMap;

public abstract class DistLineSegment extends DistComponent {
  public static final String szCIMClass = "ACLineSegment";

  public String id;
  public String name;
  public String bus1;
  public String bus2;
  public String t1id;
  public String t2id;
  public String phases;
  public double len;
  public double basev;

  public double normalCurrentLimit = 0.0;
  public double emergencyCurrentLimit = 0.0;

  protected boolean bTriplex;
  protected boolean bCable;
  protected String glm_phases;

  public abstract String LabelString();

  protected void AppendSharedGLMAttributes (StringBuilder buf, String config_root, boolean bSpacing, boolean bForceN) {

    if (phases.contains ("s")) {
      bTriplex = true;
      buf.append ("object triplex_line {\n");
      buf.append ("  name \"" + GLMObjectPrefix ("tpx_") + name + "\";\n");
    } else {
      bTriplex = false;
      if (bCable) {
        buf.append("object underground_line {\n");
      } else {
        buf.append("object overhead_line {\n");
      }
      buf.append ("  name \"" + GLMObjectPrefix ("line_") + name + "\";\n");
    }

    buf.append ("  from \"" + bus1 + "\";\n");
    buf.append ("  to \"" + bus2 + "\";\n");
    StringBuilder phs = new StringBuilder(phases.replace (":", "").replace("s1", "").replace("s2", ""));
    if (bTriplex) phs.append ("S");
    if (phases.contains ("N") || bForceN) phs.append ("N");
    glm_phases = phs.toString();
    buf.append ("  phases " + glm_phases + ";\n");
    buf.append ("  length " + df4.format(len * gFTperM) + ";\n");
    AppendGLMRatings (buf, glm_phases, normalCurrentLimit, emergencyCurrentLimit);
    if (bSpacing) {
      buf.append("  configuration \"" + config_root + "\";\n");
    } else if (bTriplex) {
      buf.append("  configuration \"" + GLMObjectPrefix ("tcon_") + config_root + "_12\";\n");
    } else {
      buf.append("  configuration \"" + GLMObjectPrefix ("lcon_") + config_root + "_" + glm_phases + "\";\n");
    }
    buf.append ("}\n");
  }

  public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
    DistCoordinates pt1 = map.get("ACLineSegment:" + id + ":1");
    DistCoordinates pt2 = map.get("ACLineSegment:" + id + ":2");
    StringBuilder lbl_phs = new StringBuilder ();
    if (phases.contains("A")) lbl_phs.append("A");
    if (phases.contains("B")) lbl_phs.append("B");
    if (phases.contains("C")) lbl_phs.append("C");
    if (phases.contains("s")) lbl_phs.append("S");
    if (lbl_phs.length() < 1) lbl_phs.append("ABC");

    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name + "\"");
    buf.append (",\"from\":\"" + bus1 + "\"");
    buf.append (",\"to\":\"" + bus2 + "\"");
    buf.append (",\"phases\":\"" + lbl_phs.toString() +"\"");
    buf.append (",\"length\":" + df2.format(len * gFTperM));
    buf.append (",\"configuration\":\"" + LabelString() + "\"");
    buf.append (",\"x1\":" + Double.toString(pt1.x));
    buf.append (",\"y1\":" + Double.toString(pt1.y));
    buf.append (",\"x2\":" + Double.toString(pt2.x));
    buf.append (",\"y2\":" + Double.toString(pt2.y));
    buf.append ("}");
    return buf.toString();
  }
}

