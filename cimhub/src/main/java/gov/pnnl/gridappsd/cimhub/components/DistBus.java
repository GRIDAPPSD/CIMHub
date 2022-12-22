package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistBus extends DistComponent {
  public String busName;
  public String safeName;
  public String busID;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"mRID\":\"" + busID +"\"");
    buf.append (",\"name\":\"" + busName +"\"");
    buf.append (",\"safeName\":\"" + safeName + "\"");
    buf.append("}");
    return buf.toString();
  }

  public DistBus (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      busID = soln.get("?id").toString();
      busName = soln.get("?name").toString();
      safeName = SafeName(busName);
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (busID + ":" + busName + ":" + safeName);
    return buf.toString();
  }

  public String GetKey() {
    return busID;
  }
}

