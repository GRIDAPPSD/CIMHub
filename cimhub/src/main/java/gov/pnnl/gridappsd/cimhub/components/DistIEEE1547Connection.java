package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2021, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistIEEE1547Connection extends DistComponent {
	public String id;
	public String name;
  public String pids;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append("}");
		return buf.toString();
	}

	public DistIEEE1547Connection (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
      pids = soln.get("?pids").toString();
      pids = pids.replace ('\n', ':');
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
		return name;  // need a PID?
	}

	public String GetDSS () {
		StringBuilder buf = new StringBuilder ("new InvControl." + name + "\n");
		return buf.toString();
	}

  public static String szCSVHeader = "Name,PECs";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + pids + "\n");
    return buf.toString();
  }
}
