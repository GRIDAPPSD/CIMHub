package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistXfmrCodeSCTest extends DistComponent {
	public String pname;
	public String tname;
	public int[] fwdg;
	public int[] twdg;
	public double[] z;
	public double[] ll;

	public int size;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + pname +"\"");
		buf.append ("}");
		return buf.toString();
	}

	private void SetSize (int val) {
		size = val;
		fwdg = new int[size];
		twdg = new int[size];
		z = new double[size];
		ll = new double[size];
	}

	public DistXfmrCodeSCTest (ResultSet results, HashMap<String,Integer> map) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			String p = soln.get("?pname").toString();
			String t = soln.get("?tname").toString();
			pname = SafeName (p);
			tname = SafeName (t);
			SetSize (map.get(tname));
			for (int i = 0; i < size; i++) {
				fwdg[i] = Integer.parseInt (soln.get("?enum").toString());
				twdg[i] = Integer.parseInt (soln.get("?gnum").toString());
				z[i] = Double.parseDouble (soln.get("?z").toString());
				ll[i] = Double.parseDouble (soln.get("?ll").toString());
				if ((i + 1) < size) {
					soln = results.next();
				}
			}
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (pname + ":" + tname);
		for (int i = 0; i < size; i++) {
			buf.append ("\n  fwdg=" + Integer.toString(fwdg[i]) + " twdg=" + Integer.toString(twdg[i]) +
								" z=" + df4.format(z[i]) + " LL=" + df4.format(ll[i]));
		}
		return buf.toString();
	}

	public String GetKey() {
		return tname;
	}
}

