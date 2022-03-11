package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2021-22, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;
import gov.pnnl.gridappsd.cimhub.CIMTerminal;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Signal;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Used;
import gov.pnnl.gridappsd.cimhub.components.DistSolar;
import gov.pnnl.gridappsd.cimhub.components.DistStorage;

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

	public String GetDSS (HashMap<String,DistSolar> mapSolars, HashMap<String,DistStorage> mapStorages,
                        HashMap<String,DistIEEE1547Used> mapUsed,
                        HashMap<String,DistIEEE1547Signal> mapSignals,
                        HashMap<String,CIMTerminal> mapTerminals) {
		StringBuilder buf = new StringBuilder ("new InvControl." + name + " // " + pids + "\n");
    for (HashMap.Entry<String,DistIEEE1547Used> pair : mapUsed.entrySet()) {
      DistIEEE1547Used dset = pair.getValue();
      if (pids.contains(dset.pecid)) {
        buf.append(dset.GetDSS());
      }
    }
    if (pids.length() > 0) { // connect this to the PowerElectronicUnits
      buf.append("~ derlist=[");
      for (HashMap.Entry<String,DistSolar> pair : mapSolars.entrySet()) {
        DistSolar dpv = pair.getValue();
        if (pids.contains(dpv.pecid)) {
          buf.append("pvsystem." + dpv.name);
        }
      }
      for (HashMap.Entry<String,DistStorage> pair : mapStorages.entrySet()) {
        DistStorage dbat = pair.getValue();
        if (pids.contains(dbat.pecid)) {
          buf.append("storage." + dbat.name);
        }
      }
      buf.append("]\n");
    }
    for (HashMap.Entry<String,DistIEEE1547Signal> pair : mapSignals.entrySet()) {
      DistIEEE1547Signal dsig = pair.getValue();
      if (pids.contains(dsig.pecid)) {
        buf.append("// rsig " + dsig.name + ":" + dsig.kind + ":" + dsig.tid + "\n");
      }
    }
    return buf.toString();
	}

  public static String szCSVHeader = "Name,PECs";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + pids + "\n");
    return buf.toString();
  }
}

