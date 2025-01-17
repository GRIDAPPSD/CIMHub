package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import org.apache.commons.math3.complex.Complex;

public class DistSequenceMatrix extends DistComponent {
  public static final String szCIMClass = "PerLengthSequenceImpedance";

  public String name;
  public String id;
  public double r1;
  public double x1;
  public double b1;
  public double r0;
  public double x0;
  public double b0;

  private String seqZs;
  private String seqZm;
  private String seqCs;
  private String seqCm;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistSequenceMatrix (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      r1 = Double.parseDouble (soln.get("?r1").toString());
      x1 = Double.parseDouble (soln.get("?x1").toString());
      b1 = Double.parseDouble (soln.get("?b1").toString());
      r0 = Double.parseDouble (soln.get("?r0").toString());
      x0 = Double.parseDouble (soln.get("?x0").toString());
      b0 = Double.parseDouble (soln.get("?b0").toString());

      seqZs = CFormat (new Complex (gMperMILE * (r0 + 2.0 * r1) / 3.0, gMperMILE * (x0 + 2.0 * x1) / 3.0));
      seqZm = CFormat (new Complex (gMperMILE * (r0 - r1) / 3.0, gMperMILE * (x0 - x1) / 3.0));
      seqCs = df4.format(1.0e9 * gMperMILE * (b0 + 2.0 * b1) / 3.0 / gOMEGA);
      seqCm = df4.format(1.0e9 * gMperMILE * (b0 - b1) / 3.0 / gOMEGA);
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + " r1=" + df6.format(r1) + " x1=" + df6.format(x1) + " b1=" + df9.format(b1));
    buf.append (" r0=" + df6.format(r0) + " x0=" + df6.format(x0) + " b0=" + df9.format(b0));
    return buf.toString();
  }

  private void AppendPermutation (StringBuilder buf, String perm, int[] permidx) {
    int cnt = permidx.length;

    buf.append("object line_configuration {\n");
    buf.append("  name \"" + GLMObjectPrefix ("lcon_") + name + "_" + perm + "\";\n");
    for (int i = 0; i < cnt; i++) {
      for (int j = 0; j < cnt; j++) {
        String indices = Integer.toString(permidx[i]) + Integer.toString(permidx[j]) + " ";
        if (i == j) {
          buf.append ("  z" + indices + seqZs + ";\n");
          buf.append ("  c" + indices + seqCs + ";\n");
        } else {
          buf.append ("  z" + indices + seqZm + ";\n");
          buf.append ("  c" + indices + seqCm + ";\n");
        }
      }
    }
    buf.append("}\n");
  }

  // TODO: implement glmUsed pattern from DistPhaseMatrix here; for now always writing the ABC permutation
  public String GetGLM() {
    StringBuilder buf = new StringBuilder ("");
    AppendPermutation (buf, "ABC", new int[] {1, 2, 3});
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("new Linecode." + name + " nphases=3 units=mi");
    buf.append (" r1=" + df6.format(gMperMILE * r1));
    buf.append (" x1=" + df6.format(gMperMILE * x1));
    buf.append (" c1=" + df6.format(1.0e9 * gMperMILE * b1/ gOMEGA));
    buf.append (" r0=" + df6.format(gMperMILE * r0));
    buf.append (" x0=" + df6.format(gMperMILE * x0));
    buf.append (" c0=" + df6.format(1.0e9 * gMperMILE * b0/ gOMEGA));
    buf.append ("\n");
    
    return buf.toString();
  }

  public static String szCSVHeader = "Name,NumPhases,Units,r1,x1,c1[nF],r0,x0,c0[nF]";

  public String GetCSV () {
    return name + ",3,mi," + 
      df6.format(gMperMILE * r1) + "," + df6.format(gMperMILE * x1) + "," + df6.format(1.0e9 * gMperMILE * b1/ gOMEGA) + "," +
      df6.format(gMperMILE * r0) + "," + df6.format(gMperMILE * x0) + "," + df6.format(1.0e9 * gMperMILE * b0/ gOMEGA) + "\n";
  }

  public String GetKey() {
    return id;
  }
}

