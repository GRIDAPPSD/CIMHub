package gov.pnnl.gridappsd.cimhub;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import java.text.DecimalFormat;
import java.util.List;
import java.util.Random;
import org.apache.commons.math3.complex.Complex;
import gov.pnnl.gridappsd.cimhub.components.DistComponent;

/** 
 Helper class to accumulate nodes and loads. 
 <p>All EnergyConsumer data will be attached to node objects, then written as load objects. This preserves the input ConnectivityNode names</p> 
 <p>TODO - another option is to leave all nodes un-loaded, and attach all loads to 
 parent nodes, closer to what OpenDSS does</p>  
*/
public class GldNode {
  /** 
   *  Rotates a phasor +120 degrees by multiplication
   */
  static final Complex pos120 = new Complex (-0.5, 0.5 * Math.sqrt(3.0));

  /** 
   *  Rotates a phasor -120 degrees by multiplication
   */
  static final Complex neg120 = new Complex (-0.5, -0.5 * Math.sqrt(3.0));

  /** 
   *  @param c complex number
   *  @return formatted string for GridLAB-D input files with 'j' at the end
   */
  static String CFormat (Complex c) {
    String sgn;
    if (c.getImaginary() < 0.0)  {
      sgn = "-";
    } else {
      sgn = "+";
    }
    return String.format("%6g", c.getReal()) + sgn + String.format("%6g", Math.abs(c.getImaginary())) + "j";
  }

  static final DecimalFormat df2 = new DecimalFormat("#0.00");
  static final DecimalFormat df6 = new DecimalFormat("#0.000000");

  /** root name of the node or meter, will have `nd_` prepended */
  public final String name;
  /** name of the load, if any, will have `ld_` prepended */
  public String loadname;
  /** ABC allowed */
  public String phases;
  /** this nominal voltage is always line-to-neutral */
  public double nomvln;
  /** real power on phase A, constant impedance portion */
  public double pa_z;
  /** real power on phase B, constant impedance portion */
  public double pb_z;
  /** real power on phase C, constant impedance portion */
  public double pc_z;
  /** reactive power on phase A, constant impedance portion */
  public double qa_z;
  /** reactive power on phase B, constant impedance portion */
  public double qb_z;
  /** reactive power on phase C, constant impedance portion */
  public double qc_z;
  /** real power on phase A, constant current portion */
  public double pa_i;
  /** real power on phase B, constant current portion */
  public double pb_i;
  /** real power on phase C, constant current portion */
  public double pc_i;
  /** reactive power on phase A, constant current portion */
  public double qa_i;
  /** reactive power on phase B, constant current portion */
  public double qb_i;
  /** reactive power on phase C, constant current portion */
  public double qc_i;
  /** real power on phase A, constant power portion */
  public double pa_p;
  /** real power on phase B, constant power portion */
  public double pb_p;
  /** real power on phase C, constant power portion */
  public double pc_p;
  /** reactive power on phase A, constant power portion */
  public double qa_p;
  /** reactive power on phase B, constant power portion */
  public double qb_p;
  /** reactive power on phase C, constant power portion */
  public double qc_p;
  /** for loads, will add N or D phasing, if not S */
  public double ps1_z;
  /** real power on phase s1, constant impedance portion */
  public double ps2_z;
  /** real power on phase s2, constant impedance portion */
  public double ps12_z;
  /** real power on phase s12, constant impedance portion */
  public double qs1_z;
  /** reactive power on phase s1, constant impedance portion */
  public double qs2_z;
  /** reactive power on phase s2, constant impedance portion */
  public double qs12_z;
  /** reactive power on phase s12, constant impedance portion */
  public double ps1_i;
  /** real power on phase s1, constant current portion */
  public double ps2_i;
  /** real power on phase s2, constant current portion */
  public double ps12_i;
  /** real power on phase s12, constant current portion */
  public double qs1_i;
  /** reactive power on phase s1, constant current portion */
  public double qs2_i;
  /** reactive power on phase s2, constant current portion */
  public double qs12_i;
  /** reactive power on phase s12, constant current portion */
  public double ps1_p;
  /** real power on phase s1, constant power portion */
  public double ps2_p;
  /** real power on phase s2, constant power portion */
  public double ps12_p;
  /** real power on phase s12, constant power portion */
  public double qs1_p;
  /** reactive power on phase s1, constant power portion */
  public double qs2_p;
  /** reactive power on phase s2, constant power portion */
  public double qs12_p;
  /** reactive power on phase s12, constant power portion */
  public boolean bDelta;  
  /** denotes the SWING bus, aka substation source bus */
  public boolean bSwing;
  /** signifies there are solar PV inverters connected to this bus */
  public boolean bSolarInverters;
  /** signifies are battery inverters connected to this bus */
  public boolean bStorageInverters;
  /** signifies there are synchronous machines connected to this bus */
  public boolean bSyncMachines;
  /** signifies local DER that can support an island */
  public boolean bSwingPQ;
  /** signifies this bus is connected to a tertiary (or higher) transformer winding,
   *  which is not supported in GridLAB-D. */
  public boolean bTertiaryWinding;

 /** if bSecondary true, the member variables for phase A and B 
  * loads actually correspond to secondary phases 1 and 2. For 
  * GridLAB-D, these are written to phase AS, BS or CS, depending
  * on the primary phase, which we find from the service 
  * transformer or triplex. 
  */ 

  public boolean bSecondary;
  
  public boolean bPlayer;
  public boolean bSchedule;
  public String gldPlayer;
  public String gldSchedule;

  /** constructor defaults to zero load and zero phases present
   *  @param name CIM name of the bus */
  public GldNode(String name) {
    this.name = name;
    nomvln = -1.0;
    phases = "";
    loadname = "";
    pa_z = pb_z = pc_z = qa_z = qb_z = qc_z = 0.0;
    pa_i = pb_i = pc_i = qa_i = qb_i = qc_i = 0.0;
    pa_p = pb_p = pc_p = qa_p = qb_p = qc_p = 0.0;
    ps1_z = ps2_z = ps12_z = qs1_z = qs2_z = qs12_z = 0.0;
    ps1_i = ps2_i = ps12_i = qs1_i = qs2_i = qs12_i = 0.0;
    ps1_p = ps2_p = ps12_p = qs1_p = qs2_p = qs12_p = 0.0;
    bDelta = false;
    bSwing = false;
    bSwingPQ = false;
    bSecondary = false;
    bSolarInverters = false;
    bStorageInverters = false;
    bSyncMachines = false;
    bTertiaryWinding = false;
    bPlayer = false;
    bSchedule = false;
  }

  public double TotalLoadRealPower() {
    return pa_z + pb_z + pc_z + pa_i + pb_i + pc_i + pa_p + pb_p + pc_p + 
      ps1_z + ps2_z + ps12_z + ps1_i + ps2_i + ps12_i + ps1_p + ps2_p + ps12_p;
  }

  public double TotalLoadReactivePower() {
    return qa_z + qb_z + qc_z + qa_i + qb_i + qc_i + qa_p + qb_p + qc_p + 
      qs1_z + qs2_z + qs12_z + qs1_i + qs2_i + qs12_i + qs1_p + qs2_p + qs12_p;
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + ":" + phases + ":" + loadname);
    buf.append (" Vln=" + df2.format(nomvln));
    buf.append (" P=" + df2.format(TotalLoadRealPower()));
    buf.append (" Q=" + df2.format(TotalLoadReactivePower()));
    buf.append (" bSec=" + Boolean.toString(bSecondary));
    buf.append (" bDelta=" + Boolean.toString(bDelta));
    buf.append (" bSwing=" + Boolean.toString(bSwing));
    buf.append (" bSwingPQ=" + Boolean.toString(bSwingPQ));
    buf.append (" bTert=" + Boolean.toString(bTertiaryWinding));
    buf.append (" bPV=" + Boolean.toString(bSolarInverters));
    buf.append (" bBat=" + Boolean.toString(bStorageInverters));
    if (bPlayer) buf.append (" player=" + gldPlayer);
    if (bSchedule) buf.append (" schedule=" + gldSchedule);
    return buf.toString();
  }

  /** accumulates phases present
   *  @param phs phases to add, may contain ABCDNSs in any order
   *  @return always true */
  public boolean AddPhases(String phs) {
    StringBuilder buf = new StringBuilder("");
    if (phases.contains("A") || phs.contains("A")) buf.append("A");
    if (phases.contains("B") || phs.contains("B")) buf.append("B");
    if (phases.contains("C") || phs.contains("C")) buf.append("C");
    if (phs.toLowerCase().contains("s")) {
      bSecondary = true;
    } else if (phs.contains("ABC")) {
      bSecondary = false;
    }
    phases = buf.toString();
    return true;
  }

  public boolean ResetPhases(String phs) {
    phases = "";
    bSecondary = false;
    return AddPhases (phs);
  }

  /** @return phasing string for GridLAB-D with appropriate D, S or N suffix
   *  @param bForLoad true if this node may have load
   *          connected, i.e., D phasing applies */
  public String GetPhases(boolean bForLoad) {
    if (bSecondary) {
      return phases + "S";
    } else {
      if (bDelta && bForLoad) {
        return phases + "D";
      }
    }
    return phases + "N";
  }

  public void AccumulateProfiles (String gldPlayer, String gldSchedule) {
    if (gldPlayer.length() > 0) {
      bPlayer = true;
      this.gldPlayer = gldPlayer;
    }
    if (gldSchedule.length() > 0) {
      bSchedule = true;
      this.gldSchedule = gldSchedule;
    }
  }

  /** Distributes a total load (pL+jqL) among the phases (phs) present on GridLAB-D node
  @param phs phases actually present at the node 
  @param pL total real power 
  @param qL total reactive power 
  @param Pv real power voltage exponent from a CIM LoadResponseCharacteristic 
  @param Qv reactive power voltage exponent from a CIM LoadResponseCharacteristic 
  @param Pz real power constant-impedance percentage from a CIM LoadResponseCharacteristic 
  @param Qz reactive power constant-impedance percentage from a CIM LoadResponseCharacteristic 
  @param Pi real power constant-current percentage from a CIM LoadResponseCharacteristic 
  @param Qi reactive power constant-current percentage from a CIM LoadResponseCharacteristic 
  @param Pp real power constant-power percentage from a CIM LoadResponseCharacteristic 
  @param Qp reactive power constant-power percentage from a CIM LoadResponseCharacteristic 
  @param ldname name of the load to prepend with ld_ 
  @param conn D for delta, otherwise wye 
  @param randomZIP true to randomize the ZIP coefficients  */ 

  public void AccumulateLoads (String ldname, String phs, String conn, double pL, double qL, double Pv, double Qv,
                 double Pz, double Pi, double Pp, double Qz, double Qi, double Qp, boolean randomZIP) {
    double fa = 0.0, fb = 0.0, fc = 0.0, fs1 = 0.0, fs2 = 0.0, fs12 = 0.0, denom = 0.0;
  //  System.out.println ("AccumulateLoads:" + ldname + ":" + phs + ":" + conn + ":" + df2.format(pL) + ":" + df2.format(qL));
    loadname =  DistComponent.GLMObjectPrefix ("ld_") + ldname;
    if (phs.contains("A")) {
      fa = 1.0;
      denom += 1.0;
    }
    if (phs.contains("B")) {
      fb = 1.0;
      denom += 1.0;
    }
    if (phs.contains("C")) {
      fc = 1.0;
      denom += 1.0;
    }
    if (phs.contains("s12")) {  // TODO: this puts load on s1 or s12, but not both
      fs12 = 1.0;
      denom += 1.0;
    } else if (phs.contains("s1")) {
      fs1 = 1.0;
      denom += 1.0;
    }
    if (phs.contains("s2")) {
      fs2 = 1.0;
      denom += 1.0;
    }
    if (fa > 0.0) fa /= denom;
    if (fb > 0.0) fb /= denom;
    if (fc > 0.0) fc /= denom;
    if (fs1 > 0.0) fs1 /= denom;
    if (fs2 > 0.0) fs2 /= denom;
    if (fs12 > 0.0) fs12 /= denom;
    if (conn.equals("D")) {
      bDelta = true;
    }

    // we also have to divide the total pL and qL among constant ZIP components
    
    double fpz = 0.0, fqz = 0.0, fpi = 0.0, fqi = 0.0, fpp = 0.0, fqp = 0.0;

    // Determine ZIP coefficient 
    if (randomZIP == false) {
      // Obtain ZIP coefficient values based on xml file data
      denom = Pz + Pi + Pp;
      if (denom > 0.0) {
        fpz = Pz / denom;
        fpi = Pi / denom;
        fpp = Pp / denom;
      } else {
        if (Pv > 0.9 && Pv < 1.1)  {
          fpi = 1.0;
        } else if (Pv > 1.9 && Pv < 2.1) {
          fpz = 1.0;
        } else {
          fpp = 1.0;
        }
      }
      denom = Qz + Qi + Qp;
      if (denom > 0.0) {
        fqz = Qz / denom;
        fqi = Qi / denom;
        fqp = Qp / denom;
      } else {
        if (Qv > 0.9 && Qv < 1.1)  {
          fqi = 1.0;
        } else if (Qv > 1.9 && Qv < 2.1) {
          fqz = 1.0;
        } else {
          fqp = 1.0;
        }
      }
    }
    else {
      // Obtain ZIP coefficient values based on randomized values and the field-validated paper 
      // Active ZIP model
      int Zpmax = 1, Zpmin = 0, Ppmax = 3, Ppmin = 0;
      Random rand = new Random();
      fpz = Double.valueOf(df2.format(Zpmin + rand.nextDouble() * (Zpmax - Zpmin)));
      fpp = Double.valueOf(df2.format(Ppmin + rand.nextDouble() * (Ppmax - Ppmin)));
      fpi = 1.0 - fpz - fpp;

      // Reactive ZIP model
      int Zqmax = 1, Zqmin = 0, Pqmax = 1, Pqmin = 0;
      fqz = Double.valueOf(df2.format(Zqmin + rand.nextDouble() * (Zqmax - Zqmin)));
      fqp = Double.valueOf(df2.format(Pqmin + rand.nextDouble() * (Pqmax - Pqmin)));
      fqi = 1.0 - fqz - fqp;
    }

    // now update the node phases and phase loads
    pL *= 1000.0;
    qL *= 1000.0;
    AddPhases(phs);
    pa_z += fa * pL * fpz;
    pb_z += fb * pL * fpz;
    pc_z += fc * pL * fpz;
    qa_z += fa * qL * fqz;
    qb_z += fb * qL * fqz;
    qc_z += fc * qL * fqz;
    pa_i += fa * pL * fpi;
    pb_i += fb * pL * fpi;
    pc_i += fc * pL * fpi;
    qa_i += fa * qL * fqi;
    qb_i += fb * qL * fqi;
    qc_i += fc * qL * fqi;
    pa_p += fa * pL * fpp;
    pb_p += fb * pL * fpp;
    pc_p += fc * pL * fpp;
    qa_p += fa * qL * fqp;
    qb_p += fb * qL * fqp;
    qc_p += fc * qL * fqp;
    ps1_z += fs1 * pL * fpz;
    ps2_z += fs2 * pL * fpz;
    ps12_z += fs12 * pL * fpz;
    qs1_z += fs1 * qL * fqz;
    qs2_z += fs2 * qL * fqz;
    qs12_z += fs12 * qL * fqz;
    ps1_i += fs1 * pL * fpi;
    ps2_i += fs2 * pL * fpi;
    ps12_i += fs12 * pL * fpi;
    qs1_i += fs1 * qL * fqi;
    qs2_i += fs2 * qL * fqi;
    qs12_i += fs12 * qL * fqi;
    ps1_p += fs1 * pL * fpp;
    ps2_p += fs2 * pL * fpp;
    ps12_p += fs12 * pL * fpp;
    qs1_p += fs1 * qL * fqp;
    qs2_p += fs2 * qL * fqp;
    qs12_p += fs12 * qL * fqp;
  }

  /** reapportion loads according to constant power (Z/sum), constant current (I/sum) and constant power (P/sum)
   *  @param Z portion of constant-impedance load
   *  @param I portion of constant-current load
   *  @param P portion of constant-power load */
  public void ApplyZIP(double Z, double I, double P) {
    double total = Z + I + P;
    Z = Z / total;
    I = I / total;
    P = P / total;
  //  System.out.println ("ApplyZIP:" + df2.format(Z) + ":" + df2.format(I) + ":" + df2.format(P));

    total = pa_z + pa_i + pa_p;
    pa_z = total * Z;
    pa_i = total * I;
    pa_p = total * P;
    total = qa_z + qa_i + qa_p;
    qa_z = total * Z;
    qa_i = total * I;
    qa_p = total * P;

    total = pb_z + pb_i + pb_p;
    pb_z = total * Z;
    pb_i = total * I;
    pb_p = total * P;
    total = qb_z + qb_i + qb_p;
    qb_z = total * Z;
    qb_i = total * I;
    qb_p = total * P;

    total = pc_z + pc_i + pc_p;
    pc_z = total * Z;
    pc_i = total * I;
    pc_p = total * P;
    total = qc_z + qc_i + qc_p;
    qc_z = total * Z;
    qc_i = total * I;
    qc_p = total * P;

    total = ps1_z + ps1_i + ps1_p;
    ps1_z = total * Z;
    ps1_i = total * I;
    ps1_p = total * P;
    total = qs1_z + qs1_i + qs1_p;
    qs1_z = total * Z;
    qs1_i = total * I;
    qs1_p = total * P;

    total = ps2_z + ps2_i + ps2_p;
    ps2_z = total * Z;
    ps2_i = total * I;
    ps2_p = total * P;
    total = qs2_z + qs2_i + qs2_p;
    qs2_z = total * Z;
    qs2_i = total * I;
    qs2_p = total * P;

    total = ps12_z + ps12_i + ps12_p;
    ps12_z = total * Z;
    ps12_i = total * I;
    ps12_p = total * P;
    total = qs12_z + qs12_i + qs12_p;
    qs12_z = total * Z;
    qs12_i = total * I;
    qs12_p = total * P;
  }

  /** scales the load by a factor that probably came from the command line's -l option
   *  @param scale multiplying factor on all of the load components */
  public void RescaleLoad(double scale) {
  //  System.out.println ("RescaleLoad:" + df2.format(scale));
    pa_z *= scale;
    pb_z *= scale;
    pc_z *= scale;
    qa_z *= scale;
    qb_z *= scale;
    qc_z *= scale;
    pa_i *= scale;
    pb_i *= scale;
    pc_i *= scale;
    qa_i *= scale;
    qb_i *= scale;
    qc_i *= scale;
    pa_p *= scale;
    pb_p *= scale;
    pc_p *= scale;
    qa_p *= scale;
    qb_p *= scale;
    qc_p *= scale;
    ps1_z *= scale;
    ps2_z *= scale;
    ps12_z *= scale;
    qs1_z *= scale;
    qs2_z *= scale;
    qs12_z *= scale;
    ps1_i *= scale;
    ps2_i *= scale;
    ps12_i *= scale;
    qs1_i *= scale;
    qs2_i *= scale;
    qs12_i *= scale;
    ps1_p *= scale;
    ps2_p *= scale;
    ps12_p *= scale;
    qs1_p *= scale;
    qs2_p *= scale;
    qs12_p *= scale;
  }

  /** @return true if a non-zero real or reactive load on any phase */
  public boolean HasLoad() {
    if (pa_z != 0.0) return true;
    if (pb_z != 0.0) return true;
    if (pc_z != 0.0) return true;
    if (qa_z != 0.0) return true;
    if (qb_z != 0.0) return true;
    if (qc_z != 0.0) return true;
    if (pa_i != 0.0) return true;
    if (pb_i != 0.0) return true;
    if (pc_i != 0.0) return true;
    if (qa_i != 0.0) return true;
    if (qb_i != 0.0) return true;
    if (qc_i != 0.0) return true;
    if (pa_p != 0.0) return true;
    if (pb_p != 0.0) return true;
    if (pc_p != 0.0) return true;
    if (qa_p != 0.0) return true;
    if (qb_p != 0.0) return true;
    if (qc_p != 0.0) return true;
    if (ps1_z != 0.0) return true;
    if (ps2_z != 0.0) return true;
    if (ps12_z != 0.0) return true;
    if (qs1_z != 0.0) return true;
    if (qs2_z != 0.0) return true;
    if (qs12_z != 0.0) return true;
    if (ps1_i != 0.0) return true;
    if (ps2_i != 0.0) return true;
    if (ps12_i != 0.0) return true;
    if (qs1_i != 0.0) return true;
    if (qs2_i != 0.0) return true;
    if (qs12_i != 0.0) return true;
    if (ps1_p != 0.0) return true;
    if (ps2_p != 0.0) return true;
    if (ps12_p != 0.0) return true;
    if (qs1_p != 0.0) return true;
    if (qs2_p != 0.0) return true;
    if (qs12_p != 0.0) return true;
  //  System.out.println ("HasLoad returning false");
    return false;
  }

  public boolean CopyLoad (GldNode src) {
    loadname = src.loadname;
    pa_z = src.pa_z;
    pa_i = src.pa_i;
    pa_p = src.pa_p;
    qa_z = src.qa_z;
    qa_i = src.qa_i;
    qa_p = src.qa_p;
    pb_z = src.pb_z;
    pb_i = src.pb_i;
    pb_p = src.pb_p;
    qb_z = src.qb_z;
    qb_i = src.qb_i;
    qb_p = src.qb_p;
    pc_z = src.pc_z;
    pc_i = src.pc_i;
    pc_p = src.pc_p;
    qc_z = src.qc_z;
    qc_i = src.qc_i;
    qc_p = src.qc_p;
    ps1_z = src.ps1_z;
    ps1_i = src.ps1_i;
    ps1_p = src.ps1_p;
    qs1_z = src.qs1_z;
    qs1_i = src.qs1_i;
    qs1_p = src.qs1_p;
    ps2_z = src.ps2_z;
    ps2_i = src.ps2_i;
    ps2_p = src.ps2_p;
    qs2_z = src.qs2_z;
    qs2_i = src.qs2_i;
    qs2_p = src.qs2_p;
    ps12_z = src.ps12_z;
    ps12_i = src.ps12_i;
    ps12_p = src.ps12_p;
    qs12_z = src.qs12_z;
    qs12_i = src.qs12_i;
    qs12_p = src.qs12_p;
    return true;
  }

  private void AppendSubMeter (StringBuilder buf, String meter_class, String suffix) {
    buf.append ("object " + meter_class + " {\n");
    buf.append ("  name \"" + name + suffix + "\";\n");
    buf.append ("  parent \"" + name + "\";\n");
    buf.append ("  phases " + GetPhases(false) + ";\n");
    buf.append ("  nominal_voltage " + df2.format(nomvln) + ";\n");
    buf.append ("}\n");
  }

  private boolean HasOpenDeltaLoad (double real_a, double imag_a, double real_b, double imag_b, double real_c, double imag_c) {
    boolean ret = false;
    if (bDelta) {
      int nphs = 0;
      if (real_a != 0.0 || imag_a != 0.0) {
        ++nphs;
      }
      if (real_b != 0.0 || imag_b != 0.0) {
        ++nphs;
      }
      if (real_c != 0.0 || imag_c != 0.0) {
        ++nphs;
      }
      if (nphs < 3) {
        ret = true;
      }
    }
    return ret;
  }

  private void AppendPowerByFraction (StringBuilder buf, String phs, double pz, double pi, double pp, 
                                      double qz, double qi, double qp, boolean bWantSched, String fSched) {
    double sz = pz*pz + qz*qz;
    double si = pi*pi + qi*qi;
    double sp = pp*pp + qp*qp;
    if (sz > 0.0 || si > 0.0 || sp > 0.0) {
      double base_power = 0.0;
      if (sz > 0.0) {
        sz = Math.sqrt(sz);
        base_power += sz;
      }
      if (si > 0.0) {
        si = Math.sqrt(si);
        base_power += si;
      }
      if (sp > 0.0) {
        sp = Math.sqrt(sp);
        base_power += sp;
      }
      if (bWantSched) {
        buf.append ("  base_power_" + phs + " " + fSched + ".value*" + df2.format(base_power) + ";\n");
      } else if (bSchedule) {
        buf.append ("  base_power_" + phs + " " + gldSchedule + "*" + df2.format(base_power) + ";\n");
      } else if (bPlayer) {
        buf.append ("  base_power_" + phs + " " + gldPlayer + ".value*" + df2.format(base_power) + ";\n");
      } else {
        buf.append ("  base_power_" + phs + " " + df2.format(base_power) + ";\n");
      }
      if (sz > 0.0) {
        buf.append ("  impedance_fraction_" + phs + " " + df6.format(sz/base_power) + ";\n");
        buf.append ("  impedance_pf_" + phs + " " + df6.format(pz/sz) + ";\n");
      }
      if (si > 0.0) {
        buf.append ("  current_fraction_" + phs + " " + df6.format(si/base_power) + ";\n");
        buf.append ("  current_pf_" + phs + " " + df6.format(pi/si) + ";\n");
      }
      if (sp > 0.0) {
        buf.append ("  power_fraction_" + phs + " " + df6.format(sp/base_power) + ";\n");
        buf.append ("  power_pf_" + phs + " " + df6.format(pp/sp) + ";\n");
      }
    }
  }

  public String GetGLM (double load_scale, boolean bWantSched, String fSched, boolean bWantZIP, boolean useHouses, 
            double Zcoeff, double Icoeff, double Pcoeff, List<String> separateLoads) {
    StringBuilder buf = new StringBuilder();

    if (bTertiaryWinding) { // we have to skip it
      return "";
    }

    if (bSwing) {
      buf.append ("object substation {\n");
      buf.append ("  name \"" + name + "\";\n");
      buf.append ("  bustype SWING;\n");
      buf.append ("  phases " + GetPhases(false) + ";\n");
      buf.append ("  nominal_voltage " + df2.format(nomvln) + ";\n");
      buf.append ("  base_power 12MVA;\n");
      buf.append ("  power_convergence_value 100VA;\n");
      buf.append ("  positive_sequence_voltage ${VSOURCE};\n");
      buf.append ("}\n");
    } else if (bSecondary) {
      buf.append ("object triplex_node {\n");
      buf.append ("  name \"" + name + "\";\n");
      buf.append ("  phases " + GetPhases(false) + ";\n");
      buf.append ("  nominal_voltage " + df2.format(nomvln) + ";\n");
  //    if (bSyncMachines) {
  //    buf.append ("  bustype SWING_PQ;\n");
  //    }
      buf.append("}\n");
      if (bSolarInverters) {
        AppendSubMeter (buf, "triplex_meter", "_pvmtr");
      }
      if (bStorageInverters) {
        AppendSubMeter (buf, "triplex_meter", "_stmtr");
      }
      if (bSyncMachines) {
        AppendSubMeter (buf, "triplex_meter", "_dgmtr");
      }
    } else { // primary connected
      buf.append ("object node {\n");
      buf.append ("  name \"" + name + "\";\n");
      buf.append ("  phases " + GetPhases(false) + ";\n");
      buf.append ("  nominal_voltage " + df2.format(nomvln) + ";\n");
      if (bSyncMachines || bStorageInverters) {
        buf.append ("  bustype SWING_PQ;\n");
        bSwingPQ = true;
      }
      buf.append ("}\n");
      if (bSolarInverters) {
        AppendSubMeter (buf, "meter", "_pvmtr");
      }
      if (bStorageInverters) {
        AppendSubMeter (buf, "meter", "_stmtr");
      }
      if (bSyncMachines) {
        AppendSubMeter (buf, "meter", "_dgmtr");
      }
    }
    if (!bSwing && HasLoad()) {
      RescaleLoad (load_scale);
      if (bWantZIP) {
        ApplyZIP (Zcoeff, Icoeff, Pcoeff);
      }   
      if (bSecondary) {
        if (useHouses) {  // houses will be grandchildren of this, but triplex loads and primary loads cannot be grandchildren
          buf.append ("object triplex_meter {\n");
          buf.append ("  name \"" + loadname + "_ldmtr\";\n");
          buf.append ("  parent \"" + name + "\";\n");
          buf.append ("  phases " + GetPhases(false) + ";\n");
          buf.append ("  nominal_voltage " + df2.format(nomvln) + ";\n");
          buf.append ("}\n");
        } else {
          buf.append ("object triplex_load {\n");
          buf.append ("  name \"" + loadname + "\";\n");
          buf.append("  parent \"" + name + "\";\n");
          buf.append ("  phases " + GetPhases(true) + ";\n");
          buf.append ("  nominal_voltage " + df2.format(nomvln) + ";\n");
          double ps1 = ps1_z + ps1_i + ps1_p;
          double ps2 = ps2_z + ps2_i + ps2_p;
          double ps12 = ps12_z + ps12_i + ps12_p;
           if (separateLoads.contains(loadname)) {
            Complex base1 = new Complex (pa_z + pa_i + pa_p, qa_z + qa_i + qa_p);
            Complex base2 = new Complex (pb_z + pb_i + pb_p, qb_z + qb_i + qb_p);
            if (base1.abs() > 0.0 && base2.abs() == 0.0) {
              buf.append ("  constant_power_12 0.0+0.0j;\n");
            } else {
              buf.append ("  constant_power_1 0.0+0.0j;\n");
              buf.append ("  constant_power_2 0.0+0.0j;\n");
            }
          } else {
              if (ps1 > 0.0 && ps2 == 0.0 && ps12 == 0.0) {
                AppendPowerByFraction (buf, "12", ps1_z, ps1_i, ps1_p, qs1_z, qs1_i, qs1_p, bWantSched, fSched);
              } else {
                AppendPowerByFraction (buf, "1", ps1_z, ps1_i, ps1_p, qs1_z, qs1_i, qs1_p, bWantSched, fSched);
                AppendPowerByFraction (buf, "2", ps2_z, ps2_i, ps2_p, qs2_z, qs2_i, qs2_p, bWantSched, fSched);
                AppendPowerByFraction (buf, "12", ps12_z, ps12_i, ps12_p, qs12_z, qs12_i, qs12_p, bWantSched, fSched);
              }
          }
          buf.append ("}\n");
        }
      } else {
        Complex va = new Complex (nomvln);
    	Complex amps;
    	Complex vmagsq = new Complex (nomvln * nomvln);  
        buf.append ("object load {\n");
        buf.append ("  name \"" + loadname + "\";\n");
        buf.append ("  parent \"" + name + "\";\n");
        buf.append ("  phases " + GetPhases(true) + ";\n");
        buf.append ("  nominal_voltage " + df2.format(nomvln) + ";\n");
        if (separateLoads.contains(loadname) || !bWantSched) {

          if (pa_p != 0.0 || qa_p != 0.0)  {
            buf.append ("  constant_power_A " + CFormat(new Complex(pa_p, qa_p)) + ";\n");
          }
          if (pb_p != 0.0 || qb_p != 0.0)  {
            buf.append ("  constant_power_B " + CFormat(new Complex(pb_p, qb_p)) + ";\n");
          }
          if (pc_p != 0.0 || qc_p != 0.0)  {
            buf.append ("  constant_power_C " + CFormat(new Complex(pc_p, qc_p)) + ";\n");
          }
          if (pa_z != 0.0 || qa_z != 0.0) {
            Complex s = new Complex(pa_z, qa_z);
            Complex z = vmagsq.divide(s.conjugate());
            buf.append ("  constant_impedance_A " + CFormat(z) + ";\n");
          }
          if (pb_z != 0.0 || qb_z != 0.0) {
            Complex s = new Complex(pb_z, qb_z);
            Complex z = vmagsq.divide(s.conjugate());
            buf.append ("  constant_impedance_B " + CFormat(z) + ";\n");
          }
          if (pc_z != 0.0 || qc_z != 0.0) {
            Complex s = new Complex(pc_z, qc_z);
            Complex z = vmagsq.divide(s.conjugate());
            buf.append ("  constant_impedance_C " + CFormat(z) + ";\n");
          }
          if (pa_i != 0.0 || qa_i != 0.0) {
            Complex s = new Complex(pa_i, qa_i);
            amps = s.divide(va).conjugate();
            buf.append ("  constant_current_A " + CFormat(amps) + ";\n");
          }
          if (pb_i != 0.0 || qb_i != 0.0) {
            Complex s = new Complex(pb_i, qb_i);
            amps = s.divide(va.multiply(neg120)).conjugate();
            buf.append ("  constant_current_B " + CFormat(amps) + ";\n");
          }
          if (pc_i != 0.0 || qc_i != 0.0) {
            Complex s = new Complex(pc_i, qc_i);
            amps = s.divide(va.multiply(pos120)).conjugate();
            buf.append ("  constant_current_C " + CFormat(amps) + ";\n");
          }
        } else {
            AppendPowerByFraction (buf, "A", pa_z, pa_i, pa_p, qa_z, qa_i, qa_p, bWantSched, fSched);
            AppendPowerByFraction (buf, "B", pb_z, pb_i, pb_p, qb_z, qb_i, qb_p, bWantSched, fSched);
            AppendPowerByFraction (buf, "C", pc_z, pc_i, pc_p, qc_z, qc_i, qc_p, bWantSched, fSched);
        }
        buf.append ("}\n");
      }
    }
    return buf.toString();
  }
}

