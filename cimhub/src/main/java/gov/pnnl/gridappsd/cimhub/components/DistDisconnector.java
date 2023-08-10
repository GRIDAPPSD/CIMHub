package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistDisconnector extends DistSwitch {
  public static final String szCIMClass = "Disconnector";

  public DistDisconnector (ResultSet results) {
    super (results);
  }

  public String CIMClass() {
    return szCIMClass;
  }
}


