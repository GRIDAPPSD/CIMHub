#!/bin/bash
declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"
declare -r CIMHUB_PATH="target/libs/*:../cimhub/target/cimhub-0.0.3-SNAPSHOT.jar"
declare -r CIMHUB_PROG="gov.pnnl.gridappsd.cimhub.CIMImporter"

#java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=idx test

#java -cp $CIMHUB_PATH $CIMHUB_PROG \
#  -s=_58EAA940-6023-4F38-B09B-3D445BAB4429 -u=$DB_URL -o=dss -l=1.0 -i=1 -h=0 -x=0 -t=1 test
#cat *base.dss

java -cp $CIMHUB_PATH $CIMHUB_PROG \
  -s=_58EAA940-6023-4F38-B09B-3D445BAB4429 -u=$DB_URL -o=csv -l=1.0 -i=1 -h=0 -x=0 -t=1 test

cat *I1547*.csv
