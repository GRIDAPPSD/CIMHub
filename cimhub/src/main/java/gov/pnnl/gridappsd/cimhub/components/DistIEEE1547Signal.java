package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2021, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistIEEE1547Signal extends DistComponent {
	public String id;
	public String name;
  public String phase;
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
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
      phase = soln.get("?phs").toString();
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
		return name + "_" + phase;
	}

	public String GetDSS () {
		StringBuilder buf = new StringBuilder ("// new InvControl." + name + "// Signal\n");
		return buf.toString();
	}

  public static String szCSVHeader = "Name,Kind,Phase,TID";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + kind + "," + phase + "," + tid + "\n");
    return buf.toString();
  }
}

