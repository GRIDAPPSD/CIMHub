from SPARQLWrapper import SPARQLWrapper2#, JSON
import cimhub.CIMHubConfig as CIMHubConfig
import sys

def drop_houses (mRID, cfg_file=None):
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
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
    VALUES ?fdrid {\"""" + mRID + """\"}
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

# run from command line for GridAPPS-D platform circuits
if __name__ == '__main__':
  cfg_file = sys.argv[1]
  mRID = sys.argv[2]
  drop_houses (mRID, cfg_file)
