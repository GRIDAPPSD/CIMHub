package gov.pnnl.gridappsd.cimhub.components;
//  ----------------------------------------------------------
//  Copyright (c) 2017-2022, Battelle Memorial Institute
//  All rights reserved.
//  ----------------------------------------------------------

import java.io.*;
import java.util.HashMap;

public abstract class DistCable extends DistWire {
  public double dcore;
  public double djacket;
  public double dins;
  public double dscreen;
  public boolean sheathNeutral;
  public double dEpsR;

  protected void AppendCableDisplay (StringBuilder buf) {
    AppendWireDisplay (buf);
    buf.append (" dcore=" + df6.format(dcore) + " djacket=" + df6.format(djacket) + " dins=" + df6.format(dins)); 
    buf.append (" dscreen=" + df6.format(dscreen) + " sheathNeutral=" + Boolean.toString(sheathNeutral) + " EpsR=" + df3.format(dEpsR)); 
  }

  protected void AppendDSSCableAttributes (StringBuilder buf) {
    AppendDSSWireAttributes (buf);
    buf.append ("\n~ EpsR=" + df2.format(dEpsR) + " Ins=" + df6.format(insthick) +
                " DiaIns=" + df6.format(dins) + " DiaCable=" + df6.format(djacket));
  }

  public static String szCSVHeader = DistWire.szCSVHeader + ",InsMat,EpsRel,InsThick,DIACore,DIAJacket,DIAIns,DIAScreen,SheathNeutral";

  protected void AppendCSVCableAttributes (StringBuilder buf) {
    AppendCSVWireAttributes (buf);
    buf.append ("," + insmat + "," + df2.format(dEpsR) + "," + df6.format(insthick) +
        "," + df6.format(dcore) + "," + df6.format(djacket) + "," + df6.format(dins) + "," + df6.format(dscreen) +
        "," + Boolean.toString (sheathNeutral));
  }

  protected void AppendGLMCableAttributes (StringBuilder buf) {
    AppendGLMWireAttributes (buf);
    buf.append ("  conductor_gmr " + df6.format (gmr * gFTperM) + ";\n");
    buf.append ("  conductor_diameter " + df6.format (2.0 * rad * gFTperM * 12.0) + ";\n");
    buf.append ("  conductor_resistance " + df6.format (r50 * gMperMILE) + ";\n");
    buf.append ("  outer_diameter " + df6.format (djacket * gFTperM * 12.0) + ";\n");
    buf.append ("  insulation_relative_permitivitty " + df2.format (dEpsR) + ";\n");
  }
}

