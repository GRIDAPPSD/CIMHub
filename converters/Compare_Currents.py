import csv
import operator
import math

# link naming convention will be "link name"_A, _B, or _C
idssnum = {}
idss = {}
icym = {}
iglm = {}
diff = {}

fdss = open ('CandleStFeeders_EXP_CURRENTS.CSV', 'r')
fcym = open ('CYMDIST_Solution/Details.csv', 'r')
fglm = open ('nantucket_curr.csv', 'r')

rdss = csv.reader (fdss, delimiter=',', skipinitialspace=True)
next (rdss)
rcym = csv.reader (fcym, delimiter=',')
next (rcym)
rglm = csv.reader (fglm, delimiter=',')
next (rglm)
next (rglm)

#Element, I1_1, Ang1_1, I1_2, Ang1_2, I1_3, Ang1_3, I1_4, Ang1_4, Iresid1, AngResid1, I2_1, Ang2_1, I2_2, Ang2_2, I2_3, Ang2_3, I2_4, Ang2_4, Iresid2, AngResid2
for row in rdss:
    link = row[0].strip('\"')
    if link.startswith('Line.'):
        link = link[len('Line.'):].lower()
        i1 = float(row[1]) # figure out the phasing later, while parsing GLM results
        i2 = float(row[3])
        i3 = float(row[5])
        idx = 1
        if i1 > 0.001:
            idssnum[link+'_'+str(idx)] = i1
            idx += 1
        if i2 > 0.001:
            idssnum[link+'_'+str(idx)] = i2
            idx += 1
        if i3 > 0.001:
            idssnum[link+'_'+str(idx)] = i3
            idx += 1

#Feeder,Section,Equipment,Code,Loading%,Va%,Ia,Ib,Ic,Sa,Sb,Sc,Qa,Qb,Qc,Pa,Pb,Pc,Vab,Vbc,Vca,Van,Vbn,Vcn
for row in rcym:
    link=row[1]
    if len(link) > 0:
        ia=row[6]
        ib=row[7]
        ic=row[8]
        if len(ia) > 0:
            iamps = float(ia)
            if iamps > 0.0:
                icym[link+'_A'] = iamps
        if len(ib) > 0:
            iamps = float(ib)
            if iamps > 0.0:
                icym[link+'_B'] = iamps
        if len(ic) > 0:
            iamps = float(ic)
            if iamps > 0.0:
                icym[link+'_C'] = iamps

#link_name,currA_mag,currA_angle,currB_mag,currB_angle,currC_mag,currC_angle
for row in rglm:
    link = row[0]
    if link.startswith('line_'):
        link = link[len('line_'):].lower()
        if link+'_1' in idssnum:
            idx = 1
            maga = float(row[1])
            if maga > 0.001:
                iglm[link+'_A'] = maga
                idss[link+'_A'] = idssnum[link+'_'+str(idx)]
                idx += 1
            magb = float(row[3])
            if magb > 0.001:
                iglm[link+'_B'] = magb
                idss[link+'_B'] = idssnum[link+'_'+str(idx)]
                idx += 1
            magc = float(row[5])
            if magc > 0.001:
                iglm[link+'_C'] = magc
                idss[link+'_C'] = idssnum[link+'_'+str(idx)]
                idx += 1

for link in idss:
    if link in icym:
        diff [link] = abs(idss[link] - icym[link])

sorted_diff = sorted(diff.items(), key=operator.itemgetter(1))

fcsv = open ('Compare_Currents.csv', 'w')
print ('link_phs,icym,idss,iglm,OpenDSS,GridLAB-D', file=fcsv)
for row in sorted_diff:
    link = row[0]
    print (link, 
        '{:.3f}'.format(icym[link]), 
        '{:.3f}'.format(idss[link]), 
        '{:.3f}'.format(iglm[link]),
        '{:.3f}'.format(row[1]), 
        '{:.3f}'.format(abs(iglm[link] - icym[link])), 
        sep=',',
        file=fcsv)

ftxt = open ('Missing_Links.txt', 'w')
nmissing_cym = 0
nmissing_dss = 0
for link in icym:
    if not link in idss:
        print (link, 'not in OpenDSS', file=ftxt)
        nmissing_dss += 1
for link in idss:
    if not link in icym:
        print (link, 'not in CYMDIST', file=ftxt)
        nmissing_cym += 1

print (len(icym), 'CYMDIST links,', nmissing_dss, 'not in OpenDSS', file=ftxt)
print (len(idss), 'OpenDSS line links,', nmissing_cym, 'not in CYMDIST', file=ftxt)
print (len(iglm), 'GridLAB-D line links', file=ftxt)

fcsv.close()
fdss.close()
fcym.close()
fglm.close()
ftxt.close()

