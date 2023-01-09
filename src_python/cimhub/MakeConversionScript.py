import sys
import os

def append_cases(casefiles, dsspath, outpath, region, subregion, fp):
    for c in casefiles:
        print('//', file=fp)
        print('cd', dsspath, file=fp)
        print('redirect', c[0] + '.dss', file=fp)
        print('set maxiterations=20', file=fp)
        print('solve', file=fp)
        print('cd', outpath, file=fp)
        print('export summary', c[1] + '.csv', file=fp)
        print('export cdpsmcombined', 'file=' + c[1] + '.xml', 'geo=' + region, 'subgeo=' + subregion,
							'fid='+c[2], 'sid='+c[3], 'sgrid='+c[4], 'rgnid='+c[5], file=fp)

#casefiles = [['IEEE13_CDPSM', 'IEEE13'],
#             ['IEEE13_Assets', 'IEEE13_Assets']]
#append_cases(casefiles, cimpath, outpath, 'ieee', 'test', fp)

#casefiles = [['./8500-Node/Master', 'IEEE8500'],
#            ['./34Bus/ieee34Mod2', 'IEEE34'],
#            ['./37Bus/ieee37', 'IEEE37'],
#            ['./123Bus/IEEE123Master', 'IEEE123'],
#            ['./4Bus-DY-Bal/4Bus-DY-Bal', 'DY-bal'],
#            ['./4Bus-GrdYD-Bal/4Bus-GrdYD-Bal', 'GYD-bal'],
#            ['./4Bus-OYOD-Bal/4Bus-OYOD-Bal', 'OYOD-bal'],
#            ['./4Bus-OYOD-UnBal/4Bus-OYOD-UnBal', 'OYOD-unbal'],
#            ['./4Bus-YD-Bal/4Bus-YD-Bal', 'YD-bal'],
#            ['./4Bus-YY-Bal/4Bus-YY-Bal', 'YY-bal'],
#            ['./8500-Node/Master-unbal', 'IEEE8500u']]
#casefiles = [['./8500-Node/Master', 'IEEE8500'],
#            ['./123Bus/IEEE123Master', 'IEEE123']]
#append_cases(casefiles, ieeepath, outpath, 'ieee', 'large',  fp)

#casefiles = [['./ckt5/Master_ckt5', 'EPRI5'],
#             ['./ckt7/Master_ckt7', 'EPRI7'],
#             ['./ckt24/master_ckt24', 'EPRI24']]
#append_cases(casefiles, epripath, outpath, 'epri', 'large', fp)
#
#casefiles = [['./new_GC_12_47_1/Master', 'GC_12_47_1'],
#             ['./new_R1_12_47_1/Master', 'R1_12_47_1'],
#             ['./new_R1_12_47_2/Master', 'R1_12_47_2'],
#             ['./new_R1_12_47_3/Master', 'R1_12_47_3'],
#             ['./new_R1_12_47_4/Master', 'R1_12_47_4'],
#             ['./new_R1_25_00_1/Master', 'R1_25_00_1'],
#             ['./new_R2_12_47_1/Master', 'R2_12_47_1'],
#             ['./new_R2_12_47_2/Master', 'R2_12_47_2'],
#             ['./new_R2_12_47_3/Master', 'R2_12_47_3'],
#             ['./new_R2_25_00_1/Master', 'R2_25_00_1'],
#             ['./new_R2_35_00_1/Master', 'R2_35_00_1'],
#             ['./new_R3_12_47_1/Master', 'R3_12_47_1'],
#             ['./new_R3_12_47_2/Master', 'R3_12_47_2'],
#             ['./new_R3_12_47_3/Master', 'R3_12_47_3'],
#             ['./new_R4_12_47_1/Master', 'R4_12_47_1'],
#             ['./new_R4_12_47_2/Master', 'R4_12_47_2'],
#             ['./new_R4_25_00_1/Master', 'R4_25_00_1'],
#             ['./new_R5_12_47_1/Master', 'R5_12_47_1'],
#             ['./new_R5_12_47_2/Master', 'R5_12_47_2'],
#             ['./new_R5_12_47_3/Master', 'R5_12_47_3'],
#             ['./new_R5_12_47_4/Master', 'R5_12_47_4'],
#             ['./new_R5_12_47_5/Master', 'R5_12_47_5'],
#             ['./new_R5_25_00_1/Master', 'R5_25_00_1'],
#             ['./new_R5_35_00_1/Master', 'R5_35_00_1']]
# input_name, output_name, fid, sid, sgrid, rgnid

def make_dss2xml_script (cases, outfile):
  fp = open (outfile, 'w')
  for row in cases:
    bControls = False
    if 'dss_controls' in row:
      if row['dss_controls'] == True:
        bControls = True
    if 'dss_tolerance' in row:
      tol = float(row['dss_tolerance'])
    else:
      tol = 1e-8
    root = row['root']
    inpath = os.path.abspath(row['inpath_dss'])
    outpath = os.path.abspath(row['path_xml'])
    if not os.path.exists(outpath):
      os.mkdir(outpath)
    print('//', file=fp)
    print('cd', inpath, file=fp)
    print('redirect', row['dssname'], file=fp)
    print('set maxiterations=80', file=fp)
    print('set tolerance={:g}'.format(tol), file=fp)
    if bControls:
      print('set controlmode=static', file=fp)
      print('set maxcontroliter=200', file=fp)
    else:
      print('set controlmode=off', file=fp)
    print('solve mode=snap', file=fp)
    print('cd', outpath, file=fp)
    print('uuids file={:s}_uuids.dat'.format (root.lower()), file=fp)
    print('export summary  ', root + '_s.csv', file=fp)
    print('export voltages ', root + '_v.csv', file=fp)
    print('export currents ', root + '_i.csv', file=fp)
    print('export taps     ', root + '_t.csv', file=fp)
    print('export nodeorder', root + '_n.csv', file=fp)
    suffix = ''
    if ('substation' in row) and (len(row['substation']) > 0):
      suffix += ' substation={:s}'.format(row['substation'])
    if ('region' in row) and (len(row['region']) > 0):
      suffix += ' geo={:s}'.format(row['region'])
    if ('subregion' in row) and (len(row['subregion']) > 0):
      suffix += ' subgeo={:s}'.format(row['subregion'])
    if ('substationID' in row) and (len(row['substationID']) > 0):
      suffix += ' sid={:s}'.format(row['substationID'])
    if ('regionID' in row) and (len(row['regionID']) > 0):
      suffix += ' rgnid={:s}'.format(row['regionID'])
    if ('subregionID' in row) and (len(row['subregionID']) > 0):
      suffix += ' sgrid={:s}'.format(row['subregionID'])
    print('export cim100 fid={:s}'.format (row['mRID']), 'file=' + root + '.xml', suffix, file=fp)
    print('// export cim100fragments fid={:s}'.format (row['mRID']), 'file=' + root, suffix, file=fp)
    print('export uuids {:s}_uuids.dat'.format (root.lower()), file=fp)
  fp.close()

if __name__ == '__main__':
  casefiles = [['./new_R2_12_47_2/Master', 'R2_12_47_2', '9CE150A8-8CC5-A0F9-B67E-BBD8C79D3095', '933D85C1-BE1C-4C05-D4DD-4B41D941C52C', '656EE259-23FF-086E-1DC0-39CB9DC60A20', '79C9D814-3CE0-DC11-534D-BDA1AF949810']]
  fp = open ('ConvertCDPSM.dss', 'w')

  if sys.platform == 'win32':
      outpath = 'c:/gridapps-d/powergrid-models/blazegraph/test/'
      cimpath = 'c:/OpenDSS/Test/'
      ieeepath = 'c:/OpenDSS/Distrib/IEEETestCases/'
      epripath = 'c:/OpenDSS/Distrib/EPRITestCircuits/'
      taxpath = 'c:/gridapps-d/powergrid-models/taxonomy/'
      dpvpath = 'c:/epri_dpv/'
  elif sys.platform == 'linux':
      srcpath = '/home/mcde601/src/'
      outpath = srcpath + 'Powergrid-Models/blazegraph/test/'
      cimpath = srcpath + 'OpenDSS/Test/'
      ieeepath = srcpath + 'OpenDSS/Distrib/IEEETestCases/'
      epripath = srcpath + 'OpenDSS/Distrib/EPRITestCircuits/'
      taxpath = srcpath + 'Powergrid-Models/taxonomy/'
      dpvpath = srcpath + 'epri_dpv/'
  else:
      srcpath = '/Users/mcde601/src/'
      outpath = srcpath + 'GRIDAPPSD/Powergrid-Models/blazegraph/test/'
      cimpath = srcpath + 'opendss/Test/'
      ieeepath = srcpath + 'opendss/Distrib/IEEETestCases/'
      epripath = srcpath + 'opendss/Distrib/EPRITestCircuits/'
      taxpath = srcpath + 'GRIDAPPSD/Powergrid-Models/taxonomy/'
      dpvpath = srcpath + 'epri_dpv/'

  append_cases(casefiles, taxpath, outpath, 'pnnl', 'taxonomy', fp)
  #
  #casefiles = [['./J1/Master_noPV', 'EPRI_DPV_J1']]
  #             ['./K1/Master_NoPV', 'EPRI_DPV_K1'],
  #             ['./M1/master_NoPV', 'EPRI_DPV_M1']]
  #append_cases(casefiles, dpvpath, outpath, 'epri', 'dpv', fp)

  fp.close()
