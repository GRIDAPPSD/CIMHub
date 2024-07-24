package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;

public class DistLoad extends DistComponent {
  public static final String szCIMClass = "EnergyConsumer";

  public String id;
  public String name;
  public String bus;
  public String t1id;
  public String phases;
  public String conn;
  public double basev;
  public double p;
  public double q;
  public double pz;
  public double qz;
  public double pi;
  public double qi;
  public double pp;
  public double qp;
  public double pe;
  public double qe;
  public int cnt;

  private int dss_load_model;
  private boolean bDelta;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append (",\"phases\":\"" + phases +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistLoad (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?id").toString();
      name = PushExportName (soln.get("?name").toString(), id, szCIMClass);
      bus = GetBusExportName (soln.get("?bus").toString());
      t1id = soln.get("?t1id").toString();
      basev = Double.parseDouble (soln.get("?basev").toString());
      phases = OptionalString (soln, "?phases", "ABC");
      phases = phases.replace ('\n', ':');
      conn = soln.get("?conn").toString();
      p = 0.001 * Double.parseDouble (soln.get("?p").toString());
      q = 0.001 * Double.parseDouble (soln.get("?q").toString());
      pz = Double.parseDouble (soln.get("?pz").toString());
      qz = Double.parseDouble (soln.get("?qz").toString());
      pi = Double.parseDouble (soln.get("?pi").toString());
      qi = Double.parseDouble (soln.get("?qi").toString());
      pp = Double.parseDouble (soln.get("?pp").toString());
      qp = Double.parseDouble (soln.get("?qp").toString());
      pe = OptionalDouble (soln, "?pe", 0.0);
      qe = OptionalDouble (soln, "?qe", 0.0);
      cnt = OptionalInt (soln, "?cnt", 1);
    }   
    dss_load_model = 8;
//    System.out.println (DisplayString());
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + " @ " + bus + " basev=" + df4.format (basev) + " phases=" + phases + " conn=" + conn);
    buf.append (" kw=" + df4.format(p) + " kvar=" + df4.format(q));
    buf.append (" Real ZIP=" + df4.format(pz) + ":" + df4.format(pi) + ":" + df4.format(pp));
    buf.append (" Reactive ZIP=" + df4.format(qz) + ":" + df4.format(qi) + ":" + df4.format(qp));
    buf.append (" Exponents=" + df4.format(pe) + ":" + df4.format(qe));
    return buf.toString();
  }

  private void SetDSSLoadModel() {
    if (conn.equals("D")) {
      bDelta = true;
    } else {
      bDelta = false;
    }
		if (pe == 1 && qe == 2) {
			dss_load_model = 4;
			return;
		}
		double sum = pz + pi + pp;
		pz = pz / sum;
		pi = pi / sum;
		pp = pp / sum;
		sum = qz + qi + qp;
		qz = qz / sum;
		qi = qi / sum;
		qp = qp / sum;
		if (pz >= 0.999999 && qz >= 0.999999) {
			dss_load_model = 2;
		}	else if (pi >= 0.999999 && qi >= 0.999999) {
			dss_load_model = 5;
		} else if (pp >= 0.999999 && qp >= 0.999999) {
			dss_load_model = 1;
		} else {
			dss_load_model = 8;
		}
	}

	private String GetZIPV() {
		return "[" + df4.format(pz) + "," + df4.format(pi) + "," + df4.format(pp) + "," + df4.format(qz)
		 + "," + df4.format(qi) + "," + df4.format(qp) + ",0.8]";
	}

	public String GetDSS (DistEnergyConnectionProfile prf) {
		StringBuilder buf = new StringBuilder ("new Load." + name);

		SetDSSLoadModel();
		int nphases = DSSPhaseCount(phases, bDelta);
		double kv = 0.001 * basev;
		if (nphases < 2 && !bDelta) { 
      if (kv < 0.22) {
        kv /= Math.sqrt(3.0);
      } else if (kv < 0.26) {// TODO: this catches the 240-volt windings with center tap?
        kv /= 2.0;
      } else {
        kv /= Math.sqrt(3.0);
      }
    } else if (nphases == 2) { // for 240-V loads on open delta secondary service
      if (kv > 0.23 && kv < 0.26) {
        kv = 0.208;
      }
    }

		buf.append (" phases=" + Integer.toString(nphases) + " bus1=" + DSSShuntPhases (bus, phases, bDelta) + 
								" conn=" + DSSConn(bDelta) + " kw=" + df3.format(p) + " kvar=" + df3.format(q) +
								" numcust=1 kv=" + df3.format(kv) + " model=" + Integer.toString(dss_load_model));
		if (dss_load_model == 8) {
			buf.append (" zipv=" + GetZIPV());
		}
    if (prf != null) {
      if (prf.dssDaily.length() > 0) {
        buf.append (" daily=" + prf.dssDaily);
      }
      if (prf.dssDuty.length() > 0) {
        buf.append (" duty=" + prf.dssDuty);
      }
      if (prf.dssYearly.length() > 0) {
        buf.append (" yearly=" + prf.dssYearly);
      }
      if (prf.dssLoadGrowth.length() > 0) {
        buf.append (" growth=" + prf.dssLoadGrowth);
      }
      if (prf.dssLoadCvrCurve.length() > 0) {
        buf.append (" cvrcurve=" + prf.dssLoadCvrCurve);
      }
      if (prf.dssSpectrum.length() > 0) {
        buf.append (" spectrum=" + prf.dssSpectrum);
      }
    }
    buf.append("\n");

    return buf.toString();
  }

  public String GetKey() {
    return id;
  }

  public static String szCSVHeader = "Name,NumPhases,Bus,Phases,kV,Model,Connection,kW,pf,pz,pi,pp,qz,qi,qp,pe,qe";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + ",");
    SetDSSLoadModel();
    int nphases = DSSPhaseCount(phases, bDelta);
    double kv = 0.001 * basev;
    if (nphases < 2 && !bDelta) { // 2-phase wye load should be line-line for secondary?
      kv /= Math.sqrt(3.0);
    }
    double s = Math.sqrt(p*p + q*q);
    double pf = 1.0;
    if (s > 0.0) {
      pf = p / s;
    }
    if (q < 0.0) {
      pf *= -1.0;
    }
    buf.append (Integer.toString(nphases) + "," + bus + "," + CSVPhaseString (phases) + "," + df3.format(kv) + "," + 
          Integer.toString (dss_load_model) + "," + DSSConn(bDelta) + "," + df3.format(p) + "," + 
          df4.format(pf) + "," + df3.format(pz) + "," + df3.format(pi) + "," + df3.format(pp) + "," + 
          df3.format(qz) + "," + df3.format(qi) + "," + df3.format(qp) + "," + df3.format(pe) + "," + df3.format(qe) + "\n");
    return buf.toString();
  }
}

