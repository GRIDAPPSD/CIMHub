import csv
import operator
import math

def dss_phase(col):
    if col==1:
        return '_A'
    elif col==2:
        return '_B'
    else:
        return '_C'

def glmVpu(v):
    if v < 10000.0:
        return v/7621.01
    else:
        return v/26558.11

def cymVpu(kv):
    if kv < 10.0:
        return kv/7.62101
    else:
        return kv/26.55811

#SectionID,DSSName,DSSBus1,DSSBus2  if ends with // we can't map the section to OpenDSS
#ToNode,SectionID  if ends with // we can't map this to a non-zero CYMDIST section
mapcym = {}
mapdss = {}
mappingCyme = False
mappingDss = False

fmap = open ('Missing_Nodes.map', 'r')
rmap = csv.reader (fmap, delimiter=',')
for row in rmap:
    if mappingCyme:
        if '#ToNode' in row[0]:
            mappingCyme = False
            mappingDss = True
        elif '//' not in row[3]:
            mapcym[row[0]] = row[3]
        else:
            mapcym[row[0]] = '' # meaning we know it can't be found in OpenDSS
    elif mappingDss:
        if '//' not in row[1]:
            mapdss[row[0]] = row[1]
        else:
            mapdss[row[0]] = ''
    else:
        if '#SectionID' in row[0]:
            mappingCyme = True
        elif '#ToNode' in row[0]:
            mappingCyme = False
            mappingDss = True

fmap.close()

# bus naming convention will be "bus name"_A, _B, or _C
vdss = {}
vcym = {}
vglm = {}
diff = {}

fdss = open ('CandleStFeeders_EXP_VOLTAGES.CSV', 'r')
fcym = open ('CYMDIST_Solution/Details.csv', 'r')
fglm = open ('nantucket_volt.csv', 'r')

rdss = csv.reader (fdss, delimiter=',', skipinitialspace=True)
next (rdss)
rcym = csv.reader (fcym, delimiter=',')
next (rcym)
rglm = csv.reader (fglm, delimiter=',')
next (rglm)
next (rglm)

#Bus, BasekV, Node1, Magnitude1, Angle1, pu1, Node2, Magnitude2, Angle2, pu2, Node3, Magnitude3, Angle3, pu3
for row in rdss:
    bus = row[0].strip('\"')
    if len(bus) > 0:
        vpu1 = float(row[5])
        vpu2 = float(row[9])
        vpu3 = float(row[13])
        if float(vpu1) > 0:
            phs = dss_phase (int(row[2]))
            vdss[bus+phs] = vpu1
        if float(vpu2) > 0:
            phs = dss_phase (int(row[6]))
            vdss[bus+phs] = vpu2
        if float(vpu3) > 0:
            phs = dss_phase (int(row[10]))
            vdss[bus+phs] = vpu3

#Feeder,Section,Equipment,Code,Loading%,Va%,Ia,Ib,Ic,Sa,Sb,Sc,Qa,Qb,Qc,Pa,Pb,Pc,Vab,Vbc,Vca,Van,Vbn,Vcn
for row in rcym:
    bus=row[1]
    if bus in mapcym:
        if len(mapcym[bus]) > 0:
            bus = mapcym[bus]
        else:
            bus = ''
    if len(bus) > 0:
        Vapct=row[5]
        Van=row[21]
        Vbn=row[22]
        Vcn=row[23]
        if len(Van) > 0:
            vpu = cymVpu (float(Van))
            if vpu > 0.0:
                vcym[bus+'_A'] = vpu
        if len(Vbn) > 0:
            vpu = cymVpu (float(Vbn))
            if vpu > 0.0:
                vcym[bus+'_B'] = vpu
        if len(Vcn) > 0:
            vpu = cymVpu (float(Vcn))
            if vpu > 0.0:
                vcym[bus+'_C'] = vpu

for row in rglm:
    bus = row[0]
    if bus.startswith('nm_'):
        bus = bus[len('nm_'):]
        maga = float(row[1])
        if maga > 0.0:
            vglm[bus+'_A'] = glmVpu (maga)
        magb = float(row[3])
        if magb > 0.0:
            vglm[bus+'_B'] = glmVpu (magb)
        magc = float(row[5])
        if magc > 0.0:
            vglm[bus+'_C'] = glmVpu (magc)

for bus in vdss:
    if bus in vcym:
        diff [bus] = abs(vdss[bus] - vcym[bus])

sorted_diff = sorted(diff.items(), key=operator.itemgetter(1))

fcsv = open ('Compare_Voltages.csv', 'w')
print ('bus_phs,vcym,vdss,vglm,OpenDSS,GridLAB-D', file=fcsv)
for row in sorted_diff:
    if row[1] < 0.8:
        bus = row[0]
        print (bus, 
                     '{:.5f}'.format(vcym[bus]), 
                     '{:.5f}'.format(vdss[bus]), 
                     '{:.5f}'.format(vglm[bus]),
                     '{:.5f}'.format(row[1]), 
                     '{:.5f}'.format(abs(vglm[bus] - vcym[bus])), 
                     sep=',',
                     file=fcsv)

ftxt = open ('Missing_Nodes.txt', 'w')
nmissing_cym = 0
nmissing_dss = 0
for bus in vcym:
    if not bus in vdss:
        print (bus, 'not in OpenDSS', file=ftxt)
        nmissing_dss += 1
for bus in vdss:
    if not bus in vcym:
        if not '-SWT' in bus and not '-XF' in bus:
            if not bus[:-2] in mapdss:
                print (bus, 'not in CYMDIST', file=ftxt)
                nmissing_cym += 1

print (len(vcym), 'CYMDIST nodes,', nmissing_dss, 'not in OpenDSS', file=ftxt)
print (len(vdss), 'OpenDSS nodes,', nmissing_cym, 'not in CYMDIST', file=ftxt)
print (len(vglm), 'GridLAB-D nodes', file=ftxt)

fcsv.close()
fdss.close()
fcym.close()
fglm.close()
ftxt.close()

