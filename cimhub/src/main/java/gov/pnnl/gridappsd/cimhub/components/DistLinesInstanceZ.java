package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import org.apache.commons.math3.complex.Complex;
import java.util.HashMap;

public class DistLinesInstanceZ extends DistLineSegment {
  public double r1; 
  public double x1; 
  public double b1; 
  public double r0; 
  public double x0; 
  public double b0; 

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistLinesInstanceZ (ResultSet results, HashMap<String,Integer> map) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      bus1 = GetBusExportName (soln.get("?bus1").toString());
      bus2 = GetBusExportName (soln.get("?bus2").toString());
      t1id = soln.get("?t1id").toString();
      t2id = soln.get("?t2id").toString();
      phases = "ABC";
      len = Double.parseDouble (soln.get("?len").toString());
      basev = Double.parseDouble (soln.get("?basev").toString());
      r1 = Double.parseDouble (soln.get("?r").toString());
      x1 = Double.parseDouble (soln.get("?x").toString());
      b1 = OptionalDouble (soln, "?b", 0.0);
      r0 = OptionalDouble (soln, "?r0", 0.0);
      x0 = OptionalDouble (soln, "?x0", 0.0);
      b0 = OptionalDouble (soln, "?b0", 0.0);
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + " from " + bus1 + " to " + bus2 + " phases=" + phases + " basev=" + df4.format(basev) + " len=" + df4.format(len));
    buf.append (" r1=" + df4.format(r1) + " x1=" + df4.format(x1) + " b1=" + df4.format(b1));
    buf.append (" r0=" + df4.format(r0) + " x0=" + df4.format(x0) + " b0=" + df4.format(b0));
    return buf.toString();
  }

  public String GetGLM() {
    StringBuilder buf = new StringBuilder ();
    AppendSharedGLMAttributes (buf, name, false, false);  // writes length in ft

    // should be per mile
    double k = gMperMILE;
    String seqZs = CFormat (new Complex (k * (r0 + 2.0 * r1) / 3.0, k * (x0 + 2.0 * x1) / 3.0));
    String seqZm = CFormat (new Complex (k * (r0 - r1) / 3.0, k * (x0 - x1) / 3.0));
    String seqCs = df4.format(k * 1.0e9 * (b0 + 2.0 * b1) / 3.0 / gOMEGA);
    String seqCm = df4.format(k * 1.0e9 * (b0 - b1) / 3.0 / gOMEGA);

    buf.append ("object line_configuration {\n");
    buf.append ("  name \"lcon_" + name + "_ABC\";\n");
    for (int i = 1; i <= 3; i++) {
      for (int j = 1; j <= 3; j++) {
        String indices = Integer.toString(i) + Integer.toString(j) + " ";
        if (i == j) {
          buf.append ("  z" + indices + seqZs + ";\n");
          buf.append ("  c" + indices + seqCs + ";\n");
        } else {
          buf.append ("  z" + indices + seqZm + ";\n");
          buf.append ("  c" + indices + seqCm + ";\n");
        }
      }
    }
    buf.append ("}\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }

  public String LabelString() {
    return "seqZ";
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("new Line." + name);

    buf.append (" phases=" + Integer.toString(DSSPhaseCount(phases, false)) + 
                " bus1=" + DSSBusPhases(bus1, phases) + " bus2=" + DSSBusPhases (bus2, phases) + 
                " length=" + df1.format(len) + " units=m\n");
    AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);
    buf.append ("~ r1=" + df6.format(r1) + " x1=" + df6.format(x1) + " c1=" + df6.format(1.0e9 * b1 / gOMEGA) + 
                " r0=" + df6.format(r0) + " x0=" + df6.format(x0) + " c0=" + df6.format(1.0e9 * b0 / gOMEGA) + "\n");

    return buf.toString();
  }
  public static String szCSVHeader = "Name,Bus1,Phases,Bus2,Phases,R1,X1,C1[nF],R0,X0,C0[nF]";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + bus1 + "," + CSVPhaseString(phases) + "," +
                       bus2 + "," + CSVPhaseString(phases) + "," +
                       df6.format(r1) + "," +
                       df6.format(x1) + "," +
                       df6.format(1.0e9 * b1 / gOMEGA) + "," +
                       df6.format(r0) + "," +
                       df6.format(x0) + "," +
                       df6.format(1.0e9 * b0 / gOMEGA) + "\n");
    return buf.toString();
  }
}

