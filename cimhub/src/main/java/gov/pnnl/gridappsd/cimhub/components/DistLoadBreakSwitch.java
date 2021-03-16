package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistLoadBreakSwitch extends DistSwitch {
	public static final String szCIMClass = "LoadBreakSwitch";

	public DistLoadBreakSwitch (ResultSet results) {
		super (results);
	}

	public String CIMClass() {
		return szCIMClass;
	}
}

