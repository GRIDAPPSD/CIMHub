from SPARQLWrapper import SPARQLWrapper2#, JSON
import sys
import CIMHubConfig

if len(sys.argv) < 3:
	print ('usage: python3 DropHouses.py cimhubconfig.json feeder_id')
	print (' (Blazegraph server must already be started)')
	exit()

CIMHubConfig.ConfigFromJsonFile (sys.argv[1])
sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'

qstr = CIMHubConfig.prefix + """DELETE {
  ?h a ?class.
  ?h c:IdentifiedObject.mRID ?uuid.
  ?h c:IdentifiedObject.name ?name.
  ?h c:House.floorArea ?floorArea.
  ?h c:House.numberOfStories ?numberOfStories.
  ?h c:House.coolingSetpoint ?coolingSetpoint.
  ?h c:House.heatingSetpoint ?heatingSetpoint.
  ?h c:House.hvacPowerFactor ?hvacPowerFactor.
  ?h c:House.coolingSystem ?coolingSystemRaw.
  ?h c:House.heatingSystem ?heatingSystemRaw.
  ?h c:House.thermalIntegrity ?thermalIntegrityRaw.
  ?h c:House.EnergyConsumer ?econ.
 } WHERE {
  VALUES ?fdrid {\"""" + sys.argv[2] + """\"}
  VALUES ?class {c:House}
  ?fdr c:IdentifiedObject.mRID ?fdrid. 
  ?econ c:Equipment.EquipmentContainer ?fdr.
  ?h a ?class.
  ?h c:IdentifiedObject.mRID ?uuid.
  ?h c:IdentifiedObject.name ?name.
  ?h c:House.floorArea ?floorArea.
  ?h c:House.numberOfStories ?numberOfStories.
  OPTIONAL{?h c:House.coolingSetpoint ?coolingSetpoint.}
  OPTIONAL{?h c:House.heatingSetpoint ?heatingSetpoint.}
  OPTIONAL{?h c:House.hvacPowerFactor ?hvacPowerFactor.}
  ?h c:House.coolingSystem ?coolingSystemRaw.
  ?h c:House.heatingSystem ?heatingSystemRaw.
  ?h c:House.thermalIntegrity ?thermalIntegrityRaw.
  ?h c:House.EnergyConsumer ?econ.
 }
"""

#print (qstr)
sparql.setQuery(qstr)
ret = sparql.query()
#print (ret.info)
print(ret.response.msg)