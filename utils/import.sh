# updated process: build a jar file using Apache Maven with pom.xml
mvn clean install

#java -cp "target/libs/*:target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.xml -o=idx test
#java -cp "target/libs/*:target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
#   -s=_2f953656-602a-a613-10f5-6579d8ed4621 -q=q17.xml -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 cef2

# java -cp target/cimhub-0.0.1-SNAPSHOT-jar-with-dependencies.jar gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.xml -o=idx test

java -cp "target/libs/*:target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -o=idx test
java -cp "target/libs/*:target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_2F953656-602A-A613-10F5-6579D8ED4621 -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 cef2_der

