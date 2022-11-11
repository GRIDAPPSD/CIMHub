package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistBreaker extends DistSwitch {
  public static final String szCIMClass = "Breaker";

  public DistBreaker (ResultSet results) {
    super (results);
  }

  public String CIMClass() {
    return szCIMClass;
  }

  public String GetDSS () {
    StringBuilder buf = new StringBuilder (super.GetDSS());

    buf.append ("  new Relay." + name + " MonitoredObj=Line." + name +
                " Type=Current Delay=0.1 PhaseTrip=20000.0 GroundTrip=10000.0");
    if (open) {
      buf.append (" state=open\n");
    } else {
      buf.append (" state=closed\n");
    }
    return buf.toString();
  }
}


