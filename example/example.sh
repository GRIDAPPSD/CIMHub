# create the CIM XML files
opendsscmd cim_test.dss

# empty the Blazegraph repository; this is optional unless you are re-uploading the same circuit
./drop_all.sh

# upload the 2 CDPSM combined XML files to Blazegraph
curl -D- -H "Content-Type: application/xml" --upload-file ieee13assets.xml -X POST "http://localhost:8889/bigdata/namespace/kb/sparql"
curl -D- -H "Content-Type: application/xml" --upload-file ieee13cdpsm.xml -X POST "http://localhost:8889/bigdata/namespace/kb/sparql"

# list feeders now in the Blazegraph repository; will need the feeder mRIDs from this output
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -o=idx test

# create OpenDSS and GridLAB-D modes of the Assets-based IEEE 13-bus model from CIM
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_DFBF372D-4291-49EF-ACCA-53DAFDE0338F -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee13assets

# create OpenDSS and GridLAB-D modes of the regular IEEE 13-bus model from CIM
# note: this version of the circuit adds photovoltaic and storage DER, and a single-phase center-tapped transformer
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29 -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee13cdpsm

# test GridLAB-D solution of both models from CIM XML; outputs to test*volt.csv and test*curr.csv
# these are commented out because GridLAB-D is not installed into the cimhub container
# if you have GridLAB-D installed on the host, then you can run these tests by copying *.glm
#   into a directory on the host
#gridlabd test_ieee13assets.glm
#gridlabd test_ieee13cdpsm.glm

# test OpenDSS solution of both models from CIM XML; outputs to sumIEEE13*.csv
opendsscmd test_opendss.dss

