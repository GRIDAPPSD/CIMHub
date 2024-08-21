rem set JAVA_HOME=c:\Program Files\Java\jdk1.8.0_192
rem java -server -Xmx4g -jar blazegraph.jar

curl -D- -X POST "http://localhost:9999/blazegraph/sparql" --data-urlencode "update=drop all"
set DB_URL="http://localhost:9999/bigdata/namespace/kb/sparql"

echo Converting DSS model to CIM100 model
opendsscmd cim_test.dss

echo Uploading CIM model to blazegraph
rem curl -D- -H "Content-Type: application/xml" --upload-file IEEE13\ieee13cdpsm.xml -X POST "http://localhost:9999/blazegraph/namespace/kb/sparql"
curl -D- -H "Content-Type: application/xml" --upload-file South_D1_Alburgh\South_D1_Alburgh.xml -X POST "http://localhost:9999/blazegraph/namespace/kb/sparql"

echo Done with Uploading
