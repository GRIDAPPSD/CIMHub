# Find the correct Blazegraph URL; defaults to running inside composed containers
#if (($# > 0)) 
#then
  declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"
#else
#  declare -r DB_URL="http://blazegraph:8080/bigdata/namespace/kb/sparql"
#fi

# empty the Blazegraph repository; this is optional unless you are re-uploading the same circuit
curl -D- -X POST $DB_URL --data-urlencode "update=drop all"

# copy the model files over here
declare -r DSSDIR=../../Powergrid-Models/blazegraph/test/dss/WSU
cp $DSSDIR/Master-bal-initial-config.dss .
cp $DSSDIR/WireData.dss .
cp $DSSDIR/CableData.dss .
cp $DSSDIR/LineGeometry.dss .
cp $DSSDIR/TriplexLineCodes.dss .
cp $DSSDIR/LinesSwitchesGeometry.dss .
cp $DSSDIR/Transformers.dss .
cp $DSSDIR/LoadXfmrCodes.dss .
cp $DSSDIR/TriplexLines.dss .
cp $DSSDIR/BalancedLoads.dss .
cp $DSSDIR/Capacitors.dss .
cp $DSSDIR/CapControls.dss .
cp $DSSDIR/Regulators.dss .
cp $DSSDIR/Generators.dss .
cp $DSSDIR/EnergyStorage.dss .
cp $DSSDIR/PV_10pen_DSSPV.dss .
cp $DSSDIR/PV_NN_100_DSSPV.dss .
cp $DSSDIR/LatLongCoords.dss .

# create the CIM XML files
opendsscmd relative_model.dss

# upload the CDPSM combined file to Blazegraph
curl -D- -H "Content-Type: application/xml" --upload-file ieee9500.xml -X POST $DB_URL

# list feeders now in the Blazegraph repository; will need the feeder mRIDs from this output
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -u=$DB_URL -o=idx test

# create OpenDSS and GridLAB-D models
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_194AC68D-C4B3-4D93-A2B5-B1C195C49954 -u=$DB_URL -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee9500

# create CSV files
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter \
  -s=_194AC68D-C4B3-4D93-A2B5-B1C195C49954 -u=$DB_URL -o=csv -l=1.0 -i=1 -h=0 -x=0 -t=1 ieee9500



