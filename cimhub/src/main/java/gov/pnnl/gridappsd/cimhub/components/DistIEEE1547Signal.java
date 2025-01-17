package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2021-22, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;
import gov.pnnl.gridappsd.cimhub.CIMTerminal;

public class DistIEEE1547Signal extends DistComponent {
  public static final String szCIMClass = "RemoteInputSignal";

  public String id;
  public String pecid;
  public String name;
  public String kind;
  public String tid;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append("}");
    return buf.toString();
  }

  public DistIEEE1547Signal (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      pecid = soln.get("?pecid").toString();
      kind = soln.get("?kind").toString();
      tid = soln.get("?tid").toString();
    }   
  }
  
  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name);
    return buf.toString();
  }

  public String GetGLM () {
    StringBuilder buf = new StringBuilder ("object inverter {\n");
    buf.append ("  name \"inv_" + name + "\";\n");
    buf.append("}\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }

  public String GetDSS () {
    StringBuilder buf = new StringBuilder ("// new InvControl." + name + "// Signal\n");
    return buf.toString();
  }

  public static String szCSVHeader = "Name,Kind,Bus,Phases,Voltage";

  public String GetCSV (HashMap<String,CIMTerminal> mapTerminals) {
    CIMTerminal trm = mapTerminals.get(tid);
    StringBuilder buf = new StringBuilder (name + "," + kind + "," + trm.bus + "," + trm.phases + "," + 
                                           df2.format(trm.voltage) + "\n");
    return buf.toString();
  }
}

