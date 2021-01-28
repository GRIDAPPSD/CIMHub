declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"

# clear out the old model and results
rm ieee13*.dss
rm sumieee13assets.csv
rm sumieee13houses.csv
rm ieee13*.glm
rm test_*.csv

# create OpenDSS and GridLAB-D models of the Assets-based IEEE 13-bus model from CIM
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_5B816B93-7A5F-B64C-8460-47C17D6E4B0F -u=$DB_URL -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee13assets

# create OpenDSS and GridLAB-D models of the regular IEEE 13-bus model from CIM, with houses
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62 -u=$DB_URL -o=both -l=1.0 -i=1 -h=1 -x=0 -t=1 ieee13houses

# try to run both simulations in OpenDSS
opendsscmd test_ieee13assets.dss
opendsscmd test_ieee13houses.dss
tail sumieee13*.csv

# try to run both simulations in GridLAB-D
gridlabd test_ieee13assets.glm
gridlabd test_ieee13houses.glm
tail test_*.csv

