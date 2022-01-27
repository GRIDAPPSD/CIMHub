package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017-2022, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;

public class DistXfmrCodeNLTest extends DistComponent {
	public String pname;
	public String tname;
	public double nll;
	public double iexc;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + pname +"\"");
		buf.append ("}");
		return buf.toString();
	}

	public DistXfmrCodeNLTest (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			pname = SafeName (soln.get("?pname").toString());
			tname = SafeName (soln.get("?tname").toString());
			nll = Double.parseDouble (soln.get("?nll").toString());
			iexc = Double.parseDouble (soln.get("?iexc").toString());
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (pname + ":" + tname + " NLL=" + df4.format(nll) + " iexc=" + df4.format(iexc));
		return buf.toString();
	}

	public String GetKey() {
		return tname;
	}
}

