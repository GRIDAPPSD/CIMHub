package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistXfmrBank extends DistComponent {
  public static final String szCIMClass = "PowerTransformer";

  public String id;
  public String name;
  public String vgrp;
  public String[] tid;

  public int size;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append ("}");
    return buf.toString();
  }

  private void SetSize (int val) {
    size = val;
    tid = new String[size];
  }

  public DistXfmrBank (ResultSet results, HashMap<String,Integer> map) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      vgrp = soln.get("?vgrp").toString();
      SetSize (map.get(id));
      for (int i = 0; i < size; i++) {
        tid[i] = soln.get("?tid").toString();
        if ((i + 1) < size) {
          soln = results.next();
        }
      }
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + " vgrp=" + vgrp);
    for (int i = 0; i < size; i++) {
      buf.append ("\n  tid=" + tid[i]);
    }
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

