package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistBus extends DistComponent {
  public String name;
  public String exportName;
  public String id;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"mRID\":\"" + id +"\"");
    buf.append (",\"name\":\"" + name +"\"");
    buf.append (",\"exportName\":\"" + exportName + "\"");
    buf.append("}");
    return buf.toString();
  }

  public DistBus (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = soln.get("?name").toString();
      exportName = MakeExportName(name, id);
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (id + ":" + name + ":" + exportName);
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

