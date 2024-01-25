Copyright (c) 2017-2022, Battelle Memorial Institute

This is a tool set for translating electric power distribution system 
models between various formats, using the IEC Standard 61970/61968 Common 
Information Model (CIM) as the "Hub".  

`Requirements <requirements.md>`_

`License <license.md>`_

The CIM data is stored in an open-source triple-store called Blazegraph.  
Python 3 scripts depend on SPARQLWrapper.  The Java code uses OpenJDK 11 
and builds with Apache Maven.  

Please make sure that GIT LFS is installed before checking out or cloning 
this repository.  

Schema
------

For an introduction to the CIM, see `EPRI's CIM Primer <https://www.epri.com/research/products/000000003002006001>`_, 
which is currently free to the public. 
Then see 
`Profile Unified Modeling Language (UML) <https://cimhub.readthedocs.io/en/latest/CDPSM.html>`_ for documentation of the schema used in CIMHub.

Installation
------------

CIMHub requires either Java 11 and Python 3.8+, or Docker.  It runs on 
Linux, Windows or Mac OS X.  Some of the **optional** `converters to 
OpenDSS <converters>`_ may only work on Windows, especially in cases where 
the input file comes from a Windows-only database.  

Option 1: Java and Python
^^^^^^^^^^^^^^^^^^^^^^^^^

Unless you already have Docker installed, this option is probably more convenient.
However, there may be technical or licensing concerns with installation of Java. If so,
please consider the Docker option below.

1. Install the Python package with ``pip install cimhub --upgrade``
2. Install Java Development Kit (JDK) 11 or later `as instructed <https://docs.oracle.com/en/java/javase/11/install/index.html>`_
3. Install Blazegraph 2.1.6 from `Blazegraph Releases <https://github.com/blazegraph/database/releases>`_
4. Install the CIMHub exporter by downloading a JAR file from `CIMHub Releases <https://github.com/GRIDAPPSD/CIMHub/tree/feature/SETO/releases>`_
5. Install `opendsscmd <https://sourceforge.net/projects/electricdss/files/OpenDSSCmd/>`_

Option 2: Docker
^^^^^^^^^^^^^^^^

With this option, you don't have to install Java directly. The Docker container
encapsulates Java 11 with a compatible version of Blazegraph and the CIMHub exporter. 

1. Install the `Docker Engine <https://docs.docker.com/install/>`_
2. Install the CIMHub exporter with *docker pull gridappsd/cimhub:1.1.0*. This
   includes Blazegraph, Python support, OpenDSSCmd, GridLAB-D, and example files.

End User Instructions
---------------------

Getting Started Example with Java/Python Option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example converts two versions of the IEEE 13-Bus case from OpenDSS to 
CIM and GridLAB-D, without writing code.  One version uses phase impedance 
matrices for line segments.  The other version, labeled "Assets", uses 
wire and spacing data for the line segments, and transformer code data for 
the transformers.  

1. From a command prompt in the Blazegraph installation directory, start the Blazegraph 
   engine with ``java -server -Xmx4g -jar blazegraph.jar``
2. From another command prompt in the examples directory **TBD**

Getting Started Example with Docker Option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Docker image for CIMHub is based on Linux (Debian 11, aka "Bullseye"),
so even when Docker is hosted on Windows, the CIMHub commands use Linux syntax.
There are three directories within the Docker image for CIMHub:

1. **/app** contains the CIMHub code and examples. Changes to this directory
   do not persist between sessions, but you may copy the contents as needed.
2. **/data** is a persistent volume of data for your own use. The Blazegraph
   database engine keeps data here, and you may copy or create new files here.
3. **/platform** is a volume bound to a directory on your host computer, i.e.,
   you may exchange data between the Docker image and the host file system
   through this volume. As shipped, **/platform** points to a directory of
   GridAPPS-D feeder models cloned from GitHub, which you may not have on
   your host file system. However, you can change or add bound volumes
   to match your own use case. See the last line of `docker-compose.yml <docker-compose.yml>`_
   for an example.

The first example converts two versions of the IEEE 13-Bus case from OpenDSS to 
CIM and GridLAB-D, without writing code.  One version uses phase impedance 
matrices for line segments.  The other version, labeled "Assets", uses 
wire and spacing data for the line segments, and transformer code data for 
the transformers.  

1. From a Terminal, start the converter and Blazegraph with *./start.sh*
2. From inside the Docker Terminal, run two example conversions of the IEEE 13-Bus example:


   - *cd /data*
   - *./go.sh &*
   - *cd /app/example*
   - *./example.sh*
   - *tail sum\*.csv* to verify that the converted OpenDSS files ran correctly
   - see the comments embedded in *example.sh* for more information

3. Still inside the Docker Terminal, run a Python-based test suite:

   - *cd ../tests*
   - *./test\_combiner.sh* will combine 6 CDPSM profiles into a single CIM XML file.
   - *python3 test_cimhub.py* checks the basic functionality of circuit conversion, measurements, houses and DER. 
     Six tuples are left in the database; these are CIM version strings.
   - *python3 test_comparisons.py* compares OpenDSS and GridLAB-D solutions, to the pre-conversion OpenDSS model
   - *python3 test_drop.py* checks the drop_circuit function
   - *python3 test_der.py* checks the insert_der and drop_der functions
   - *python3 onestep.py* checks power flow solutions on 5 variants of the IEEE 13-bus system
   - *python3 naming.py* checks power flow solutions with mRID naming

4. Still inside the Docker Terminal, run the full set of examples:

   - *cd ..*
   - *python3 batch\_tests.py* will run a set of examples that may take several minutes to complete.
   - Check *\*.inc* files in the example sub-directories for output results.
   - Check *\*.log* files in the example sub-directories for detailed warnings and errors.

5. To shut down the container:

   - *exit* from inside the Docker Terminal
   - *./stop.sh* from the host Terminal (**TODO**: this currently empties the /data volume)

The example script may produce error messages upon first invocation, 
because the Blazegraph engine doesn't start immediately.  However, the 
example does complete successfully.  You may re-run the example starting 
from step 1.  You may also wish to modify *docker-compose.yml* so that it 
mounts a local directory inside the converter, for transferring your own 
files between the host and Docker.

Converting Other Circuits
^^^^^^^^^^^^^^^^^^^^^^^^^

To convert your own circuits from OpenDSS to CIM and GridLAB-D, follow the IEEE 13-Bus
example described above, with some changes:

1. First read the `OpenDSS note on Common Information Model <doc/Common_Information_Model.pdf>`_ 
   for background on how the univeral unique identifiers (UUID) are managed for CIM.
2. The first time you run the conversion process on a new circuit, OpenDSS must create 
   random UUID values. To account for this:

   - In the example `cim_test.dss <example/cim_test.dss>`_ file, comment out (with //) 
     any lines invoking the *uuids* command
   - In the `example.sh <example/example.sh>`_ file, you have to replace the *-s* 
     parameter with a correct one for your new circuit. For example, 
     *DFBF372D-4291-49EF-ACCA-53DAFDE0338F* should be changed to a new value. 
     The correct value will be found on line 1 of the generated *\*UUIDS.dat* 
     file for your new circuit. You can generate this file by executing line 13 
     of *example.sh* by itself, i.e., run *opendsscmd cim_test.dss*. Then, 
     copy the new mRID from line 1 of the output *\*UUIDS.dat* file into 
     line 24 and/or line 29 of the *example.sh* file. Optionally, comment out 
     line 13 because you don't need to run that step again, although it does 
     no harm to do so.
   - To re-run the conversion process on the same circuit, you should first 
     uncomment the *uuids* command that you commented out in the first bullet. 
     This way, OpenDSS will reuse the UUID values, including the first one for the circuit.

If you don't have an OpenDSS model, see the `converters <./converters>`_ provided in this repository.

Command-line Reference
^^^^^^^^^^^^^^^^^^^^^^

Usage and options for ``java gov.pnnl.gridappsd.cimhub.CIMImporter [options] output_root``, in 
the format like ``-h=1`` to use houses in GridLAB-D exports.

====== ========================= =========================================================================================================================================================
Option Values                    Description
====== ========================= =========================================================================================================================================================
-q     XML filename              Optional file with CIM namespace and component queries (defaults to built-in CIM100 with GMDM and PNNL extensions)
-s     mRID                      Select one feeder by CIM mRID; selects all feeders if not specified
-o     glm,dss,both,idx,cim,csv  Output format; defaults to glm; currently cim supports only CIM14
-l     [0.0 - 1.0]               Load scaling factor; defaults to 1
-f     50, 60                    System frequency; defaults to 60
-e     Deri,Carson,FullCarson    Earth model for OpenDSS, defaults to Deri but GridLAB-D supports only Carson
-n     schedule name             Root filename for scheduled ZIP loads (defaults to none), valid only for -o=glm
-z     [0.0 - 1.0]               Constant Z portion of load (defaults to 0 for CIM-defined LoadResponseCharacteristic)
-i     [0.0 - 1.0]               Constant I portion of load (defaults to 0 for CIM-defined LoadResponseCharacteristic)
-p     [0.0 - 1.0]               Constant P portion of load (defaults to 0 for CIM-defined LoadResponseCharacteristic)
-r     0, 1                      Determine ZIP load fraction based on given xml file or randomized fractions
-h     0, 1                      Ask for house load objects exported to supplement EnergyConsumers
-x     0, 1                      Indicate whether for glm, the model will be called with a fault_check already created
-t     0, 1                      Request timing of top-level methods and SPARQL queries, requires -o=both for methods
-u     URI                       Blazegraph uniform resource identifier (if connecting over HTTP); defaults to http:localhost:8889/bigdata/namespace/kb/sparql
-a     0, 1                      Ask for shape, schedule, and player references to be exported for time-series power flow
-m     0, 1, 2, 3                Insert a reference to an include file of manual edits to exported models; 0=none, 1=before network, 2=after network, 3=both locations
-d     0, 1, 2                   Use of safe name, name, or mRID to identify simulator objects; defaults to safe name. Safe name replaces characters from the set " .=+^$*|[]{}\\" with \_
====== ========================= =========================================================================================================================================================

The output format options for ``-o=`` are:

===== ===============================================================================================================
Value Description
===== ===============================================================================================================
cim   creates a CIM14 model from CIM100
csv   creates a set of comma-delimited text files from CIM100
dss   creates an OpenDSS model from CIM100
glm   creates a GridLAB-D model from CIM 100
both  creates both OpenDSS and GridLAB-D models from CIM100 
idx   creates a JSON index of all Feeders in the triple-store. Use this to obtain valid mRID values for the -s option
===== ===============================================================================================================

If you will need both OpenDSS and GridLAB-D files, the ``-o=both`` option 
is much more efficient than generating them individually, because over 90% 
of the execution time is taken up with SPARQL queries that are common to 
both.  

Test Case Configuration
^^^^^^^^^^^^^^^^^^^^^^^

In each directory, the main suite of test cases is configured by entries in the *cases.json* file,
where each case has the following attributes:

The *cases.json* file contains an array of case definitions, where each 
case has the following attributes: 

- **mRID** master resource identifier (mRID) of the Feeder to select from Blazegraph for this case. 
  Most CIM objects have a mRID, which is a universally unique identifier (UUID) following the Web standard RFC 4122.
- **root** common part of case file names, usually matches the incoming OpenDSS circuit name
- **inpath\_dss** relative path to incoming OpenDSS models, including shapes. Will store base 
  *snapshot* and/or *time-series* power flow results. Must be specified. For example, *./base/*
- **dssname** file name of the incoming "master" OpenDSS file, often *root.dss*
- **path\_xml** relative path to output CIM XML files, including archived UUID files to persist 
  the mRIDs. Stores the base **snapshot** power flow results. Typically *./xml/*
- **outpath\_dss** relative path to output OpenDSS files, typically *./dss/*. 
  WARNING: contents may be deleted and rewritten on subsequent exports. To forego OpenDSS export, 
  omit this attribute, or specify as None or an empty string.
- **outpath\_glm** relative path to output GridLAB-D files, typically *./glm/*. 
  WARNING: contents may be deleted and rewritten on subsequent exports. To forego GridLAB-D export, 
  omit this attribute, or specify as None or an empty string.
- **dss\_controls** if specified and *true*, will run the incoming and converted OpenDSS files 
  in static control mode. The default is to run with controls off.
- **dss\_tolerance** if specified, will run the incoming and converted OpenDSS files with this 
  solution tolerance. The default is 1e-8.
- **skip\_gld** will forego GridLAB-D export and validation if *true*, regardless of whether
  *outpath\_glm* has been set. This can be more convenient than removing *outpath\_glm*, which is now the
  preferred method, if you are temporarily using an older version of GridLAB-D.
- **outpath\_csv** relative path to output comma-separated value (CSV) files, typically *./csv/*. 
  WARNING: contents may be deleted and rewritten on subsequent exports. 
  To forego CSV export, omit this attribute, or specify as None or an empty string.
- **glmvsrc** RMS line-to-neutral voltage for the GridLAB-D *substation* source. Use nominal 
  line-to-line voltage, divided by square root of three, then multiplied by per-unit voltage 
  from the OpenDSS circuit definition.
- **bases** array of nominal line-to-line voltage bases for power flow comparisons of per-unit 
  voltages. Specify in ascending order, not including 208.0, which is always considered.
- **substation** optional name of the CIM Substation. This may be used to help organize multiple feeders.
- **region** optional name of the CIM GeographicalRegion. This may be used to help organize multiple feeders.
- **subregion** optional name of the CIM SubGeographicalRegion. This may be used to help organize multiple feeders.
- **substationID** optional mRID of the CIM Substation. This may be used to help organize multiple feeders.
- **regionID** optional mRID of the CIM GeographicalRegion. This may be used to help organize multiple feeders.
- **subregionID** optional mRID of the CIM SubGeographicalRegion. This may be used to help organize multiple feeders.
- **export\_options** command-line options passed to the Java model exporter.  
  See `Command-line Reference`_ for more details.
- **check\_branches** optional array of individual branches to compare pre-conversion and post-conversion 
  snapshot power flow solutions. Either the *dss* or *gld* pairs may be omitted.

  - **dss\_link** name of an OpenDSS branch to compare the current and power flow.
  - **dss\_bus** name of an OpenDSS bus at one end of the **dss\_link** for comparing voltages, 
    and calculating power from the current flow.
  - **gld\_link** name of a GridLAB-D branch to compare the current and power flow.
  - **gld\_bus** name of a GridLAB-D bus at one end of the **gld\_link** for comparing voltages, 
    and calculating power from the current flow.

The *onestep.py* file reads *cases.json* into a Python dictionary, then processes it. Alternatively, you may create
this dictionary programmatically in the Python script.

- The last line of the script, calling *convert\_and\_check\_models*, performs all steps in sequence.
- The first argument is the *case* dictionary, in which attribute values control how the conversions 
  and comparisons are done.
- The second argument *bClearDB*, will empty the Blazegraph database right away. 
  This is most convenenient for testing, but use caution if the database may contain other circuits.
- The third argument, *bClearOutput*, will remove any *outpath\_dss*, *outpath\_glm*, *outpath\_csv* 
  specified in *cases*. USE CAUTION if these directories may contain other files, or manual edits. 
  The output directories are created or re-created as necessary.
- The fourth argument, *glmScheduleDir*, specifies where to find GridLAB-D's appliance and 
  commercial schedules, which may be needed for the *-h* and *-a* export options.

Round-trip Validation
^^^^^^^^^^^^^^^^^^^^^

The script outputs include the comparisons requested from **check_branches**, and summary information:

- **Nbus** is the number of buses found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **Nlink** is the number of links found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **MAEv** is the mean absolute voltage error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in per-unit. This is based on line-to-neutral voltages.
  In an ungrounded system, MAEv can be large. Use the line-to-line voltage comparisons from **check_branches** for ungrounded systems.
- **MAEi** is the mean absolute link current error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in Amperes

**GridLAB-D results were obtained with v5 on Ubuntu.** This version has 
important fixes that are not yet released on Windows.  Furthermore, 
GridLAB-D has assumptions and component models that differ from those in 
OpenDSS, which may affect the comparison of solutions between them: 

1. There is no neutral impedance for transformer connections in GridLAB-D.
2. The ``shunt_impedance`` is only implemented for WYE-WYE or SINGLE_PHASE transfromers in GridLAB-D.
3. GridLAB-D transformers only have two windings.
4. The regulator impedance is modeled differently.
5. Capacitor banks are always on in the converted GridLAB-D model; control parameters are translated but not activated.
6. GridLAB-D calculates line parameters with Carson's equations, as simplified in Kersting's book. 
   OpenDSS defaults to Deri's method, but it offers Full Carson and Carson options. Specify ``Carson`` 
   for compatibility. (Deri is the OpenDSS default because it's easy to calculate, and it closely 
   matches Full Carson.)
7. In GridLAB-D, wye/delta transformers have to be converted to delta/wye, swapping primary and 
   secondary windings. With **check_branches**, choose an adjacent branch for proper comparisons.
8. Single-phase generators (*diesel\_dg*) are not allowed in GridLAB-D, and in version 5,
   the *phases* attribute has been removed from *diesel\_dg*.
9. In a constant-current load model, the angle rotations are not exactly correct, especially for unbalanced loads or 
   loads connected in Delta. See `GridLAB-D Issue 1312 <https://github.com/gridlab-d/gridlab-d/issues/1312>`_. 
   This has been corrected in GridLAB-D version 5.
10. In GridLAB-D, the IEEE13 results are affected by a bug in default solar insolation.  
    See `GridLAB-D Issue 1333 <https://github.com/gridlab-d/gridlab-d/issues/1333>`_. 
    This has been corrected in GridLAB-D version 5.

If these effects cannot be mitigated, one could either remove the unsupported feature from the test case, or
use **skip_gld** for the test case.

Some other limitations on the validation process include:

1. **MAEv** is limited to the line-to-neutral voltages. Using **check_branches** can partially mitigate this, but it does not implement a systematic comparison of line-to-line voltages.
2. **MAEi** misses the regulators; it captures lines, transformers and switches.
3. **MAEi** misses the shunt components, e.g., loads, capacitors, DER.

Developer Notes
---------------

In order to develop Python code for the CIM, it should suffice to *pip3 install sparqlwrapper* and then
use existing Python code under *./src\_python* for guidance.

In order to modify the CIMHub Java code, you will need to install `Apache Maven <https://maven.apache.org>`_ and then use *mvn clean install*.

In order to build the cimhub docker container, use the *./build.sh* script. However, that script assumes
that opendsscmd and liblinenoise have been built in sibling directories to this one. When finished, an
authorized developer can push the new image to DockerHub, e.g., *docker push gridappsd/cimhub:1.1.0*

Automated Test Suite
^^^^^^^^^^^^^^^^^^^^

From this directory, ``python3 batch_tests.py`` will recursively execute the test suites
in several sub-directories.

- The Blazegraph engine must have been started first.  Existing contents will be deleted.
- Previous test suite outputs will be erased.
- The test suites will take several minutes to finish.
- Upon completion:

  - Use *git status* to identify any summary outputs that have changed
    in files named *\*.inc*.  Then use *git diff* on those *\*.inc* files to
    determine the significance of any changed outputs that occurred.
  - Check *\*.log* files in the sub-directories for detailed warnings and errors.

- This automated test suite should be run before making any pull requests.
- New CIMHub features and examples should be added to *batch\_tests.py* as they are developed.

cimhub Python Package Testing and Deployment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Python source code is now in ``src_python/cimhub``. To test it:

1. ``cd tests``
2. ``python3 test_cimhub.py`` checks the basic functionality of circuit conversion, measurements, houses and DER. Six tuples are left in the database; these are CIM version strings.
3. ``python3 test_comparisons.py`` compares OpenDSS and GridLAB-D solutions, to the pre-conversion OpenDSS model
4. ``./test_combiner.sh`` uses ``test_combiner.py`` to combine 6 CDPSM profiles into a single CIM XML file. Note: you must first run *./example.sh arg* from the *example* subdirectory, as described above.
5. ``python3 test_drop.py`` checks the drop_circuit function
6. ``python3 test_der.py`` checks the insert_der and drop_der functions
7. ``python3 onestep.py`` checks power flow solutions on 5 variants of the IEEE 13-bus system
8. ``python3 naming.py`` checks power flow solutions with mRID naming

The steps for deployment to PyPi are:

1. ``rm -rf dist``
2. ``python3 -m build``
3. ``twine check dist/*`` should not show any errors
4. ``twine upload -r testpypi dist/*`` requires project credentials for cimhub on test.pypi.org
5. ``pip install -i https://test.pypi.org/simple/ cimhub==1.1.0`` for local testing of the deployable package, example version 1.1.0
6. ``twine upload dist/*`` final deployment; requires project credentials for cimhub on pypi.org

GridAPPS-D Platform Circuit Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If working on the platform:

- ``mvn clean install`` from this repository to ensure you have the latest, branch-compatible CIMHub
- Make sure you have the latest, branch-compatible opendsscmd from `GOSS-GridAPPS-D <https://github.com/GRIDAPPSD/GOSS-GridAPPS-D/tree/opendss/v1.2.16/opendss>`_
- Perform the GridAPPS-D tests from the latest, branch-compatible `Powergrid-Models/platform` <https://github.com/GRIDAPPSD/Powergrid-Models/tree/issue/1175/platform>`_.

Working with Blazegraph in Docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It could be more convenient to run only Blazegraph in a Docker container, writing code and queries on the host.

1. Start the containerized Blazegraph engine:

   - *docker run --name blazegraph -d -p 8889:8080 lyrasis/blazegraph:2.1.5* to create and start the container for Blazegraph
   - Only if something goes wrong: *docker logs -f blazegraph* to log the database and Java messages to the console
   - consult the Docker documentation for more details on how to stop and otherwise manage containers
   - subsequently, use *docker restart blazegraph* to restart the container

2. Point a web browser to *http://localhost:8889/bigdata*. On-line help on Blazegraph is available from the browser
3. Load some data from a CIM XML file into the browser
4. Run a query in the browser

   - the file *queries.txt* contains sample SPARQL that can be pasted into the Blazegraph browser window

You can also run the IEEE 13-bus example conversions from the host Terminal.

1. *cd example*
2. *./example.sh arg*

Step 2 provides a dummy argument so that the example script will select a different URL for Blazegraph. When
querying from the host, the URL contains *localhost:8889* but when querying from a Docker terminal, the URL
contains *blazegraph:8080*, which is valid only on the internal network that Docker creates. Also, with a
dummy argument, the example will try to run GridLAB-D on the converted example models. This will fail unless
you have GridLAB-D installed on the host. If you do have GridLAB-D, *tail test\*.csv* to check the results.

Directories
-----------

The actively maintained directories are:

- ``BES`` XML files for a 118-bus IEEE test system and 240-bus WECC test system, enhanced with inverter-based resources (IBR)
- ``CPYDAR`` Python scripts to create spreadsheet input files for the ePHASORSIM module of Opal-RT
- ``OEDI`` creates a version of the IEEE 123-Bus test circuit with DER, for the OEDI project
- ``cimhub/src`` Java source for CIMHub
- ``converters`` CYMDist and Synergi conversion to OpenDSS
- ``der`` test cases for DER with smart inverter functions as defined in IEEE Std. 1547-2018
- ``docs`` description of the CIM support in OpenDSS
- ``ecp`` test cases for load, PV, generator, and storage profiles, schedules, and shapes
- ``example`` test CIMHub on the IEEE 13-bus model
- ``gmdm`` test cases and scripts for the Grid Model Data Management interoperability tests in June 2022
- ``helics`` illustration of a CIM-defined link between transmission and distribution simulators under [HELICS](https://helics.org/)
- ``ieee4`` test cases for transformer connections
- ``ieee9500`` CIM, OpenDSS, GridLAB-D and CSV versions of the IEEE 9500-node test feeder
- ``line_constants`` test cases for calculating line parameters from CIM spacing and wire data
- ``lv_network`` test cases for European and North American low-voltage distribution networks
- ``model_output_tests`` scratch directory for model output tst results
- ``opendsscmd`` builds of opendsscmd for Windows and Linux to match the current CIMHub version
- ``queries`` text and xml files with SPARQL queries to use in a web browser, or from a Python script
- ``releases`` downloadable CIMHub files for end users
- ``src_python/cimhub`` Python source, bash scripts and supporting data files
- ``support`` contains GridLAB-D schedules for end-use, commercial, and thermostat-controlled loads
- ``tutorial`` illustrates use of CIMHub with houses in GridLAB-D to simulate data from load meters
- ``tests`` contains scripts to test functions of the cimhub Python module

To run the Python code, you may need to adjust the Blazegraph URL and CIM Namespace in ``cimhubconfig.json``. 
Set ``use_proxy: true`` in this file if your computer is running a proxy server, e.g., if you are connected 
to the PNNL VPN.

Unused code or data from the Powergrid-Models repository is now in *archive*

