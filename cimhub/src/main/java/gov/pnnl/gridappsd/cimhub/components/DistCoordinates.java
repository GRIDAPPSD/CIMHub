package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;

public class DistCoordinates extends DistComponent {
  public String name;
  public String id;
  public double x;
  public double y;
  public int seq;
  public String cname;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistCoordinates (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      name = soln.get("?name").toString();
      id = soln.get("?id").toString();
      x = Double.parseDouble (soln.get("?x").toString());
      y = Double.parseDouble (soln.get("?y").toString());
      seq = Integer.parseInt (soln.get("?seq").toString());
      cname = soln.get("?class").toString();
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (cname + ":" + name + ":" + Integer.toString(seq) + " x=" + df4.format(x) + " y=" + df4.format(y));
    return buf.toString();
  }

  public static String szCSVHeader = "Busname,X,Y";

  public String GetKey() {
    return cname + ":" + name + ":" + Integer.toString(seq);
  }
}

