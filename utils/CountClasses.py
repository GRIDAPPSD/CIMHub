from SPARQLWrapper import SPARQLWrapper2
import constants
import os

sparql = SPARQLWrapper2(constants.blazegraph_url)

def clear_database():
    sparql.method = 'POST'
    sparql.setQuery(constants.prefix + 
    """
    DROP ALL
    """)
    return sparql.query()

def count_classes():
    sparql.method = 'GET'
    sparql.setQuery(constants.prefix + 
    """
    SELECT ?class (COUNT(?class) as ?cnt)
    WHERE {
      ?s a ?rawclass .
      bind(strafter(str(?rawclass),"#") as ?class)
    } group by ?class order by ?class
    """)
    return sparql.query()

xml_path = '../model_output_tests/'
xml_files = {'ACEP_PSIL':{}, 
             'IEEE13':{}, 
             'IEEE13_Assets':{}}
all_classes = []

for fname in xml_files:
    clear_database()
    cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_path + fname + '.xml' + ' -X POST ' + constants.blazegraph_url
    os.system (cmd)
    ret = count_classes()
    for b in ret.bindings:
        cls = b['class'].value
        cnt = b['cnt'].value
        xml_files[fname][cls] = cnt
        if cls not in all_classes:
            all_classes.append (cls)

csvfile = xml_path + 'class_counts.csv'
mdfile = xml_path + 'class_counts.md'
print ('Writing Class Summaries to {:s} and {:s}'.format (csvfile, mdfile))
fp1 = open (csvfile, 'w')
fp2 = open (mdfile, 'w')

print ('Class,' + ','.join(xml_files.keys()), file=fp1)
print ('| Class | ' + ' | '.join(xml_files.keys()) + ' |', file=fp2)
mdhdr = '| :--- |'
for fname in xml_files.keys():
    mdhdr = mdhdr + ' :---: |'
print (mdhdr, file=fp2)

for cls in sorted (all_classes):
    counts = []
    for fname in xml_files.keys():
        cnt = '0'
        if cls in xml_files[fname]:
            cnt = xml_files[fname][cls]
        counts.append (cnt)
    print (cls + ',' + ','.join(counts), file=fp1)
    print ('| ' + cls + ' | ' + ' | '.join(counts) + ' |', file=fp2)

fp1.close()
fp2.close()
