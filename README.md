# CIMHub

Copyright (c) 2017-2020, Battelle Memorial Institute

This is a tool set for translating electric power distribution system models between
various formats, using the IEC Standard 61970/61968 Common Information Model (CIM) as the "Hub".

The CIM data is stored in an open-source triple-store called Blazegraph.  
Python 3 scripts depend on SPARQLWrapper.  The Java code uses 
OpenJDK 11 and builds with Apache Maven.  

Please make sure that GIT LFS is installed before checking out or cloning this repository.

## Docker and Blazegraph Setup

Blazegraph requires Java 8, which is no longer widely available for new installations.  Blazegraph isn't compatible with Java 9 or newer versions. Therefore, we recommend using Blazegraph in a Docker container: 

1. Install the [Docker Engine](https://docs.docker.com/install/)
2. Install the Blazegraph engine with _docker pull lyrasis/blazegraph:2.1.5_

## End User Instructions

To convert files from OpenDSS to CIM and GridLAB-D, without writing code:

1. Install the converter with _docker pull temcderm/cimhub:0.0.1_
2. From a Terminal, start the converter and Blazegraph with _./start.sh_
3. From inside the Docker Terminal, run two example conversions of the IEEE 13-Bus example:
   * _cd example_
   * _./example.sh_
   * _tail sum*.csv_ to verify that the converted OpenDSS files ran correctly
   * see the comments embedded in _example.sh_ for more information
4. To shut down the converter:
   * _exit_ from inside the Docker Terminal
   * _./stop.sh_ from the host Terminal

You may re-run the example starting from step 2.  You may also wish to modify 
_docker-compose.yml_ so that it mounts a local directory inside the 
converter, for transferring your own files between the host and Docker.

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
that opendsscmd and liblinenoise have been built in sibling directories to this one.

