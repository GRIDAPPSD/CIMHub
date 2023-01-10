package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Connection;
import gov.pnnl.gridappsd.cimhub.components.DistIEEE1547Used;

public class DistStorage extends DistComponent {
  public static final String szCIMClass = "BatteryUnit";

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
  public double maxQ;
  public double minQ;
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
    if (s.equals("charging")) return "charging";
    if (s.equals("discharging")) return "discharging";
    if (s.equals("waiting")) return "idling";
    if (s.equals("full")) return "idling";
    if (s.equals("empty")) return "idling";
    return "idling";
  }

  public DistStorage (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      pecid = soln.get("?pecid").toString();
      String qname = soln.get("?name").toString();
      name = PushExportName (qname, id, szCIMClass);
      PushExportName (qname, pecid, "PowerElectronicsConnection");
      bus = GetBusExportName (soln.get("?bus").toString());
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
      maxQ = Double.parseDouble (soln.get("?maxQ").toString());
      minQ = Double.parseDouble (soln.get("?minQ").toString());
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
    DistCoordinates pt = map.get("BatteryUnit:" + id + ":1");

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

  public String GetGLM(HashMap<String,DistIEEE1547Connection> mapConnections, HashMap<String,DistIEEE1547Used> mapUsed,
                       DistEnergyConnectionProfile prf) {
    StringBuilder buf = new StringBuilder ("object inverter {\n");

    double pf = 1.0;
    double s = Math.sqrt(p * p + q * q);
    if (s > 0.0) {
      pf = p / s;
    }
    if (q < 0.0) {
      pf *= -1.0;
    }

    buf.append ("  name \"" + GLMObjectPrefix ("inv_bat_") + name + "\";\n");
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
    buf.append ("  use_multipoint_efficiency FALSE;\n");
    buf.append ("  V_base " + df3.format (ratedU) + ";\n");
    buf.append ("  rated_power " + df3.format (ratedS/GLMPhaseCount(phases)) + "; // per phase!\n");
    buf.append ("  max_charge_rate " + df3.format (-minP) + ";\n");
    buf.append ("  max_discharge_rate " + df3.format (maxP) + ";\n");
    String Pout = df3.format (p);
    boolean bDispatchCurve = false;
    if (prf != null) {
      if (prf.gldPlayer.length() > 0) {
        Pout = prf.gldPlayer + ".value*" + df3.format(ratedP);
        bDispatchCurve = true;
      } else if (prf.gldSchedule.length() > 0) {
        Pout = prf.gldSchedule + "*" + df3.format(ratedP);
        bDispatchCurve = true;
      }
    }
    buf.append ("  P_Out " + Pout + ";\n");
    if (bDispatchCurve) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PQ; // required for player or schedule control \n");
      buf.append ("  Q_Out " + df3.format (q) + ";\n");
    } else if (mode == ConverterControlMode.CONSTANT_PF) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PF;\n");
      buf.append ("  power_factor " + df4.format (pf) + ";\n");
    } else if (mode == ConverterControlMode.CONSTANT_Q) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PQ; // LOAD_FOLLOWING not supported in CIM \n");
      buf.append ("  Q_Out " + df3.format (q) + ";\n");
    } else if (mode == ConverterControlMode.DYNAMIC) {
      boolean bSet = false;
      for (HashMap.Entry<String,DistIEEE1547Connection> pair1 : mapConnections.entrySet()) {
        DistIEEE1547Connection dconn = pair1.getValue();
        if (dconn.pids.contains(pecid)) { // this is my connection to IEEE1547 dynamics
          for (HashMap.Entry<String,DistIEEE1547Used> pair2 : mapUsed.entrySet()) {
            DistIEEE1547Used dset = pair2.getValue();
            if (dconn.pids.contains(dset.pecid)) {  // these are my connection settings
              buf.append (dset.GetGLM (q, pf));
              bSet = true;
              break;
            }
          }
        }
        if (bSet) break;
      }
      if (!bSet) {
        buf.append ("  four_quadrant_control_mode NOT_FOUND; // TODO - an IEEE1547 controller should be associated in the CIM XML \n");
      }
    }
    buf.append ("  object battery {\n");
    buf.append ("    name \"" + GLMObjectPrefix ("bat_", true) + name + "\";\n");
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

  public String GetDSS(DistEnergyConnectionProfile prf) {
    StringBuilder buf = new StringBuilder ("new Storage." + name);

    int nphases = DSSPhaseCount(phases, bDelta);
    double kv = 0.001 * ratedU;
    double kva = 0.001 * ratedS;
    if (nphases < 2) { // 2-phase wye load should be line-line for secondary?
      kv /= Math.sqrt(3.0);
    }
    double pf = 1.0;
    double kvar = 0.001 * q;
    double kvarMax = 0.001 * maxQ;
    double kvarMaxAbs = kvarMax;
    if (minQ < 0.0) {
      kvarMaxAbs = Math.abs(0.001 * minQ);
    }
    // in default dispatch mode, the battery determines P from its idling, discharging, or charging state
    // P cannot be set directly, so we mimic that by setting %charge or %discharge to get the desired P
    String dssState = DSSBatteryState(state);
    double pctCharge = -100.0 * minP / ratedP;
    double pctDischarge = 100.0 * maxP / ratedP;
    if (dssState.contains("charging")) {
      pctCharge = 100.0 * Math.abs (p/ratedP);
      pctDischarge = pctCharge;
    }
    if (pctCharge < 0.0) pctCharge = 0.0;
    if (pctDischarge < 0.0) pctDischarge = 0.0;
    if (pctCharge > 100.0) pctCharge = 100.0;
    if (pctDischarge > 100.0) pctDischarge = 100.0;
      buf.append (" phases=" + Integer.toString(nphases) + " bus1=" + DSSShuntPhases (bus, phases, bDelta) + 
                  " conn=" + DSSConn(bDelta) + " kva=" + df3.format(kva) + 
          " kwrated=" + df3.format(0.001 * ratedP) + 
          " kv=" + df3.format(kv) + " kwhrated=" + df3.format(0.001 * ratedE) + 
                  " kwhstored=" + df3.format(0.001 * storedE) + " state=" + dssState +
                  " vminpu=" + df4.format(1/maxIFault) + " LimitCurrent=yes" + // "kw=" + df2.format(p/1000.0) +
          " %charge=" + df2.format(pctCharge) + " %discharge=" + df2.format(pctDischarge) + 
          " kvarMax=" + df3.format(kvarMax) + " kvarMaxAbs=" + df3.format(kvarMaxAbs));
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
    if (prf != null) {
      if (prf.dssDaily.length() > 0) {
        buf.append (" daily=" + prf.dssDaily);
        buf.append (" dispmode=follow");
      }
      if (prf.dssDuty.length() > 0) {
        buf.append (" duty=" + prf.dssDuty);
        buf.append (" dispmode=follow");
      }
      if (prf.dssYearly.length() > 0) {
        buf.append (" yearly=" + prf.dssYearly);
        buf.append (" dispmode=follow");
      }
      if (prf.dssSpectrum.length() > 0) {
        buf.append (" spectrum=" + prf.dssSpectrum);
      }
    }
    buf.append("\n");

    return buf.toString();
  }

  public static String szCSVHeader = "Name,NumPhases,Bus,Phases,kV,kVArated,kWrated,kWhCapacity,Connection,kW,kVAR,pf,ctrlMode,kWhStored,State,kWmax,kWmin,kVARmax,kVARmin,IfaultPU";

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
          df3.format(kva) + "," + df3.format(0.001 * ratedP) + "," + df3.format(0.001 * ratedE) + "," + DSSConn(bDelta) + "," + df3.format(0.001 + p) + "," + 
          df3.format(0.001 + q) + "," + df4.format(pf) + "," + mode.toString() + "," + df3.format(0.001 * storedE) + "," + DSSBatteryState(state) + "," +
          df3.format(0.001 * maxP) + "," + df3.format(0.001 * minP) + "," +
          df3.format(0.001 * maxQ) + "," + df3.format(0.001 * minQ) + "," + df3.format(maxIFault) + "\n");

    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

