package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;

public class DistOverheadWire extends DistWire {
  public static final String szCIMClass = "OverheadWireInfo";

  public boolean canBury;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistOverheadWire (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      rad = Double.parseDouble (soln.get("?rad").toString());
      gmr = Double.parseDouble (soln.get("?gmr").toString());
      rdc = OptionalDouble (soln, "?rdc", 0.0);
      r25 = OptionalDouble (soln, "?r25", 0.0);
      r50 = OptionalDouble (soln, "?r50", 0.0);
      r75 = OptionalDouble (soln, "?r75", 0.0);
      corerad = OptionalDouble (soln, "?corerad", 0.0);
      amps = OptionalDouble (soln, "?amps", 0.0);
      insthick = OptionalDouble (soln, "?insthick", 0.0);
      ins = OptionalBoolean (soln, "?ins", false);
      insmat = OptionalString (soln, "?insmat", "N/A");
      canBury = false;
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    AppendWireDisplay (buf);
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("new WireData.");
    AppendDSSWireAttributes (buf);
    buf.append ("\n");
    return buf.toString();
  }

  public String GetGLM() {
    double diaOut = 2.0 * rad * gFTperM * 12.0;
    double resOut = r50 * gMperMILE;
    double gmrOut = gmr * gFTperM;

    StringBuilder buf = new StringBuilder("object overhead_line_conductor {\n");
      buf.append ("  name \"" + GLMObjectPrefix ("wire_") + name + "\";\n");
      buf.append ("  geometric_mean_radius " + df6.format (gmrOut) + ";\n");
      buf.append ("  diameter " + df6.format (diaOut) + ";\n");
      buf.append ("  resistance " + df6.format (resOut) + ";\n");
      AppendGLMWireAttributes (buf);
      buf.append("}\n");

    if (canBury) {
      buf.append ("object underground_line_conductor {\n");
      buf.append ("  name \"" + GLMObjectPrefix ("ugwire_", true) + name + "\";\n");
      buf.append ("  conductor_gmr " + df6.format (gmrOut) + ";\n");
      buf.append ("  conductor_diameter " + df6.format (diaOut) + ";\n");
      buf.append ("  outer_diameter " + df6.format (1.2 * diaOut) + ";\n");
      buf.append ("  conductor_resistance " + df6.format (resOut) + ";\n");
      AppendGLMWireAttributes (buf);
      buf.append("}\n");
    }
    return buf.toString();
  }

  public static String szCSVHeader = DistWire.szCSVHeader;

  public String GetCSV () {
    StringBuilder buf = new StringBuilder ("");
    AppendCSVWireAttributes (buf);
    buf.append ("\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

