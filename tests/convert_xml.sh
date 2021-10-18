#!/bin/bash
source envars.sh
mkdir ./dss/
mkdir ./glm/
rm ./dss/*.*
rm ./glm/*.*
curl -D- -X POST $DB_URL --data-urlencode "update=drop all"
curl -D- -H "Content-Type: application/xml" --upload-file ./IEEE13_Assets.xml -X POST $DB_URL
java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=dss -l=1.0 -i=1 ./dss/IEEE13_Assets
java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=glm -l=1.0 -i=1 ./glm/IEEE13_Assets
curl -D- -X POST $DB_URL --data-urlencode "update=drop all"
curl -D- -H "Content-Type: application/xml" --upload-file ./IEEE13_CDPSM.xml -X POST $DB_URL
java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=dss -l=1.0 -i=1 ./dss/IEEE13_CDPSM
java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=glm -l=1.0 -i=1 ./glm/IEEE13_CDPSM
