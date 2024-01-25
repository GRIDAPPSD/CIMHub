package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistPowerXfmrMesh extends DistComponent {
  public static final String szCIMClass = "TransformerMeshImpedances";

  public String pid;
  public int[] fwdg;
  public int[] twdg;
  public double[] r;
  public double[] x;
  public int size;

  private void SetSize (int val) {
    size = val;
    fwdg = new int[size];
    twdg = new int[size];
    r = new double[size];
    x = new double[size];
  }

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"pid\":\"" + pid +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistPowerXfmrMesh (ResultSet results, HashMap<String,Integer> map) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      pid = soln.get("?pid").toString();
      SetSize (map.get(pid));
      for (int i = 0; i < size; i++) {
        fwdg[i] = Integer.parseInt (soln.get("?fnum").toString());
        twdg[i] = Integer.parseInt (soln.get("?tnum").toString());
        r[i] = Double.parseDouble (soln.get("?r").toString());
        x[i] = Double.parseDouble (soln.get("?x").toString());
        if ((i + 1) < size) {
          soln = results.next();
        }
      }
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (pid + " " + Integer.toString(size));
    for (int i = 0; i < size; i++) {
      buf.append ("\n  fwdg=" + Integer.toString(fwdg[i]) + " twdg=" + Integer.toString(twdg[i]) +
                  " r=" + df6.format(r[i]) + " x=" + df6.format(x[i]));
    }
    return buf.toString();
  }

  public String GetKey() {
    return pid;
  }
}

