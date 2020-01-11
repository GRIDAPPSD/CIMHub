# updated process: build a jar file using Apache Maven with pom.xml
mvn clean install

java -classpath "target/*:/Users/mcde601/src/apache-jena-3.6.0/lib/*:/Users/mcde601/src/commons-math3-3.6.1/*" \
   gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.txt -o=idx test

#java -classpath "target/*:/Users/mcde601/src/apache-jena-3.6.0/lib/*:/Users/mcde601/src/commons-math3-3.6.1/*" \
#     gov.pnnl.goss.cim2glm.CIMImporter \
#     -s=_2f953656-602a-a613-10f5-6579d8ed4621 -q=q17.txt -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 cef2


