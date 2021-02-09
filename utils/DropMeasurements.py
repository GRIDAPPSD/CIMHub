from SPARQLWrapper import SPARQLWrapper2
import sys
import CIMHubConfig

if len(sys.argv) < 3:
	print ('usage: python DropMeasurements.py cimhubconfig.json feeder_id')
	print (' (Blazegraph server must already be started)')
	exit()

CIMHubConfig.ConfigFromJsonFile (sys.argv[1])
sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
sparql.method = 'POST'

qstr = CIMHubConfig.prefix + """DELETE {
  ?m a ?class.
  ?m c:IdentifiedObject.mRID ?uuid.
  ?m c:IdentifiedObject.name ?name.
  ?m c:Measurement.PowerSystemResource ?psr.
  ?m c:Measurement.Terminal ?trm.
  ?m c:Measurement.phases ?phases.
  ?m c:Measurement.measurementType ?type.
 } WHERE {
  VALUES ?fdrid {\"""" + sys.argv[2] + """\"}
  VALUES ?class {c:Analog c:Discrete}
  ?fdr c:IdentifiedObject.mRID ?fdrid. 
  ?eq c:Equipment.EquipmentContainer ?fdr.
  ?trm c:Terminal.ConductingEquipment ?eq.
  ?m a ?class.
  ?m c:IdentifiedObject.mRID ?uuid.
  ?m c:IdentifiedObject.name ?name.
  ?m c:Measurement.PowerSystemResource ?psr.
  ?m c:Measurement.Terminal ?trm.
  ?m c:Measurement.phases ?phases.
  ?m c:Measurement.measurementType ?type.
 }
"""

#print (qstr)
sparql.setQuery(qstr)
ret = sparql.query()
#print (ret.info)
print(ret.response.msg)