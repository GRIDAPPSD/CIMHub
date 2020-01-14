package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistDisconnector extends DistSwitch {
	public DistDisconnector (ResultSet results) {
		super (results);
	}

	public String CIMClass() {
		return "Disconnector";
	}
}


