# CIMHub

Copyright (c) 2017-2021, Battelle Memorial Institute

This is a tool set for translating electric power distribution system models between
various formats, using the IEC Standard 61970/61968 Common Information Model (CIM) as the "Hub". [Requirements](requirements.md)

The CIM data is stored in an open-source triple-store called Blazegraph.
Python 3 scripts depend on SPARQLWrapper.  The Java code uses 
OpenJDK 11 and builds with Apache Maven.

Please make sure that GIT LFS is installed before checking out or cloning this repository.

## Docker and Blazegraph Setup

Blazegraph requires Java 8, which is no longer widely available for new installations.  Blazegraph isn't compatible with Java 9 or newer versions. Therefore, we recommend using Blazegraph in a Docker container: 

1. Install the [Docker Engine](https://docs.docker.com/install/)
2. Install the Blazegraph engine with _docker pull lyrasis/blazegraph:2.1.5_

## Conversion Example

This example converts two versions of the IEEE 13-Bus case from OpenDSS to CIM and GridLAB-D,
without writing code. One version uses phase impedance matrices for line segments. The other version,
labeled "Assets", uses wire and spacing data for the line segments, and transformer code data
for the transformers.

1. Install the converter with _docker pull gridappsd/cimhub:0.0.1_
2. From a Terminal, start the converter and Blazegraph with _./start.sh_
3. From inside the Docker Terminal, run two example conversions of the IEEE 13-Bus example:
   * _cd example_
   * _./example.sh_
   * _tail sum*.csv_ to verify that the converted OpenDSS files ran correctly
   * see the comments embedded in _example.sh_ for more information
4. To shut down the converter:
   * _exit_ from inside the Docker Terminal
   * _./stop.sh_ from the host Terminal

The example script may produce error messages upon first invocation, 
because the Blazegraph engine doesn't start immediately.  However, the 
example does complete successfully.  You may re-run the example starting 
from step 2.  You may also wish to modify _docker-compose.yml_ so that it 
mounts a local directory inside the converter, for transferring your own 
files between the host and Docker.

## End User Instructions

To convert your own circuits from OpenDSS to CIM and GridLAB-D, follow the IEEE 13-Bus
example described above, with some changes:

1. First read the [OpenDSS note on Common Information Model](doc/Common_Information_Model.pdf) for background on how the univeral unique identifiers (UUID) are managed for CIM.
2. The first time you run the conversion process on a new circuit, OpenDSS must create random UUID values. To account for this:
   * In the example [cim_test.dss](example/cim_test.dss) file, comment out (with //) any lines invoking the _uuids_ command
   * In the [example.sh](example/example.sh) file, you have to replace the _-s_ parameter with a correct one for your new circuit. For example, __DFBF372D-4291-49EF-ACCA-53DAFDE0338F should be changed to a new value. The correct value will be found on line 1 of the generated _*UUIDS.dat_ file for your new circuit.
   * To re-run the conversion process on the same circuit, you should first uncomment the _uuids_ command that you commented out in the first bullet. This way, OpenDSS will reuse the UUID values, including the first one for the circuit.

## Developer Instructions

It could be more convenient to run only Blazegraph in a Docker container, writing code and queries on the host.

1. Start the containerized Blazegraph engine:
	 * _docker run --name blazegraph -d -p 8889:8080 lyrasis/blazegraph:2.1.5_ to create and start the container for Blazegraph
	 * Only if something goes wrong: _docker logs -f blazegraph_ to log the database and Java messages to the console
	 * consult the Docker documentation for more details on how to stop and otherwise manage containers
   * subsequently, use _docker restart blazegraph_ to restart the container
2. Point a web browser to _http://localhost:8889/bigdata_. On-line help on Blazegraph is available from the browser
3. Load some data from a CIM XML file into the browser
4. Run a query in the browser
	 * the file _queries.txt_ contains sample SPARQL that can be pasted into the Blazegraph browser window

You can also run the IEEE 13-bus example conversions from the host Terminal.

1. _cd example_
2. _./example.sh arg_

Step 2 provides a dummy argument so that the example script will select a different URL for Blazegraph. When
querying from the host, the URL contains _localhost:8889_ but when querying from a Docker terminal, the URL
contains _blazegraph:8080_, which is valid only on the internal network that Docker creates. Also, with a
dummy argument, the example will try to run GridLAB-D on the converted example models. This will fail unless
you have GridLAB-D installed on the host. If you do have GridLAB-D, _tail test*.csv_ to check the results.

In order to develop Python code for the CIM, it should suffice to _pip3 install sparqlwrapper_ and then
use existing Python code under _./utils_ for guidance.

In order to modify the CIMHub Java code, you will need to install [Apache Maven](https://maven.apache.org) and then use _mvn clean install_.

In order to build the cimhub docker container, use the _./build.sh_ script. However, that script assumes
that opendsscmd and liblinenoise have been built in sibling directories to this one. When finished, an
authorized developer can push the new image to DockerHub, e.g., _docker push gridappsd/cimhub:0.0.1_

## GridAPPS-D Model Import

Please be able to build CIMHub as described in the previous section, so that you can
perform this model import process as a developer.

Verify that the Blazegraph namespace is _kb_ and use that for the rest of these examples
   * You can use a different namespace, but you'll have to specify that using the -u option for the CIMImporter, handediting the default _-u=http://localhost:8889/bigdata/namespace/kb/sparql_
   * You can use a different namespace, but you may have to hand-edit some of the Python files (e.g. under the Meas directory)
   * The GridAPPS-D platform itself may use a different namespace

Helper scripts for Linux/Mac OS X:

* _import.sh_ will compile and run the Java importer against the triple-store. Within this file:
  * the ```-o=cim``` option creates a CIM14 model from CIM100
  * the ```-o=csv``` option creates a set of comma-delimited text files from CIM100
  * the ```-o=dss``` option creates an OpenDSS model from CIM100
  * the ```-o=glm``` option creates a GridLAB-D model from CIM 100
  * the ```-o=both``` option creates both OpenDSS and GridLAB-D models from CIM100 
  * the ```-o=idx``` option creates a JSON index of all Feeders in the triple-store. Use this to obtain valid mRID values for the -s option

If you will need both OpenDSS and GridLAB-D files, the ```-o=both``` option is much more efficient than generating them individually, because over 90% of the execution time is taken up with SPARQL queries that are common to both.

Usage and options for ```java gov.pnnl.gridappsd.cimhub.CIMImporter [options] output_root```

* ```-q={queries file}  // optional file with CIM namespace and component queries (defaults to CIM100)```
* ```-s={mRID}          // select one feeder by CIM mRID; selects all feeders if not specified```
* ```-o={glm|dss|both|idx|cim|csv}   // output format; defaults to glm; currently cim supports only CIM14```
* ```-l={0..1}          // load scaling factor; defaults to 1```
* ```-f={50|60}         // system frequency; defaults to 60```                                                 
* ```-n={schedule_name} // root filename for scheduled ZIP loads (defaults to none), valid only for -o=glm```      
* ```-z={0..1}          // constant Z portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)```
* ```-i={0..1}          // constant I portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)```
* ```-p={0..1}          // constant P portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)```
* ```-r={0..1}          // determine ZIP load fraction based on given xml file or randomized fractions```
* ```-h={0..1}          // determine if house load objects should be added to supplement EnergyConsumers```
* ```-x={0, 1}          // indicate whether for glm, the model will be called with a fault_check already created```
* ```-t={0, 1}          // request timing of top-level methods and SPARQL queries, requires -o=both for methods```
* ```-u={http://localhost:8889/bigdata/namespace/kb/sparql} // blazegraph uri (if connecting over HTTP); defaults to http://localhost:8889/bigdata/namespace/kb/sparql```

The following steps are used to ingest these models, and verify that exports from CIM will solve in both GridLAB-D and OpenDSS. (Note: on Linux and Mac OS X, use ```python3``` as shown below. On Windows, it may be that ```python3``` is not defined, in which case use ```python``` to invoke Python 3.)

1. Start the Blazegraph engine; _existing contents will be removed in the steps below_. GridLAB-D and OpenDSSCmd must also have been installed.
2. From blazegraph/test directory, issue ```./go.sh``` to create the CIM XML files and baseline OpenDSS power flow solutions.
   - Results will be in the ```model_output_tests``` directory
   - ```rootname.xml``` is the CIM XML file
   - ```rootname_s.csv``` contains exported snapshot loadflow summary
   - ```rootname_i.csv``` contains exported branch currents
   - ```rootname_v.csv``` contains exported bus voltages
   - ```rootname_t.csv``` contains exported regulator tap positions
3. From utils directory, issue ```python3 MakeLoopScript.py -b``` to create the platform-dependent script for step 3
4. From utils directory, issue ```./convert_xml.sh``` to:
   - Empty and create a new ```model_output_tests/both``` directory
   - Sequentially ingest the CIM XML files into Blazegraph, and export both OpenDSS and GridLAB-D models
   - This step may take a few minutes. When finished, all of the GridLAB-D and OpenDSS models will be in ```model_output_tests/both``` directory
   - When finished, only the last CIM XML will still be in Blazegraph. _This should be deleted before doing any more work in Blazegraph, to ensure compatible namespaces_.
5. From utils directory, issue ```python3 MakeLoopScript.py -d``` and then ```opendsscmd check.dss``` to run OpenDSS power flows on the exported models.
   - Results will be in the ```model_output_tests/both``` directory
   - ```rootname_s.csv``` contains exported snapshot loadflow summary
   - ```rootname_i.csv``` contains exported branch currents
   - ```rootname_v.csv``` contains exported bus voltages
   - ```rootname_t.csv``` contains exported regulator tap positions
6. From utils directory, issue ```python3 MakeGlmTestScript.py``` to create the GridLAB-D wrapper files, ```*run.glm``` and a script execution file in ```blazegraph/both```
7. From model_output_tests/both diretory, if on Linux or Mac OS X, issue ```chmod +x *.sh``` and then ```./check_glm.sh```.  This runs GridLAB-D power flow on the exported models.
   - Results will be in the ```model_output_tests/both``` directory
   - ```rootname_volt.csv``` contains the output from a GridLAB-D voltdump, i.e., the node (bus) voltages
   - ```rootname_curr.csv``` contains the output from a GridLAB-D currdump, i.e., the link (branch) currents
8. From utils directory, issue ```python3 Compare_Cases.py``` to compare the power flow solutions from steps 5 and 7 to the baseline solutions from step 2
9. In the model_output_tests/both directory, comparison results are in a set of files:
   - ```*Summary.log``` compares the OpenDSS snapshot load flow solutions
   - Other ```*.log``` files capture GridLAB-D warnings and errors. At present, the exported IEEE 37-bus model, which is a delta system, does not solve in GridLAB-D
   - ```*Missing_Nodes_DSS.txt``` identifies nodes (buses) that appear in one OpenDSS model (baseline step 2 or exported step 5), but not the other.
   - ```*Missing_Links_DSS.txt``` identifies links (branches) that appear in one OpenDSS model (baseline step 2 or exported step 5), but not the other.
   - ```*Compare_Voltages_DSS.csv``` compares the bus voltages from steps 2 and 5, sorted by increasing difference
   - ```*Compare_Voltages_GLM.csv``` compares the bus voltages from steps 2 and 7, sorted by increasing difference
   - ```*Compare_Currents_DSS.csv``` compares the branch currents from steps 2 and 5, sorted by increasing difference
   - ```*Compare_Currents_GLM.csv``` compares the branch currents from steps 2 and 7, sorted by increasing difference

## GridAPPS-D Circuit Validation Scripts

This is work in progress. The goal is to verify round-trip model translation
and solution between the supported model formats. It also forms the basis for validing eleven feeder models including with GridAPPS-D.

There are currently three supporting Python files in the _utils_ subdirectory:

* _MakeLoopScript.py_ loads the CIM XML files one at a time into Blazegraph, and then extracts a feeder model
  * Use this after the CIM XML files have been created  
  * Blazegraph must be set up
  * Invoke ```python MakeLoopScript.py -b``` to make  _convert\_xml.sh_, which converts all CIM XML into DSS and GLM files
  * Invoke ```python MakeLoopScript.py -d``` to make _check.dss_, after which invoke ```opendsscmd check.dss``` to batch-solve all converted DSS files
* _MakeGlmTestScript.py_ creates _check\_glm.sh_ that will solve all supported test circuits in GridLAB-D
* _Compare_Cases.py_ has been described in steps 8 and 9 above

The funcionality of these two scripts has been incorporated above, so they might be removed:

* _MakeTable.py_ gathers OpenDSS solution summary information from CSV files into _table.txt_
* _MakeConversionScript.py_ creates _ConvertCDPSM.dss_ that will batch-load all supported test circuits into OpenDSS, and export CIM XML
	* Assumes the OpenDSS **source tree** has been checked out to _c:\opendss_
	* Assumes the EPRI DPV models have been downloaded to directories like _c:\epri_dpv|J1_ or _~/src/epri_dpv/J1_
	* After ```python MakeConversionScript.py``` invoke ```opendsscmd ConvertCDPSM.dss```

## Deprecated

Helper scripts on Windows (have not been updated for containerized Blazegraph):

* _compile.bat_ recompiles the Java CIM Importer; this step can't be included within _import.bat_ on Windows
* _drop\_all.bat_ empties the triple-store
* _import.bat_ will run the Java importer against the triple-store. Within this file:
  * the ```-o=dss``` option creates an OpenDSS model from CIM
  * the ```-o=glm``` option creates a GridLAB-D model from CIM 
  * the ```-o=both``` option creates both OpenDSS and GridLAB-D models from CIM 
  * the ```-o=idx``` option creates a JSON index of all Feeders in the triple-store. Use this to obtain valid mRID values for the -s option


