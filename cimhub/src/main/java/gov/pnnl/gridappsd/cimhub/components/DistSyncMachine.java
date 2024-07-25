package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistSyncMachine extends DistComponent {
  public static final String szCIMClass = "SynchronousMachine";

  public String id;
  public String name;
  public String bus;
  public String t1id;
  public String phases;
  public double ratedS;
  public double ratedU;
  public double p;
  public double q;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name + "\"");
    buf.append (",\"mRID\":\"" + id + "\"");
    buf.append (",\"CN1\":\"" + bus + "\"");
    buf.append (",\"phases\":\"" + phases + "\"");
    buf.append (",\"ratedS\":" + df1.format(ratedS));
    buf.append (",\"ratedU\":" + df1.format(ratedU));
    buf.append (",\"p\":" + df3.format(p));
    buf.append (",\"q\":" + df3.format(q));
    buf.append ("}");
    return buf.toString();
  }

  public DistSyncMachine (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      bus = GetBusExportName (soln.get("?bus").toString());
      t1id = soln.get("?t1id").toString();
      phases = OptionalString (soln, "?phases", "ABC");
      phases = phases.replace ('\n', ':');
      p = Double.parseDouble (soln.get("?p").toString());
      q = Double.parseDouble (soln.get("?q").toString());
      ratedU = Double.parseDouble (soln.get("?ratedU").toString());
      ratedS = Double.parseDouble (soln.get("?ratedS").toString());
    }
  }
  public DistSyncMachine (String name, Double p, Double q) {
    this.name = name;
    this.p = p;
    this.q = q;
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + " @ " + bus + " phases=" + phases);
    buf.append (" vnom=" + df4.format(ratedU) + " vanom=" + df4.format(ratedS));
    buf.append (" kw=" + df4.format(0.001 * p) + " kvar=" + df4.format(0.001 * q));
    return buf.toString();
  }

  public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
    DistCoordinates pt = map.get("SynchronousMachine:" + id + ":1");

    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"parent\":\"" + bus +"\"");
    buf.append (",\"phases\":\"" + phases +"\"");
    buf.append (",\"ratedS\":" + df1.format(ratedS));
    buf.append (",\"x1\":" + Double.toString(pt.x));
    buf.append (",\"y1\":" + Double.toString(pt.y));
    buf.append ("}");
    return buf.toString();
  }

  public String GetGLM(DistEnergyConnectionProfile prf) {
//  diesel_dg only ever supported ABC phasing, and in GLD v5 the phases property was removed
    StringBuilder buf = new StringBuilder ("object diesel_dg {\n");

    buf.append ("  name \"dg_" + name + "\";\n");
    buf.append ("  parent \"" + bus + "_dgmtr\";\n");
    String Sphase;
    if (phases.contains ("S")) {
      if (q < 0.0) {
        Sphase = df2.format(p) + "-" + df2.format(-q) + "j";
      } else {
        Sphase = df2.format(p) + "+" + df2.format(q) + "j";
      }
      if (phases.contains("A")) {
        buf.append ("  power_out_A " + Sphase + ";\n");
      } else if (phases.contains("B")) {
        buf.append ("  power_out_B " + Sphase + ";\n");
      } else {
        buf.append ("  power_out_C " + Sphase + ";\n");
      }
    } else {
      String Pphase = df2.format(p/3.0);
      String Qphase = df2.format(q/3.0);
      if (prf != null) {
        if (prf.gldPlayer.length() > 0) {
          Pphase = prf.gldPlayer + ".value*" + df2.format(p/3.0);
          Qphase = prf.gldPlayer + ".value*" + df2.format(q/3.0);
        } else if (prf.gldSchedule.length() > 0) {
          Pphase = prf.gldSchedule + "*" + df2.format(p/3.0);
          Qphase = prf.gldSchedule + "*" + df2.format(q/3.0);
        } else {
          Pphase = df2.format(p/3.0);
          Qphase = df2.format(q/3.0);
        }
        buf.append ("  real_power_out_A " + Pphase + ";\n");
        buf.append ("  real_power_out_B " + Pphase + ";\n");
        buf.append ("  real_power_out_C " + Pphase + ";\n");
        buf.append ("  reactive_power_out_A " + Qphase + ";\n");
        buf.append ("  reactive_power_out_B " + Qphase + ";\n");
        buf.append ("  reactive_power_out_C " + Qphase + ";\n");
      } else {
        if (q < 0.0) {
          Sphase = df2.format(p/3.0) + "-" + df2.format(-q/3.0) + "j";
        } else {
          Sphase = df2.format(p/3.0) + "+" + df2.format(q/3.0) + "j";
        }
        buf.append ("  power_out_A " + Sphase + ";\n");
        buf.append ("  power_out_B " + Sphase + ";\n");
        buf.append ("  power_out_C " + Sphase + ";\n");
      }
    }
    buf.append ("  Gen_type CONSTANT_PQ;\n");
    buf.append ("  Rated_V " + df2.format(ratedU) + ";\n");
    buf.append ("  Rated_VA " + df2.format(ratedS) + ";\n");
    buf.append ("}\n");

    return buf.toString();
  }

  public String GetDSS(DistEnergyConnectionProfile prf) {
    StringBuilder buf = new StringBuilder ("new Generator." + name);
    buf.append (" phases=" + Integer.toString(DSSPhaseCount(phases, false)) + " bus1=" + DSSShuntPhases (bus, phases, false) + 
                " model=1 kv=" + df2.format(0.001*ratedU) + " kva=" + df2.format(0.001*ratedS) + 
                " kw=" + df2.format(0.001*p) + " kvar=" + df2.format(0.001*q));
    if (prf != null) {
      if (prf.dssDaily.length() > 0) {
        buf.append (" daily=" + prf.dssDaily);
      }
      if (prf.dssDuty.length() > 0) {
        buf.append (" duty=" + prf.dssDuty);
      }
      if (prf.dssYearly.length() > 0) {
        buf.append (" yearly=" + prf.dssYearly);
      }
      if (prf.dssSpectrum.length() > 0) {
        buf.append (" spectrum=" + prf.dssSpectrum);
      }
    }
    buf.append("\n");
    return buf.toString();
  }

  public static String szCSVHeader = "Name,NumPhases,Bus,Phases,kV,kVA,kW,pf";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + ",");

    int nphases = DSSPhaseCount(phases, false);
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
          df3.format(kva) + "," + df3.format(0.001 * p) + "," + df4.format(pf) + "\n");

    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

