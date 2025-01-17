package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistSubstation extends DistComponent {
  public static final String szCIMClass = "EnergySource";

  public String id;
  public String name;
  public String fdrid;
  public String fdrname;
  public String bus;
  public String t1id;
  public double basev;
  public double nomv;
  public double vmag;
  public double vang;
  public double r1;
  public double x1;
  public double r0;
  public double x0;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistSubstation (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      bus = GetBusExportName (soln.get("?bus").toString());
      fdrid = soln.get("?fdrid").toString();
      fdrname = PushExportName (soln.get("?fdrname").toString(), fdrid, "Feeder");
      t1id = soln.get("?t1id").toString();
      basev = Double.parseDouble (soln.get("?basev").toString());
      nomv = Double.parseDouble (soln.get("?nomv").toString());
      vmag = Double.parseDouble (soln.get("?vmag").toString());
      vang = Double.parseDouble (soln.get("?vang").toString());
      r1 = Double.parseDouble (soln.get("?r1").toString());
      x1 = Double.parseDouble (soln.get("?x1").toString());
      r0 = Double.parseDouble (soln.get("?r0").toString());
      x0 = Double.parseDouble (soln.get("?x0").toString());
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + ":" + fdrname + " @ " + bus + " basev=" + df4.format(basev) + " nomv=" + df4.format(nomv));
    buf.append (" vmag=" + df4.format(vmag));
    buf.append (" vang=" + df4.format(vang));
    buf.append (" r1=" + df4.format(r1));
    buf.append (" x1=" + df4.format(x1));
    buf.append (" r0=" + df4.format(r0));
    buf.append (" x0=" + df4.format(x0));
    return buf.toString();
  }

  public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
    DistCoordinates pt = map.get("EnergySource:" + id + ":1");

    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"fdrname\":\"" + fdrname +"\"");
    buf.append (",\"bus\":\"" + bus +"\"");
    buf.append (",\"phases\":\"ABC\"");
    buf.append (",\"nominal_voltage\":" + df1.format(nomv / Math.sqrt(3.0)));
    if (pt != null) {
      buf.append(",\"x1\":" + Double.toString(pt.x));
      buf.append (",\"y1\":" + Double.toString(pt.y));
    }
    buf.append ("}");
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("new Circuit." + fdrname);

    buf.append (" phases=3 bus1=" + bus + " basekv=" + df3.format(0.001 * nomv) + " pu=" + df5.format(vmag/nomv) +
                " angle=" + df5.format(vang * 180.0 / Math.PI) + " r0=" + df5.format(r0) + 
                " x0=" + df5.format(x0) + " r1=" + df5.format(r1) + " x1=" + df5.format(x1));
    buf.append("\n");

    return buf.toString();
  }

  public static String szCSVHeader = "Name,FdrName,Bus,kV,pu,ang,R1,X1,R0,X0";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + fdrname + "," + bus + "," + df3.format(0.001 * nomv) + "," +
                         df5.format(vmag/nomv) + "," + df5.format(vang) + "," + df5.format(r1) + "," + df5.format(x1) + "," + 
                         df5.format(r0) + "," + df5.format(x0) + "\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

