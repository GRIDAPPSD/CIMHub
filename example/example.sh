opendsscmd cim_test.dss

./drop_all.sh

curl -D- -H "Content-Type: application/xml" --upload-file ieee13assets.xml -X POST "http://localhost:8889/bigdata/namespace/kb/sparql"
curl -D- -H "Content-Type: application/xml" --upload-file ieee13cdpsm.xml -X POST "http://localhost:8889/bigdata/namespace/kb/sparql"

java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -o=idx test

java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_DFBF372D-4291-49EF-ACCA-53DAFDE0338F -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee13assets

java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29 -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee13cdpsm

gridlabd test_ieee13assets.glm
gridlabd test_ieee13cdpsm.glm

opendsscmd test_opendss.dss

