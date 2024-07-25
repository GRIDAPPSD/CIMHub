rem standalone Blazegraph on Windows
set DB_URL="http://localhost:9999/blazegraph/namespace/kb/sparql"
set CIMHUB_PATH="../releases/cimhub-1.1.0.jar"
set CIMHUB_PROG="gov.pnnl.gridappsd.cimhub.CIMImporter"

rem empty the Blazegraph repository; this is optional unless you are re-uploading the same circuit
curl -D- -X POST %DB_URL% --data-urlencode "update=drop all"

rem create the CIM XML files
opendsscmd cim_test.dss

rem upload the 2 CDPSM combined XML files to Blazegraph
curl -D- -H "Content-Type: application/xml" --upload-file ieee13assets.xml -X POST %DB_URL%
curl -D- -H "Content-Type: application/xml" --upload-file ieee13cdpsm.xml -X POST %DB_URL%

rem testing CSV exports
java -cp %CIMHUB_PATH% %CIMHUB_PROG% ^
  -s=DFBF372D-4291-49EF-ACCA-53DAFDE0338F -u=%DB_URL% -o=csv -l=1.0 -i=1 ieee13assets
java -cp %CIMHUB_PATH% %CIMHUB_PROG% ^
  -s=F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29 -u=%DB_URL% -o=csv -l=1.0 -i=1 ieee13cdpsm

rem list feeders now in the Blazegraph repository; will need the feeder mRIDs from this output
java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=idx test

rem create OpenDSS and GridLAB-D modes of the Assets-based IEEE 13-bus model from CIM
java -cp %CIMHUB_PATH% %CIMHUB_PROG% ^
  -s=DFBF372D-4291-49EF-ACCA-53DAFDE0338F -u=%DB_URL% -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee13assets

rem create OpenDSS and GridLAB-D modes of the regular IEEE 13-bus model from CIM
rem note: this version of the circuit adds photovoltaic and storage DER, and a single-phase center-tapped transformer
java -cp %CIMHUB_PATH% %CIMHUB_PROG% ^
  -s=F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29 -u=%DB_URL% -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 -m=0 ieee13cdpsm

rem test GridLAB-D solution of both models from CIM XML; outputs to test*volt.csv and test*curr.csv
rem these are bypassed by default because GridLAB-D is not installed into the cimhub container
rem if you have GridLAB-D installed on the host, then you can run these tests by copying *.glm
rem   into a directory on the host
gridlabd test_ieee13assets.glm
gridlabd test_ieee13cdpsm.glm

rem test OpenDSS solution of both models from CIM XML; outputs to sumIEEE13*.csv
opendsscmd test_opendss.dss

