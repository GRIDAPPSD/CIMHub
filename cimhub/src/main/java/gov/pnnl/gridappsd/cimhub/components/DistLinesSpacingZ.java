package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017-2022, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistLinesSpacingZ extends DistLineSegment {
	public String spacing;
	public String spcid;
	public int nwires;
	public String[] wire_phases;
	public String[] wire_names;
	public String[] wire_classes;

	public String glm_config;

  private boolean bSpacingHasNeutral = false;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append (",\"mRID\":\"" + id +"\"");
		buf.append ("}");
		return buf.toString();
	}

	public DistLinesSpacingZ (ResultSet results, HashMap<String,Integer> map) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
			bus1 = SafeName (soln.get("?bus1").toString()); 
			bus2 = SafeName (soln.get("?bus2").toString()); 
			len = Double.parseDouble (soln.get("?len").toString());
      t1id = soln.get("?t1id").toString();
      t2id = soln.get("?t2id").toString();
			basev = Double.parseDouble (soln.get("?basev").toString());
			spacing = soln.get("?spacing").toString();
			spcid = soln.get("?spcid").toString();
			nwires = map.get (name);
			wire_phases = new String[nwires];
			wire_names = new String[nwires];
			wire_classes = new String[nwires];
			StringBuilder buf = new StringBuilder ("");
			for (int i = 0; i < nwires; i++) {
				wire_phases[i] = soln.get("?phs").toString();
				wire_classes[i] = soln.get("?phclass").toString();
				wire_names[i] = soln.get("?phname").toString();
				if (wire_phases[i].equals("N") == false) {
					buf.append (wire_phases[i]);
				} else {
          bSpacingHasNeutral = true;
        }
				if ((i + 1) < nwires) {
					soln = results.next();
				}
			}
			phases = buf.toString();
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name + " from " + bus1 + " to " + bus2 + 
								" basev=" + df4.format(basev) + " len=" + df4.format(len) + " spacing=" + spacing);
		for (int i = 0; i < nwires; i++) {
			buf.append ("\n  phs=" + wire_phases[i] + " wire=" + wire_names[i] + " class=" + wire_classes[i]);
		}
		return buf.toString();
	}

	public String GetGLM() {
    boolean bForceN = bSpacingHasNeutral;
		StringBuilder buf = new StringBuilder ();
		if (wire_classes[0].equals("OverheadWireInfo")) {
			bCable = false;
		} else {
			bCable = true;
      if (wire_classes[nwires-1].equals("OverheadWireInfo")) {
        bForceN = true;
      }
		}
		AppendSharedGLMAttributes(buf, glm_config, true, bForceN);
		return buf.toString();
	}

	public String GetKey() {
		return name;
	}

	public String LabelString() {
		return spacing + ":" + wire_names[0];
	}

	public String GetDSS() {
		StringBuilder buf = new StringBuilder ("new Line." + name);
		boolean bCable = false;

		buf.append (" phases=" + Integer.toString(DSSPhaseCount(phases, false)) + 
								" bus1=" + DSSBusPhases(bus1, phases) + " bus2=" + DSSBusPhases (bus2, phases) + 
								" length=" + df1.format(len * gFTperM) + " spacing=" + spacing + "_" + phases + " units=ft\n");
		AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);
		if (wire_classes[0].equals("OverheadWireInfo")) {
			buf.append ("~ wires=[");
		} else if (wire_classes[0].equals("ConcentricNeutralCableInfo")) {
			buf.append ("~ CNCables=[");
			bCable = true;
		} else if (wire_classes[0].equals("TapeShieldCableInfo")) {
			buf.append ("~ TSCables=[");
			bCable = true;
		}
		for (int i = 0; i < nwires; i++) {
			if (bCable == true && wire_classes[i].equals("OverheadWireInfo")) {
				buf.append ("] wires=[");
			} else if (i > 0) {
				buf.append (",");
			}
			buf.append(wire_names[i]);
		}
		buf.append("]\n");
		return buf.toString();
	}

  public static String szCSVHeader = "Name,Bus1,Phases,Bus2,Phases,Spacing,WireType,WireNames,Length,Units";

  public String GetCSV () {
    String WireType;
    if (wire_classes[0].equals("TapeShieldCableInfo")) {
      WireType = "TS";
    } else if (wire_classes[0].equals("ConcentricNeutralCableInfo")) {
      WireType = "CN";
    } else {
      WireType = "OHD";
    }
    StringBuilder WireNames = new StringBuilder ("\"" + wire_names[0]);
    for (int i = 1; i < nwires; i++) {
      WireNames.append ("," + wire_names[i]);
    }
    WireNames.append ("\"");
    StringBuilder buf = new StringBuilder (name + "," + bus1 + "," + CSVPhaseString(phases) + "," +
                                           bus2 + "," + CSVPhaseString(phases) + "," + spacing + "," +
                                           WireType + "," + WireNames.toString() + "," +
                                           df3.format(len * gFTperM) + ",ft\n");
    return buf.toString();
  }
}

