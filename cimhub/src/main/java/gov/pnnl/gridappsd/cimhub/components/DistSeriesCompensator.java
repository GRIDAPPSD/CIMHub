package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017-2022, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import org.apache.commons.math3.complex.Complex;
import java.util.HashMap;

public class DistSeriesCompensator extends DistComponent {
  public String id;
  public String name;
  public String bus1;
  public String bus2;
  public String phases;
  public String t1id;
  public String t2id;
  public double basev;
	public double r1; 
	public double x1; 
	public double r0; 
	public double x0; 

  public double normalCurrentLimit = 0.0;
  public double emergencyCurrentLimit = 0.0;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append (",\"mRID\":\"" + id +"\"");
		buf.append ("}");
		return buf.toString();
	}

	public DistSeriesCompensator (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
      t1id = soln.get("?t1id").toString();
      t2id = soln.get("?t2id").toString();
			bus1 = SafeName (soln.get("?bus1").toString()); 
			bus2 = SafeName (soln.get("?bus2").toString()); 
			phases = "ABC";
			basev = Double.parseDouble (soln.get("?basev").toString());
			r1 = Double.parseDouble (soln.get("?r").toString());
			x1 = Double.parseDouble (soln.get("?x").toString());
			r0 = OptionalDouble (soln, "?r0", 0.0);
			x0 = OptionalDouble (soln, "?x0", 0.0);
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name + " from " + bus1 + " to " + bus2 + " phases=" + phases + " basev=" + df4.format(basev));
		buf.append (" r1=" + df4.format(r1) + " x1=" + df4.format(x1));
		buf.append (" r0=" + df4.format(r0) + " x0=" + df4.format(x0));
		return buf.toString();
	}

	public String GetGLM() {
		StringBuilder buf = new StringBuilder ();

    buf.append ("object series_reactor {\n");
    buf.append ("  name \"reac_" + name + "\";\n");
    buf.append ("  from \"" + bus1 + "\";\n");
    buf.append ("  to \"" + bus2 + "\";\n");
    buf.append ("  phases ABC;\n");
    AppendGLMRatings (buf, "ABC", normalCurrentLimit, emergencyCurrentLimit);
    String sR = df4.format (r1);
    String sX = df4.format (x1);
    buf.append ("  phase_A_resistance " + sR + ";\n");
    buf.append ("  phase_B_resistance " + sR + ";\n");
    buf.append ("  phase_C_resistance " + sR + ";\n");
    buf.append ("  phase_A_reactance " + sX + ";\n");
    buf.append ("  phase_B_reactance " + sX + ";\n");
    buf.append ("  phase_C_reactance " + sX + ";\n");
		buf.append ("}\n");
		return buf.toString();
	}

	public String GetKey() {
		return name;
	}

	public String LabelString() {
		return "Reac";
	}

  public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
    DistCoordinates pt1 = map.get("SeriesCompensator:" + name + ":1");
    DistCoordinates pt2 = map.get("SeriesCompensator:" + name + ":2");

    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name + "\"");
    buf.append (",\"from\":\"" + bus1 + "\"");
    buf.append (",\"to\":\"" + bus2 + "\"");
    buf.append (",\"phases\":\"ABC\"");
    buf.append (",\"x1\":" + Double.toString(pt1.x));
    buf.append (",\"y1\":" + Double.toString(pt1.y));
    buf.append (",\"x2\":" + Double.toString(pt2.x));
    buf.append (",\"y2\":" + Double.toString(pt2.y));
    buf.append ("}");
    return buf.toString();
  }

  public String GetDSS() {
		StringBuilder buf = new StringBuilder ("new Reactor." + name);

		buf.append (" phases=" + Integer.toString(DSSPhaseCount(phases, false)) + 
								" bus1=" + DSSBusPhases(bus1, phases) + " bus2=" + DSSBusPhases (bus2, phases) + "\n");
		AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);
		buf.append ("~ r=" + df6.format(r1) + " x=" + df6.format(x1) + "\n");

		return buf.toString();
	}
  public static String szCSVHeader = "Name,Bus1,Phases,Bus2,Phases,R1,X1,R0,X0";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + bus1 + "," + CSVPhaseString(phases) + "," +
                                           bus2 + "," + CSVPhaseString(phases) + "," +
                                           df6.format(r1) + "," +
                                           df6.format(x1) + "," +
                                           df6.format(r0) + "," +
                                           df6.format(x0) + "\n");
    return buf.toString();
  }
}

