package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.lang.Math.*;
import java.util.HashMap;
import java.util.HashSet;

public class DistLineSpacing extends DistComponent {
  public static final String szCIMClass = "WireSpacingInfo";

  public String name;
  public String id;
  public double[] xarray;
  public double[] yarray;
  public String usage;
  public int nwires;
  public boolean cable;
  public double b_sep;
  public int b_cnt;

  // only write the phasing permutations that are actually used
  private HashSet<String> perms = new HashSet<>();
  private boolean bTriplex;
  // nphases inferred locally from the permutation
  // bNeutral inferred locally from nwires > nphases

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public void MarkPermutationsUsed (String s) {
    if (s.contains ("ABC") && nwires >= 3) {
      perms.add ("ABC");
    } else if (s.contains ("ACB") && nwires >= 3) {
      perms.add ("ACB");
    } else if (s.contains ("BAC") && nwires >= 3) {
      perms.add ("BAC");
    } else if (s.contains ("BCA") && nwires >= 3) {
      perms.add ("BCA");
    } else if (s.contains ("CAB") && nwires >= 3) {
      perms.add ("CAB");
    } else if (s.contains ("CBA") && nwires >= 3) {
      perms.add ("CBA");
    } else if (s.contains ("AB") && nwires >= 2) {
      perms.add ("AB");
    } else if (s.contains ("BA") && nwires >= 2) {
      perms.add ("BA");
    } else if (s.contains ("BC") && nwires >= 2) {
      perms.add ("BC");
    } else if (s.contains ("CB") && nwires >= 2) {
      perms.add ("CB");
    } else if (s.contains ("AC") && nwires >= 2) {
      perms.add ("AC");
    } else if (s.contains ("CA") && nwires >= 2) {
      perms.add ("CA");
    } else if (s.contains ("A") && nwires >= 1) {
      perms.add ("A");
    } else if (s.contains ("B") && nwires >= 1) {
      perms.add ("B");
    } else if (s.contains ("C") && nwires >= 1) {
      perms.add ("C");
    }
  }

  public DistLineSpacing (ResultSet results, HashMap<String,Integer> map) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      cable = OptionalBoolean (soln, "?cable", false);
      usage = OptionalString (soln, "?usage", "distribution");
      b_sep = OptionalDouble (soln, "?bundle_sep", 0.0);
      b_cnt = OptionalInt (soln, "?bundle_count", 0);
      nwires = map.get (id);
      xarray = new double[nwires];
      yarray = new double[nwires];
      xarray[0] = OptionalDouble (soln, "?x", 0.0);
      yarray[0] = OptionalDouble (soln, "?y", 0.0);
      for (int i = 1; i < nwires; i++) {
        soln = results.next();
        xarray[i] = OptionalDouble (soln, "?x", 0.0);
        yarray[i] = OptionalDouble (soln, "?y", 0.0);
      }
    }
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + " nwires=" + Integer.toString(nwires) + " cable=" + Boolean.toString(cable) + " usage=" + usage); 
    buf.append (" b_cnt=" + Integer.toString(b_cnt) + " b_sep=" + df4.format(b_sep));
    for (int i = 0; i < nwires; i++) {
      buf.append ("\n  x=" + df4.format(xarray[i]) + " y=" + df4.format(yarray[i]));
    }
    return buf.toString();
  }

  private void AppendDSSPermutation(StringBuilder buf, String perm) {
    int i;

    int nphases = perm.length();
    boolean has_neutral = false;
    if (nwires > nphases) {
      has_neutral = true;
    }

    buf.append ("new LineSpacing." + name + "_" + perm + " nconds=" + Integer.toString(nwires) + " nphases=" + Integer.toString(nphases) + " units=m\n");
    buf.append ("~ x=[");
    for (i = 0; i < nwires; i++) {
      buf.append (df4.format(xarray[i]));
      if (i+1 < nwires) {
        buf.append (",");
      }
    }
    buf.append ("]\n~ h=[");
    for (i = 0; i < nwires; i++) {
      buf.append (df4.format(yarray[i]));
      if (i+1 < nwires) {
        buf.append (",");
      }
    }
    buf.append ("]\n");
  }

  private void AppendCSVPermutation(StringBuilder buf, String perm) {
    int i;

    int nphases = perm.length();
    boolean has_neutral = false;
    if (nwires > nphases) {
      has_neutral = true;
    }

    buf.append (name + "_" + perm + "," + Integer.toString(nwires) + "," + Integer.toString(nphases) + ",m");
    buf.append (",[");
    for (i = 0; i < nwires; i++) {
      buf.append (df4.format(xarray[i]));
      if (i+1 < nwires) {
        buf.append (",");
      }
    }
    buf.append ("],[");
    for (i = 0; i < nwires; i++) {
      buf.append (df4.format(yarray[i]));
      if (i+1 < nwires) {
        buf.append (",");
      }
    }
    buf.append ("]\n");
  }

  private double WireSeparation (int i, int j) {
    double dx = xarray[i] - xarray[j];
    double dy = yarray[i] - yarray[j];
    return Math.sqrt (dx * dx + dy * dy);
  }

  private void AppendGLMPermutation (StringBuilder buf, String perm) {
    int nphases = perm.length();
    boolean has_neutral = false;
    if (nwires > nphases) {
      has_neutral = true;
    }
    buf.append("object line_spacing {\n");
    if (has_neutral) {
      buf.append("  name \"" + GLMObjectPrefix ("spc_") + name + "_" + perm + "N\";\n");
    } else {
      buf.append("  name \"" + GLMObjectPrefix ("spc_") + name + "_" + perm + "\";\n");
    }

    int idxA=0, idxB=0, idxC=0;
    int idxN = nwires-1;
    if (nphases == 2) {
      if (perm.contains ("AB")) {
        idxA = 0; idxB = 1;
      } else if (perm.contains ("BA")) {
        idxB = 0; idxA = 1;
      } else if (perm.contains ("BC")) {
        idxB = 0; idxC = 1;
      } else if (perm.contains ("CB")) {
        idxC = 0; idxB = 1;
      } else if (perm.contains ("CA")) {
        idxC = 0; idxA = 1;
      } else if (perm.contains ("AC")) {
        idxA = 0; idxC = 1;
      }
    } else if (nphases == 3) {
      if (perm.contains ("ABC")) {
        idxA = 0; idxB = 1; idxC = 2;
      } else if (perm.contains ("ACB")) {
        idxA = 0; idxB = 2; idxC = 1;
      } else if (perm.contains ("BAC")) {
        idxA = 1; idxB = 0; idxC = 2;
      } else if (perm.contains ("BCA")) {
        idxA = 2; idxB = 0; idxC = 1;
      } else if (perm.contains ("CAB")) {
        idxA = 1; idxB = 2; idxC = 0;
      } else if (perm.contains ("CBA")) {
        idxA = 2; idxB = 1; idxC = 0;
      }
    }

    if (perm.contains("A")) {
      if (perm.contains ("B")) {
        buf.append ("  distance_AB " + df4.format(gFTperM * WireSeparation (idxA, idxB)) + ";\n");
      }
      if (perm.contains ("C")) {
        buf.append ("  distance_AC " + df4.format(gFTperM * WireSeparation (idxA, idxC)) + ";\n");
      }
      if (has_neutral) {
        buf.append ("  distance_AN " + df4.format(gFTperM * WireSeparation (idxA, idxN)) + ";\n");
      }
      buf.append ("  distance_AE " + df4.format(gFTperM * yarray[idxA]) + ";\n");
    }
    if (perm.contains ("B")) {
      if (perm.contains ("C")) {
        buf.append ("  distance_BC " + df4.format(gFTperM * WireSeparation (idxB, idxC)) + ";\n");
      }
      if (has_neutral) {
        buf.append ("  distance_BN " + df4.format(gFTperM * WireSeparation (idxB, idxN)) + ";\n");
      }
      buf.append ("  distance_BE " + df4.format(gFTperM * yarray[idxB]) + ";\n");
    }
    if (perm.contains ("C")) {
      if (has_neutral) {
        buf.append ("  distance_CN " + df4.format(gFTperM * WireSeparation (idxC, idxN)) + ";\n");
      }
      buf.append ("  distance_CE " + df4.format(gFTperM * yarray[idxC]) + ";\n");
    }
    if (has_neutral) {
      buf.append ("  distance_NE " + df4.format(gFTperM * yarray[idxN]) + ";\n");
    }
    buf.append("}\n");
  }

  public String GetGLM() {
    StringBuilder buf = new StringBuilder ("");
    for (String phs: perms) {
      AppendGLMPermutation(buf, phs);
    }

    return buf.toString();
  }

  public String GetDSS() {
    StringBuilder buf = new StringBuilder ("");
    for (String phs: perms) {
      AppendDSSPermutation(buf, phs);
    }

    return buf.toString();
  }

  public static String szCSVHeader = "Name,Ncond,Nphase,Units,Xvals,Yvals";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder ("");
    for (String phs: perms) {
      AppendCSVPermutation(buf, phs);
    }
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

