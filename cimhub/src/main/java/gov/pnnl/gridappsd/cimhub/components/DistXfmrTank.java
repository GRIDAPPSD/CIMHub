package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistXfmrTank extends DistComponent {
  public static final String szCIMClass = "TransformerTanks";

  public String id;
  public String name;
  public String pid;
  public String vgrp;
  public String pname;
  public String tankinfo;
  public String infoid;
  public String[] bus;
  public String[] t1id;
  public String[] orderedPhases;
  public String[] eid;
  public double[] basev;
  public double[] rg;
  public double[] xg;
  public int[] wdg;
  public boolean[] grounded;

  public double normalCurrentLimit = 0.0;
  public double emergencyCurrentLimit = 0.0;

  public boolean glmUsed;

  public int size;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + pname +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  private void SetSize (int val) {
    size = val;
    bus = new String[size];
    t1id = new String[size];
    orderedPhases = new String[size];
    eid = new String[size];
    wdg = new int[size];
    grounded = new boolean[size];
    basev = new double[size];
    rg = new double[size];
    xg = new double[size];
  }

  public DistXfmrTank (ResultSet results, HashMap<String,Integer> map) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      pid = soln.get("?pid").toString();
      infoid = soln.get("?infoid").toString();
      vgrp = soln.get("?vgrp").toString();
      SetSize (map.get(id));
      glmUsed = true;
      for (int i = 0; i < size; i++) {
        eid[i] = soln.get("?eid").toString();
        bus[i] = GetBusExportName (soln.get("?bus").toString());
        t1id[i] = soln.get("?t1id").toString();
        basev[i] = Double.parseDouble (soln.get("?basev").toString());
        orderedPhases[i] = soln.get("?orderedPhases").toString();
        rg[i] = OptionalDouble (soln, "?rground", 0.0);
        xg[i] = OptionalDouble (soln, "?xground", 0.0);
        wdg[i] = Integer.parseInt (soln.get("?enum").toString());
        grounded[i] = Boolean.parseBoolean (soln.get("?grounded").toString());
        if ((i + 1) < size) {
          soln = results.next();
        }
      }
    }   
  }

  public void PrepForExport() {
    pname = GetEquipmentExportName (pid);
    tankinfo = GetEquipmentExportName (infoid);
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append ("pname=" + pname + " vgrp=" + vgrp + " name=" + name + " tankinfo=" + tankinfo);
    for (int i = 0; i < size; i++) {
      buf.append ("\n  " + Integer.toString(wdg[i]) + " bus=" + bus[i] + " basev=" + df4.format(basev[i]) + " phs=" + orderedPhases[i]);
      buf.append (" grounded=" + Boolean.toString(grounded[i]) + " rg=" + df4.format(rg[i]) + " xg=" + df4.format(xg[i]));
    }
    return buf.toString();
  }

  public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
    DistCoordinates pt1 = map.get("PowerTransformer:" + pid + ":1");
    DistCoordinates pt2 = map.get("PowerTransformer:" + pid + ":2");
    if (pt2 == null) { // catches the one-bus, multiphase autotransformer exception
      pt2 = pt1;
    }
    String bus1 = bus[0];
    String bus2 = bus[1];
    StringBuilder lbl_phs = new StringBuilder ();
    for (int i = 0; i < orderedPhases.length; i++) {
      lbl_phs.append(orderedPhases[i]);
    }

    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + pname + "\"");
    buf.append (",\"from\":\"" + bus1 + "\"");
    buf.append (",\"to\":\"" + bus2 + "\"");
    buf.append (",\"phases\":\"" + orderedPhases[0] +"\"");
    buf.append (",\"configuration\":\"" + tankinfo + ":" + vgrp + "\"");
    buf.append (",\"x1\":" + Double.toString(pt1.x));
    buf.append (",\"y1\":" + Double.toString(pt1.y));
    buf.append (",\"x2\":" + Double.toString(pt2.x));
    buf.append (",\"y2\":" + Double.toString(pt2.y));
    buf.append ("}");
    return buf.toString();
  }

  private String PhasedTankName () {
    if (orderedPhases[0].contains ("A") && orderedPhases[0].contains ("B") && orderedPhases[0].contains ("C")) return tankinfo;
    if (orderedPhases[0].contains ("A")) return tankinfo + "A";
    if (orderedPhases[0].contains ("B")) return tankinfo + "B";
    if (orderedPhases[0].contains ("C")) return tankinfo + "C";
    return tankinfo;
  }

  public String GetGLM () {
    StringBuilder buf = new StringBuilder ("object transformer {\n");

    buf.append ("  name \"" + GLMObjectPrefix ("xf_") + pname + "\";\n");
    buf.append ("  from \"" + bus[0] + "\";\n");
    buf.append ("  to \"" + bus[1] + "\";\n");
    if (orderedPhases[1].contains("s")) {
      buf.append("  phases " + orderedPhases[0].replace("N","") + "S;\n");
    } else {
      buf.append("  phases " + PhaseCodeFromOrderedPhases(orderedPhases[0]) + ";\n");
    }
    buf.append ("  configuration \"" + GLMObjectPrefix ("xcon_") + PhasedTankName() + "\";\n");
    AppendGLMRatings (buf, orderedPhases[0], normalCurrentLimit, emergencyCurrentLimit);
    buf.append ("  // vector group " + vgrp + ";\n");
    buf.append("}\n");
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("new Transformer." + name + " bank=" + pname + " xfmrcode=" + tankinfo + "\n");

    // winding ratings
    AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);
    for (int i = 0; i < size; i++) {
      buf.append("~ wdg=" + Integer.toString(i + 1) + " bus=" + DSSXfmrTankPhasesAndGround (vgrp, bus[i], orderedPhases[i], grounded[i], rg[i], xg[i]) + "\n");
    }
    return buf.toString();
  }

  public static String szCSVHeader = "Name,Wdg1Bus,Phases,Grnd,Rg,Xg,Wdg2Bus,Phases,Grnd,Rg,Xg,Wdg3Bus,Phases,Grnd,Rg,Xg,XfmrCode,VectorGroup,BankName";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name);
    for (int i = 0; i < size; i++) {
      buf.append ("," + bus[i] + "," + orderedPhases[i] + "," + Boolean.toString(grounded[i]) + "," + df3.format(rg[i]) + "," + df3.format(xg[i]));
    }
    if (size < 3) buf.append (",,,,,");
    buf.append ("," + tankinfo + "," + vgrp + "," + pname + "\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

