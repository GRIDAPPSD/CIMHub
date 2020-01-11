package gov.pnnl.gridappsd.cimhub;
// ----------------------------------------------------------
// Copyright (c) 2017-2020, Battelle Memorial Institute
// All rights reserved.
// ----------------------------------------------------------

import java.io.*;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;

import gov.pnnl.gridappsd.cimhub.CIMImporter;
import gov.pnnl.gridappsd.cimhub.components.DistComponent;
import gov.pnnl.gridappsd.cimhub.components.DistBaseVoltage;
import gov.pnnl.gridappsd.cimhub.components.DistCapacitor;
import gov.pnnl.gridappsd.cimhub.components.DistConcentricNeutralCable;
import gov.pnnl.gridappsd.cimhub.components.DistCoordinates;
import gov.pnnl.gridappsd.cimhub.components.DistFeeder;
import gov.pnnl.gridappsd.cimhub.components.DistLineSpacing;
import gov.pnnl.gridappsd.cimhub.components.DistLinesSpacingZ;
import gov.pnnl.gridappsd.cimhub.components.DistLoad;
import gov.pnnl.gridappsd.cimhub.components.DistOverheadWire;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeOCTest;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeRating;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrCodeSCTest;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrBank;
import gov.pnnl.gridappsd.cimhub.components.DistXfmrTank;

public class CIMQuerySetter extends Object {
	String obj = "";
	StringBuilder buf = new StringBuilder("");
	String delims = "[ ]+";

	private void updateQuery () {
		if ((buf.length() > 0) && (obj.length() > 0)) {
			System.out.println (obj + ":" + buf.toString());
			if (obj.equals("nsCIM")) {
				DistComponent.nsCIM = buf.toString();
			} else if (obj.equals("DistFeeder")) {
				DistFeeder.szQUERY = buf.toString();
			}
		}
		buf = new StringBuilder("");
	}

	private boolean wantThisLine (String ln) {
		if (ln.length() < 0) return false;
		if (ln.contains("PREFIX")) return false;
		if (ln.startsWith("#")) return false;
		return true;
	}

	private String getCharacterDataFromElement(Element e) {
    NodeList list = e.getChildNodes();
    String data;
    for(int index = 0; index < list.getLength(); index++){
      if(list.item(index) instanceof CharacterData){
        CharacterData child = (CharacterData) list.item(index);
        data = child.getData();
        if (data != null && data.trim().length() > 0) {
          return child.getData();
				}
      }
    }
    return "";
	}

	private String condenseQuery (String root) {
		String lines[] = root.split("\\r?\\n");
		buf = new StringBuilder("");
		for (String ln : lines) {
			if (wantThisLine (ln)) buf.append (ln);
		}
		return buf.toString();
	}

	public void setQueriesFromXMLFile (String fname) {
		System.out.println ("Reading queries from XML file " + fname);
		try {
			DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			DocumentBuilder db = dbf.newDocumentBuilder();
			Document doc = db.parse (new File (fname));
			Element elm = doc.getDocumentElement();

			NodeList namespaces = elm.getElementsByTagName ("nsCIM");
			for (int i = 0; i < namespaces.getLength(); i++) {
				Element nsElm = (Element) namespaces.item(i);
				String val = condenseQuery (getCharacterDataFromElement (nsElm));
				System.out.println ("nsCIM:" + val);
				DistComponent.nsCIM = val;
			}

			NodeList queries = elm.getElementsByTagName ("query");
			for (int i = 0; i < queries.getLength(); i++) {
				Element elmId = (Element) ((Element) queries.item(i)).getElementsByTagName("id").item(0);
				String id = getCharacterDataFromElement (elmId);
				Element elmVal = (Element) ((Element) queries.item(i)).getElementsByTagName("value").item(0);
				String val = condenseQuery (getCharacterDataFromElement (elmVal));
				boolean used = applyNewQuery (id, val);
				if (!used) {
					System.out.println(id + ":" + Boolean.toString(used));
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private boolean applyNewQuery (String id, String val) {
		if (id.equals ("DistBaseVoltage")) {
			DistBaseVoltage.szQUERY = val;
			return true;
		}
		if (id.equals ("DistCapacitor")) {
			DistCapacitor.szQUERY = val;
			return true;
		}
		if (id.equals ("DistConcentricNeutralCable")) {
			DistConcentricNeutralCable.szQUERY = val;
			return true;
		}
		if (id.equals ("DistCoordinates")) {
			DistCoordinates.szQUERY = val;
			return true;
		}
		if (id.equals ("DistFeeder")) {
			DistFeeder.szQUERY = val;
			return true;
		}
		if (id.equals ("DistLineSpacing")) {
			DistLineSpacing.szQUERY = val;
			return true;
		}
		if (id.equals ("DistLinesSpacingZ")) {
			DistLinesSpacingZ.szQUERY = val;
			return true;
		}
		if (id.equals ("DistLoad")) {
			DistLoad.szQUERY = val;
			return true;
		}
		if (id.equals ("DistOverheadWire")) {
			DistOverheadWire.szQUERY = val;
			return true;
		}
		if (id.equals ("DistXfmrBank")) {
			DistXfmrBank.szQUERY = val;
			return true;
		}
		if (id.equals ("CountTanksInBank")) {
			DistXfmrBank.szCountQUERY = val;
			return true;
		}
		if (id.equals ("DistXfmrCodeRating")) {
			DistXfmrCodeRating.szQUERY = val;
			return true;
		}
		if (id.equals ("DistXfmrCodeOCTest")) {
			DistXfmrCodeOCTest.szQUERY = val;
			return true;
		}
		if (id.equals ("DistXfmrCodeSCTest")) {
			DistXfmrCodeSCTest.szQUERY = val;
			return true;
		}
		if (id.equals ("CountShortCircuitTests")) {
			DistXfmrCodeSCTest.szCountQUERY = val;
			return true;
		}
		if (id.equals ("DistXfmrTank")) {
			DistXfmrTank.szQUERY = val;
			return true;
		}
		if (id.equals ("CountTankEnds")) {
			DistXfmrTank.szCountQUERY = val;
			return true;
		}
		return false;
	}

	public void setQueriesFromTextFile (String fname) {
		String ln;
		boolean inQuery = false;

		System.out.println ("Reading queries from text file " + fname);

		try {
			BufferedReader br = new BufferedReader(new FileReader(fname));
			while ((ln = br.readLine()) != null) {
				if (ln.contains ("#@")) {
					if (inQuery) {
						updateQuery();
					} else {
						obj = ln.split (delims)[1];
					}
					inQuery = !inQuery;
				} else if (inQuery) {
					if (wantThisLine (ln)) {
						buf.append(ln);
					}
				}
			}
			updateQuery();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}

