from SPARQLWrapper import SPARQLWrapper2
import re
import uuid
import os.path
import cimhub.CIMHubConfig as CIMHubConfig
import sys
import math

cfg_file = 'cimhubjar.json'

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
ORDER BY ?bus ?tid
"""

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

def insert_profile (fname):
  fdr_id = None # 'CBE09B55-091B-4BB0-95DA-392237B12640'
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

  CIMHubConfig.ConfigFromJsonFile (cfg_file)
  sparql = SPARQLWrapper2(CIMHubConfig.blazegraph_url)
  sparql.method = 'POST'
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
  print (loads)

  # write the profiles
  for key, profile in profiles.items():
    uuidProfile = GetCIMID ('EnergyConnectionProfile', key, uuids)

  # add profiles to loads
  if fuidname is not None:
    print ('saving identifiable instance mRIDs to', fuidname)
    fuid = open (fuidname, 'w')
    for key, val in uuids.items():
      print ('{:s},{:s}'.format (key.replace(':', ',', 1), val), file=fuid)
    fuid.close()

if __name__ == '__main__':
#  cfg_file = sys.argv[1]
#  fname = sys.argv[2]
  fname = 'oedi_profiles.dat'
  insert_profile (fname)

