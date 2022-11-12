package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistEnergyConnectionProfile extends DistComponent {
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
  public String gldWeather;

  public DistEnergyConnectionProfile (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      name = SafeName (soln.get("?name").toString());
      id = soln.get("?id").toString();
      load_name = SafeName (soln.get("?ldname").toString());
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
      gldWeather = OptionalString (soln, "?gldWeather", "");
    }
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + ":" + id + ":" + dssDaily + ":" + dssDuty + ":" + dssLoadCvrCurve + ":" + dssLoadGrowth
                + ":" + dssPVTDaily + ":" + dssPVTDuty + ":" + dssPVTYearly + ":" + dssSpectrum + ":" + dssYearly
                + ":" + gldPlayer + ":" + gldSchedule + ":" + gldWeather + ":" + load_name + ":" + load_id);
    return buf.toString();
  }

  public String GetKey() {
    return load_id;
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

