package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017-2022, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistSwitch extends DistComponent {
	public String id;
	public String name;
	public String bus1;
	public String bus2;
  public String t1id;
  public String t2id;
	public String phases;
	public boolean open;
	public double basev;
	public double rated;
	public double breaking;

	public double normalCurrentLimit = 0.0;
	public double emergencyCurrentLimit = 0.0;

	public String glm_phases;

	public String CIMClass() {
		return null;
	}

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append (",\"mRID\":\"" + id +"\"");
		buf.append (",\"CN1\":\"" + bus1 + "\"");
		buf.append (",\"CN2\":\"" + bus2 + "\"");
		buf.append (",\"phases\":\"" + phases.replace("\n", "") + "\"");
		buf.append (",\"ratedCurrent\":" + df1.format(rated));
		buf.append (",\"breakingCapacity\":" + df1.format(breaking));
		if (open) {
			buf.append (",\"normalOpen\":true");
		} else {
			buf.append (",\"normalOpen\":false");
		}
		buf.append("}");
		return buf.toString();
	}

	public DistSwitch (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
			basev = Double.parseDouble (soln.get("?basev").toString());
			rated = OptionalDouble (soln, "?rated", 0.0);
			breaking = OptionalDouble (soln, "?breaking", 0.0);
			bus1 = SafeName (soln.get("?bus1").toString()); 
			bus2 = SafeName (soln.get("?bus2").toString()); 
      t1id = soln.get("?t1id").toString();
      t2id = soln.get("?t2id").toString();
			phases = OptionalString (soln, "?phases", "ABC");
      phases = phases.replace ('\n', ':');
			open = Boolean.parseBoolean (soln.get("?open").toString());
			StringBuilder glm_phs = new StringBuilder ();
			if (phases.contains("A")) glm_phs.append("A");
			if (phases.contains("B")) glm_phs.append("B");
			if (phases.contains("C")) glm_phs.append("C");
			if (phases.contains("s")) glm_phs.append("S");
			if (glm_phs.length() < 1) glm_phs.append("ABC");
			if (glm_phs.toString().equals("AB") && basev <= 208.1) { // TODO - artifact of non-triplex secondaries in CIM and OpenDSS
				glm_phases = "S"; // need to figure out AS, BS, or CS from connected triplex
			} else {
				glm_phases = glm_phs.toString();
			}
		}		
	}
	
	public DistSwitch (String name, boolean open) {
		this.name = SafeName (name);
		this.open = open;
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name + " from " + bus1 + " to " + bus2 + " basev=" + df2.format(basev) + " rated=" + df1.format(rated) +
								" breaking=" + df1.format(breaking) +	" phases=" + glm_phases + " open=" + Boolean.toString (open));
		return buf.toString();
	}

	public String GetGLM () {
		StringBuilder buf = new StringBuilder ("object switch { // CIM " + CIMClass() + "\n");

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

	public String GetKey() {
		return name;
	}

	public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
		DistCoordinates pt1 = map.get(CIMClass() + ":" + name + ":1");
		DistCoordinates pt2 = map.get(CIMClass() + ":" + name + ":2");

		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name + "\"");
		buf.append (",\"from\":\"" + bus1 + "\"");
		buf.append (",\"to\":\"" + bus2 + "\"");
		buf.append (",\"phases\":\"" + glm_phases +"\"");
		buf.append (",\"open\":\"" + Boolean.toString(open) +"\"");
		buf.append (",\"x1\":" + Double.toString(pt1.x));
		buf.append (",\"y1\":" + Double.toString(pt1.y));
		buf.append (",\"x2\":" + Double.toString(pt2.x));
		buf.append (",\"y2\":" + Double.toString(pt2.y));
		buf.append ("}");
		return buf.toString();
	}

	public String GetDSS () {
		StringBuilder buf = new StringBuilder ("new Line." + name);

		buf.append (" phases=" + Integer.toString(DSSPhaseCount(phases, false)) + 
								" bus1=" + DSSBusPhases(bus1, phases) + " bus2=" + DSSBusPhases (bus2, phases) + 
								" switch=y r1=1e-4 r0=1e-4 x1=0 x0=0 c1=0 c0=0 // CIM " + CIMClass() + "\n");
		AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);
		if (open) {
			buf.append ("  open Line." + name + " 1\n");
		} else {
			buf.append ("  close Line." + name + " 1\n");
		}

		return buf.toString();
	}

  public static String szCSVHeader = "Name,Bus1,Phases,Bus2,Phases,Type,Status";

  public String GetOpenClosedStatus() {
    if (open) return "Open";
    return "Closed";
  }

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + bus1 + "," + CSVPhaseString(phases) + "," + bus2 + "," +
                                           CSVPhaseString(phases) + "," + CIMClass() + "," + GetOpenClosedStatus() + "\n");
    return buf.toString();
  }
}

