package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistEquipment extends DistComponent {
  public String name;
  public String id;
  public String exportName;
  public String eqClass;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"mRID\":\"" + id +"\"");
    buf.append (",\"class\":\"" + eqClass +"\"");
    buf.append (",\"name\":\"" + name +"\"");
    buf.append (",\"exportName\":\"" + exportName + "\"");
    buf.append("}");
    return buf.toString();
  }

  public DistEquipment (String name, String id, String exportName, String eqClass) {
    this.name = name;
    this.id = id;
    this.eqClass = eqClass;
    this.exportName = exportName;
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (id + ":" + eqClass + ":" + name + ":" + exportName);
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

