package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistEquipment extends DistComponent {
  public String eqName;
  public String safeName;
  public String eqID;
  public String eqClass;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"mRID\":\"" + eqID +"\"");
    buf.append (",\"class\":\"" + eqClass +"\"");
    buf.append (",\"name\":\"" + eqName +"\"");
    buf.append (",\"safeName\":\"" + safeName + "\"");
    buf.append("}");
    return buf.toString();
  }

  public DistEquipment (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      eqID = soln.get("?id").toString();
      eqName = soln.get("?name").toString();
      eqClass = soln.get("?cimclass").toString();
      safeName = SafeName(eqName);
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (eqID + ":" + eqClass + ":" + eqName + ":" + safeName);
    return buf.toString();
  }

  public String GetKey() {
    return eqID;
  }
}

