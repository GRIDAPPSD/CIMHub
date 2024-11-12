.. role:: math(raw)
   :format: html latex
..

Installation
============

CIMHub runs on Windows, Linux, and Mac OS.  The components include an 
open-source NoSQL database, Java code, and Python code.  (Docker was 
required in earlier versions, but no longer.) All end-user scripting can 
be done in Python.  

Recommended Process with Java Installation
------------------------------------------

To install the pre-requisite components: 

- Install Java Development Kit (JDK) 11 or later from https://docs.oracle.com/en/java/javase/11/install/index.html
- Install Blazegraph 2.1.6 from https://github.com/blazegraph/database/releases 
  On Windows, it's suggested that you download this file to c:\\blazegraph\\blazegraph.jar, 
  and then create a helper file c:\\blazegraph\\go.bat with contents ``java -server -Xmx4g -jar blazegraph.jar``
- Install the CIMHub exporter by downloading a JAR file from https://github.com/GRIDAPPSD/CIMHub/tree/feature/SETO/releases
  This may be downloaded to the same directory as Blazegraph, or a different directory.
  You may also download the tutorial input files and sample queries from this web site.

   - Please choose ``blazegraph.jar`` to download. The tutorial configuration file ``cimhubjar.json`` will match.
   - If you download ``bigdata.jar``, the functionality is the same, but you'll have to change the namespace in ``cimhubjar.json``

- Install the latest Python from https://www.python.org/ or https://docs.conda.io/en/latest/
- Install the CIMHub Python package, and its dependencies, by invoking ``pip install cimhub`` from a command prompt.
- Install opendsscmd from https://sourceforge.net/projects/electricdss/files/OpenDSSCmd/

At this point, the non-tutorial examples are only available from the GitHub repository. These
will be packaged at a later time. For now:

- | From a command prompt, invoke 
  | ``git clone -b feature/SETO https://github.com/GRIDAPPSD/CIMHub.git``
- For testing SPARQL queries against CIM from a web browser, you then have access to examples in ``./queries/queries.txt``
- As a Java developer, you can then build from the repository's ``./cimhub`` subdirectory using Maven
- As a Python developer, you can then use ``pip install -e .`` from the repository's main directory

Using Docker to Avoid Java Installation
---------------------------------------

With this option, you would not have to install Java directly. The Docker container
encapsulates Java 8 with a compatible (and sufficient) version of Blazegraph. 

- Install the Python package with ``pip install cimhub --upgrade``
- Install the Docker Engine from https://docs.docker.com/install/
- Install the Blazegraph engine with ``docker pull lyrasis/blazegraph:2.1.5``

   - The namespace will have ``bigdata`` instead of ``blazegraph``. The ``cimhubdocker.json`` configuration file matches this assumption.

- Install the CIMHub exporter with ``docker pull gridappsd/cimhub:1.0.1``
- Install opendsscmd from https://sourceforge.net/projects/electricdss/files/OpenDSSCmd/

**Caveats**: the CIMHub container has not been updated for the tutorial and the
most recent CIMHub enhancements. Plans for future support are not firm, because
of recent changes in Docker terms. The main readme page for CIMHub still contains
instructions for running an example with the Docker container.

Source Code Installation
------------------------

- | From a command prompt, invoke 
  | ``git clone -b feature/SETO https://github.com/GRIDAPPSD/CIMHub.git``

