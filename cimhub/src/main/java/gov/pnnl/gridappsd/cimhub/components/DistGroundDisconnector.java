package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistGroundDisconnector extends DistSwitch {
  public static final String szCIMClass = "GroundDisconnector";

  public DistGroundDisconnector (ResultSet results) {
    super (results);
  }

  public String CIMClass() {
    return szCIMClass;
  }
}

