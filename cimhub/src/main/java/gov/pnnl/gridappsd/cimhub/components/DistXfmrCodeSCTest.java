package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistXfmrCodeSCTest extends DistComponent {
  public static final String szCIMClass = "ShortCircuitTests";

  public String id;
  public int[] fwdg;
  public int[] twdg;
  public double[] z;
  public double[] ll;
  public double[] sbase;

  public int size;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"id\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  private void SetSize (int val) {
    size = val;
    fwdg = new int[size];
    twdg = new int[size];
    z = new double[size];
    ll = new double[size];
    sbase = new double[size];
  }

  public DistXfmrCodeSCTest (ResultSet results, HashMap<String,Integer> map) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?tid").toString();
      SetSize (map.get(id));
      for (int i = 0; i < size; i++) {
        fwdg[i] = Integer.parseInt (soln.get("?enum").toString());
        twdg[i] = Integer.parseInt (soln.get("?gnum").toString());
        z[i] = Double.parseDouble (soln.get("?z").toString());
        ll[i] = Double.parseDouble (soln.get("?ll").toString());
        sbase[i] = Double.parseDouble (soln.get("?base").toString());
        if ((i + 1) < size) {
          soln = results.next();
        }
      }
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder (id);
    for (int i = 0; i < size; i++) {
      buf.append ("\n  fwdg=" + Integer.toString(fwdg[i]) + " twdg=" + Integer.toString(twdg[i]) +
          " z=" + df4.format(z[i]) + " LL=" + df4.format(ll[i]) + " base=" + df4.format(sbase[i]));
    }
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

