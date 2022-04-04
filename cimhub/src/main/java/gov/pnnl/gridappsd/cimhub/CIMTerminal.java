package gov.pnnl.gridappsd.cimhub;
//	----------------------------------------------------------
//	Copyright (c) 2022, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import java.text.DecimalFormat;

/** 
 Helper class to for bus names, phases, and voltage of Terminals
*/
public class CIMTerminal {
  static final DecimalFormat df3 = new DecimalFormat("#0.000");

  public final String id;
	public String bus;
	public String phases;
  public String eq;
	public double voltage;

	public CIMTerminal (String id, String bus, String phases, double voltage, String eq) {
		this.id = id;
		this.bus = bus;
		this.phases = phases;
    this.eq = eq;
		this.voltage = voltage;
	}

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (eq + ":" + id + ":" + bus + ":" + phases + ":" + df3.format (voltage));
    return buf.toString();
  }
}

