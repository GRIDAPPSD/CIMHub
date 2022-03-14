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
    boolean bA = false;
    boolean bB = false;
    boolean bC = false;
    boolean bs1 = false;
    boolean bs2 = false;
    StringBuilder buf = new StringBuilder("");
    for (HashMap.Entry<String,DistIEEE1547Used> pair : mapUsed.entrySet()) {
      DistIEEE1547Used dset = pair.getValue();
      if (pids.contains(dset.pecid)) {
        buf.append(dset.GetDSS()); // write the settings and XY curve, use that name
        break;
      }
    }
    if (pids.length() > 0) { // connect this to the PowerElectronicUnits
      buf.append("~ derlist=[");
      for (HashMap.Entry<String,DistSolar> pair : mapSolars.entrySet()) {
        DistSolar dpv = pair.getValue();
        if (pids.contains(dpv.pecid)) {
          if (dpv.phases.contains("A")) bA = true;
          if (dpv.phases.contains("B")) bB = true;
          if (dpv.phases.contains("C")) bC = true;
          if (dpv.phases.contains("1")) bs1 = true;
          if (dpv.phases.contains("2")) bs2 = true;
          buf.append(" pvsystem." + dpv.name);
        }
      }
      for (HashMap.Entry<String,DistStorage> pair : mapStorages.entrySet()) {
        DistStorage dbat = pair.getValue();
        if (pids.contains(dbat.pecid)) {
          if (dbat.phases.contains("A")) bA = true;
          if (dbat.phases.contains("B")) bB = true;
          if (dbat.phases.contains("C")) bC = true;
          if (dbat.phases.contains("1")) bs1 = true;
          if (dbat.phases.contains("2")) bs2 = true;
          buf.append(" storage." + dbat.name);
        }
      }
      buf.append("]\n");
    }
    for ( HashMap.Entry<String, DistIEEE1547Signal> pair: mapSignals.entrySet() ) { // remote signals, if used
      DistIEEE1547Signal dsig = pair.getValue();
      if (pids.contains(dsig.pecid)) {
        CIMTerminal trm = mapTerminals.get(dsig.tid);
        int nph = DSSPhaseCount (trm.phases, false);
        double vbase = trm.voltage;
        if (nph > 1) vbase /= Math.sqrt(3.0);
        int nphused = 0;
        buf.append("~ MonBus=["); // " + trm.DisplayString() + "\n");
        if (bA && trm.phases.contains("A")) {
          buf.append (" " + trm.bus + ".1");
          nphused += 1;
        }
        if (bB && trm.phases.contains("B")) {
          buf.append (" " + trm.bus + ".2");
          nphused += 1;
        }
        if (bC && trm.phases.contains("C")) {
          buf.append (" " + trm.bus + ".3");
          nphused += 1;
        }
        if (bs1 && trm.phases.contains("1")) {
          buf.append (" " + trm.bus + ".1");
          nphused += 1;
        }
        if (bs2 && trm.phases.contains("2")) {
          buf.append (" " + trm.bus + ".2");
          nphused += 1;
        }
        buf.append("] MonBusesVBase=[");
        for (int i = 0; i < nphused; i++) {
          buf.append (" " + df3.format(vbase));
        }
        buf.append("]\n");
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

