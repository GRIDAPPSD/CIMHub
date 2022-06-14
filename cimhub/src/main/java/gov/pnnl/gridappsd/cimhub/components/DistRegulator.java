package gov.pnnl.gridappsd.cimhub.components;
//      ----------------------------------------------------------
//      Copyright (c) 2017-2022, Battelle Memorial Institute
//      All rights reserved.
//      ----------------------------------------------------------

import org.apache.jena.query.*;

import gov.pnnl.gridappsd.cimhub.queryhandler.QueryHandler;

import java.util.HashMap;

public class DistRegulator extends DistComponent {
  public String pname;
  public String bankphases; // set of phases present for GridLAB-D

  public boolean hasTanks;

  // GridLAB-D only supports different bank parameters for tap (step), R and X
  public int[] step;
  public double[] fwdR;
  public double[] fwdX;
  // GridLAB-D codes phs variations into certain attribute labels
  public String[] orderedPhases;
  // TODO: if any of these vary within the bank, should write separate single-phase instances for GridLAB-D
  public String[] tname;
  public String[] rname;
  public String[] id;
  public String[] monphs;
  public String[] ctlmode;
  public int[] wnum;
  public int[] highStep;
  public int[] lowStep;
  public int[] neutralStep;
  public int[] normalStep;
  public boolean[] enabled;
  public boolean[] ldc;
  public boolean[] ltc;
  public boolean[] discrete; 
  public boolean[] ctl_enabled;
  public double[] incr;
  public double[] neutralU;
  public double[] initDelay; 
  public double[] subDelay;
  public double[] vlim;
  public double[] vmin;
  public double[] vset;
  public double[] vbw;
  public double[] revR;
  public double[] revX;
  public double[] ctRating;
  public double[] ctRatio;
  public double[] ptRatio;

  public int size;

  public double normalCurrentLimit = 0.0;
  public double emergencyCurrentLimit = 0.0;

  public String pxfid;

  private void AddJSONDoubleArray (StringBuilder buf, String tag, double[] vals) {
    buf.append (",\"" + tag + "\":[");
    for (int i = 0; i < size; i++) {
      buf.append (df4.format (vals[i]));
      if (i+1 < size) {
        buf.append (",");
      } else {
        buf.append ("]");
      }
    }
  }

  private void AddJSONIntegerArray (StringBuilder buf, String tag, int[] vals) {
    buf.append (",\"" + tag + "\":[");
    for (int i = 0; i < size; i++) {
      buf.append (Integer.toString (vals[i]));
      if (i+1 < size) {
        buf.append (",");
      } else {
        buf.append ("]");
      }
    }
  }

  private void AddJSONBooleanArray (StringBuilder buf, String tag, boolean[] vals) {
    buf.append (",\"" + tag + "\":[");
    for (int i = 0; i < size; i++) {
      if (vals[i]) {
        buf.append("true");
      } else {
        buf.append("false");
      }
      if (i+1 < size) {
        buf.append (",");
      } else {
        buf.append ("]");
      }
    }
  }

  private void AddJSONStringArray (StringBuilder buf, String tag, String[] vals) {
    buf.append (",\"" + tag + "\":[");
    for (int i = 0; i < size; i++) {
      if (vals[i] == null) {
        buf.append ("null");
      } else {
        buf.append("\"" + vals[i] + "\"");
      }
      if (i+1 < size) {
        buf.append (",");
      } else {
        buf.append ("]");
      }
    }
  }

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"bankName\":\"" + pname +"\"");
    buf.append (",\"size\":\"" + Integer.toString (size) +"\"");
    buf.append (",\"bankPhases\":\"" + bankphases +"\"");
    AddJSONStringArray (buf, "tankName", tname);
    AddJSONIntegerArray (buf, "endNumber", wnum);
    AddJSONStringArray (buf, "endPhase", orderedPhases);
    AddJSONStringArray (buf, "rtcName", rname);
    AddJSONStringArray (buf, "mRID", id);
    AddJSONStringArray (buf, "monitoredPhase", monphs);
    AddJSONIntegerArray (buf, "highStep", highStep);
    AddJSONIntegerArray (buf, "lowStep", lowStep);
    AddJSONIntegerArray (buf, "neutralStep", neutralStep);
    AddJSONIntegerArray (buf, "normalStep", normalStep);
    AddJSONBooleanArray (buf, "TapChanger.controlEnabled", enabled);
    AddJSONBooleanArray (buf, "lineDropCompensation", ldc);
    AddJSONBooleanArray (buf, "ltcFlag", ltc);
    AddJSONBooleanArray (buf, "RegulatingControl.enabled", ctl_enabled);
    AddJSONBooleanArray (buf, "RegulatingControl.discrete", discrete); 
    AddJSONStringArray (buf, "RegulatingControl.mode", ctlmode);
    AddJSONIntegerArray (buf, "step", step);
    AddJSONDoubleArray (buf, "targetValue", vset);
    AddJSONDoubleArray (buf, "targetDeadband", vbw);
    AddJSONDoubleArray (buf, "maxLmitVoltage", vlim);
    AddJSONDoubleArray (buf, "minLimitVoltage", vmin);
    AddJSONDoubleArray (buf, "stepVoltageIncrement", incr);
    AddJSONDoubleArray (buf, "neutralU", neutralU);
    AddJSONDoubleArray (buf, "initialDelay", initDelay); 
    AddJSONDoubleArray (buf, "subsequentDelay", subDelay);
    AddJSONDoubleArray (buf, "lineDropR", fwdR);
    AddJSONDoubleArray (buf, "lineDropX", fwdX);
    AddJSONDoubleArray (buf, "reverseLineDropR", revR);
    AddJSONDoubleArray (buf, "reverseLineDropX", revX);
    AddJSONDoubleArray (buf, "ctRating", ctRating);
    AddJSONDoubleArray (buf, "ctRatio", ctRatio);
    AddJSONDoubleArray (buf, "ptRatio", ptRatio);
    buf.append ("}");
    return buf.toString();
  }

  private void SetSize (QueryHandler queryHandler) {
    size = 1;
    hasTanks = false;
    String szCount = "SELECT (count (?tank) as ?count) WHERE {"+
      " ?tank c:TransformerTank.PowerTransformer ?pxf."+
      " ?pxf c:IdentifiedObject.mRID \"" + pxfid + "\"."+
      "}";
    ResultSet results = queryHandler.query (szCount, "XF count for regulator sizing");
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      int nTanks = soln.getLiteral("?count").getInt();
      if (nTanks > 0) {
        hasTanks = true;
        size = nTanks;
      }
    }
    orderedPhases = new String[size];
    rname = new String[size];
    tname = new String[size];
    id = new String[size];
    monphs = new String[size];
    ctlmode = new String[size];
    wnum = new int[size];
    highStep = new int[size];
    lowStep = new int[size];
    neutralStep = new int[size];
    normalStep = new int[size];
    enabled = new boolean[size];
    ldc = new boolean[size];
    ltc = new boolean[size];
    discrete = new boolean[size]; 
    ctl_enabled = new boolean[size];
    incr = new double[size];
    neutralU = new double[size];
    initDelay = new double[size]; 
    subDelay = new double[size];
    vlim = new double[size];
    vmin = new double[size];
    vset = new double[size];
    vbw = new double[size];
    step = new int[size];
    fwdR = new double[size];
    fwdX = new double[size];
    revR = new double[size];
    revX = new double[size];
    ctRating = new double[size];
    ctRatio = new double[size];
    ptRatio = new double[size];
  }

  public DistRegulator (ResultSet results, QueryHandler queryHandler) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      pname = SafeName (soln.get("?pname").toString());
      pxfid = soln.get("?pxfid").toString();
      SetSize (queryHandler);
      for (int i = 0; i < size; i++) {
        id[i] = soln.get("?id").toString();
        rname[i] = SafeName (soln.get("?rname").toString());
        if (hasTanks) {
          tname[i] = SafeName(soln.get("?tname").toString());
          orderedPhases[i] = soln.get("?orderedPhases").toString();
        } else {
          tname[i] = "";
          orderedPhases[i] = "ABC";
        }
        wnum[i] = Integer.parseInt (soln.get("?wnum").toString());
        highStep[i] = Integer.parseInt (soln.get("?highStep").toString());
        lowStep[i] = Integer.parseInt (soln.get("?lowStep").toString());
        neutralStep[i] = Integer.parseInt (soln.get("?neutralStep").toString());
        normalStep[i] = Integer.parseInt (soln.get("?normalStep").toString());
        enabled[i] = Boolean.parseBoolean (soln.get("?enabled").toString());
        ltc[i] = Boolean.parseBoolean (soln.get("?ltc").toString());
        incr[i] = Double.parseDouble (soln.get("?incr").toString());
        neutralU[i] = Double.parseDouble (soln.get("?neutralU").toString());
        step[i] = Integer.parseInt (soln.get("?step").toString());

        ctl_enabled[i] = OptionalBoolean (soln, "?ctl_enabled", false);
        discrete[i] = OptionalBoolean (soln, "?discrete", false);
        ldc[i] = OptionalBoolean (soln, "?ldc", false);
        monphs[i] = OptionalString (soln, "?monphs", "");
        ctlmode[i] = OptionalString (soln, "?ctlmode", "");
        initDelay[i] = OptionalDouble (soln, "?initDelay", 0.0);
        subDelay[i] = OptionalDouble (soln, "?subDelay", 0.0);
        vlim[i] = OptionalDouble (soln, "?vlim", 0.0);
        vmin[i] = OptionalDouble (soln, "?vmin", 0.0);
        vset[i] = OptionalDouble (soln, "?vset", 0.0);
        vbw[i] = OptionalDouble (soln, "?vbw", 0.0);
        fwdR[i] = OptionalDouble (soln, "?fwdR", 0.0);
        fwdX[i] = OptionalDouble (soln, "?fwdX", 0.0);
        revR[i] = OptionalDouble (soln, "?revR", 0.0);
        revX[i] = OptionalDouble (soln, "?revX", 0.0);
        ctRating[i] = OptionalDouble (soln, "?ctRating", 0.0);
        ctRatio[i] = OptionalDouble (soln, "?ctRatio", 0.0);
        ptRatio[i] = OptionalDouble (soln, "?ptRatio", 1.0); // if left at 0, GridLAB-D will use that value, and OpenDSS defaults to 60
        if ((i + 1) < size) {
          soln = results.next();
        }
      }
      StringBuilder buf = new StringBuilder ();
      for (int i = 0; i < size; i++) {
        buf.append (orderedPhases[i].replace("N","").replace("s", "").replace("1","").replace("2",""));
      }
      bankphases = buf.toString();
    }
//        System.out.println (DisplayString());     
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (pname + " bankphases=" + bankphases);
    for (int i = 0; i < size; i++) {
      buf.append ("\n  " + Integer.toString(i));
      buf.append (" " + Integer.toString(wnum[i]) + ":" +rname[i] + ":" + orderedPhases[i]);
      buf.append (" tank=" + tname[i]);
      buf.append (" ctlmode=" + ctlmode[i]);
      buf.append (" monphs=" + monphs[i]);
      buf.append (" enabled=" + Boolean.toString(enabled[i]));
      buf.append (" ctl_enabled=" + Boolean.toString(ctl_enabled[i]));
      buf.append (" discrete=" + Boolean.toString(discrete[i]));
      buf.append (" ltc=" + Boolean.toString(ltc[i]));
      buf.append (" ldc=" + Boolean.toString(ldc[i]));
      buf.append (" highStep=" + Integer.toString(highStep[i]));
      buf.append (" lowStep=" + Integer.toString(lowStep[i]));
      buf.append (" neutralStep=" + Integer.toString(neutralStep[i]));
      buf.append (" normalStep=" + Integer.toString(normalStep[i]));
      buf.append (" neutralU=" + df4.format(neutralU[i]));
      buf.append (" step=" + Integer.toString(step[i]));
      buf.append (" incr=" + df4.format(incr[i]));
      buf.append (" initDelay=" + df4.format(initDelay[i]));
      buf.append (" subDelay=" + df4.format(subDelay[i]));
      buf.append (" vlim=" + df4.format(vlim[i]));
      buf.append (" vmin=" + df4.format(vmin[i]));
      buf.append (" vset=" + df4.format(vset[i]));
      buf.append (" vbw=" + df4.format(vbw[i]));
      buf.append (" fwdR=" + df4.format(fwdR[i]));
      buf.append (" fwdX=" + df4.format(fwdX[i]));
      buf.append (" revR=" + df4.format(revR[i]));
      buf.append (" revX=" + df4.format(revX[i]));
      buf.append (" ctRating=" + df4.format(ctRating[i]));
      buf.append (" ctRatio=" + df4.format(ctRatio[i]));
      buf.append (" ptRatio=" + df4.format(ptRatio[i]));
    }
    return buf.toString();
  }

  public String GetJSONSymbols(HashMap<String,DistCoordinates> map, 
                               HashMap<String,DistXfmrTank> mapTank,
                               HashMap<String,DistPowerXfmrWinding> mapXfmr) {
    DistCoordinates pt1 = map.get("PowerTransformer:" + pname + ":1");
    DistCoordinates pt2 = map.get("PowerTransformer:" + pname + ":2");
    if (pt2 == null) {
      pt2 = pt1;
    } else if (pt1 == null) {
      pt1 = pt2;
    }
    String bus1, bus2;
    if (hasTanks) {
      DistXfmrTank tank = mapTank.get(tname[0]);
      bus1 = tank.bus[0];
      bus2 = tank.bus[1];
    } else {
      DistPowerXfmrWinding xfmr = mapXfmr.get(pname);
      bus1 = xfmr.bus[0];
      bus2 = xfmr.bus[1];
    }

    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + pname + "\"");
    buf.append (",\"from\":\"" + bus1 + "\"");
    buf.append (",\"to\":\"" + bus2 + "\"");
    buf.append (",\"phases\":\"" + bankphases +"\"");
    buf.append (",\"x1\":" + Double.toString(pt1.x));
    buf.append (",\"y1\":" + Double.toString(pt1.y));
    buf.append (",\"x2\":" + Double.toString(pt2.x));
    buf.append (",\"y2\":" + Double.toString(pt2.y));
    buf.append ("}");
    return buf.toString();
  }

  public String GetGangedGLM (DistPowerXfmrWinding xfmr) {
    return GetCommonGLM ("Yy", xfmr.bus[0], xfmr.bus[1]);
  }

  public String GetTankedGLM (DistXfmrTank tank) {
    return GetCommonGLM (tank.vgrp, tank.bus[0], tank.bus[1]);
  }

  private String GetCommonGLM (String vgrp, String bus1, String bus2) {
    StringBuilder buf = new StringBuilder ("object regulator_configuration {\n");
    double dReg = 0.01 * 0.5 * incr[0] * (highStep[0] - lowStep[0]);
    boolean bDeltaRegulator = false;

    buf.append ("  name \"rcon_" + pname + "\";\n");
    if (vgrp.contains("D") || vgrp.contains("d"))  {
      bDeltaRegulator = true;
      if (bankphases.equals ("ABBC")) {
        buf.append("  connect_type WYE_WYE; // OPEN_DELTA_ABBC not supported for NR\n");
      } else if (bankphases.equals ("CABA")) {
        buf.append("  connect_type WYE_WYE; // OPEN_DELTA_CABA not supported for NR\n");
      } else if (bankphases.equals ("BCAC")) {
        buf.append("  connect_type WYE_WYE; // OPEN_DELTA_BCAC not supported for NR\n");
      } else {
        buf.append("  connect_type WYE_WYE; // CLOSED_DELTA not supported for NR\n");
      }
      bankphases = "ABC";
    } else {
      buf.append ("  connect_type WYE_WYE;\n");
    }
    if (vset[0] > 0.0 && vbw[0] > 0.0 && ltc[0]) {  // for GridAPPS-D, we don't actually use the control modes from CIM
      if (ldc[0]) {
        buf.append("    Control MANUAL; // LINE_DROP_COMP;\n");
      } else {
        buf.append("    Control MANUAL; // OUTPUT_VOLTAGE;\n");
      }
    } else {
      buf.append("    Control MANUAL;\n");
    }
    buf.append ("  // use these for OUTPUT_VOLTAGE mode\n");
    buf.append ("  // band_center " + df6.format(vset[0] * ptRatio[0]) + ";\n");
    buf.append ("  // band_width " + df6.format(vbw[0] * ptRatio[0]) + ";\n");
    buf.append ("  // use these for LINE_DROP_COMP mode\n");
    buf.append ("  // band_center " + df6.format(vset[0]) + ";\n");
    buf.append ("  // band_width " + df6.format(vbw[0]) + ";\n");
    buf.append ("  // transducer ratios only apply to LINE_DROP_COMP mode\n");
    buf.append ("  current_transducer_ratio " + df6.format(ctRatio[0]) + ";\n");
    if (bDeltaRegulator == true) {
      buf.append("  power_transducer_ratio " + df6.format(ptRatio[0] / Math.sqrt(3.0)) + "; // adjusted for WYE_WYE instead of DELTA regulator connection\n");
    } else {
      buf.append("  power_transducer_ratio " + df6.format(ptRatio[0]) + ";\n");
    }
    buf.append ("  dwell_time " + df6.format(initDelay[0]) + ";\n");
    buf.append ("  raise_taps " + Integer.toString(Math.abs (highStep[0] - neutralStep[0])) + ";\n");
    buf.append ("  lower_taps " + Integer.toString(Math.abs (neutralStep[0] - lowStep[0])) + ";\n");
    buf.append ("  regulation " + df6.format(dReg) + ";\n");
    buf.append ("  Type B;\n");
    if (hasTanks) {
      for (int i = 0; i < size; i++) {
  //          int iTap = (int) Math.round((step[i] - 1.0) / incr[i] * 100.0); // TODO - verify this should be an offset from neutralStep
        buf.append ("  compensator_r_setting_" + orderedPhases[i].substring(0,1) + " " + df6.format(fwdR[i]) + ";\n"); // TODO
        buf.append ("  compensator_x_setting_" + orderedPhases[i].substring(0,1) + " " + df6.format(fwdX[i]) + ";\n");
        buf.append ("  // comment out the manual tap setting if using automatic control\n");
        buf.append ("  tap_pos_" + orderedPhases[i].substring(0,1) + " " + Integer.toString(step[i]) + ";\n");
      }
    } else {
      buf.append ("  compensator_r_setting_A " + df6.format(fwdR[0]) + ";\n");
      buf.append ("  compensator_r_setting_B " + df6.format(fwdR[0]) + ";\n");
      buf.append ("  compensator_r_setting_C " + df6.format(fwdR[0]) + ";\n");
      buf.append ("  compensator_x_setting_A " + df6.format(fwdX[0]) + ";\n");
      buf.append ("  compensator_x_setting_B " + df6.format(fwdX[0]) + ";\n");
      buf.append ("  compensator_x_setting_C " + df6.format(fwdX[0]) + ";\n");
      buf.append ("  // comment out the manual tap settings if using automatic control\n");
      buf.append ("  tap_pos_A " + Integer.toString(step[0]) + ";\n");
      buf.append ("  tap_pos_B " + Integer.toString(step[0]) + ";\n");
      buf.append ("  tap_pos_C " + Integer.toString(step[0]) + ";\n");
    }
    buf.append ("}\n");

    buf.append ("object regulator {\n");
    buf.append ("  name \"reg_" + pname + "\";\n");
    buf.append ("  from \"" + bus1 + "\";\n");
    buf.append ("  to \"" + bus2 + "\";\n");
    buf.append ("  phases " + bankphases + ";\n");
    buf.append ("  configuration \"rcon_" + pname + "\";\n");
    AppendGLMRatings (buf, bankphases, normalCurrentLimit, emergencyCurrentLimit);
    buf.append ("}\n");
    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder("");
    String xfName;

    for (int i = 0; i < size; i++) {
      if (size > 1) {
        xfName = tname[i];
      } else if (hasTanks) {
        xfName = tname[i];
      } else {
        xfName = pname;
      }
      buf.append("new RegControl." + rname[i] + " transformer=" + xfName + " winding=" + Integer.toString(wnum[i]) +
                 " TapNum=" + Integer.toString(step[i]));
      if (ltc[i]) {
        if (vset[i] > 0.0) buf.append(" vreg=" + df2.format(vset[i]));
        if (vbw[i] > 0.0) buf.append(" band=" + df2.format(vbw[i]));
        if (ptRatio[i] > 0.0) buf.append(" ptratio=" + df2.format(ptRatio[i]));
        if (ctRating[i] > 0.0) buf.append(" ctprim=" + df2.format(ctRating[i]));
        if (fwdR[i] != 0.0) buf.append(" r=" + df2.format(fwdR[i]));
        if (fwdX[i] != 0.0) buf.append(" x=" + df2.format(fwdX[i]));
        if (revR[i] != 0.0) buf.append(" revr=" + df2.format(revR[i]));
        if (revX[i] != 0.0) buf.append(" revx=" + df2.format(revX[i]));
        if (initDelay[i] > 0.0) buf.append(" delay=" + df2.format(initDelay[i]));
        if (subDelay[i] > 0.0) buf.append(" tapdelay=" + df2.format(subDelay[i]));
        if (vlim[i] > 0.0) buf.append(" vlimit=" + df2.format(vlim[i]));
      }
      // ptphase, enabled
      double turnsRatio = 1.0 + 0.01 * step[i] * incr[i];
      buf.append ("\nedit transformer." + xfName + " wdg=" + Integer.toString(wnum[i]) + " tap=" + df6.format(turnsRatio));
      buf.append("\n");
    }

    return buf.toString();
  }

  public static String szCSVHeader = "Name,Bus1,Phase,Bus2,Phase,Vreg,PTRatio,CTRating,CTRatio,Band,R,X,revR,revX,Step,lowStep,highStep,neutralStep,normalStep,initDelay,subDelay,vLimit,vMin,Increment,neutralU,Wdg,CtlMode,MonPhs,Enabled,LDC,LTC,Discrete,CtlEnabled";

  public String GetCSV (String bus1, String phs1, String bus2, String phs2) {
    StringBuilder buf = new StringBuilder ("");
    for (int i = 0; i < size; i++) {
      buf.append(rname[i] + "," + bus1 + "," + phs1 + "," + bus2 + "," + phs2 + ",");
      buf.append(df2.format(vset[i]) + "," + df2.format(ptRatio[i]) + "," + df2.format(ctRating[i]) + "," + df2.format(ctRatio[i]) + ",");
      buf.append(df2.format(vbw[i]) + "," + df2.format(fwdR[i])  + "," + df2.format(fwdX[i]) + ",");
      buf.append(df2.format(revR[i]) + "," + df2.format(revX[i]) + "," + Integer.toString(step[i]) + ",");
      buf.append(Integer.toString(lowStep[i]) + "," + Integer.toString(highStep[i]) + "," + Integer.toString(neutralStep[i]) + ",");
      buf.append(Integer.toString(normalStep[i]) + "," + df2.format(initDelay[i]) + "," + df2.format(subDelay[i]) + ",");
      buf.append(df2.format(vlim[i]) + "," + df2.format(vmin[i]) + "," + df4.format(incr[i]) + ",");
      buf.append(df2.format(neutralU[i]) + "," + Integer.toString(wnum[i]) + "," + ctlmode[i] + "," + monphs[i] + ",");
      buf.append(Boolean.toString(enabled[i]) + "," + Boolean.toString(ldc[i]) + "," + Boolean.toString(ltc[i]) + ",");
      buf.append(Boolean.toString(discrete[i]) + "," + Boolean.toString(ctl_enabled[i]) + "\n");
    }
    return buf.toString();
  }

  public String GetKey() {
    return pname;
  }
}

