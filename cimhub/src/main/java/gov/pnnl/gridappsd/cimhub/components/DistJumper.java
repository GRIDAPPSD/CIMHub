package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistJumper extends DistSwitch {
  public static final String szCIMClass = "Jumper";

  public DistJumper (ResultSet results) {
    super (results);
  }

  public String CIMClass() {
    return szCIMClass;
  }
}


