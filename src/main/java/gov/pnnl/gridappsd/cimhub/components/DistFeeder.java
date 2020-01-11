package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017-2020, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistFeeder extends DistComponent {
	public static String szQUERY = 
		"SELECT ?feeder ?fid ?station ?sid ?subregion ?sgrid ?region ?rgnid WHERE {"+
		"?s r:type c:Feeder."+
		"?s c:IdentifiedObject.name ?feeder."+
		"?s c:IdentifiedObject.mRID ?fid."+
		"?s c:Feeder.NormalEnergizingSubstation ?sub."+
		"?sub c:IdentifiedObject.name ?station."+
		"?sub c:IdentifiedObject.mRID ?sid."+
		"?sub c:Substation.Region ?sgr."+
		"?sgr c:IdentifiedObject.name ?subregion."+
		"?sgr c:IdentifiedObject.mRID ?sgrid."+
		"?sgr c:SubGeographicalRegion.Region ?rgn."+
		"?rgn c:IdentifiedObject.name ?region."+
		"?rgn c:IdentifiedObject.mRID ?rgnid."+
		"}"+
		" ORDER by ?station ?feeder";
/*
	public static final String szQUERY = 
		"SELECT ?feeder ?fid ?region ?rgnid WHERE {"+
		"?s r:type c:Line."+
		"?s c:IdentifiedObject.name ?feeder."+
		"?s c:IdentifiedObject.mRID ?fid."+
		"?s c:Line.Region ?rgn."+
		"?rgn c:IdentifiedObject.name ?region."+
		"?rgn c:IdentifiedObject.mRID ?rgnid."+
		"}"+
		" ORDER by ?feeder";
*/
	public String feederName;
	public String feederID;
	public String substationName;
	public String substationID;
	public String subregionName;
	public String subregionID;
	public String regionName;
	public String regionID;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + feederName +"\"");
		buf.append (",\"mRID\":\"" + feederID +"\"");
		buf.append (",\"substationName\":\"" + substationName + "\"");
		buf.append (",\"substationID\":\"" + substationID + "\"");
		buf.append (",\"subregionName\":\"" + subregionName + "\"");
		buf.append (",\"subregionID\":\"" + subregionID + "\"");
		buf.append (",\"regionName\":\"" + regionName + "\"");
		buf.append (",\"regionID\":\"" + regionID + "\"");
		buf.append("}");
		return buf.toString();
	}

	public DistFeeder (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			feederName = SafeName (soln.get("?feeder").toString());
			feederID = soln.get("?fid").toString();
			regionName = SafeName (soln.get("?region").toString());
			regionID = soln.get("?rgnid").toString();
			substationName = SafeName (OptionalString (soln, "?station", null));
			substationID = OptionalString (soln, "?sid", null);
			subregionName = SafeName (OptionalString (soln, "?subregion", null));
			subregionID = OptionalString (soln, "?sgrid", null);
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (feederName + ":" + feederID + "\n");
		buf.append ("  " + substationName + ":" + substationID + "\n");
		buf.append ("  " + subregionName + ":" + subregionID + "\n");
		buf.append ("  " + regionName + ":" + regionID + "\n");
		return buf.toString();
	}

	public String GetKey() {
		return feederName;
	}
}

