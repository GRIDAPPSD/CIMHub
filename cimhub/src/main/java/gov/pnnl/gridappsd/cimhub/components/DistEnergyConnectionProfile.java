package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistEnergyConnectionProfile extends DistComponent {
  public static final String szCIMClass = "EnergyConnectionProfile";

  public String id;
  public String name;
  public String load_id;
  public String load_name;
  public String dssDaily;
  public String dssDuty;
  public String dssLoadCvrCurve;
  public String dssLoadGrowth;
  public String dssPVTDaily;
  public String dssPVTDuty;
  public String dssPVTYearly;
  public String dssSpectrum;
  public String dssYearly;
  public String gldPlayer;
  public String gldSchedule;

  public DistEnergyConnectionProfile (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      load_id = soln.get("?ldid").toString();
      dssDaily = OptionalString (soln, "?dssDaily", "");
      dssDuty = OptionalString (soln, "?dssDuty", "");
      dssLoadCvrCurve = OptionalString (soln, "?dssLoadCvrCurve", "");
      dssLoadGrowth = OptionalString (soln, "?dssLoadGrowth", "");
      dssPVTDaily = OptionalString (soln, "?dssPVTDaily", "");
      dssPVTDuty = OptionalString (soln, "?dssPVTDuty", "");
      dssPVTYearly = OptionalString (soln, "?dssPVTYearly", "");
      dssSpectrum = OptionalString (soln, "?dssSpectrum", "");
      dssYearly = OptionalString (soln, "?dssYearly", "");
      gldPlayer = OptionalString (soln, "?gldPlayer", "");
      gldSchedule = OptionalString (soln, "?gldSchedule", "");
    }
  }

  public void PrepForExport() {
    load_name = GetEquipmentExportName (load_id);
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + ":" + id + ":" + dssDaily + ":" + dssDuty + ":" + dssLoadCvrCurve + ":" + dssLoadGrowth
                + ":" + dssPVTDaily + ":" + dssPVTDuty + ":" + dssPVTYearly + ":" + dssSpectrum + ":" + dssYearly
                + ":" + gldPlayer + ":" + gldSchedule + ":" + load_name + ":" + load_id);
    return buf.toString();
  }

  public String GetKey() {
    return load_id;  // TODO?
  }

  public boolean ForGLM() {
    if (!gldPlayer.isEmpty()) return true;
    if (!gldSchedule.isEmpty()) return true;
    return false;
  }

  public boolean ForDSS() {
    if (!dssDaily.isEmpty()) return true;
    if (!dssDuty.isEmpty()) return true;
    if (!dssYearly.isEmpty()) return true;
    if (!dssLoadGrowth.isEmpty()) return true;
    if (!dssLoadCvrCurve.isEmpty()) return true;
    if (!dssPVTDaily.isEmpty()) return true;
    if (!dssPVTDuty.isEmpty()) return true;
    if (!dssPVTYearly.isEmpty()) return true;
    if (!dssSpectrum.isEmpty()) return true;
    return false;
  }

  public String GetGLM() {
    StringBuilder buf = new StringBuilder ("// for:"+load_name);
    if (!gldPlayer.isEmpty()) buf.append (" player="+gldPlayer);
    if (!gldSchedule.isEmpty()) buf.append (" schedule="+gldSchedule);
    buf.append("\n");
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("// ");
    if (name.startsWith("Load:")) {
      buf.append ("for loads: ");
    } else if (name.startsWith("Gen:")) {
      buf.append ("for generators: ");
    } else if (name.startsWith("PV:")) {
      buf.append ("for PVsystems: ");
    } else if (name.startsWith("Bat:")) {
      buf.append ("for storages: ");
    } else {
      buf.append ("for:" + load_name);
    }
    if (!dssDaily.isEmpty()) buf.append (" daily="+dssDaily);
    if (!dssDuty.isEmpty()) buf.append (" duty="+dssDuty);
    if (!dssYearly.isEmpty()) buf.append (" yearly="+dssYearly);
    if (!dssLoadGrowth.isEmpty()) buf.append (" growth="+dssLoadGrowth);
    if (!dssLoadCvrCurve.isEmpty()) buf.append (" cvrcurve="+dssLoadCvrCurve);
    if (!dssPVTDaily.isEmpty()) buf.append (" Tdaily="+dssPVTDaily);
    if (!dssPVTDuty.isEmpty()) buf.append (" Tduty="+dssPVTDuty);
    if (!dssPVTYearly.isEmpty()) buf.append (" Tyearly="+dssPVTYearly);
    if (!dssSpectrum.isEmpty()) buf.append (" spectrum="+dssSpectrum);
    buf.append("\n");
    return buf.toString();
  }

  public static String szCSVHeader = "Profile,Class,Name,DssDaily,DssDuty,DssYearly,DssLoadCvr,DssLoadGrowth,DssPVTDaily,DssPVTDuty,DssPVTYearly,DssSpectrum,GldPlayer,GldSchedule";

  public String GetCSV () {
    DistEquipment eq = mapEquipmentNames.get(load_id);
    StringBuilder buf = new StringBuilder (name + "," + eq.eqClass + "," + eq.exportName + ",");
    buf.append (dssDaily + "," + dssDuty + "," + dssYearly + "," + dssLoadCvrCurve + "," + 
                dssLoadGrowth + "," + dssPVTDaily + "," + dssPVTDuty + "," + dssPVTYearly + "," + 
                dssSpectrum + "," + gldPlayer + "," + gldSchedule + "\n");
    return buf.toString();
  }

  @Override
  public String GetJSONEntry() {
    StringBuilder buf = new StringBuilder ();
    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("{\"load_name\":\"" + load_name +"\"");
    buf.append (",\"load_mRID\":\"" + load_id +"\"");
    buf.append ("}");
    return buf.toString();
  }	
}

