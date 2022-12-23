package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;

public class DistPowerXfmrCore extends DistComponent {
  public static final String szCIMClass = "TransformerCoreAdmittance";

  public String pid;
  public int wdg;
  public double b;
  public double g;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"pid\":\"" + pid +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistPowerXfmrCore (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      pid = soln.get("?pid").toString();
      wdg = Integer.parseInt (soln.get("?enum").toString());
      b = Math.abs(Double.parseDouble (soln.get("?b").toString()));
      g = Double.parseDouble (soln.get("?g").toString());
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (pid + " wdg=" + Integer.toString(wdg) + " g=" + df4.format(g) + " b=" + df4.format(b));
    return buf.toString();
  }

  public String GetKey() {
    return pid;
  }
}

