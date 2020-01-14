package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2018, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistJumper extends DistSwitch {
	public DistJumper (ResultSet results) {
		super (results);
	}

	public String CIMClass() {
		return "Jumper";
	}
}


