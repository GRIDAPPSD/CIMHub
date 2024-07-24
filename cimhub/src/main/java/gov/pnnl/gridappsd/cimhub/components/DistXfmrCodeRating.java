package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;
import org.apache.commons.math3.complex.Complex;

public class DistXfmrCodeRating extends DistComponent {
  public static final String szCIMClass = "TransformerEndInfos";

  public String name;
  public String id;
  public String[] eid;
  public int[] wdg;
  public String[] conn;
  public int[] ang;
  public double[] ratedS; 
  public double[] ratedU;
  public double[] r;
  public int size;

  public boolean glmUsed;
  public boolean glmAUsed;
  public boolean glmBUsed;
  public boolean glmCUsed;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  private void SetSize (int val) {
    size = val;
    eid = new String[size];
    wdg = new int[size];
    conn = new String[size];
    ang = new int[size];
    ratedS = new double[size];
    ratedU = new double[size];
    r = new double[size];
  }

  public DistXfmrCodeRating (ResultSet results, HashMap<String,Integer> map) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      SetSize (map.get(id));
      for (int i = 0; i < size; i++) {
        eid[i] = soln.get("?eid").toString();
        wdg[i] = Integer.parseInt (soln.get("?enum").toString());
        conn[i] = soln.get("?conn").toString();
        ang[i] = Integer.parseInt (soln.get("?ang").toString());
        ratedS[i] = Double.parseDouble (soln.get("?ratedS").toString());
        ratedU[i] = Double.parseDouble (soln.get("?ratedU").toString());
        r[i] = Double.parseDouble (soln.get("?res").toString());
        if ((i + 1) < size) {
          soln = results.next();
        }
      }
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder (id);
    for (int i = 0; i < size; i++) {
      buf.append ("\n  wdg=" + Integer.toString(wdg[i]) + " conn=" + conn[i] + " ang=" + Integer.toString(ang[i]));
      buf.append (" U=" + df4.format(ratedU[i]) + " S=" + df4.format(ratedS[i]) + " r=" + df4.format(r[i]));
    }
    return buf.toString();
  }

  // phs may contain A, B, C, N, s1, s2, s12 in any order
  public void AddGldPrimaryPhase (String phs) {
    if (phs.contains("A")) glmAUsed = true;
    if (phs.contains("B")) glmBUsed = true;
    if (phs.contains("C")) glmCUsed = true;
  }

  // format all parameters except the name, power ratings and phases
  private String TankParameterString (DistXfmrCodeSCTest sct, DistXfmrCodeNLTest oct) {
    StringBuilder buf = new StringBuilder("");
    double rpu = 0.0;
    double zpu = 0.0;
    double zbase1 = ratedU[0] * ratedU[0] / ratedS[0];
    double zbase2 = ratedU[1] * ratedU[1] / ratedS[1];
    if ((sct.ll[0] > 0.0) && (size < 3)) { // sct.ll was on sct.sbase, but want rpu on ratedS
      rpu = 1000.0 * sct.ll[0] * ratedS[0] / sct.sbase[0] / sct.sbase[0];
    } else {
      // hard-wired for SINGLE_PHASE_CENTER_TAPPED,
      // which is the only three-winding case that GridLAB-D supports
      rpu = (r[0] / zbase1) + 0.5 * (r[1] / zbase2);
    }
    if (rpu <= 0.000001) {
      rpu = 0.000001; // GridLAB-D doesn't like zero
    }
    if (sct.fwdg[0] == 1) {
      zpu = sct.z[0] / zbase1;
    } else if (sct.fwdg[0] == 2) {
      zpu = sct.z[0] / zbase2;
    }
    double xpu = zpu;
    if (zpu >= rpu) {
      xpu = Math.sqrt (zpu * zpu - rpu * rpu);
    }

    String sConnect = GetGldTransformerConnection (conn, size);
    if (sConnect.equals("SINGLE_PHASE")) {
      sConnect = "WYE_WYE";
    }
    buf.append ("  primary_voltage " + df3.format (ratedU[0]) + ";\n");
    buf.append ("  secondary_voltage " + df3.format (ratedU[1]) + ";\n");
    if (sConnect.equals ("Y_D")) {
      buf.append("  connect_type WYE_WYE; // should be Y_D\n");
    } else {
      buf.append("  connect_type " + sConnect + ";\n");
    }
    if (sConnect.equals ("SINGLE_PHASE_CENTER_TAPPED")) {
      // the hard-wired interlace assumptions use 0.8*zpu, 0.4*zpu, 0.4*zpu for X values,
      // which would match X12 and X13, but not X23 from the original short-circuit test data
      double r1 = 0.5 * rpu;
      double r2 = rpu;
      double r3 = rpu;
      double x1 = 0.8 * zpu;
      double x2 = 0.4 * zpu;
      double x3 = x2;
      if (size == 3) { // use the OpenDSS approach, should match Z23, should also work for non-interlaced
        double Sbase = ratedS[0];
        double r12 = 1000.0 * sct.ll[0] * Sbase / sct.sbase[0] / sct.sbase[0];  // convert from test base to winding 1 base
        double r13 = 1000.0 * sct.ll[1] * Sbase / sct.sbase[1] / sct.sbase[1];
        double r23 = 1000.0 * sct.ll[2] * Sbase / sct.sbase[2] / sct.sbase[2];
        zpu = sct.z[0] * Sbase / ratedU[0] / ratedU[0];
        double x12 = Math.sqrt(zpu*zpu - r12*r12);
        zpu = sct.z[1] * Sbase / ratedU[0] / ratedU[0];
        double x13 = Math.sqrt(zpu*zpu - r13*r13);
        zpu = sct.z[2] * Sbase / ratedU[1] / ratedU[1];
        double x23 = Math.sqrt(zpu*zpu - r23*r23);
        r1 = 0.5 * (r12 + r13 - r23);
        r2 = 0.5 * (r12 + r23 - r13);
        r3 = 0.5 * (r13 + r23 - r12);
        x1 = 0.5 * (x12 + x13 - x23);
        x2 = 0.5 * (x12 + x23 - x13);
        x3 = 0.5 * (x13 + x23 - x12);
      }
      String impedance = CFormat (new Complex (r1, x1));
      String impedance1 = CFormat (new Complex (r2, x2));
      String impedance2 = CFormat (new Complex (r3, x3));
      buf.append ("  impedance " + impedance + ";\n");
      buf.append ("  impedance1 " + impedance1 + ";\n");
      buf.append ("  impedance2 " + impedance2 + ";\n");
    } else {
      buf.append ("  resistance " + df6.format (rpu) + ";\n");
      buf.append ("  reactance " + df6.format (xpu) + ";\n");
    }
    // as of v4.3, GridLAB-D implementing shunt_impedance for only two connection types
    if (sConnect.equals ("SINGLE_PHASE_CENTER_TAPPED") || sConnect.equals ("WYE_WYE")) {
      double puloss = 1000.0 * oct.nll / ratedS[0];
      double puimag = 0.01 * oct.iexc * oct.sbase / ratedS[0];
      if ((puloss > 0.0) && (puloss <= puimag)) {
        puimag = Math.sqrt(puimag * puimag - puloss * puloss);
      }
      if (puimag > 0.0) {
        buf.append ("  shunt_reactance " + df6.format (1.0 / puimag) + ";\n");
      }
      if (puloss > 0.0) {
        buf.append ("  shunt_resistance " + df6.format (1.0 / puloss) + ";\n");
      }
    }
    return buf.toString();
  }

  private void AppendOneTank (StringBuilder buf, String name, String sKVA, boolean useA, boolean useB, boolean useC, String parms) {
    buf.append ("object transformer_configuration {\n");
    buf.append ("  name \"" + GLMObjectPrefix ("xcon_") + name + "\";\n");
    buf.append ("  power_rating " + sKVA + ";\n");
    if (useA) {
      buf.append ("  powerA_rating " + sKVA + ";\n");
      buf.append ("  powerB_rating 0.0;\n");
      buf.append ("  powerC_rating 0.0;\n");
    } else if (useB) {
      buf.append ("  powerA_rating 0.0;\n");
      buf.append ("  powerB_rating " + sKVA + ";\n");
      buf.append ("  powerC_rating 0.0;\n");
    } else if (useC) {
      buf.append ("  powerA_rating 0.0;\n");
      buf.append ("  powerB_rating 0.0;\n");
      buf.append ("  powerC_rating " + sKVA + ";\n");
    }
    buf.append (parms);
    buf.append ("}\n");
  }

  // write one, two or three of these depending on the phases used
  public String GetGLM (DistXfmrCodeSCTest sct, DistXfmrCodeNLTest oct) {
    String parms = TankParameterString (sct, oct);

    StringBuilder buf = new StringBuilder("");

    String sConnect = GetGldTransformerConnection (conn, size);
    String sKVA = df3.format (ratedS[0] * 0.001);
    if (sConnect.equals("SINGLE_PHASE_CENTER_TAPPED") || sConnect.equals("SINGLE_PHASE")) {
      if (glmAUsed) AppendOneTank (buf, name + "A", sKVA, true, false, false, parms);
      if (glmBUsed) AppendOneTank (buf, name + "B", sKVA, false, true, false, parms);
      if (glmCUsed) AppendOneTank (buf, name + "C", sKVA, false, false, true, parms);
    } else {
      AppendOneTank (buf, name, sKVA, false, false, false, parms);
    }
    return buf.toString();
  }

  // physical ohms to match the short circuit test load losses
  public void SetWindingResistances (DistXfmrCodeSCTest sct) {
    double r12pu, r13pu, r23pu, r1pu, r2pu, r3pu, Sbase;
    Sbase = sct.sbase[0]; // the per-unit manipulations have to be done on this common base
    if (sct.size == 1) {
      r12pu = 1000.0 * sct.ll[0] / Sbase;
      r1pu = 0.5 * r12pu;
      r2pu = r1pu;
      r[0] = r1pu * ratedU[0] * ratedU[0] / Sbase;
      r[1] = r2pu * ratedU[1] * ratedU[1] / Sbase;
    } else if (sct.size == 3) {
      // test resistances on their own base
      r12pu = 1000.0 * sct.ll[0] / sct.sbase[0];
      r13pu = 1000.0 * sct.ll[1] / sct.sbase[1];
      r23pu = 1000.0 * sct.ll[2] / sct.sbase[2];
      // convert r13 and r23 to a common base
      r13pu *= (Sbase / sct.sbase[1]);
      r23pu *= (Sbase / sct.sbase[2]);
      // determine the star equivalent in per-unit
      r1pu = 0.5 * (r12pu + r13pu - r23pu);
      r2pu = 0.5 * (r12pu + r23pu - r13pu);
      r3pu = 0.5 * (r13pu + r23pu - r12pu);
      // convert to ohms from the common Sbase
      r[0] = r1pu * ratedU[0] * ratedU[0] / Sbase;
      r[1] = r2pu * ratedU[1] * ratedU[1] / Sbase;
      r[2] = r3pu * ratedU[2] * ratedU[2] / Sbase;
    }
  }

  public String GetDSS(DistXfmrCodeSCTest sct, DistXfmrCodeNLTest oct) {
    boolean bDelta;
    int phases = 3;
    double zbase, xpct, zpct, rpct, pctloss, pctimag, pctiexc, rescale;
    int fwdg, twdg, i;

    for (i = 0; i < size; i++) {
      if (conn[i].contains("I")) {
        phases = 1;
      }
    }
    StringBuilder buf = new StringBuilder("new Xfmrcode." + name + " windings=" + Integer.toString(size) +
                        " phases=" + Integer.toString(phases));

    // short circuit tests - valid only up to 3 windings; put on the Winding 1 base
    for (i = 0; i < sct.size; i++) {
      fwdg = sct.fwdg[i];
      twdg = sct.twdg[i];
      zbase = ratedU[fwdg-1] * ratedU[fwdg-1] / sct.sbase[i];
      zpct = 100.0 * sct.z[i] / zbase;
      rpct = 100.0 * 1000.0 * sct.ll[i] / sct.sbase[i];
      xpct = Math.sqrt(zpct*zpct - rpct*rpct);
      // convert rpct, xpct from the test base power to winding 1 base power
      rescale = ratedS[0] / sct.sbase[i];
      rpct *= rescale;
      xpct *= rescale;
      if ((fwdg == 1 && twdg == 2) || (fwdg == 2 && twdg == 1)) {
        buf.append(" xhl=" + df6.format(xpct));
      } else if ((fwdg == 1 && twdg == 3) || (fwdg == 3 && twdg == 1)) {
        buf.append(" xht=" + df6.format(xpct));
      } else if ((fwdg == 2 && twdg == 3) || (fwdg == 3 && twdg == 2)) {
        buf.append(" xlt=" + df6.format(xpct));
      }
    }
    // open circuit test, must put on winding 1 base for OpenDSS
    pctloss = 100.0 * 1000.0 * oct.nll / ratedS[0];
    pctiexc = oct.iexc * oct.sbase / ratedS[0];
    if ((pctloss > 0.0) && (pctloss <= pctiexc)) {
      pctimag = Math.sqrt(pctiexc * pctiexc - pctloss * pctloss);
    } else {
      pctimag = pctiexc;
    }
    buf.append (" %imag=" + df3.format(pctimag) + " %noloadloss=" + df3.format(pctloss) + "\n");

    // winding ratings
    SetWindingResistances (sct);
    for (i = 0; i < size; i++) {
      if (conn[i].contains("D")) {
        bDelta = true;
      } else {
        bDelta = false;
      }
      zbase = ratedU[i] * ratedU[i] / ratedS[0]; // PU impedances always on winding 1's kva base
      buf.append("~ wdg=" + Integer.toString(i + 1) + " conn=" + DSSConn(bDelta) +
           " kv=" + df3.format(0.001 * ratedU[i]) + " kva=" + df1.format(0.001 * ratedS[i]) +
           " %r=" + df6.format(100.0 * r[i] / zbase) + "\n");
    }
    return buf.toString();
  }

  public static String szCSVHeader = "Name,NumWindings,NumPhases,Wdg1kV,Wdg1kVA,Wdg1Conn,Wdg1R,Wdg1ClockAng,Wdg2kV,Wdg2kVA,Wdg2Conn,Wdg2R,Wdg2ClockAng,Wdg3kV,Wdg3kVA,Wdg3Conn,Wdg3R,Wdg3ClockAng,%x12,%x13,%x23,%imag,%NoLoadLoss";

  public String GetCSV (DistXfmrCodeSCTest sct, DistXfmrCodeNLTest oct) {
    boolean bDelta;
    int phases = 3;
    double zbase, xpct, zpct, rpct, pctloss, pctimag, pctiexc, rescale;
    int fwdg, twdg, i;

    for (i = 0; i < size; i++) {
      if (conn[i].contains("I")) {
        phases = 1;
      }
    }
    StringBuilder buf = new StringBuilder(name + "," + Integer.toString(size) + "," + Integer.toString(phases));

    // winding ratings: kV, kVA, Conn, R
    SetWindingResistances (sct);
    for (i = 0; i < size; i++) {
      if (conn[i].contains("D")) {
        bDelta = true;
      } else {
        bDelta = false;
      }
      zbase = ratedU[i] * ratedU[i] / ratedS[i];
      buf.append ("," + df3.format(0.001 * ratedU[i]) + "," + df1.format(0.001 * ratedS[i]) + "," + DSSConn(bDelta) +
           "," + df6.format(100.0 * r[i] / zbase) + "," + Integer.toString(ang[i]));
    }
    if (size < 3) buf.append (",,,");

    // short circuit tests - valid only up to 3 windings; put on winding 1 base
    double x12 = 0.0, x13 = 0.0, x23 = 0.0;
    for (i = 0; i < sct.size; i++) {
      fwdg = sct.fwdg[i];
      twdg = sct.twdg[i];
      zbase = ratedU[fwdg-1] * ratedU[fwdg-1] / sct.sbase[i];
      zpct = 100.0 * sct.z[i] / zbase;
      rpct = 100.0 * 1000.0 * sct.ll[i] / sct.sbase[i];
      xpct = Math.sqrt(zpct*zpct - rpct*rpct);
      // convert rpct, xpct from the test base power to winding 1 base power
      rescale = ratedS[0] / sct.sbase[i];
      rpct *= rescale;
      xpct *= rescale;
      if ((fwdg == 1 && twdg == 2) || (fwdg == 2 && twdg == 1)) {
        x12 = xpct;
      } else if ((fwdg == 1 && twdg == 3) || (fwdg == 3 && twdg == 1)) {
        x13 = xpct;
      } else if ((fwdg == 2 && twdg == 3) || (fwdg == 3 && twdg == 2)) {
        x23 = xpct;
      }
    }
    buf.append ("," + df6.format(x12) + "," + df6.format(x13) + "," + df6.format(x23));

    // open circuit test; put on winding 1 base
    pctloss = 100.0 * 1000.0 * oct.nll / ratedS[0];
    pctiexc = oct.iexc * oct.sbase / ratedS[0];
    if ((pctloss > 0.0) && (pctloss <= pctiexc)) {
      pctimag = Math.sqrt(pctiexc * pctiexc - pctloss * pctloss);
    } else {
      pctimag = pctiexc;
    }
    buf.append ("," + df3.format(pctimag) + "," + df3.format(pctloss) + "\n");
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

