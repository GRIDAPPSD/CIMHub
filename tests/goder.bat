#!/bin/bash
declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"
declare -r CIMHUB_PATH="../cimhub/target/libs/*:../cimhub/target/cimhub-1.0.0-SNAPSHOT.jar"
declare -r CIMHUB_PROG="gov.pnnl.gridappsd.cimhub.CIMImporter"

declare -r CIMHUB_FID="49AD8E07-3BF9-A4E2-CB8F-C3722F837B62" # ieee13

python3 test_dercat.py
#java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=idx test

#java -cp $CIMHUB_PATH $CIMHUB_PROG \
#  -s=$CIMHUB_FID -u=$DB_URL -o=glm -l=1.0 -i=1 -h=0 -x=0 -t=1 test
#cat test_base.glm

java -cp $CIMHUB_PATH $CIMHUB_PROG \
  -s=$CIMHUB_FID -u=$DB_URL -o=dss -l=1.0 -i=1 -h=0 -x=0 -t=0 test
#cat *base.dss
opendsscmd test_base.dss

#java -cp $CIMHUB_PATH $CIMHUB_PROG \
#  -s=$CIMHUB_FID -u=$DB_URL -o=csv -l=1.0 -i=1 -h=0 -x=0 -t=1 test
#cat test_Solar.csv
#cat test_Storage.csv
