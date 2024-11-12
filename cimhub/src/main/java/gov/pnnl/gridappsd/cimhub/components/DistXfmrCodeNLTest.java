package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;

public class DistXfmrCodeNLTest extends DistComponent {
  public static final String szCIMClass = "NoLoadTest";

  public String id;
  public double nll;
  public double iexc;
  public double sbase;

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"id\":\"" + id +"\"");
    buf.append ("}");
    return buf.toString();
  }

  public DistXfmrCodeNLTest (ResultSet results) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      id = soln.get("?tid").toString();
      nll = Double.parseDouble (soln.get("?nll").toString());
      iexc = Double.parseDouble (soln.get("?iexc").toString());
      sbase = Double.parseDouble (soln.get("?base").toString());
    }   
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (id + " NLL=" + df4.format(nll) + " iexc=" + df4.format(iexc) + " base=" + df4.format(sbase));
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

