rem mvn clean install

set CLASSPATH=target/*;c:/apache-jena-3.6.0/lib/*;c:/commons-math3-3.6.1/*
java gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.xml -o=idx test

java gov.pnnl.gridappsd.cimhub.CIMImporter ^
-q=q17.xml -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 cef2
rem  -s=_2f953656-602a-a613-10f5-6579d8ed4621 -q=q17.xml -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 cef2


