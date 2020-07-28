declare -r PGM_DIR="../../Powergrid-Models"
declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"

# empty the Blazegraph repository
curl -D- -X POST $DB_URL --data-urlencode "update=drop all"

# upload the 2 CDPSM combined XML files to Blazegraph
curl -D- -H "Content-Type: application/xml" --upload-file $PGM_DIR/blazegraph/test/IEEE13.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file $PGM_DIR/blazegraph/test/IEEE13_Assets.xml -X POST $DB_URL

# list feeders now in the Blazegraph repository; will need the feeder mRIDs from this output
java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -u=$DB_URL -o=idx test

# insert measurements for both circuits
python3 ListMeasureables.py ieee13assets _5B816B93-7A5F-B64C-8460-47C17D6E4B0F
python3 ListMeasureables.py ieee13houses _49AD8E07-3BF9-A4E2-CB8F-C3722F837B62
python3 InsertMeasurements.py ieee13assets_lines_pq.txt
python3 InsertMeasurements.py ieee13assets_loads.txt
python3 InsertMeasurements.py ieee13assets_node_v.txt
python3 InsertMeasurements.py ieee13assets_special.txt
python3 InsertMeasurements.py ieee13assets_switch_i.txt
python3 InsertMeasurements.py ieee13assets_xfmr_pq.txt
python3 InsertMeasurements.py ieee13houses_lines_pq.txt
python3 InsertMeasurements.py ieee13houses_loads.txt
python3 InsertMeasurements.py ieee13houses_node_v.txt
python3 InsertMeasurements.py ieee13houses_special.txt
python3 InsertMeasurements.py ieee13houses_switch_i.txt
python3 InsertMeasurements.py ieee13houses_xfmr_pq.txt

# insert houses for just the 13-node circuit that has a split-phase secondary load
PYTHONPATH=$PYTHONPATH:$PGM_DIR python3 $PGM_DIR/houses/insertHouses.py _49AD8E07-3BF9-A4E2-CB8F-C3722F837B62 3

