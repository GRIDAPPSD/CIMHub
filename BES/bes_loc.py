import re
import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import networkx as nx
import json
import os
import uuid

CASES = [
  {'id': '1783D2A8-1204-4781-A0B4-7A73A2FA6038', 'name': 'IEEE118'},
  {'id': '2540AF5C-4F83-4C0F-9577-DEE8CC73BBB3', 'name': 'WECC240'},
]

ins_pt_template = """
 <urn:uuid:{res}> a c:PositionPoint.
 <urn:uuid:{res}> c:PositionPoint.Location <urn:uuid:{resLoc}>.
 <urn:uuid:{res}> c:PositionPoint.sequenceNumber \"{seq}\".
 <urn:uuid:{res}> c:PositionPoint.xPosition \"{x}\".
 <urn:uuid:{res}> c:PositionPoint.yPosition \"{y}\".
"""

ins_loc_template = """
 <urn:uuid:{res}> a c:Location.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
 <urn:uuid:{res}> c:Location.CoordinateSystem <urn:uuid:{resCrs}>.
"""

prefix = """<?xml version="1.0" encoding="utf-8"?>
<!-- un-comment this line to enable validation
-->
<rdf:RDF xmlns:cim="http://iec.ch/TC57/CIM100#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<!--
-->"""

suffix = """</rdf:RDF>"""

crs_template = """<cim:CoordinateSystem rdf:about="urn:uuid:{res}">
  <cim:IdentifiedObject.mRID>{res}</cim:IdentifiedObject.mRID>
  <cim:IdentifiedObject.name>{nm}_CrsUrn</cim:IdentifiedObject.name>
  <cim:CoordinateSystem.crsUrn>{nm}_BusCoordinates</cim:CoordinateSystem.crsUrn>
</cim:CoordinateSystem>"""

loc_template = """<cim:Location rdf:about="urn:uuid:{res}">
  <cim:IdentifiedObject.mRID>{res}</cim:IdentifiedObject.mRID>
  <cim:IdentifiedObject.name>{typ}_{nm}_Loc</cim:IdentifiedObject.name>
  <cim:Location.CoordinateSystem rdf:resource="urn:uuid:{crs}"/>
</cim:Location>"""

xy_template = """<cim:PositionPoint rdf:about="urn:uuid:{res}">
  <cim:PositionPoint.Location rdf:resource="urn:uuid:{locId}"/>
  <cim:PositionPoint.sequenceNumber>{seq}</cim:PositionPoint.sequenceNumber>
  <cim:PositionPoint.xPosition>{x}</cim:PositionPoint.xPosition>
  <cim:PositionPoint.yPosition>{y}</cim:PositionPoint.yPosition>
</cim:PositionPoint>"""

psr_template = """<cim:{cls} rdf:about="urn:uuid:{res}">
  <cim:PowerSystemResource.Location rdf:resource="urn:uuid:{locId}"/>
</cim:{cls}>"""

def load_bus_coordinates (fname):
  lp = open (fname).read()
  mdl = json.loads(lp)
  G = nx.readwrite.json_graph.node_link_graph(mdl)
  xy = {}
  for n, data in G.nodes(data=True):
    ndata = data['ndata']
    if ('x' in ndata) and ('y' in ndata):
      xy[n] = [float(ndata['x']), float(ndata['y'])]
  return xy

def get_cim_id (cls, nm, uuids):
  if nm is not None:
    key = cls + ':' + nm
    if key not in uuids:
      uuids[key] = str(uuid.uuid4()).upper()
    return uuids[key]
  return str(uuid.uuid4()).upper() # for unidentified CIM instances

def get_loc_id (cls, base, uuids):
  nm = '{:s}_{:s}_Loc'.format (cls, base)
  return get_cim_id ('Location', nm, uuids)

if __name__ == '__main__':
  CIMHubConfig.ConfigFromJsonFile ('cimhubconfig.json')
  case_id = 0
  if len(sys.argv) > 1:
    case_id = int(sys.argv[1])
  sys_id = CASES[case_id]['id']
  sys_name = CASES[case_id]['name']

  uuids = {}
  fuidname = '{:s}_Loc_mRID.dat'.format(sys_name)
  if os.path.exists(fuidname):
    print ('reading identifiable instance mRIDs from', fuidname)
    fuid = open (fuidname, 'r')
    for uuid_ln in fuid.readlines():
      uuid_toks = re.split('[,\s]+', uuid_ln)
      if len(uuid_toks) > 2 and not uuid_toks[0].startswith('//'):
        cls = uuid_toks[0]
        nm = uuid_toks[1]
        key = cls + ':' + nm
        val = uuid_toks[2]
        uuids[key] = val
    fuid.close()

  d = cimhub.load_bes_dict ('qbes.xml', sys_id, bTime=False)
  cimhub.summarize_bes_dict (d)
  cimhub.list_dict_table (d, 'BESContainer')

  busxy = load_bus_coordinates ('{:s}_Network.json'.format(sys_name))

  fp = open ('{:s}_CIM_Loc.xml'.format(sys_name), 'w')
  print (prefix, file=fp)
  crsId = get_cim_id('CoordinateSystem', sys_name + '_CrsUrn', uuids)
  print (crs_template.format(nm=sys_name, res=crsId), file=fp)

  # accumulate the transformer windings into transformers
  xfmrs = {}
  for key, data in d['BESPowerXfmrWinding']['vals'].items():
    toks = key.split(':')
    pname = toks[0]
    enum = toks[1]
    if pname not in xfmrs:
      xfmrs[pname] = {'nseq': 1, 'xys': [busxy[data['bus']]], 'pid': data['pid']}
    else:
      xfmrs[pname]['xys'].append (busxy[data['bus']])
      xfmrs[pname]['nseq'] += 1
  for key, data in xfmrs.items():
    locId = get_loc_id('Xfmr', key, uuids)
    print (psr_template.format(cls='PowerTransformer', res=data['pid'], locId=locId), file=fp)
    print (loc_template.format(typ='Xfmr', res=locId, crs=crsId, nm=key), file=fp)
    for seq in range(1, data['nseq']+1):
      xy = data['xys'][seq-1]
      print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=seq, x=xy[0], y=xy[1]), file=fp)
    
  # generating sources with an EnergyConnection and GeneratingUnit
  for key, data in d['BESMachine']['vals'].items():
    locId = get_loc_id(data['type'], key, uuids)
    print (psr_template.format(cls='{:s}GeneratingUnit'.format(data['type']), res=data['uid'], locId=locId), file=fp)
    print (psr_template.format(cls='SynchronousMachine', res=data['id'], locId=locId), file=fp)
    print (loc_template.format(typ=data['type'], res=locId, crs=crsId, nm=key), file=fp)
    xy = busxy[data['bus']]
    print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=1, x=xy[0], y=xy[1]), file=fp)
  for key, data in d['BESSolar']['vals'].items():
    locId = get_loc_id('Solar', key, uuids)
    print (psr_template.format(cls='PhotovoltaicUnit', res=data['id'], locId=locId), file=fp)
    print (psr_template.format(cls='PowerElectronicsConnection', res=data['pecid'], locId=locId), file=fp)
    print (loc_template.format(typ='Solar', res=locId, crs=crsId, nm=key), file=fp)
    xy = busxy[data['bus']]
    print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=1, x=xy[0], y=xy[1]), file=fp)
  for key, data in d['BESWind']['vals'].items():
    locId = get_loc_id('Wind', key, uuids)
    print (psr_template.format(cls='WindGeneratingUnit', res=data['id'], locId=locId), file=fp)
    print (psr_template.format(cls='PowerElectronicsConnection', res=data['pecid'], locId=locId), file=fp)
    print (loc_template.format(typ='Wind', res=locId, crs=crsId, nm=key), file=fp)
    xy = busxy[data['bus']]
    print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=1, x=xy[0], y=xy[1]), file=fp)

  # single-terminal components
  for key, data in d['BESCompShunt']['vals'].items():
    locId = get_loc_id('Shunt', key, uuids)
    print (psr_template.format(cls='LinearShuntCompensator', res=data['id'], locId=locId), file=fp)
    print (loc_template.format(typ='Shunt', res=locId, crs=crsId, nm=key), file=fp)
    xy = busxy[data['bus']]
    print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=1, x=xy[0], y=xy[1]), file=fp)
  for key, data in d['BESLoad']['vals'].items():
    locId = get_loc_id('Load', key, uuids)
    print (psr_template.format(cls='EnergyConsumer', res=data['id'], locId=locId), file=fp)
    print (loc_template.format(typ='Load', res=locId, crs=crsId, nm=key), file=fp)
    xy = busxy[data['bus']]
    print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=1, x=xy[0], y=xy[1]), file=fp)

  # two-terminal components
  for key, data in d['BESCompSeries']['vals'].items():
    locId = get_loc_id('Series', key, uuids)
    print (psr_template.format(cls='SeriesCompensator', res=data['id'], locId=locId), file=fp)
    print (loc_template.format(typ='Series', res=locId, crs=crsId, nm=key), file=fp)
    for seq in range(1, 3):
      xy = busxy[data['bus{:d}'.format(seq)]]
      print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=seq, x=xy[0], y=xy[1]), file=fp)
  for key, data in d['BESLine']['vals'].items():
    locId = get_loc_id('Line', key, uuids)
    print (psr_template.format(cls='ACLineSegment', res=data['id'], locId=locId), file=fp)
    print (loc_template.format(typ='Line', res=locId, crs=crsId, nm=key), file=fp)
    for seq in range(1, 3):
      xy = busxy[data['bus{:d}'.format(seq)]]
      print (xy_template.format(res=get_cim_id('PositionPoint', None, uuids), locId=locId, seq=seq, x=xy[0], y=xy[1]), file=fp)

  print (suffix, file=fp)
  fp.close()

  print ('saving identifiable instance mRIDs to', fuidname)
  fuid = open (fuidname, 'w')
  for key, val in uuids.items():
    print ('{:s},{:s}'.format (key.replace(':', ',', 1), val), file=fuid)
  fuid.close()

