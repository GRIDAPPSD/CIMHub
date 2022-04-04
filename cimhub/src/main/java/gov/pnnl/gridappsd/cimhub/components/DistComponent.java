package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*; 
import org.apache.jena.rdf.model.RDFNode;
import org.apache.commons.math3.complex.Complex;
import java.text.DecimalFormat;
import java.util.HashMap;
import gov.pnnl.gridappsd.cimhub.components.ConverterControlMode;

public abstract class DistComponent {
  public static String nsCIM = "http://iec.ch/TC57/CIM100#";
  public static final String nsRDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
  public static final String nsXSD = "http://www.w3.org/2001/XMLSchema#";

  static double gFREQ = 60.0;
  static double gOMEGA = gFREQ * 2.0 * Math.PI; // 376.9911
  static final double gMperMILE = 1609.344;
  static final double gFTperM = 1.0 / 0.3048;

  static final DecimalFormat df1 = new DecimalFormat("#0.0");
  static final DecimalFormat df2 = new DecimalFormat("#0.00");
  static final DecimalFormat df3 = new DecimalFormat("#0.000");
  static final DecimalFormat df4 = new DecimalFormat("#0.0000");
  static final DecimalFormat df5 = new DecimalFormat("#0.00000");
  static final DecimalFormat df6 = new DecimalFormat("#0.000000");
  static final DecimalFormat df12 = new DecimalFormat("#0.000000000000");

//  public static ResultSet RunQuery (String szQuery) {
//    String qPrefix = "PREFIX r: <" + nsRDF + "> PREFIX c: <" + nsCIM + "> PREFIX xsd:<" + nsXSD + "> ";
//    Query query = QueryFactory.create (qPrefix + szQuery);
//    QueryExecution qexec = QueryExecutionFactory.sparqlService (szEND, query);
//    return qexec.execSelect();
//  }

  public static void SetSystemFrequency (double freq) {
    gFREQ = freq;
    gOMEGA = gFREQ * 2.0 * Math.PI;
  }

  public static double GetSystemFrequency () {
    return gFREQ;
  }

  static String OptionalString (QuerySolution soln, String parm, String def) {
    RDFNode nd = soln.get(parm);
    if (nd != null) {
      String str = nd.toString();
      if (str.length() > 0) {
        return str;
      }
    }
    return def;
  }

  static int OptionalInt (QuerySolution soln, String parm, int def) {
    RDFNode nd = soln.get(parm);
    if (nd != null) {
      String str = nd.toString();
      if (str.length() > 0) {
        return Integer.parseInt (str);
      }
    }
    return def;
  }

  static double OptionalDouble (QuerySolution soln, String parm, double def) {
    RDFNode nd = soln.get(parm);
    if (nd != null) {
      String str = nd.toString();
      if (str.length() > 0) {
        return Double.parseDouble (str);
      }
    }
    return def;
  }

  static boolean OptionalBoolean (QuerySolution soln, String parm, boolean def) {
    RDFNode nd = soln.get(parm);
    if (nd != null) {
      String str = nd.toString();
      if (str.length() > 0) {
        return Boolean.parseBoolean (str);
      }
    }
    return def;
  }

  /** prefix all bus names with `nd_` for GridLAB-D, so they "should" be unique
   *  @param arg the root bus name
   *  @return nd_arg
   */
  static String GldBusName (String arg) {
    return "nd_" + arg;
  }

  /** 
   *  convert a CIM name to simulator name, replacing unallowed characters
   *  @param arg the root bus or component name, aka CIM name
   *  @return the compatible name for GridLAB-D or OpenDSS
   */  
  public static String SafeName (String arg) {      // GLD conversion
    if (arg == null) {
      return null;
    }
    String s = arg.replace (' ', '_');
    s = s.replace ('.', '_');
    s = s.replace ('=', '_');
    s = s.replace ('+', '_');
    s = s.replace ('^', '_');
    s = s.replace ('$', '_');
    s = s.replace ('*', '_');
    s = s.replace ('|', '_');
    s = s.replace ('[', '_');
    s = s.replace (']', '_');
    s = s.replace ('{', '_');
    s = s.replace ('}', '_');
    s = s.replace ('(', '_');
    s = s.replace (')', '_');
    return s;
  }

  public static ConverterControlMode ParseControlMode (String arg) {
    ConverterControlMode s = ConverterControlMode.CONSTANT_PF;
    if (arg == null) {
      return s;
    } else if (arg.contains ("constantReactivePower")) {
      s = ConverterControlMode.CONSTANT_Q;
    } else if (arg.contains ("dynamic")) {
      s = ConverterControlMode.DYNAMIC;
    }
    return s;
  }

  static String GLMClassPrefix (String t) {  // GLD conversion
    if (t.equals("LinearShuntCompensator")) return "cap";
    if (t.equals("ACLineSegment")) return "line"; // assumes we prefix both overhead and underground with line_
    if (t.equals("EnergyConsumer")) return "";  // TODO should we name load:?
    if (t.equals("PowerTransformer")) return "xf";
    return "##UNKNOWN##";
  }

  static String DSSClassPrefix (String t) {  // DSS conversion
    if (t.equals("LinearShuntCompensator")) return "capacitor";
    if (t.equals("ACLineSegment")) return "line";
    if (t.equals("EnergyConsumer")) return "load";
    if (t.equals("PowerTransformer")) return "transformer";
    return "##UNKNOWN##";
  }

  static String FirstDSSPhase (String phs) {
    if (phs.contains ("A")) return "1";
    if (phs.contains ("B")) return "2";
    return "3";
  }

  static int DSSPhaseCount (String phs, boolean bDelta) {
    int nphases = 0;
    if (phs.contains ("A")) nphases += 1;
    if (phs.contains ("B")) nphases += 1;
    if (phs.contains ("C")) nphases += 1;
    if (phs.contains ("s1")) nphases += 1;
    if (phs.contains ("s2")) nphases += 1;
    if ((nphases < 3) && bDelta) {
      nphases = 1;
    }
//    System.out.println (phs + "," + Boolean.toString(bDelta) + "," + Integer.toString(nphases));
    return nphases;
  }

  static int GLMPhaseCount (String phs) {
    int nphases = 0;
    if (phs.contains ("A")) nphases += 1;
    if (phs.contains ("B")) nphases += 1;
    if (phs.contains ("C")) nphases += 1;
    if (phs.contains ("1")) nphases += 1;
    if (phs.contains ("2")) nphases += 1;
    return nphases;
  }

  static String DSSConn (boolean bDelta) {
    if (bDelta) {
      return "d";
    }
    return "w";
  }

  static String DSSShuntPhases (String bus, String phs, boolean bDelta) {
    if (phs.contains ("ABC")) {
      return bus + ".1.2.3";
    }
    if (!bDelta) {
      return DSSBusPhases(bus, phs);
    }
//    if (phs_cnt == 1) {
      if (phs.contains ("A")) {
        return bus + ".1.2";
      } else if (phs.contains ("B")) {
        return bus + ".2.3";
      } else if (phs.contains ("C")) {
        return bus + ".3.1";
      }
//    }
    // TODO - can we have two-phase delta in the CIM?
//    if (phs.contains ("AB")) {
//      return ".1.2.3";
//    } else if (phs.contains ("AC")) {
//      return ".3.1.2";
//    }
    // phs.contains ("BC")) for 2-phase delta
    return bus;// ".2.3.1";
  }

  static String DSSBusPhases (String bus, String phs) {
    if (phs.contains ("ABC") || phs.contains ("A:B:C")) {
      return bus + ".1.2.3";
    } else if (phs.contains ("ACB") || phs.contains ("A:C:B")) {
      return bus + ".1.3.2";
    } else if (phs.contains ("BAC") || phs.contains ("B:A:C")) {
      return bus + ".2.1.3";
    } else if (phs.contains ("BCA") || phs.contains ("B:C:A")) {
      return bus + ".2.3.1";
    } else if (phs.contains ("CAB") || phs.contains ("C:A:B")) {
      return bus + ".3.1.2";
    } else if (phs.contains ("CBA") || phs.contains ("C:B:A")) {
      return bus + ".3.2.1";
    } else if (phs.contains ("12")) {  // secondary
      return bus + ".1.2";
    } else if (phs.contains ("AB") || phs.contains ("A:B")) {
      return bus + ".1.2";
    } else if (phs.contains ("AC") || phs.contains ("A:C")) {
      return bus + ".1.3";
    } else if (phs.contains ("BC") || phs.contains ("B:C")) {
      return bus + ".2.3";
    } else if (phs.contains ("BA") || phs.contains ("B:A")) {
      return bus + ".2.1";
    } else if (phs.contains ("CA") || phs.contains ("C:A")) {
      return bus + ".3.1";
    } else if (phs.contains ("CB") || phs.contains ("C:B")) {
      return bus + ".3.2";
    } else if (phs.contains ("s1:s2") || phs.contains ("s1s2")) {
      return bus + ".1.2";
    } else if (phs.contains ("s2:s1") || phs.contains ("s2s1")) {
      return bus + ".2.1";
    } else if (phs.contains ("s1")) {
      return bus + ".1";
    } else if (phs.contains ("s2")) {
      return bus + ".2";
    } else if (phs.contains ("A")) {
      return bus + ".1";
    } else if (phs.contains ("B")) {
      return bus + ".2";
    } else if (phs.contains ("C")) {
      return bus + ".3";
    } else if (phs.contains ("1")) {
      return bus + ".1";
    } else if (phs.contains ("2")) {
      return bus + ".2";
    } else {
      return bus;  // defaults to 3 phases
    }
  }

  public static String PhaseCodeFromOrderedPhases (String orderedPhases) {
    if (orderedPhases.equals("ABC")) return "ABC";
    if (orderedPhases.equals("ACB")) return "ABC";
    if (orderedPhases.equals("BAC")) return "ABC";
    if (orderedPhases.equals("BCA")) return "ABC";
    if (orderedPhases.equals("CAB")) return "ABC";
    if (orderedPhases.equals("CBA")) return "ABC";

    if (orderedPhases.equals("AB")) return "AC";
    if (orderedPhases.equals("AC")) return "AC";
    if (orderedPhases.equals("BA")) return "AB";
    if (orderedPhases.equals("BC")) return "BC";
    if (orderedPhases.equals("CA")) return "AC";
    if (orderedPhases.equals("CB")) return "BC";

    if (orderedPhases.equals("A")) return "A";
    if (orderedPhases.equals("B")) return "B";
    if (orderedPhases.equals("C")) return "C";

    if (orderedPhases.equals("s1")) return "s1";
    if (orderedPhases.equals("s2")) return "s2";
    if (orderedPhases.equals("s12")) return "s12";
    if (orderedPhases.equals("s21")) return "s12";

    if (orderedPhases.equals("ABCN")) return "ABCN";
    if (orderedPhases.equals("ACBN")) return "ABCN";
    if (orderedPhases.equals("BACN")) return "ABCN";
    if (orderedPhases.equals("BCAN")) return "ABCN";
    if (orderedPhases.equals("CABN")) return "ABCN";
    if (orderedPhases.equals("CBAN")) return "ABCN";

    if (orderedPhases.equals("ABN")) return "ABN";
    if (orderedPhases.equals("ACN")) return "ACN";
    if (orderedPhases.equals("BAN")) return "ABN";
    if (orderedPhases.equals("BCN")) return "BCN";
    if (orderedPhases.equals("CAN")) return "ACN";
    if (orderedPhases.equals("CBN")) return "BCN";

    if (orderedPhases.equals("AN")) return "AN";
    if (orderedPhases.equals("NA")) return "AN";
    if (orderedPhases.equals("BN")) return "BN";;
    if (orderedPhases.equals("NB")) return "BN";
    if (orderedPhases.equals("CN")) return "CN";
    if (orderedPhases.equals("NC")) return "CN";

    if (orderedPhases.equals("s1N")) return "s1N";
    if (orderedPhases.equals("Ns1")) return "s1N";
    if (orderedPhases.equals("s2N")) return "s2N";
    if (orderedPhases.equals("Ns2")) return "s2N";
    if (orderedPhases.equals("s12N")) return "s12N";
    if (orderedPhases.equals("s21N")) return "s12N";

    return "";
  }

  // from the new CIM Core::OrderedPhaseCodeKind enumeration for TransformerTankEnd phasing
  // the floating neutral node (phase) is always numbered 4
  static String DSSOrderedPhases (String orderedPhases, boolean floatNeutral) {
    if (orderedPhases.equals("ABC")) return ".1.2.3";
    if (orderedPhases.equals("ACB")) return ".1.3.2";
    if (orderedPhases.equals("BAC")) return ".2.1.3";
    if (orderedPhases.equals("BCA")) return ".2.3.1";
    if (orderedPhases.equals("CAB")) return ".3.1.2";
    if (orderedPhases.equals("CBA")) return ".3.2.1";

    if (orderedPhases.equals("AB")) return ".1.2";
    if (orderedPhases.equals("AC")) return ".1.3";
    if (orderedPhases.equals("BA")) return ".2.1";
    if (orderedPhases.equals("BC")) return ".2.3";
    if (orderedPhases.equals("CA")) return ".3.1";
    if (orderedPhases.equals("CB")) return ".3.2";

    if (orderedPhases.equals("A")) return ".1";
    if (orderedPhases.equals("B")) return ".2";
    if (orderedPhases.equals("C")) return ".3";

    if (orderedPhases.equals("s1")) return ".1";
    if (orderedPhases.equals("s2")) return ".2";
    if (orderedPhases.equals("s12")) return ".1.2";
    if (orderedPhases.equals("s21")) return ".2.1";

    if (floatNeutral) {
      if (orderedPhases.equals("ABCN")) return ".1.2.3.4";
      if (orderedPhases.equals("ACBN")) return ".1.3.2.4";
      if (orderedPhases.equals("BACN")) return ".2.1.3.4";
      if (orderedPhases.equals("BCAN")) return ".2.3.1.4";
      if (orderedPhases.equals("CABN")) return ".3.1.2.4";
      if (orderedPhases.equals("CBAN")) return ".3.2.1.4";

      if (orderedPhases.equals("ABN")) return ".1.2.4";
      if (orderedPhases.equals("ACN")) return ".1.3.4";
      if (orderedPhases.equals("BAN")) return ".2.1.4";
      if (orderedPhases.equals("BCN")) return ".2.3.4";
      if (orderedPhases.equals("CAN")) return ".3.1.4";
      if (orderedPhases.equals("CBN")) return ".3.2.4";

      if (orderedPhases.equals("AN")) return ".1.4";
      if (orderedPhases.equals("NA")) return ".4.1";
      if (orderedPhases.equals("BN")) return ".2.4";
      if (orderedPhases.equals("NB")) return ".4.2";
      if (orderedPhases.equals("CN")) return ".3.4";
      if (orderedPhases.equals("NC")) return ".4.3";

      if (orderedPhases.equals("s1N")) return ".1.4";
      if (orderedPhases.equals("Ns1")) return ".4.1";
      if (orderedPhases.equals("s2N")) return ".2.4";
      if (orderedPhases.equals("Ns2")) return ".4.2";
      if (orderedPhases.equals("s12N")) return ".1.2.4";
      if (orderedPhases.equals("s21N")) return ".2.1.4";
    } else {
      if (orderedPhases.equals("ABCN")) return ".1.2.3.0";
      if (orderedPhases.equals("ACBN")) return ".1.3.2.0";
      if (orderedPhases.equals("BACN")) return ".2.1.3.0";
      if (orderedPhases.equals("BCAN")) return ".2.3.1.0";
      if (orderedPhases.equals("CABN")) return ".3.1.2.0";
      if (orderedPhases.equals("CBAN")) return ".3.2.1.0";

      if (orderedPhases.equals("ABN")) return ".1.2.0";
      if (orderedPhases.equals("ACN")) return ".1.3.0";
      if (orderedPhases.equals("BAN")) return ".2.1.0";
      if (orderedPhases.equals("BCN")) return ".2.3.0";
      if (orderedPhases.equals("CAN")) return ".3.1.0";
      if (orderedPhases.equals("CBN")) return ".3.2.0";

      if (orderedPhases.equals("AN")) return ".1.0";
      if (orderedPhases.equals("NA")) return ".0.1";
      if (orderedPhases.equals("BN")) return ".2.0";
      if (orderedPhases.equals("NB")) return ".0.2";
      if (orderedPhases.equals("CN")) return ".3.0";
      if (orderedPhases.equals("NC")) return ".0.3";

      if (orderedPhases.equals("s1N")) return ".1.0";
      if (orderedPhases.equals("Ns1")) return ".0.1";
      if (orderedPhases.equals("s2N")) return ".2.0";
      if (orderedPhases.equals("Ns2")) return ".0.2";
      if (orderedPhases.equals("s12N")) return ".1.2.0";
      if (orderedPhases.equals("s21N")) return ".2.1.0";
    }

    return "";
  }

  static String DSSXfmrTankPhasesAndGround (String vgrp, String bus, String orderedPhases, boolean grounded, double rg, double xg) {
    boolean floatNeutral = !grounded;
    if (rg > 0.0 || xg > 0.0) {
      floatNeutral = true;
    }
    StringBuilder buf = new StringBuilder (bus + DSSOrderedPhases (orderedPhases, floatNeutral));
    if (vgrp.contains ("I") && orderedPhases.length() > 1 && !orderedPhases.contains("N")) {
      buf.append (" conn=d");
    }
    if (rg > 0.0 || xg > 0.0) {
      buf.append(" rneut=" + df3.format(rg) + " xneut=" + df3.format(xg));
    }
    return buf.toString();
  }

  // not used yet. should return ABCNSDG set, TODO: when to return G instead of N?
  static String GLMOrderedPhases (String orderedPhases, boolean floatNeutral, boolean delta) {
    String root = "ABC";

    if (orderedPhases.equals("AB") || orderedPhases.equals("ABN")) root = "AB";
    if (orderedPhases.equals("AC") || orderedPhases.equals("ACN")) root = "AC";
    if (orderedPhases.equals("BA") || orderedPhases.equals("BAN")) root = "AB";
    if (orderedPhases.equals("BC") || orderedPhases.equals("BCN")) root = "BC";
    if (orderedPhases.equals("CA") || orderedPhases.equals("CAN")) root = "AC";
    if (orderedPhases.equals("CB") || orderedPhases.equals("CBN")) root = "BC";

    if (orderedPhases.equals("A") || orderedPhases.equals("AN") || orderedPhases.equals("NA")) root = "A";
    if (orderedPhases.equals("B") || orderedPhases.equals("BN") || orderedPhases.equals("NB")) root = "B";
    if (orderedPhases.equals("C") || orderedPhases.equals("CN") || orderedPhases.equals("NC")) root = "C";

    if (orderedPhases.contains("s")) root = "S"; // we don't know the primary-side phase from here

    if (delta && !root.equals("S")) {
      return root + "D";
    } else if (orderedPhases.contains("N")) {
      return root + "N";
    }
    return root;
  }

  static String GLMPhaseString (String cim_phases) {
    StringBuilder ret = new StringBuilder();
    if (cim_phases.contains ("A")) ret.append ("A");
    if (cim_phases.contains ("B")) ret.append ("B");
    if (cim_phases.contains ("C")) ret.append ("C");
    if (cim_phases.contains ("s")) ret.append ("S");
    return ret.toString();
  }

  static String CSVPhaseString (String cim_phases) {
    StringBuilder ret = new StringBuilder();
    if (cim_phases.contains ("A")) ret.append ("A");
    if (cim_phases.contains ("B")) ret.append ("B");
    if (cim_phases.contains ("C")) ret.append ("C");
    if (cim_phases.contains ("s1")) ret.append ("s1");
    if (cim_phases.contains ("s2")) ret.append ("s2");
    if (cim_phases.contains ("s12")) ret.append ("s12");
    return ret.toString();
  }

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

  /** <p>Map CIM connectionKind to GridLAB-D winding connections. TODO: some of the returnable types aren't actually supported in GridLAB-D</p>
  @param wye array of CIM connectionKind attributes per winding 
  @param nwdg number of transformer windings, also the size of wye 
  @return the GridLAB-D winding connection. This may be something not supported in GridLAB-D, which should be treated as a feature request 
  */
  static String GetGldTransformerConnection(String [] conn, int nwdg) {
    if (nwdg == 3) {
      if (conn[0].equals("I") && conn[1].equals("I") && conn[1].equals("I")) return "SINGLE_PHASE_CENTER_TAPPED"; // supported in GridLAB-D
    }
    if (conn[0].equals("D"))
    {
      if (conn[1].equals("D"))  {
        return "DELTA_DELTA";  // supported in GridLAB-D
      } else if (conn[1].equals("Y")) {
        return "DELTA_GWYE"; // supported in GridLAB-D
      } else if (conn[1].equals("Z")) {
        return "D_Z";
      } else if (conn[1].equals("Yn")) {
        return "DELTA_GWYE"; // supported in GridLAB-D
      } else if (conn[1].equals("Zn")) {
        return "D_Zn";
      } else if (conn[1].equals("A")) {
        return "D_A";
      } else if (conn[1].equals("I")) {
        return "D_I";
      }
    } else if (conn[0].equals("Y")) {
      if (conn[1].equals("D"))  {
        return "Y_D";  // TODO - flip to DELTA_GWYE and reverse the node order?
      } else if (conn[1].equals("Y")) {
        return "WYE_WYE"; // supported in GridLAB-D
      } else if (conn[1].equals("Z")) {
        return "Y_Z";
      } else if (conn[1].equals("Yn")) {
        return "WYE_WYE"; // supported in GridLAB-D
      } else if (conn[1].equals("Zn")) {
        return "Y_Z";
      } else if (conn[1].equals("A")) {
        return "WYE_WYE";   // supported in GridLAB-D // TODO - approximately correct
      } else if (conn[1].equals("I")) {
        return "Y_I";
      }
    } else if (conn[0].equals("Z")) {
      if (conn[1].equals("D"))  {
        return "Z_D";
      } else if (conn[1].equals("Y")) {
        return "Z_Y";
      } else if (conn[1].equals("Z")) {
        return "Z_Z";
      } else if (conn[1].equals("Yn")) {
        return "Z_Yn";
      } else if (conn[1].equals("Zn")) {
        return "Z_Zn";
      } else if (conn[1].equals("A")) {
        return "Z_A";
      } else if (conn[1].equals("I")) {
        return "Z_I";
      }
    } else if (conn[0].equals("Yn")) {
      if (conn[1].equals("D"))  {
        return "Yn_D";
      } else if (conn[1].equals("Y")) {
        return "WYE_WYE"; // supported in GridLAB-D
      } else if (conn[1].equals("Z")) {
        return "Yn_Z";
      } else if (conn[1].equals("Yn")) {
        return "WYE_WYE"; // supported in GridLAB-D
      } else if (conn[1].equals("Zn")) {
        return "Yn_Zn";
      } else if (conn[1].equals("A")) {
        return "WYE_WYE";  // supported in GridLAB-D // TODO - approximately correct
      } else if (conn[1].equals("I")) {
        return "Yn_I";
      }
    } else if (conn[0].equals("Zn")) {
      if (conn[1].equals("D"))  {
        return "Zn_D";
      } else if (conn[1].equals("Y")) {
        return "Zn_Y";
      } else if (conn[1].equals("Z")) {
        return "Zn_Z";
      } else if (conn[1].equals("Yn")) {
        return "Zn_Yn";
      } else if (conn[1].equals("Zn")) {
        return "Zn_Zn";
      } else if (conn[1].equals("A")) {
        return "Zn_A";
      } else if (conn[1].equals("I")) {
        return "Zn_I";
      }
    } else if (conn[0].equals("A")) {
      if (conn[1].equals("D"))  {
        return "A_D";
      } else if (conn[1].equals("Y")) {
        return "WYE_WYE";  // supported in GridLAB-D // TODO - approximately correct
      } else if (conn[1].equals("Z")) {
        return "A_Z";
      } else if (conn[1].equals("Yn")) {
        return "WYE_WYE";  // supported in GridLAB-D // TODO - approximately correct
      } else if (conn[1].equals("Zn")) {
        return "A_Zn";
      } else if (conn[1].equals("A")) {
        return "WYE_WYE";  // supported in GridLAB-D // TODO - approximately correct
      } else if (conn[1].equals("I")) {
        return "A_I";
      }
    } else if (conn[0].equals("I")) {
      if (conn[1].equals("D"))  {
        return "I_D";
      } else if (conn[1].equals("Y")) {
        return "I_Y";
      } else if (conn[1].equals("Z")) {
        return "I_Z";
      } else if (conn[1].equals("Yn")) {
        return "I_Yn";
      } else if (conn[1].equals("Zn")) {
        return "I_Zn";
      } else if (conn[1].equals("A")) {
        return "I_A";
      } else if (conn[1].equals("I")) {
        return "SINGLE_PHASE"; // partially supported in GridLAB-D, but implement as WYE_WYE with one non-zero power rating
      }
    }
    return "** Unsupported **";  // TODO - this could be solvable as UNKNOWN in some cases
  }

  protected void AppendGLMRatings (StringBuilder buf, String phs, double normAmps, double emergAmps) {
    String[] phases = {"A", "B", "C"};
    if (normAmps > 0.0) {
      String sNorm = df2.format (normAmps);
      for (String p: phases) {
        if (phs.contains(p)) {
          buf.append ("  continuous_rating_" + p + " " + sNorm + ";\n");
        }
      }
    }
    if (emergAmps > 0.0) {
      String sEmerg = df2.format (emergAmps);
      for (String p: phases) {
        if (phs.contains(p)) {
          buf.append ("  emergency_rating_" + p + " " + sEmerg + ";\n");
        }
      }
    }
  }

  protected void AppendDSSRatings (StringBuilder buf, double normAmps, double emergAmps) {
    if (normAmps > 0.0) {
      buf.append ("~ normamps=" + df2.format (normAmps));
      if (emergAmps > 0.0) {
        buf.append (" emergamps=" + df2.format (emergAmps));
      }
      buf.append ("\n");
    }
  }

  public abstract String DisplayString();
  public abstract String GetKey();
  public abstract String GetJSONEntry();

  public String GetJSONSymbols (HashMap<String,DistCoordinates> map) {
    return "";
  }
}

