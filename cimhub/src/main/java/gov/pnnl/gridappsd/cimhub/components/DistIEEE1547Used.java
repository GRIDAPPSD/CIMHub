package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2021-22, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistIEEE1547Used extends DistComponent {
  public static final String szCIMClass = "DERIEEEType1";

  public String id;
  public String name;
  public boolean enabled;
  public String cat;
  public String pecid;

  public double acVnom;
  public double acVmin;
  public double acVmax;
  public double sMax;
  public double pMax;
  public double pMaxUnderPF;
  public double pMaxOverPF;
  public double underPF;
  public double overPF;
  public double qMaxInj;
  public double qMaxAbs;
  public double pMaxCharge;
  public double apparentPowerChargeMax;

  public boolean bUsePG;
  public boolean bUsePN;
  public boolean bUsePP;
  public boolean bHasConstPF;
  public boolean bHasConstQ;
  public boolean bHasPV;
  public boolean bHasPF;
  public boolean bHasQV;
  public boolean bHasQP;

  public boolean vvEnabled;
  public double vvV1;
  public double vvV2;
  public double vvV3;
  public double vvV4;
  public double vvQ1;
  public double vvQ2;
  public double vvQ3;
  public double vvQ4;
  public double vvRef;
  public boolean vvRefAuto;
  public double vvRefOlrt;
  public double vvOlrt;

  public boolean wvEnabled;
  public double wvP1gen;
  public double wvP2gen;
  public double wvP3gen;
  public double wvP1load;
  public double wvP2load;
  public double wvP3load;
  public double wvQ1gen;
  public double wvQ2gen;
  public double wvQ3gen;
  public double wvQ1load;
  public double wvQ2load;
  public double wvQ3load;

  public boolean pfEnabled;
  public double powerFactor;
  public String pfKind;

  public boolean cqEnabled;
  public double reactivePower;

  public boolean vwEnabled;
  public double vwV1;
  public double vwV2;
  public double vwP1;
  public double vwP2gen;
  public double vwP2load;
  public double vwOlrt;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append("}");
    return buf.toString();
  }

  public DistIEEE1547Used (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      pecid = soln.get("?pecid").toString();
      enabled = Boolean.parseBoolean (soln.get("?enabled").toString());
      cat = soln.get("?cat").toString();

      acVnom = Double.parseDouble (soln.get("?acVnom").toString());
      acVmin = Double.parseDouble (soln.get("?acVmin").toString());
      acVmax = Double.parseDouble (soln.get("?acVmax").toString());
      sMax = Double.parseDouble (soln.get("?sMax").toString());
      pMax = Double.parseDouble (soln.get("?pMax").toString());
      pMaxUnderPF = Double.parseDouble (soln.get("?pMaxUnderPF").toString());
      pMaxOverPF = Double.parseDouble (soln.get("?pMaxOverPF").toString());
      underPF = Double.parseDouble (soln.get("?underPF").toString());
      overPF = Double.parseDouble (soln.get("?overPF").toString());
      qMaxInj = Double.parseDouble (soln.get("?qMaxInj").toString());
      qMaxAbs = Double.parseDouble (soln.get("?qMaxAbs").toString());
      pMaxCharge = Double.parseDouble (soln.get("?pMaxCharge").toString());
      apparentPowerChargeMax = Double.parseDouble (soln.get("?apparentPowerChargeMax").toString());

      bUsePG = Boolean.parseBoolean (soln.get("?usePG").toString());
      bUsePN = Boolean.parseBoolean (soln.get("?usePN").toString());
      bUsePP = Boolean.parseBoolean (soln.get("?usePP").toString());
      bHasConstPF = Boolean.parseBoolean (soln.get("?hasConstPF").toString());
      bHasConstQ = Boolean.parseBoolean (soln.get("?hasConstQ").toString());
      bHasPV = Boolean.parseBoolean (soln.get("?hasPV").toString());
      bHasPF = Boolean.parseBoolean (soln.get("?hasPF").toString());
      bHasQV = Boolean.parseBoolean (soln.get("?hasQV").toString());
      bHasQP = Boolean.parseBoolean (soln.get("?hasQP").toString());

      vvEnabled = Boolean.parseBoolean (soln.get("?vvEnabled").toString());
      vvV1 = Double.parseDouble (soln.get("?vvV1").toString());
      vvV2 = Double.parseDouble (soln.get("?vvV2").toString());
      vvV3 = Double.parseDouble (soln.get("?vvV3").toString());
      vvV4 = Double.parseDouble (soln.get("?vvV4").toString());
      vvQ1 = Double.parseDouble (soln.get("?vvQ1").toString());
      vvQ2 = Double.parseDouble (soln.get("?vvQ2").toString());
      vvQ3 = Double.parseDouble (soln.get("?vvQ3").toString());
      vvQ4 = Double.parseDouble (soln.get("?vvQ4").toString());
      vvRef = Double.parseDouble (soln.get("?vvRef").toString());
      vvRefAuto = Boolean.parseBoolean (soln.get("?vvRefAuto").toString());
      vvRefOlrt = Double.parseDouble (soln.get("?vvRefOlrt").toString());
      vvOlrt = Double.parseDouble (soln.get("?vvOlrt").toString());

      wvEnabled = Boolean.parseBoolean (soln.get("?wvEnabled").toString());
      wvP1gen = Double.parseDouble (soln.get("?wvP1gen").toString());
      wvP2gen = Double.parseDouble (soln.get("?wvP2gen").toString());
      wvP3gen = Double.parseDouble (soln.get("?wvP3gen").toString());
      wvP1load = Double.parseDouble (soln.get("?wvP1load").toString());
      wvP2load = Double.parseDouble (soln.get("?wvP2load").toString());
      wvP3load = Double.parseDouble (soln.get("?wvP3load").toString());
      wvQ1gen = Double.parseDouble (soln.get("?wvQ1gen").toString());
      wvQ2gen = Double.parseDouble (soln.get("?wvQ2gen").toString());
      wvQ3gen = Double.parseDouble (soln.get("?wvQ3gen").toString());
      wvQ1load = Double.parseDouble (soln.get("?wvQ1load").toString());
      wvQ2load = Double.parseDouble (soln.get("?wvQ2load").toString());
      wvQ3load = Double.parseDouble (soln.get("?wvQ3load").toString());

      pfEnabled = Boolean.parseBoolean (soln.get("?pfEnabled").toString());
      powerFactor = Double.parseDouble (soln.get("?powerFactor").toString());
      pfKind = soln.get("?pfKind").toString();

      cqEnabled = Boolean.parseBoolean (soln.get("?cqEnabled").toString());
      reactivePower = Double.parseDouble (soln.get("?reactivePower").toString());

      vwEnabled = Boolean.parseBoolean (soln.get("?vwEnabled").toString());
      vwV1 = Double.parseDouble (soln.get("?vwV1").toString());
      vwV2 = Double.parseDouble (soln.get("?vwV2").toString());
      vwP1 = Double.parseDouble (soln.get("?vwP1").toString());
      vwP2gen = Double.parseDouble (soln.get("?vwP2gen").toString());
      vwP2load = Double.parseDouble (soln.get("?vwP2load").toString());
      vwOlrt = Double.parseDouble (soln.get("?vwOlrt").toString());
    }   
  }
  
  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + " cat=" + cat + " enabled=" + Boolean.toString(enabled) + " pf=" + Boolean.toString(pfEnabled));
    buf.append (" cq=" + Boolean.toString(cqEnabled) + " vv=" + Boolean.toString(vvEnabled));
    buf.append (" vw=" + Boolean.toString(vwEnabled) + " wv=" + Boolean.toString(wvEnabled) + " vvRefAuto=" + Boolean.toString(vvRefAuto));
    if (vwEnabled) {
      if (vvEnabled || wvEnabled) {
        buf.append (" combo=" + Boolean.toString (true));
      }
    }
    return buf.toString();
  }

  public String GetGLM (double const_q, double const_pf) {
    StringBuilder buf = new StringBuilder ("");
    if (vvEnabled) {
      buf.append ("  four_quadrant_control_mode VOLT_VAR;\n");
      buf.append ("  V1 " + df3.format(vvV1) + ";\n");
      buf.append ("  Q1 " + df3.format(vvQ1) + ";\n");
      buf.append ("  V2 " + df3.format(vvV2) + ";\n");
      buf.append ("  Q2 " + df3.format(vvQ2) + ";\n");
      buf.append ("  V3 " + df3.format(vvV3) + ";\n");
      buf.append ("  Q3 " + df3.format(vvQ3) + ";\n");
      buf.append ("  V4 " + df3.format(vvV4) + ";\n");
      buf.append ("  Q4 " + df3.format(vvQ4) + ";\n");
      buf.append ("  volt_var_control_lockout 30.0;\n");
    } else if (vwEnabled) {
      buf.append ("  four_quadrant_control_mode VOLT_WATT;\n");
      buf.append ("  VW_V1 " + df3.format(vwV1) + ";\n");
      buf.append ("  VW_P1 " + df3.format(vwP1) + ";\n");
      buf.append ("  VW_V2 " + df3.format(vwV2) + ";\n");
      if (vwP2load < 0.0) {
        buf.append("  VW_P2 " + df3.format(vwP2load) + ";\n");
      } else {
        buf.append("  VW_P2 " + df3.format(vwP2gen) + ";\n");
      }
      buf.append("  volt_var_control_lockout 30.0;\n");
    } else if (wvEnabled) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PF;\n");
      double wv_pf = 1.0;
      double wv_p = Math.abs(wvP1gen) + Math.abs(wvP2gen) + Math.abs(wvP3gen) + Math.abs(wvP1load) + Math.abs(wvP2load) + Math.abs(wvP3load);
      double wv_q = Math.abs(wvQ1gen) + Math.abs(wvQ2gen) + Math.abs(wvQ3gen) + Math.abs(wvQ1load) + Math.abs(wvQ2load) + Math.abs(wvQ3load);
      double wv_s = Math.sqrt(wv_p*wv_p + wv_q*wv_q);
      if (wv_s > 0.0) {
        wv_pf = wv_p / wv_s;
      }
      buf.append("  power_factor " + df4.format(wv_pf) + "; // approximating a WATT_VAR mode\n");
    } else if (pfEnabled) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PF;\n");
      buf.append ("  power_factor " + df4.format (const_pf) + ";\n");
    } else if (cqEnabled) {
      buf.append ("  four_quadrant_control_mode CONSTANT_PQ;\n");
      buf.append ("  Q_Out " + df3.format (const_q) + ";\n");
    }
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }

  public String GetExpControl() {
    StringBuilder buf = new StringBuilder("new ExpControl." + name + " // " + cat + " " + id + "\n");
    double slope = (vvQ2 - vvQ3) / (vvV3 - vvV2);
//  buf.append ("~ vreg=" + df4.format(vvRef) + " slope=" + df4.format(slope) + " vregtau=" + df2.format(vvRefOlrt) + " Tresponse=" + df2.format(vvOlrt) + " deltaQ_factor=0.3\n");
    buf.append ("~ vreg=0.0 slope=" + df4.format(slope) + " vregtau=" + df2.format(vvRefOlrt) + " Tresponse=" + df2.format(vvOlrt) + " deltaQ_factor=0.3\n");
    return buf.toString();
  }

  public String GetDSS (boolean bStorage) {
    if (vvEnabled && vvRefAuto) {
      return GetExpControl();
    }
    StringBuilder buf = new StringBuilder("");
    if (vvEnabled) {
      if (vvV2 == vvV3) { // catA
        buf.append("new XyCurve." + name + "_vvar npts=4 Yarray=[" + df4.format (vvQ1) + " " + df4.format (vvQ1) + " " + df4.format (vvQ4) + " " + df4.format (vvQ4));
        buf.append("] Xarray=[0.5 " + df4.format (vvV1) + " " + df4.format (vvV4) + " 1.5]\n");
      } else { // catB
        buf.append("new XyCurve." + name + "_vvar npts=6 Yarray=[" + df4.format (vvQ1) + " " + df4.format (vvQ1) + " " + df4.format (vvQ2) + " " + df4.format (vvQ3) + " " + df4.format (vvQ4) + " " + df4.format (vvQ4));
        buf.append("] Xarray=[0.5 " + df4.format (vvV1) + " " + df4.format (vvV2) + " " + df4.format (vvV3) + " " + df4.format (vvV4) + " 1.5]\n");
      }
    }
    if (vwEnabled) {
      buf.append("new XyCurve." + name + "_vwatt npts=4 Yarray=[" + df4.format (vwP1) + " " + df4.format (vwP1) + " " + df4.format (vwP2gen) + " " + df4.format (vwP2gen));
      buf.append("] Xarray=[0.0 " + df4.format (vwV1) + " " + df4.format (vwV2) + " 2.0]\n");
      if (bStorage) {
        buf.append("new XyCurve." + name + "_vwattch npts=4 Yarray=[0 0 " + df4.format (-vwP2load) + " " + df4.format (-vwP2load));
        buf.append("] Xarray=[0.0 " + df4.format (vwV1) + " " + df4.format (vwV2) + " 2.0]\n");
      }
    }
    if (wvEnabled) {
      buf.append("new XyCurve." + name + "_wattvar npts=8 Yarray=[" + df4.format (wvQ3load) + " " + df4.format (wvQ3load) + " " + df4.format (wvQ2load) + " " + df4.format (wvQ1load) +
           " " + df4.format (wvQ1gen) + " " + df4.format (wvQ2gen) + " " + df4.format (wvQ3gen) + " " + df4.format (wvQ3gen) + "]\n");
      buf.append("~ Xarray=[-2.0 " + df4.format (wvP3load) + " " + df4.format (wvP2load) + " " + df4.format (wvP1load) +
           " " + df4.format (wvP1gen) + " " + df4.format (wvP2gen) + " " + df4.format (wvP3gen) + " 2.0]\n");
    }
    buf.append("new InvControl." + name + " // " + cat + " " + id + "\n");
    if (vvEnabled && vwEnabled) {
      buf.append ("~ combimode=VV_VW voltage_curvex_ref=rated deltaQ_factor=0.4 VV_RefReactivePower=VARMAX_VARS deltaP_factor=0.2\n");
      buf.append ("~ vvc_curve1=" + name + "_vvar voltwatt_curve=" + name + "_vwatt\n");
    } else if (vvEnabled) {
      buf.append ("~ mode=VOLTVAR voltage_curvex_ref=rated deltaQ_factor=0.4 VV_RefReactivePower=VARMAX_VARS vvc_curve1=" + name + "_vvar\n");
    } else if (vwEnabled) {
      buf.append ("~ mode=VOLTWATT voltage_curvex_ref=rated deltaP_factor=0.2 voltwatt_curve=" + name + "_vwatt");
      if (bStorage) {
        buf.append (" voltwattch_curve=" + name + "_vwattch\n");
      }
      buf.append ("\n");
    } else if (wvEnabled) {
      buf.append ("~ mode=WATTVAR voltage_curvex_ref=rated wattvar_curve=" + name + "_wattvar\n");
    }
    return buf.toString();
  }

  public static String szCSVHeader = "Name,Enabled,Cat,acVnom,acVmin,acVmax,sMax,pMax,pMaxOverPF,overPF,pMaxUnderPF,underPF,qMaxInj,"+
   "qMaxAbs,pMaxCharge,apparentPowerChargeMax,usePG,usePN,usePP,hasConstPF,hasConstQ,hasPV,hasPF,hasQV,hasQP,"+
   "vvEnabled,vvV1,vvV2,vvV3,vvV4,vvQ1,vvQ2,vvQ3,vvQ4,vvRef,vvRefAuto,vvRefOlrt,vvOlrt,"+
   "wvEnabled,wvP1gen,wvP2gen,wvP3gen,wvQ1gen,wvQ2gen,wvQ3gen,wvP1load,wvP2load,wvP3load,wvQ1load,wvQ2load,wvQ3load,"+
   "pfEnabled,powerFactor,pfKind,cqEnabled,reactivePower,vwEnabled,vwV1,vwP1,vwV2,vwP2gen,vwP2load,vwOlrt";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + Boolean.toString(enabled) + "," + cat);

    buf.append ("," + df2.format (acVnom));
    buf.append ("," + df2.format (acVmin));
    buf.append ("," + df2.format (acVmax));
    buf.append ("," + df2.format (sMax));
    buf.append ("," + df2.format (pMax));
    buf.append ("," + df2.format (pMaxOverPF));
    buf.append ("," + df4.format (overPF));
    buf.append ("," + df2.format (pMaxUnderPF));
    buf.append ("," + df4.format (underPF));
    buf.append ("," + df2.format (qMaxInj));
    buf.append ("," + df2.format (qMaxAbs));
    buf.append ("," + df2.format (pMaxCharge));
    buf.append ("," + df2.format (apparentPowerChargeMax));

    buf.append ("," + Boolean.toString (bUsePG));
    buf.append ("," + Boolean.toString (bUsePN));
    buf.append ("," + Boolean.toString (bUsePP));
    buf.append ("," + Boolean.toString (bHasConstPF));
    buf.append ("," + Boolean.toString (bHasConstQ));
    buf.append ("," + Boolean.toString (bHasPV));
    buf.append ("," + Boolean.toString (bHasPF));
    buf.append ("," + Boolean.toString (bHasQV));
    buf.append ("," + Boolean.toString (bHasQP));

    buf.append ("," + Boolean.toString (vvEnabled));
    buf.append ("," + df3.format (vvV1));
    buf.append ("," + df3.format (vvV2));
    buf.append ("," + df3.format (vvV3));
    buf.append ("," + df3.format (vvV4));
    buf.append ("," + df3.format (vvQ1));
    buf.append ("," + df3.format (vvQ2));
    buf.append ("," + df3.format (vvQ3));
    buf.append ("," + df3.format (vvQ4));
    buf.append ("," + df3.format (vvRef));
    buf.append ("," + Boolean.toString (vvRefAuto));
    buf.append ("," + df2.format (vvRefOlrt));
    buf.append ("," + df4.format (vvOlrt));

    buf.append ("," + Boolean.toString (wvEnabled));
    buf.append ("," + df3.format (wvP1gen));
    buf.append ("," + df3.format (wvP2gen));
    buf.append ("," + df3.format (wvP3gen));
    buf.append ("," + df3.format (wvP1load));
    buf.append ("," + df3.format (wvP2load));
    buf.append ("," + df3.format (wvP3load));
    buf.append ("," + df3.format (wvQ1gen));
    buf.append ("," + df3.format (wvQ2gen));
    buf.append ("," + df3.format (wvQ3gen));
    buf.append ("," + df3.format (wvQ1load));
    buf.append ("," + df3.format (wvQ2load));
    buf.append ("," + df3.format (wvQ3load));

    buf.append ("," + Boolean.toString (pfEnabled));
    buf.append ("," + df4.format (powerFactor));
    buf.append ("," + pfKind);

    buf.append ("," + Boolean.toString (cqEnabled));
    buf.append ("," + df2.format (reactivePower));

    buf.append ("," + Boolean.toString (vwEnabled));
    buf.append ("," + df3.format (vwV1));
    buf.append ("," + df3.format (vwP1));
    buf.append ("," + df3.format (vwV2));
    buf.append ("," + df3.format (vwP2gen));
    buf.append ("," + df3.format (vwP2load));
    buf.append ("," + df4.format (vwOlrt));

    buf.append("\n");
    return buf.toString();
  }
}

