from SPARQLWrapper import SPARQLWrapper2#, JSON
import cimhub.CIMHubConfig as CIMHubConfig
import sys

def drop_profiles (cfg_file, mRID):
  CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'

  qstr = CIMHubConfig.prefix + """DELETE {
    ?p a ?class.
    ?p c:IdentifiedObject.mRID ?uuid.
    ?p c:IdentifiedObject.name ?name.
    ?p c:EnergyConnectionProfile.EnergyConsumer ?econ.
    ?p c:EnergyConnectionProfile.dssDaily ?dssDaily.
    ?p c:EnergyConnectionProfile.dssDuty ?dssDuty.
    ?p c:EnergyConnectionProfile.dssYearly ?dssYearly.
    ?p c:EnergyConnectionProfile.dssSpectrum ?dssSpectrum.
    ?p c:EnergyConnectionProfile.dssLoadCvrCurve ?dssLoadCvrCurve.
    ?p c:EnergyConnectionProfile.dssLoadGrowth ?dssLoadGrowth.
    ?p c:EnergyConnectionProfile.dssPVTDaily ?dssPVTDaily.
    ?p c:EnergyConnectionProfile.dssPVTDuty ?dssPVTDuty.
    ?p c:EnergyConnectionProfile.dssPVTYearly ?dssPVTYearly.
    ?p c:EnergyConnectionProfile.gldPlayer ?gldPlayer.
    ?p c:EnergyConnectionProfile.gldSchedule ?gldSchedule.
    ?p c:EnergyConnectionProfile.gldWeather ?gldWeather.
   } WHERE {
    VALUES ?fdrid {\"""" + mRID + """\"}
    VALUES ?class {c:EnergyConnectionProfile}
    ?fdr c:IdentifiedObject.mRID ?fdrid. 
    ?econ c:Equipment.EquipmentContainer ?fdr.
    ?p a ?class.
    ?p c:IdentifiedObject.mRID ?uuid.
    ?p c:IdentifiedObject.name ?name.
    ?p c:EnergyConnectionProfile.EnergyConsumer ?econ.
    OPTIONAL{?p c:EnergyConnectionProfile.dssDaily ?dssDaily.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssDuty ?dssDuty.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssYearly ?dssYearly.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssSpectrum ?dssSpectrum.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssLoadCvrCurve ?dssLoadCvrCurve.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssLoadGrowth ?dssLoadGrowth.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssPVTDaily ?dssPVTDaily.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssPVTDuty ?dssPVTDuty.}
    OPTIONAL{?p c:EnergyConnectionProfile.dssPVTYearly ?dssPVTYearly.}
    OPTIONAL{?p c:EnergyConnectionProfile.gldPlayer ?gldPlayer.}
    OPTIONAL{?p c:EnergyConnectionProfile.gldSchedule ?gldSchedule.}
    OPTIONAL{?p c:EnergyConnectionProfile.gldWeather ?gldWeather.}
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
  drop_profiles (cfg_file, mRID)
