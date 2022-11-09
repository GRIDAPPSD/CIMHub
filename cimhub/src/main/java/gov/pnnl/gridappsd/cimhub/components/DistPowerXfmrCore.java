package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;

public class DistPowerXfmrCore extends DistComponent {
	public String name;
	public int wdg;
	public double b;
	public double g;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append ("}");
		return buf.toString();
	}

	public DistPowerXfmrCore (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?pname").toString());
			wdg = Integer.parseInt (soln.get("?enum").toString());
			b = Double.parseDouble (soln.get("?b").toString());
			g = Double.parseDouble (soln.get("?g").toString());
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name + " wdg=" + Integer.toString(wdg) + " g=" + df4.format(g) + " b=" + df4.format(b));
		return buf.toString();
	}

	public String GetKey() {
		return name;
	}
}

