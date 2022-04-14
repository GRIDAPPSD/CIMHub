package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2018-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistMeasurement extends DistComponent {
  public String id;
  public String eqid;
  public String trmid;
  public String name;
  public String bus;
  public String measType;
  public String measClass;
  public String phases;
  public String eqname;
  public String eqtype;
  public String simobj;
  public boolean useHouses;

  public DistMeasurement (ResultSet results, boolean useHouses) {
    if (results.hasNext()) {
      QuerySolution soln = results.next();
      name = SafeName (soln.get("?name").toString());
      eqname = SafeName (soln.get("?eqname").toString());
      eqtype = SafeName (soln.get("?eqtype").toString());
      measType = SafeName (soln.get("?type").toString());
      measClass = SafeName (soln.get("?class").toString());
      id = soln.get("?id").toString();
      eqid = soln.get("?eqid").toString();
      trmid = soln.get("?trmid").toString();
      bus = SafeName (soln.get("?bus").toString());
      phases = OptionalString (soln, "?phases", "ABC");
    }
    this.useHouses = useHouses;
//    System.out.println (DisplayString());
  }

  public String GetGldLoadName () {
    if (eqtype.equals("EnergyConsumer")) {
      if (phases.contains ("s")) {
        return "ld_" + bus + "_240v";
      }
    }
    return bus;
  }

  public void FindSimObject (String loadname, String busphases, boolean bStorage, boolean bSolar, boolean bSyncMachines) {
    if (eqtype.equals ("LinearShuntCompensator")) {
      simobj = "cap_" + eqname;
    } else if (eqtype.equals ("PowerElectronicsConnection")) {
      if (bStorage) {
        if (measType.equals ("SoC")) {
          simobj = "bat_" + eqname;
        } else {
          simobj = bus + "_stmtr";
        }
      } else if (bSolar) {
        simobj = bus + "_pvmtr";
      } else {
        simobj = "UKNOWN INVERTER";
      }
    } else if (eqtype.equals("ACLineSegment")) {
      if (phases.contains("s")) {
        simobj = "tpx_" + eqname;
      } else {
        simobj = "line_" + eqname;
      }
    } else if (eqtype.equals ("PowerTransformer")) { // RatioTapChanger or PowerTransformer
      if (measClass.equals("Discrete")) {
        simobj = "reg_" + eqname;
      } else {
        simobj = "xf_" + eqname;
      }
    } else if (eqtype.equals("LoadBreakSwitch")) {
      simobj = "swt_" + eqname;
    } else if (eqtype.equals ("Recloser")) {
      simobj = "swt_" + eqname;
    } else if (eqtype.equals ("Breaker")) {
      simobj = "swt_" + eqname;
    } else if (eqtype.equals ("SynchronousMachine")) {
      simobj = bus + "_dgmtr";
    } else if (eqtype.equals ("EnergyConsumer")) {
      simobj = loadname;
    } else {
      simobj = "UKNOWN";
    }
  }

  public boolean LinkedToSimulatorObject () {
    if (simobj != null) {
      if (!simobj.contains ("UKNOWN")) {
        return true;
      }
    }
    return false;
  }

  public String GetJSONEntry () {
    StringBuilder buf = new StringBuilder ();

    buf.append ("{\"name\":\"" + name +"\"");
    buf.append (",\"mRID\":\"" + id +"\"");
    buf.append (",\"ConductingEquipment_mRID\":\"" + eqid +"\"");
    buf.append (",\"Terminal_mRID\":\"" + trmid +"\"");
    buf.append (",\"measurementType\":\"" + measType + "\"");
    buf.append (",\"phases\":\"" + phases + "\"");
    buf.append (",\"MeasurementClass\":\"" + measClass + "\"");
    buf.append (",\"ConductingEquipment_type\":\"" + eqtype + "\"");
    buf.append (",\"ConductingEquipment_name\":\"" + eqname + "\"");
    buf.append (",\"ConnectivityNode\":\"" + bus + "\"");
    if (useHouses && eqtype.equals ("EnergyConsumer")) {
      buf.append (",\"SimObject\":\"" + simobj + "_ldmtr\"");
    } else {
      buf.append (",\"SimObject\":\"" + simobj + "\"");
    }
    buf.append ("}");
    return buf.toString();
  }

  public String DisplayString() {
    StringBuilder buf = new StringBuilder ("");
    buf.append (name + ":" + id + ":" + eqid + ":" + trmid + ":" + measType + ":" + phases
                 + ":" + measClass + ":" + eqtype + ":" + eqname + ":" + bus + ":" + useHouses);
    return buf.toString();
  }

  public String GetKey() {
    return id;
  }
}

