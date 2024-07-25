from SPARQLWrapper import SPARQLWrapper2
import cimhub.CIMHubConfig as CIMHubConfig
import sys

def drop_measurements (mRID, cfg_file = None):
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
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
    VALUES ?fdrid {\"""" + mRID + """\"}
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

# run from command line for GridAPPS-D platform circuits
if __name__ == '__main__':
  cfg_file = sys.argv[1]
  mRID = sys.argv[2]
  drop_measurements (mRID, cfg_file)
