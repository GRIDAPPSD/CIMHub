package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2018, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistRecloser extends DistSwitch {
	public static final String szCIMClass = "Recloser";

	public DistRecloser (ResultSet results) {
		super (results);
	}

	public String CIMClass() {
		return szCIMClass;
	}

	public String GetGLM () {
		StringBuilder buf = new StringBuilder ("object recloser {\n");

		buf.append ("  name \"swt_" + name + "\";\n");
		buf.append ("  from \"" + bus1 + "\";\n");
		buf.append ("  to \"" + bus2 + "\";\n");
		buf.append ("  phases " + glm_phases + ";\n");
		if (open) {
			buf.append ("  status OPEN;\n");
		} else {
			buf.append ("  status CLOSED;\n");
		}
		AppendGLMRatings (buf, glm_phases, normalCurrentLimit, emergencyCurrentLimit);
		buf.append("}\n");
		return buf.toString();
	}

	public String GetDSS () {
		StringBuilder buf = new StringBuilder (super.GetDSS());

		buf.append ("  new Recloser." + name + " MonitoredObj=Line." + name +
								" PhaseTrip=20000.0 GroundTrip=10000.0 ");
    if (open) {
      buf.append (" state=open\n");
    } else {
      buf.append (" state=closed\n");
    }
		return buf.toString();
	}
}


