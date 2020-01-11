package gov.pnnl.gridappsd.cimhub;
// ----------------------------------------------------------
// Copyright (c) 2017-2020, Battelle Memorial Institute
// All rights reserved.
// ----------------------------------------------------------

import java.io.*;

import gov.pnnl.gridappsd.cimhub.CIMImporter;
import gov.pnnl.gridappsd.cimhub.components.DistComponent;
import gov.pnnl.gridappsd.cimhub.components.DistFeeder;

public class CIMQuerySetter extends Object {
	String obj = "";
	StringBuilder buf = new StringBuilder("");
	String delims = "[ ]+";

	private void updateQuery () {
		if ((buf.length() > 0) && (obj.length() > 0)) {
			System.out.println (obj + ":" + buf.toString());
			if (obj.equals("nsCIM")) {
				DistComponent.nsCIM = buf.toString();
			} else if (obj.equals("DistFeeder")) {
				DistFeeder.szQUERY = buf.toString();
			}
		}
		buf = new StringBuilder("");
	}

	private boolean wantThisLine (String ln) {
		if (ln.length() < 0) return false;
		if (ln.contains("PREFIX")) return false;
		if (ln.startsWith("#")) return false;
		return true;
	}

	public void setQueriesFromFile (String fname) {
		String ln;
		boolean inQuery = false;

		System.out.println ("Reading queries from " + fname);

		try {
			BufferedReader br = new BufferedReader(new FileReader(fname));
			while ((ln = br.readLine()) != null) {
				if (ln.contains ("#@")) {
					if (inQuery) {
						updateQuery();
					} else {
						obj = ln.split (delims)[1];
					}
					inQuery = !inQuery;
				} else if (inQuery) {
					if (wantThisLine (ln)) {
						buf.append(ln);
					}
				}
			}
			updateQuery();
		} catch (IOException e) {
		}
	}
}

