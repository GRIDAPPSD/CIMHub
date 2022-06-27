# CIMHub

Copyright (c) 2017-2022, Battelle Memorial Institute

This is a tool set for translating electric power distribution system models between
various formats, using the IEC Standard 61970/61968 Common Information Model (CIM) as the "Hub".

[Requirements](requirements.md)

[License](license.md)

The CIM data is stored in an open-source triple-store called Blazegraph.
Python 3 scripts depend on SPARQLWrapper.  The Java code uses 
OpenJDK 11 and builds with Apache Maven.

Please make sure that GIT LFS is installed before checking out or cloning this repository.

## Documentation

For an introduction to the CIM, see [EPRI's CIM Primer](https://www.epri.com/research/products/000000003002006001), which is currently free to the public. Then see [Profile Unified Modeling Language (UML)](https://gridappsd.readthedocs.io/en/develop/developer_resources/index.html#class-diagrams-for-the-profile) for documentation of the schema used in CIMHub.

## End User Instructions

CIMHub requires either Java 11 or Docker for the database engine, and 
Python version 3.8 or later.  It runs on Linux, Windows or Mac OS 
X.  Some of the [converters to OpenDSS](converters) may only work on 
Windows, in cases where the input file comes from a Windows-only database.  

### Option 1: Java and Blazegraph Setup

Unless you already have Docker installed, this option is probably more convenient.
However, there may be technical or licensing concerns with installation of Java. If so,
please consider the Docker option below.

1. Install the Python package with ```pip install cimhub --upgrade```
2. Install Java Development Kit (JDK) 11 or later [as instructed](https://docs.oracle.com/en/java/javase/11/install/index.html)
3. Install Blazegraph 2.1.6 from [releases](https://github.com/blazegraph/database/releases)
4. Install the CIMHub exporter by downloading a JAR file from [releases](https://github.com/GRIDAPPSD/CIMHub/tree/feature/SETO/releases)

### Option 2: Docker and Blazegraph Setup

With this option, you don't have to install Java directly. The Docker container
encapsulates Java 8 with a compatible (and sufficient) version of Blazegraph. 

1. Install the Python package with ```pip install cimhub --upgrade```
2. Install the [Docker Engine](https://docs.docker.com/install/)
3. Install the Blazegraph engine with _docker pull lyrasis/blazegraph:2.1.5_
4. Install the CIMHub exporter with _docker pull gridappsd/cimhub:1.0.4_

### Option 1: Getting Started Example with Java and Windows

This example converts two versions of the IEEE 13-Bus case from OpenDSS to CIM and GridLAB-D,
without writing code. One version uses phase impedance matrices for line segments. The other version,
labeled "Assets", uses wire and spacing data for the line segments, and transformer code data
for the transformers.

1. From a command prompt in the Blazegraph installation directory, start the Blazegraph engine with ```java -server -Xmx4g -jar blazegraph.jar```
2. From another command prompt in the examples directory _TBD_

### Option 2: Getting Started Example with Docker and Linux

This example converts two versions of the IEEE 13-Bus case from OpenDSS to CIM and GridLAB-D,
without writing code. One version uses phase impedance matrices for line segments. The other version,
labeled "Assets", uses wire and spacing data for the line segments, and transformer code data
for the transformers.

1. From a Terminal, start the converter and Blazegraph with _./start.sh_
2. From inside the Docker Terminal, run two example conversions of the IEEE 13-Bus example:
   * _cd example_
   * _./example.sh_
   * _tail sum*.csv_ to verify that the converted OpenDSS files ran correctly
   * see the comments embedded in _example.sh_ for more information
3. To shut down the converter:
   * _exit_ from inside the Docker Terminal
   * _./stop.sh_ from the host Terminal

The example script may produce error messages upon first invocation, 
because the Blazegraph engine doesn't start immediately.  However, the 
example does complete successfully.  You may re-run the example starting 
from step 1.  You may also wish to modify _docker-compose.yml_ so that it 
mounts a local directory inside the converter, for transferring your own 
files between the host and Docker.

### Converting Other Circuits

To convert your own circuits from OpenDSS to CIM and GridLAB-D, follow the IEEE 13-Bus
example described above, with some changes:

1. First read the [OpenDSS note on Common Information Model](doc/Common_Information_Model.pdf) for background on how the univeral unique identifiers (UUID) are managed for CIM.
2. The first time you run the conversion process on a new circuit, OpenDSS must create random UUID values. To account for this:
   * In the example [cim_test.dss](example/cim_test.dss) file, comment out (with //) any lines invoking the _uuids_ command
   * In the [example.sh](example/example.sh) file, you have to replace the _-s_ parameter with a correct one for your new circuit. For example, __DFBF372D-4291-49EF-ACCA-53DAFDE0338F should be changed to a new value. The correct value will be found on line 1 of the generated _*UUIDS.dat_ file for your new circuit. You can generate this file by executing line 13 of _example.sh_ by itself, i.e., run _opendsscmd cim_test.dss_. Then, copy the new mRID from line 1 of the output _*UUIDS.dat_ file into line 24 and/or line 29 of the _example.sh_ file. Optionally, comment out line 13 because you don't need to run that step again, although it does no harm to do so.
   * To re-run the conversion process on the same circuit, you should first uncomment the _uuids_ command that you commented out in the first bullet. This way, OpenDSS will reuse the UUID values, including the first one for the circuit.

If you don't have an OpenDSS model, see the [converters](./converters) provided in this repository.

### Command-line Reference

Usage and options for ```java gov.pnnl.gridappsd.cimhub.CIMImporter [options] output_root```

* ```-q={queries file}  // optional file with CIM namespace and component queries (defaults to CIM100)```
* ```-s={mRID}          // select one feeder by CIM mRID; selects all feeders if not specified```
* ```-o={glm|dss|both|idx|cim|csv}   // output format; defaults to glm; currently cim supports only CIM14```
* ```-l={0..1}          // load scaling factor; defaults to 1```
* ```-f={50|60}         // system frequency; defaults to 60```
* ```-e={Deri|Carson|FullCarson} // earth model for OpenDSS, defaults to Deri but GridLAB-D supports only Carson```
* ```-n={schedule_name} // root filename for scheduled ZIP loads (defaults to none), valid only for -o=glm```
* ```-z={0..1}          // constant Z portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)```
* ```-i={0..1}          // constant I portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)```
* ```-p={0..1}          // constant P portion (defaults to 0 for CIM-defined LoadResponseCharacteristic)```
* ```-r={0..1}          // determine ZIP load fraction based on given xml file or randomized fractions```
* ```-h={0..1}          // determine if house load objects should be added to supplement EnergyConsumers```
* ```-x={0, 1}          // indicate whether for glm, the model will be called with a fault_check already created```
* ```-t={0, 1}          // request timing of top-level methods and SPARQL queries, requires -o=both for methods```
* ```-u={http://localhost:8889/bigdata/namespace/kb/sparql} // blazegraph uri (if connecting over HTTP); defaults to http://localhost:8889/bigdata/namespace/kb/sparql```

The output format options are:

  * ```-o=cim```  creates a CIM14 model from CIM100
  * ```-o=csv```  creates a set of comma-delimited text files from CIM100
  * ```-o=dss```  creates an OpenDSS model from CIM100
  * ```-o=glm```  creates a GridLAB-D model from CIM 100
  * ```-o=both``` creates both OpenDSS and GridLAB-D models from CIM100 
  * ```-o=idx```  creates a JSON index of all Feeders in the triple-store. Use this to obtain valid mRID values for the -s option

If you will need both OpenDSS and GridLAB-D files, the ```-o=both``` option is much more efficient than generating them individually, 
because over 90% of the execution time is taken up with SPARQL queries that are common to both.

## Developer Notes

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
authorized developer can push the new image to DockerHub, e.g., _docker push gridappsd/cimhub:0.0.3_

### cimhub Python Package Testing and Deployment

The Python source code is now in ```src_python/cimhub```. To test it:

1. ```cd tests```
2. ```python3 test_cimhub.py``` checks the basic functionality of circuit conversion, measurements, houses and DER. Six tuples are left in the database; these are CIM version strings.
3. ```python3 test_comparisons.py``` compares OpenDSS and GridLAB-D solutions, to the pre-conversion OpenDSS model
4. ```./test_combiner.sh``` uses ```test_combiner.py``` to combine 6 CDPSM profiles into a single CIM XML file. Note: you must first run _./example.sh arg_ from the _example_ subdirectory, as described above.

The steps for deployment to PyPi are:

1. ```rm -rf dist```
2. ```python3 setup.py sdist```
3. ```python3 setup.py bdist_wheel```
4. ```twine check dist/*``` should not show any errors
5. ```python3 -m twine upload dist/*``` requires project credentials for cimhub on pypi.org

### GridAPPS-D Platform Circuit Validation

If working on the platform:

* ```mvn clean install``` from this repository to ensure you have the latest, branch-compatible CIMHub
* Make sure you have the latest, branch-compatible opendsscmd from [GOSS-GridAPPS-D](https://github.com/GRIDAPPSD/GOSS-GridAPPS-D/tree/opendss/v1.2.16/opendss)
* Perform the GridAPPS-D tests from the latest, branch-compatible [Powergrid-Models/platform](https://github.com/GRIDAPPSD/Powergrid-Models/tree/issue/1175/platform).

## Directories

The actively maintained directories are:

* ```cimhub/src``` Java source for CIMHub
* ```converters``` CYMDist and Synergi conversion to OpenDSS
* ```CPYDAR``` Python scripts to create spreadsheet input files for the ePHASORSIM module of Opal-RT
* ```der``` test cases for DER with smart inverter functions as defined in IEEE Std. 1547-2018
* ```doc``` description of the CIM support in OpenDSS
* ```example``` test CIMHub on the IEEE 13-bus model
* ```helics``` illustration of a CIM-defined link between transmission and distribution simulators under [HELICS](https://helics.org/)
* ```ieee4``` test cases for transformer connections
* ```ieee9500``` CIM, OpenDSS, GridLAB-D and CSV versions of the IEEE 9500-node test feeder
* ```model_output_tests``` scratch directory for model output tst results
* ```lv_network``` test cases for European and North American low-voltage distribution networks
* ```OEDI``` creates a version of the IEEE 123-Bus test circuit with DER, for the OEDI project
* ```queries``` text and xml files with SPARQL queries to use in a web browser, or from a Python script
* ```src_python/cimhub``` Python source, bash scripts and supporting data files
* ```support``` contains GridLAB-D schedules for end-use, commercial, and thermostat-controlled loads
* ```tests``` contains scripts to test functions of the cimhub Python module

To run the Python code, you may need to adjust the Blazegraph URL and CIM Namespace in ```cimhubconfig.json```. Set ```use_proxy: true``` in this file if your computer is running a proxy server, e.g., if you are connected to the PNNL VPN.

Unused code or data from the Powergrid-Models repository is now in ```archive```

