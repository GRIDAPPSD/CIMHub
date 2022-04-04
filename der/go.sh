#!/bin/bash
declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"
declare -r CIMHUB_PATH="../cimhub/target/libs/*:../cimhub/target/cimhub-1.0.0-SNAPSHOT.jar"
declare -r CIMHUB_PROG="gov.pnnl.gridappsd.cimhub.CIMImporter"

rm -rf dss
rm -rf glm
mkdir dss
mkdir glm

curl -D- -X POST $DB_URL --data-urlencode "update=drop all"
opendsscmd cim_test.dss
curl -D- -H "Content-Type: application/xml" --upload-file ieee13der.xml -X POST $DB_URL

java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=idx test
java -cp $CIMHUB_PATH $CIMHUB_PROG \
  -s=_F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29 -u=$DB_URL -o=dss -l=1.0 -p=1 -h=0 -x=0 dss/ieee13der
java -cp $CIMHUB_PATH $CIMHUB_PROG \
  -s=_F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29 -u=$DB_URL -o=glm -l=1.0 -p=1 -h=0 -x=0 glm/ieee13der

opendsscmd test_opendss.dss
cp test_glm.glm glm
cd glm
gridlabd test_glm.glm > test.log
cd ..

python3 -c """import cimhub.api as cimhub;cimhub.compare_cases ([{'root':'ieee13der','bases':[480.0, 4160.0, 13200.0, 115000.0]}],'./','./dss/','./glm/')"""

echo "**** OpenDSS Topology and Summary Check"
cat dss/*Missing*.txt
cat dss/*.log

echo "**** OpenDSS Bus Comparison"
cat dss/*Compare_Voltages*DSS.*

echo "**** OpenDSS Bus Comparison"
cat dss/*Compare_Currents*DSS.*

echo "**** GridLAB-D Solution Log"
cat glm/*.log

echo "**** GridLAB-D Bus Comparison"
cat dss/*Compare_Voltages*GLM.*

echo "**** GridLAB-D Branch Comparison"
cat dss/*Compare_Currents*GLM.*

