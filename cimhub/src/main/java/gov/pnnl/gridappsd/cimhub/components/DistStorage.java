package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2018-2022, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Connection;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Used;

public class DistStorage extends DistComponent {
	public String id;
	public String name;
	public String bus;
  public String t1id;
	public String phases;
	public String state;
  public String pecid;
	public double p;
	public double q;
	public double ratedU;
	public double ratedS;
  public double ratedP; // TODO: OpenDSS allowed a different kvaRated from kwRated, but CIM does not
  public double maxP;
  public double minP;
	public double ratedE;
	public double storedE;
	public double maxIFault;
	public boolean bDelta;
  public ConverterControlMode mode;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append (",\"mRID\":\"" + id +"\"");
		buf.append (",\"CN1\":\"" + bus + "\"");
		buf.append (",\"phases\":\"" + phases + "\"");
		buf.append (",\"ratedS\":" + df1.format(ratedS));
		buf.append (",\"ratedU\":" + df1.format(ratedU));
		buf.append (",\"p\":" + df1.format(p));
		buf.append (",\"q\":" + df1.format(q));
		buf.append (",\"ratedE\":" + df1.format(ratedE));
		buf.append (",\"storedE\":" + df1.format(storedE));
		buf.append (",\"batteryState\":\"" + state + "\"");
		buf.append (",\"maxIFault\":" + df3.format(maxIFault));
		buf.append ("}");
		return buf.toString();
	}

	private String DSSBatteryState (String s) {
		if (s.equals("Charging")) return "charging";
		if (s.equals("Discharging")) return "discharging";
		if (s.equals("Waiting")) return "idling";
		if (s.equals("Full")) return "idling";
		if (s.equals("Empty")) return "idling";
		return "idling";
	}

	public DistStorage (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
      pecid = soln.get("?pecid").toString();
			bus = SafeName (soln.get("?bus").toString());
      t1id = soln.get("?t1id").toString();
			phases = OptionalString (soln, "?phases", "ABC");
			phases = phases.replace ('\n', ':');
			p = Double.parseDouble (soln.get("?p").toString());
			q = Double.parseDouble (soln.get("?q").toString());
      mode = ParseControlMode (soln.get("?controlMode").toString());
			ratedU = Double.parseDouble (soln.get("?ratedU").toString());
			ratedS = Double.parseDouble (soln.get("?ratedS").toString());
      maxP = Double.parseDouble (soln.get("?maxP").toString());
      minP = Double.parseDouble (soln.get("?minP").toString());
      ratedP = Math.max(maxP, Math.abs(minP));
			maxIFault = Double.parseDouble (soln.get("?ipu").toString());
			bDelta = false;
			ratedE = Double.parseDouble (soln.get("?ratedE").toString());
			storedE = Double.parseDouble (soln.get("?storedE").toString());
			state = soln.get("?state").toString();
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name + " @ " + bus + " phases=" + phases);
		buf.append (" vnom=" + df4.format(ratedU) + " vanom=" + df4.format(ratedS));
		buf.append (" kw=" + df4.format(0.001 * p) + " kvar=" + df4.format(0.001 * q));
		buf.append (" capacity=" + df4.format(0.001 * ratedE) + " stored=" + df4.format(0.001 * storedE));
		buf.append (" " + DSSBatteryState (state) + " ilimit=" + df4.format(maxIFault) + " id=" + id + " pecid=" + pecid);
		return buf.toString();
	}

	public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
		DistCoordinates pt = map.get("BatteryUnit:" + name + ":1");

		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append (",\"parent\":\"" + bus +"\"");
		buf.append (",\"phases\":\"" + phases +"\"");
		buf.append (",\"kva\":" + df1.format(0.001 * ratedS));
		buf.append (",\"x1\":" + Double.toString(pt.x));
		buf.append (",\"y1\":" + Double.toString(pt.y));
		buf.append ("}");
		return buf.toString();
	}

	public String GetGLM(HashMap<String,DistIEEE1547Connection> mapConnections, HashMap<String,DistIEEE1547Used> mapUsed) {
		StringBuilder buf = new StringBuilder ("object inverter {\n");

		buf.append ("  name \"inv_bat_" + name + "\";\n");
		buf.append ("  parent \"" + bus + "_stmtr\";\n");
		if (bDelta && !phases.contains("D")) {
			buf.append ("  phases " + phases.replace (":", "") + "D;\n");
		} else if (!phases.contains("S") && !phases.contains("N")) {
			buf.append ("  phases " + phases.replace (":", "") + "N;\n");
		} else {
			buf.append ("  phases " + phases.replace (":", "") + ";\n");
		}
		buf.append ("  generator_status ONLINE;\n");
		buf.append ("  generator_mode CONSTANT_PQ;\n");
		buf.append ("  inverter_type FOUR_QUADRANT;\n");
		buf.append ("  charge_lockout_time 1;\n");
		buf.append ("  discharge_lockout_time 1;\n");
		buf.append ("  sense_object \"" + bus + "_stmtr\";\n");
		buf.append ("  charge_on_threshold " + df3.format (-0.02 * ratedS) + ";\n");
		buf.append ("  charge_off_threshold " + df3.format (0.0 * ratedS) + ";\n");
		buf.append ("  discharge_off_threshold " + df3.format (0.4 * ratedS) + ";\n");
		buf.append ("  discharge_on_threshold " + df3.format (0.6 * ratedS) + ";\n");
		buf.append ("  inverter_efficiency 0.975;\n");
		buf.append ("  V_base " + df3.format (ratedU) + ";\n");
		buf.append ("  rated_power " + df3.format (ratedS) + ";\n");
		buf.append ("  max_charge_rate " + df3.format (-minP) + ";\n");
		buf.append ("  max_discharge_rate " + df3.format (maxP) + ";\n");
		buf.append ("  P_Out " + df3.format (p) + ";\n");
    if (mode == ConverterControlMode.CONSTANT_PF) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PF;\n");
      double pf = 1.0;
      double s = Math.sqrt(p * p + q * q);
      if (s > 0.0) {
        pf = p / s;
      }
      if (q < 0.0) {
        pf *= -1.0;
      }
      buf.append ("  power_factor " + df4.format (pf) + ";\n");
    } else if (mode == ConverterControlMode.CONSTANT_Q) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PQ; // LOAD_FOLLOWING? \n");
      buf.append ("  Q_Out " + df3.format (q) + ";\n");
    } else if (mode == ConverterControlMode.DYNAMIC) {
      buf.append ("  four_quadrant_control_mode VOLT_VAR;\n");  // TODO - parse the IEEE1547 controller
    }
		buf.append ("  object battery {\n");
		buf.append ("    name \"bat_" + name + "\";\n");
		buf.append ("    nominal_voltage 48;\n");
		buf.append ("    battery_capacity " + df1.format (ratedE) + ";\n");
		buf.append ("    state_of_charge " + df4.format (storedE / ratedE) + ";\n");
		buf.append ("    use_internal_battery_model true;\n");
		buf.append ("    battery_type LI_ION;\n");
		buf.append ("    round_trip_efficiency 0.86;\n");
		buf.append ("    rated_power " + df3.format (ratedP) + ";\n");
		buf.append ("  };\n");
		buf.append ("}\n");

		return buf.toString();
	}

	public String GetDSS() {
		StringBuilder buf = new StringBuilder ("new Storage." + name);

		int nphases = DSSPhaseCount(phases, bDelta);
		double kv = 0.001 * ratedU;
		double kva = 0.001 * ratedS;
		if (nphases < 2) { // 2-phase wye load should be line-line for secondary?
			kv /= Math.sqrt(3.0);
		}
    double pf = 1.0;
    double kvar = 0.001 * q;
		buf.append (" phases=" + Integer.toString(nphases) + " bus1=" + DSSShuntPhases (bus, phases, bDelta) + 
								" conn=" + DSSConn(bDelta) + " kva=" + df3.format(kva) + 
                " kwrated=" + df3.format(0.001 * ratedP) + 
                " kv=" + df3.format(kv) + " kwhrated=" + df3.format(0.001 * ratedE) + 
								" kwhstored=" + df3.format(0.001 * storedE) + " state=" + DSSBatteryState(state) +
								" vminpu=" + df4.format(1/maxIFault) + " LimitCurrent=yes kw=" + df2.format(p/1000.0) +
                " %charge=" + df2.format(-100.0 * minP / ratedP) + " %discharge=" + df2.format(100.0 * maxP / ratedP));
    if (mode == ConverterControlMode.CONSTANT_PF) {
      double s = Math.sqrt(p * p + q * q);
      if (s > 0.0) {
        pf = p / s;
      }
      if (q < 0.0) {
        pf *= -1.0;
      }
      buf.append (" pf=" + df4.format(pf));
    } else {
      buf.append (" kvar=" + df2.format(kvar));
    }
    buf.append("\n");

		return buf.toString();
	}

  public static String szCSVHeader = "Name,NumPhases,Bus,Phases,kV,kVA,Capacity,Connection,kW,kVAR,pf,ctrlMode,kWh,State";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + ",");

    int nphases = DSSPhaseCount(phases, bDelta);
    double kv = 0.001 * ratedU;
    double kva = 0.001 * ratedS;
    if (nphases < 2) { // 2-phase wye load should be line-line for secondary?
      kv /= Math.sqrt(3.0);
    }
    double s = Math.sqrt(p*p + q*q);
    double pf = 1.0;
    if (s > 0.0) {
      pf = p / s;
    }
    if (q < 0.0) {
      pf *= -1.0;
    }

    buf.append (Integer.toString(nphases) + "," + bus + "," + CSVPhaseString (phases) + "," + df3.format(kv) + "," + 
                df3.format(kva) + "," + df3.format(0.001 * ratedE) + "," + DSSConn(bDelta) + "," + df3.format(0.001 + p) + "," + 
                df3.format(0.001 + q) + "," + df4.format(pf) + "," + mode.toString() + "," + df3.format(0.001 * storedE) + "," + DSSBatteryState(state) + "\n");

    return buf.toString();
  }

	public String GetKey() {
		return name;
	}
}

