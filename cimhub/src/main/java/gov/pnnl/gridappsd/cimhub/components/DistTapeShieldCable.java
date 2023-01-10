package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;

public class DistTapeShieldCable extends DistCable {
  public static final String szCIMClass = "TapeShieldCableInfo";

  public double tlap;
  public double tthick;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistTapeShieldCable (ResultSet results) {
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
      tlap = OptionalDouble (soln, "?tapelap", 0.0);
      tthick = OptionalDouble (soln, "?tapethickness", 0.0);
      dEpsR = OptionalDouble (soln, "?epsr", 2.3);
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    AppendCableDisplay (buf);
    buf.append (" tlap=" + df2.format(tlap) + " tthick=" + df6.format(tthick));
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("new TSData.");
    AppendDSSCableAttributes (buf);
    buf.append ("\n~ DiaShield=" + df6.format(dscreen + 2.0 * tthick) + " tapeLayer=" + df6.format(tthick) +
                " tapeLap=" + df3.format(tlap));
    buf.append ("\n");
    return buf.toString();
  }

  public String GetGLM() {
    StringBuilder buf = new StringBuilder("object underground_line_conductor {\n");
    // equation 4.89 from Kersting 3rd edition gives rshield = 18.826/ds/T [Ohms/mile]
    //  where ds is shield diameter [in] and T is tape thickness [mil]
    double rshield = 1.214583e-5 / dscreen / tthick; // for dscreen and tthick in [m]

    buf.append ("  name \"" + GLMObjectPrefix ("tscab_") + name + "\";\n");
    buf.append ("  shield_gmr " + df6.format (0.5 * dscreen * gFTperM) + ";\n");
    buf.append ("  shield_diameter " + df6.format (dscreen * gFTperM * 12.0) + ";\n");
    buf.append ("  shield_resistance " + df6.format (rshield) + ";\n");
    buf.append ("  shield_thickness " + df6.format (tthick * gFTperM * 12.0) + ";\n");
    AppendGLMCableAttributes (buf);
    buf.append("}\n");
    return buf.toString();
  }

  public static String szCSVHeader = DistCable.szCSVHeader + ",Tlap,Tthick";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder ("");
    AppendCSVCableAttributes (buf);
    buf.append ("," + df3.format(tlap) + "," + df6.format(tthick) + "\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

