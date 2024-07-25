package gov.pnnl.gridappsd.cimhub.queryhandler.impl;

import java.io.File;

import org.apache.jena.query.ResultSet;
import org.apache.jena.query.ResultSetCloseable;

import gov.pnnl.gridappsd.cimhub.queryhandler.QueryHandler;

public class InternalBlazegraphQueryHandler implements QueryHandler{
  
  public InternalBlazegraphQueryHandler(){
    File ieee8500 = new File("ieee13.xml");
    
    try {
    } catch (Exception e) {
      e.printStackTrace();
    } 
  }

  @Override
  public ResultSetCloseable query(String szQuery, String szTag) {
    return null;
  }
  public ResultSet construct(String szQuery) {
    return null;
  }
  public boolean addFeederSelection (String mRID) {
    return false;
  }
  public boolean clearFeederSelections () {
    return false;
  }
  public String getFeederSelection () {
    return "";
  }
}
