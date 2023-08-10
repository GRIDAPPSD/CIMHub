package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;

public class DistConcentricNeutralCable extends DistCable {
  public static final String szCIMClass = "ConcentricNeutralCableInfo";

  public double dneut;
  public int strand_cnt; 
  public double strand_gmr;
  public double strand_rad;
  public double strand_rdc;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistConcentricNeutralCable (ResultSet results) {
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
      dcore = OptionalDouble (soln, "?diacore", 0.0);
      djacket = OptionalDouble (soln, "?diajacket", 0.0);
      dins = OptionalDouble (soln, "?diains", 0.0);
      dscreen = OptionalDouble (soln, "?diascreen", 0.0);
      sheathNeutral = OptionalBoolean (soln, "?sheathneutral", false);
      dneut = OptionalDouble (soln, "?dianeut", 0.0);
      strand_cnt = OptionalInt (soln, "?strand_cnt", 0);
      strand_gmr = OptionalDouble (soln, "?strand_gmr", 0.0);
      strand_rad = OptionalDouble (soln, "?strand_rad", 0.0);
      strand_rdc = OptionalDouble (soln, "?strand_rdc", 0.0);
      dEpsR = OptionalDouble (soln, "?epsr", 2.3);
    }
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    AppendCableDisplay (buf);
    buf.append (" dneut=" + df6.format(dneut) + " strand_cnt=" + Integer.toString(strand_cnt));
    buf.append (" strand_gmr=" + df6.format(strand_gmr) + " strand_rad=" + df6.format(strand_rad) + " strand_rdc=" + df6.format(strand_rdc));
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("new CNData.");
    AppendDSSCableAttributes (buf);
    buf.append ("\n~ k=" + Integer.toString(strand_cnt) + " GmrStrand=" + df6.format(strand_gmr) +
                " DiaStrand=" + df6.format(2.0 * strand_rad) + " Rstrand=" + df6.format(strand_rdc));
    buf.append ("\n");
    return buf.toString();
  }

  public String GetGLM() {
    StringBuilder buf = new StringBuilder("object underground_line_conductor {\n");

    buf.append ("  name \"" + GLMObjectPrefix ("cncab_") + name + "\";\n");
    buf.append ("  neutral_gmr " + df6.format (strand_gmr * gFTperM) + ";\n");
    buf.append ("  neutral_diameter " + df6.format (2.0 * strand_rad * gFTperM * 12.0) + ";\n");
    buf.append ("  neutral_resistance " + df6.format (strand_rdc * gMperMILE) + ";\n");
    buf.append ("  neutral_strands " + Integer.toString(strand_cnt) + ";\n");
    AppendGLMCableAttributes (buf);
    buf.append("}\n");
    return buf.toString();
  }

  public static String szCSVHeader = DistCable.szCSVHeader + ",DIAn,Ns,GMRs,DIAs,RESs";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder ("");
    AppendCSVCableAttributes (buf);
    buf.append ("," + df6.format(dneut) + "," + Integer.toString(strand_cnt) + "," + df6.format(strand_gmr) + "," +
          df6.format(2.0 * strand_rad) + "," + df6.format(strand_rdc) + "\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

