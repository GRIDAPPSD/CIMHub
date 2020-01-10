# CIMHub

Copyright (c) 2017-2019, Battelle Memorial Institute

This is a tool set for translating electric power distribution system models between
various formats, using the IEC Standard 61970/61968 Common Information Model (CIM) as the "Hub".

## Blazegraph Setup

Blazegraph requires Java 8, which is no longer widely available for new installations.  Blazegraph isn't compatible with Java 9 or newer versions. Therefore, we recommend using Blazegraph in a Docker container:

1. Install the [Docker Engine](https://docs.docker.com/install/)
2. Issue commands that install and start the containerized Blazegraph engine:
	 * _docker pull lyrasis/blazegraph:2.1.5_ to download the container for Blazegraph, only necessary the first time
	 * _docker run --name blazegraph -d -p 8889:8080 lyrasis/blazegraph:2.1.5_ to create and start the container for Blazegraph
	 * _docker logs -f blazegraph_ to log the database and Java messages to the console
	 * consult the Docker documentation for more details on how to stop and otherwise manage containers
   * subsequently, use _docker restart blazegraph_ to restart the containter
3. Point a web browser to _http://localhost:8889/bigdata_. On-line help on Blazegraph is available from the browser
4. Load some data from a CIM XML file, or any other XML triple-store
5. Run a query in the browser
	 * the file _queries.txt_ contains sample SPARQL that can be pasted into the Blazegraph browser window
6. Verify that the Blazegraph namespace is _kb_ and use that for the rest of these examples
	 * You can use a different namespace, but you'll have to specify that using the -u option for the CIMImporter, handediting the default _-u=http://localhost:8889/bigdata/namespace/kb/sparql_
	 * You can use a different namespace, but you may have to hand-edit some of the Python files (e.g. under the Meas directory)
	 * The GridAPPS-D platform itself may use a different namespace

