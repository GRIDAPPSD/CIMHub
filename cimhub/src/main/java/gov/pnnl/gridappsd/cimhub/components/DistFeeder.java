package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistFeeder extends DistComponent {
  public String feederName;
  public String feederID;
  public String substationName;
  public String substationID;
  public String subregionName;
  public String subregionID;
  public String regionName;
  public String regionID;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + feederName +"\"");
    buf.append (",\"mRID\":\"" + feederID +"\"");
    buf.append (",\"substationName\":\"" + substationName + "\"");
    buf.append (",\"substationID\":\"" + substationID + "\"");
    buf.append (",\"subregionName\":\"" + subregionName + "\"");
    buf.append (",\"subregionID\":\"" + subregionID + "\"");
    buf.append (",\"regionName\":\"" + regionName + "\"");
    buf.append (",\"regionID\":\"" + regionID + "\"");
    buf.append("}");
    return buf.toString();
  }

  public DistFeeder (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      feederName = SafeName (soln.get("?feeder").toString());
      feederID = soln.get("?fid").toString();
      regionName = SafeName (soln.get("?region").toString());
      regionID = soln.get("?rgnid").toString();
      substationName = SafeName (OptionalString (soln, "?station", null));
      substationID = OptionalString (soln, "?sid", null);
      subregionName = SafeName (OptionalString (soln, "?subregion", null));
      subregionID = OptionalString (soln, "?sgrid", null);
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (feederName + ":" + feederID + "\n");
    buf.append ("  " + substationName + ":" + substationID + "\n");
    buf.append ("  " + subregionName + ":" + subregionID + "\n");
    buf.append ("  " + regionName + ":" + regionID + "\n");
    return buf.toString();
  }

  public String GetKey() {
    return feederName;
  }
}

