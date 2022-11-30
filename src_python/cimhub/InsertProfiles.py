from SPARQLWrapper import SPARQLWrapper2
import re
import uuid
import os.path
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import math

qload_template = """# list the loads by name, id and nominal power
SELECT ?name ?id ?p ?q WHERE {{
VALUES ?fdrid {{"{:s}"}}
 ?s r:type c:EnergyConsumer.
 ?fdr c:IdentifiedObject.mRID ?fdrid.
 ?s c:Equipment.EquipmentContainer ?fdr.
 ?s c:IdentifiedObject.mRID ?id.
 ?s c:IdentifiedObject.name ?name.
 ?s c:EnergyConsumer.p ?p.
 ?s c:EnergyConsumer.q ?q.
}}
ORDER BY ?name ?id
"""

creation_template = """
 <urn:uuid:{res}> a c:EnergyConnectionProfile.
 <urn:uuid:{res}> c:IdentifiedObject.mRID \"{res}\".
 <urn:uuid:{res}> c:IdentifiedObject.name \"{nm}\".
"""

attribute_template = """
 <urn:uuid:{res}> c:EnergyConnectionProfile.{attr} \"{value}\".
"""

link_template = """
 <urn:uuid:{res}> c:EnergyConnectionProfile.EnergyConnections <urn:uuid:{resLoad}>.
"""

def PostTriples (sparql, qtriples):  # TODO: batch
  print ('==> inserting', len(qtriples), 'instances for DER')
  qtriples.append ('}')
  qstr = CIMHubConfig.prefix + ' INSERT DATA { ' + ''.join(qtriples)
#  print (qstr)
  sparql.setQuery(qstr)
  ret = sparql.query()
#  print (ret)
  return

def GetCIMID (cls, nm, uuids):
  if nm is not None:
    key = cls + ':' + nm
    if key not in uuids:
      uuids[key] = str(uuid.uuid4()).upper()
    return uuids[key]
  return str(uuid.uuid4()).upper() # for unidentified CIM instances

def get_profile (profiles, load_name):
  for key, profile in profiles.items():
    if load_name in profile['loads']:
      return key
  return None

def insert_profiles (fname, cfg_file=None):
  if cfg_file is not None:
    CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'

  fdr_id = None
  loads = {}
  profiles = {}
  fuidname = None
  uuids = {}
  batch_size = 100
  qtriples = []

  fp = open (fname, 'r')
  lines = fp.readlines()
  for ln in lines:
    toks = re.split('[,\s]+', ln)
    if toks[0] == 'feederID':
      fdr_id = toks[1]
    elif toks[0] == 'uuid_file':
      fuidname = toks[1]
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
    elif not toks[0].startswith('//') and len(toks[0]) > 0:
      key = toks[0]
      profiles[key] = {}
      for tok in toks:
        if '=' in tok:
          if 'loads=' not in tok:
            words = tok.split('=')
            profiles[key][words[0]] = words[1]
          else:
            print (ln)
            profile_loads = ln.split('loads=')[1].strip().split(',')
            load_array = []
            for load_name in profile_loads:
              if len(load_name) > 0:
                load_array.append(load_name)
            profiles[key]['loads'] = load_array
  fp.close()
  print (profiles)

  qload = CIMHubConfig.prefix + qload_template.format(fdr_id)

  sparql.setQuery(qload)
  ret = sparql.query()
  for b in ret.bindings:
    key = b['name'].value
    eqid = b['id'].value
    kw = float(b['p'].value) / 1000.0
    kvar = float(b['q'].value) / 1000.0
    profile = get_profile(profiles, key)
    if profile is not None:
      loads[key] = {'id':eqid, 'kw':kw, 'kvar':kvar, 'profile':profile}
  print ('Retrieved', len(loads), 'loads from circuit model')
#  print (loads)

  # write the profiles
  for key, profile in profiles.items():
    res = GetCIMID ('EnergyConnectionProfile', key, uuids)
    triple = creation_template.format(res=res, nm=key)
    qtriples.append(triple)
    for attr, value in profile.items():
      if attr == 'loads':
        for load_name in value:
          resLoad = loads[load_name]['id']
          triple = link_template.format(res=res, resLoad=resLoad)
          qtriples.append(triple)
      else:
        triple = attribute_template.format(res=res, attr=attr, value=value)
        qtriples.append(triple)

  if len(qtriples) > 0:
    PostTriples (sparql, qtriples)
    qtriples = []

  if fuidname is not None:
    print ('saving identifiable instance mRIDs to', fuidname)
    fuid = open (fuidname, 'w')
    for key, val in uuids.items():
      print ('{:s},{:s}'.format (key.replace(':', ',', 1), val), file=fuid)
    fuid.close()

# run from command line for GridAPPS-D platform circuits
if __name__ == '__main__':
  cfg_file = sys.argv[1]
  fname = sys.argv[2]
  insert_profiles (fname, cfg_file)

