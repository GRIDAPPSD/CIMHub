package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017-2022, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistLinesCodeZ extends DistLineSegment {
	public String lname;
	public String codeid;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append (",\"mRID\":\"" + id +"\"");
		buf.append ("}");
		return buf.toString();
	}

	public DistLinesCodeZ (ResultSet results, HashMap<String,Integer> map) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
			bus1 = SafeName (soln.get("?bus1").toString()); 
			bus2 = SafeName (soln.get("?bus2").toString());
      t1id = soln.get("?t1id").toString();
      t2id = soln.get("?t2id").toString();
			basev = Double.parseDouble (soln.get("?basev").toString());
			len = Double.parseDouble (soln.get("?len").toString());
			lname = SafeName (soln.get("?lname").toString());
			codeid = soln.get("?codeid").toString();
			int nphs = map.get (name);
			if (nphs > 0) {
				StringBuilder buf = new StringBuilder(soln.get("?phs").toString());
				for (int i = 1; i < nphs; i++) {
					soln = results.next();
					buf.append (soln.get("?phs").toString());
				}
				phases = buf.toString();
			} else {
				phases = "ABC";
			}
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name + " from " + bus1 + " to " + bus2 + " phases=" + phases + " basev=" + df4.format(basev) + " len=" + df4.format(len)  + " linecode=" + lname);
		return buf.toString();
	}

	public String GetGLM() {
		StringBuilder buf = new StringBuilder ();
		AppendSharedGLMAttributes (buf, lname, false, false);
		return buf.toString();
	}

	public String GetKey() {
		return name;
	}

	public String LabelString() {
		return lname;
	}

	public String GetDSS() {
		StringBuilder buf = new StringBuilder ("new Line." + name);

		buf.append (" phases=" + Integer.toString(DSSPhaseCount(phases, false)) + 
								" bus1=" + DSSBusPhases(bus1, phases) + " bus2=" + DSSBusPhases (bus2, phases) + 
								" length=" + df3.format(len * gFTperM) + " linecode=" + lname + " units=ft\n");
		AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);

		return buf.toString();
	}

  public static String szCSVHeader = "Name,Bus1,Phases,Bus2,Phases,LineCode,Length,Units";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + bus1 + "," + CSVPhaseString(phases) + "," +
                                           bus2 + "," + CSVPhaseString(phases) + "," + lname + "," +
                                           df3.format(len * gFTperM) + ",ft\n");
    return buf.toString();
  }
}

