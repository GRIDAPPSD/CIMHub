package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistPowerXfmrWinding extends DistComponent {
	public String name;
	public String id;
	public String vgrp;
	public String[] ename;
	public String[] eid;
	public String[] bus;
	public String[] conn;
	public double[] basev;
	public double[] ratedU;
	public double[] ratedS;
	public double[] r;
	public int[] wdg;
	public int[] ang;
	public boolean[] grounded;
	public double[] rg;
	public double[] xg;
	public int size;

	public double normalCurrentLimit = 0.0;
	public double emergencyCurrentLimit = 0.0;

	public boolean glmUsed;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append (",\"mRID\":\"" + id +"\"");
		buf.append ("}");
		return buf.toString();
	}

	private void SetSize (int val) {
		size = val;
		bus = new String[size];
		conn = new String[size];
		ename = new String[size];
		eid = new String[size];
		basev = new double[size];
		ratedU = new double[size];
		ratedS = new double[size];
		r = new double[size];
		wdg = new int[size];
		ang = new int[size];
		grounded = new boolean[size];
		rg = new double[size];
		xg = new double[size];
	}

	public DistPowerXfmrWinding (ResultSet results, HashMap<String,Integer> map) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			String pname = soln.get("?pname").toString();
			name = SafeName (pname);
			id = soln.get("?id").toString();
			vgrp = soln.get("?vgrp").toString();
			SetSize (map.get(pname));
			glmUsed = true;
			for (int i = 0; i < size; i++) {
				eid[i] = soln.get("?eid").toString();
				ename[i] = SafeName (soln.get("?ename").toString());
				bus[i] = SafeName (soln.get("?bus").toString());
				basev[i] = Double.parseDouble (soln.get("?basev").toString());
				conn[i] = soln.get("?conn").toString();
				ratedU[i] = Double.parseDouble (soln.get("?ratedU").toString());
				ratedS[i] = Double.parseDouble (soln.get("?ratedS").toString());
				r[i] = Double.parseDouble (soln.get("?r").toString());
				wdg[i] = Integer.parseInt (soln.get("?enum").toString());
				ang[i] = Integer.parseInt (soln.get("?ang").toString());
				grounded[i] = Boolean.parseBoolean (soln.get("?grounded").toString());
				rg[i] = OptionalDouble (soln, "?rground", 0.0);
				xg[i] = OptionalDouble (soln, "?xground", 0.0);
				if ((i + 1) < size) {
					soln = results.next();
				}
			}
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name + " " + vgrp);
		for (int i = 0; i < size; i++) {
			buf.append("\n  bus=" + bus[i] + " basev=" + df4.format(basev[i]) + " conn=" + conn[i] + " ang=" + Integer.toString(ang[i]));
			buf.append (" U=" + df4.format(ratedU[i]) + " S=" + df4.format(ratedS[i]) + " r=" + df4.format(r[i]));
			buf.append (" grounded=" + Boolean.toString(grounded[i]) + " rg=" + df4.format(rg[i]) + " xg=" + df4.format(xg[i]));
		}
		return buf.toString();
	}

	public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
		DistCoordinates pt1 = map.get("PowerTransformer:" + name + ":1");
		DistCoordinates pt2 = map.get("PowerTransformer:" + name + ":2");
		String bus1 = bus[0];
		String bus2 = bus[1];

		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name + "\"");
		buf.append (",\"from\":\"" + bus1 + "\"");
		buf.append (",\"to\":\"" + bus2 + "\"");
		buf.append (",\"phases\":\"ABC\"");
		buf.append (",\"configuration\":\"" + vgrp + "\"");
		buf.append (",\"x1\":" + Double.toString(pt1.x));
		buf.append (",\"y1\":" + Double.toString(pt1.y));
		buf.append (",\"x2\":" + Double.toString(pt2.x));
		buf.append (",\"y2\":" + Double.toString(pt2.y));
		buf.append ("}");
		return buf.toString();
	}

	public String GetGLM (DistPowerXfmrMesh mesh, DistPowerXfmrCore core) {
		StringBuilder buf = new StringBuilder ("object transformer_configuration {\n"); 
		buf.append ("  name \"xcon_" + name + "\";\n");
		String sConnect = GetGldTransformerConnection (conn, size);
		if (sConnect.equals ("Y_D")) {
			buf.append ("  connect_type WYE_WYE; // should be Y_D\n");
		} else {
			buf.append ("  connect_type " + sConnect + ";\n");
		}
		buf.append ("  primary_voltage " + df3.format (ratedU[0]) + ";\n");
		buf.append ("  secondary_voltage " + df3.format (ratedU[1]) + ";\n");
		buf.append ("  power_rating " + df3.format (ratedS[0] * 0.001) + ";\n");
		int idx;
		double Zbase;
		double rpu = 0.0, xpu = 0.0;
		for (int i = 0; i < mesh.size; i++) {
			if ((mesh.fwdg[i] == 1) && (mesh.twdg[i] == 2)) {
				Zbase = ratedU[0] * ratedU[0] / ratedS[0];
				rpu = mesh.r[i] / Zbase;
				xpu = mesh.x[i] / Zbase;
				break;
			}
			if ((mesh.fwdg[i] == 2) && (mesh.twdg[i] == 1)) {
				Zbase = ratedU[1] * ratedU[1] / ratedS[1];
				rpu = mesh.r[i] / Zbase;
				xpu = mesh.x[i] / Zbase;
				break;
			}
		}
		if (rpu <= 0.000001) {
			rpu = 0.000001; // GridLAB-D doesn't like zero
		}
		buf.append ("  resistance " + df6.format (rpu) + ";\n");
		buf.append ("  reactance " + df6.format (xpu) + ";\n");
		idx = core.wdg - 1;
		Zbase = ratedU[idx] * ratedU[idx] / ratedS[idx];
		if (core.b > 0.0) {
			buf.append ("  shunt_reactance " + df6.format (1.0 / Zbase / core.b) + ";\n");
		}
		if (core.g > 0.0) {
			buf.append ("  shunt_resistance " + df6.format (1.0 / Zbase / core.g) + ";\n");
		}
		buf.append ("}\n");

		buf.append ("object transformer {\n");
		buf.append ("  name \"xf_" + name + "\";\n");
		buf.append ("  from \"" + bus[0] + "\";\n");
		buf.append ("  to \"" + bus[1] + "\";\n");
		buf.append ("  phases ABC;\n");
		buf.append ("  configuration \"xcon_" + name + "\";\n");
		AppendGLMRatings (buf, "ABC", normalCurrentLimit, emergencyCurrentLimit);
		buf.append ("  // vector group " + vgrp + ";\n");
		buf.append("}\n");

		return buf.toString();
	}

	/*

		double rpu = 0.0;
		double zpu = 0.0;
		double zbase1 = ratedU[0] * ratedU[0] / ratedS[0];
		double zbase2 = ratedU[1] * ratedU[1] / ratedS[1];
		if (sct.ll[0] > 0.0) {
			rpu = sct.ll[0] / ratedS[0];
		} else {
			rpu = (r[0] / zbase1) + (r[1] / zbase2);
		}
		if (sct.fwdg[0] == 1) {
			zpu = sct.z[0] / zbase1;
		} else if (sct.fwdg[0] == 2) {
			zpu = sct.z[0] / zbase2;
		}
		double xpu = zpu;
		if (zpu >= rpu) {
//			xpu = Math.sqrt (zpu * zpu - rpu * rpu);  // TODO: this adjustment is correct, but was not done in RC1
		}

*/

	public String GetDSS(DistPowerXfmrMesh mesh, DistPowerXfmrCore core) {
		boolean bDelta;
		int i, fwdg, twdg;
		double zbase, xpct;

		StringBuilder buf = new StringBuilder ("new Transformer." + name + " phases=3 windings=" + Integer.toString(size));

		// mesh impedance - valid only up to 3 windings, and use winding instead of mesh resistances
		for (i = 0; i < mesh.size; i++) {
			fwdg = mesh.fwdg[i];
			twdg = mesh.twdg[i];
			zbase = ratedU[fwdg-1] * ratedU[fwdg-1] / ratedS[fwdg-1];
			xpct = 100.0 * mesh.x[i] / zbase;
			if ((fwdg == 1 && twdg == 2) || (fwdg == 2 && twdg == 1)) {
				buf.append(" xhl=" + df6.format(xpct));
			} else if ((fwdg == 1 && twdg == 3) || (fwdg == 3 && twdg == 1)) {
				buf.append(" xht=" + df6.format(xpct));
			} else if ((fwdg == 2 && twdg == 3) || (fwdg == 3 && twdg == 2)) {
				buf.append(" xlt=" + df6.format(xpct));
			}
		}

		// core admittance
		i = core.wdg - 1;
		zbase = ratedU[i] * ratedU[i] / ratedS[i];
		buf.append(" %imag=" + df3.format(core.b * zbase * 100.0) + " %noloadloss=" + df3.format(core.g * zbase * 100.0) + "\n");

		// winding ratings
		AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);
		for (i = 0; i < size; i++) {
			if (conn[i].contains("D")) {
				bDelta = true;
			} else {
				bDelta = false;
			}
			zbase = ratedU[i] * ratedU[i] / ratedS[i];
			buf.append("~ wdg=" + Integer.toString(i + 1) + " bus=" + bus[i] + " conn=" + DSSConn(bDelta) +
								 " kv=" + df3.format(0.001 * ratedU[i]) + " kva=" + df1.format(0.001 * ratedS[i]) +
								 " %r=" + df6.format(100.0 * r[i] / zbase) + "\n");
		}
		return buf.toString();
	}

  public static String szCSVHeader = "Name,NumPhases,NumWindings,Bus1,kV1,Conn1,kVA1,Bus2,kV2,Conn2,kVA2,Bus3,kV3,Conn3,kVA3,%x12,%x13,%x23,%loadloss,%imag,%noloadloss";

  public String GetCSV (DistPowerXfmrMesh mesh, DistPowerXfmrCore core) {
    boolean bDelta;
    int i, fwdg, twdg;
    double zbase, xpct;
    double x12 = 0.0, x13 = 0.0, x23 = 0.0, loadloss = 0.0;

    StringBuilder buf = new StringBuilder (name + ",3," + Integer.toString(size));

    // mesh impedance - valid only up to 3 windings, and use winding instead of mesh resistances
    for (i = 0; i < mesh.size; i++) {
      fwdg = mesh.fwdg[i];
      twdg = mesh.twdg[i];
      zbase = ratedU[fwdg-1] * ratedU[fwdg-1] / ratedS[fwdg-1];
      xpct = 100.0 * mesh.x[i] / zbase;
      if ((fwdg == 1 && twdg == 2) || (fwdg == 2 && twdg == 1)) {
        x12 = xpct;
      } else if ((fwdg == 1 && twdg == 3) || (fwdg == 3 && twdg == 1)) {
        x13 = xpct;
      } else if ((fwdg == 2 && twdg == 3) || (fwdg == 3 && twdg == 2)) {
        x23 = xpct;
      }
    }

    // winding connections and ratings
    for (i = 0; i < size; i++) {
      if (conn[i].contains("D")) {
        bDelta = true;
      } else {
        bDelta = false;
      }
      zbase = ratedU[i] * ratedU[i] / ratedS[i];
      loadloss += 100.0 * r[i] / zbase;
      buf.append("," + bus[i] + "," + df3.format(0.001 * ratedU[i]) + "," + DSSConn(bDelta)  + "," + df1.format(0.001 * ratedS[i]));
    }
    if (i < 3) buf.append (",,,,");
    buf.append ("," + df4.format (x12) +"," + df4.format (x13) +"," + df4.format (x23));
    // load loss and core admittance
    i = core.wdg;
    zbase = ratedU[i] * ratedU[i] / ratedS[i];
    buf.append("," + df3.format(loadloss) + "," + df3.format(core.b * zbase * 100.0) + "," + df3.format(core.b * zbase * 100.0) + "\n");

    return buf.toString();
  }

	public String GetKey() {
		return name;
	}
}

