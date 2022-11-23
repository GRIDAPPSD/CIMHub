import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig

cfg_json = '../queries/cimhubconfig.json'
CIMHubConfig.ConfigFromJsonFile (cfg_json)
xml_file = '../queries/q100.xml'

dict = cimhub.load_feeder_dict (xml_file, fid=None, bTime=False)
cimhub.summarize_feeder_dict (dict)

tables = ['DistFuse', 'DistBreaker', 'DistLoadBreakSwitch', 'DistRecloser', 'DistCapacitor', 'DistSubstation',
          'DistOverheadWire', 'DistStorage', 'DistSolar', 'DistRegulatorBanked', 'DistRegulatorTanked',
          'DistXfmrCodeNLTest', 'DistXfmrCodeSCTest', 'DistLoad', 'DistBaseVoltage', 'DistLineSpacing',
          'DistPhaseMatrix', 'DistLinesCodeZ', 'DistLinesSpacingZ', 'DistXfmrTank', 'DistXfmrCodeRating']
tables.sort()

for tbl in tables: #['DistCoordinates', 'DistBreaker', 'DistLoadBreakSwitch', 'DistRecloser', 'DistLoad', 'DistXfmrBank']:
  cimhub.list_dict_table (dict, tbl)

