# updated process: build a jar file using Apache Maven with pom.xml
#mvn clean install

#java -classpath "target/*:/Users/mcde601/src/apache-jena-3.6.0/lib/*:/Users/mcde601/src/commons-math3-3.6.1/*" \
#java -classpath "target/*:/home/tom/.m2/repository/org/apache/jena" \
#   gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.xml -o=idx test

java -cp target/libs/*;target/cimhub-0.0.1-SNAPSHOT.jar gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.xml -o=idx test

# java -cp target/cimhub-0.0.1-SNAPSHOT-jar-with-dependencies.jar gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.xml -o=idx test

#java -classpath "target/*:/Users/mcde601/src/apache-jena-3.6.0/lib/*:/Users/mcde601/src/commons-math3-3.6.1/*" \
#   gov.pnnl.gridappsd.cimhub.CIMImporter -q=q17.xml -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 cef2
#   -s=_2f953656-602a-a613-10f5-6579d8ed4621 -q=q17.xml -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 cef2


