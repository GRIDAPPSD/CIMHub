IEEE 9500-Node Test Case Files
==============================

Copyright (c) 2017-2022, Battelle Memorial Institute

This directory contains the power system model files and scripts to help 
convert the CIM XML model to other formats and compare the power flow 
solutions.  

CIM XML Model Files
-------------------

These are contained in the Base subdirectory.  There are separate model 
versions for balanced and unbalanced load models.  

Original DSS Source File
------------------------

These are the original files used to derive the model from IEEE 8500 Node 
model and contain in-line comments explaining the model changes.  There 
are separate model versions for balanced and unbalanced load models.  
These files are located in the original_dss subdirectory.  

Model Semi-Geographic Rendering
-------------------------------

.. image:: geoview.png

Test Procedure (CIMHub Installed)
---------------------------------

The purpose of this test is to verify the model after changes to the CIM 
schema or CIMHub code, and package the model files for distribution.  It 
assumes you already have CIMHub installed, including Blazegraph, the 
Python package, and the Java program.  If not, please see directions at 
the bottom of this page.
  
The test cases in *cases.json* are configured as decribed in 
`Test Case Configuration <../README.rst#Test-Case-Configuration>`_. The
`Command-Line Reference <../README.rst#Command-Line-Reference>`_ describes available
**export\_options** for each case..

1. Invoke *python3 onestep.py*. Check the new results against those below.  
   Also use *git diff* to identify any changes to the XML or UUID files.
2. These cases use the *-m=2* export option to include files *\*edits2.dss*
   after the network model. An editing command in these include files sets
   the OpenDSS *vminpu* parameter to 0.88, which matches the source files.
   The default value of *vminpu* is 0.95, and non-default values are not part
   of the CIM-based schema.
3. Invoke *./zipall.sh* to update the downloadable archives.  

Load Flow Comparisons
---------------------

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on 
interpreting the results.

`Balanced Load Results <onestep_bal.inc>`_.

`Unbalanced Load Results <onestep_unbal.inc>`_.

..
    literalinclude:: onestep_bal.inc
   :language: none
   However, GitHub README will not support include files

Test Procedure while Building CIMHub / (DEPRECATED)
---------------------------------------------------

The CIMHub repo contains a set of scripts for converting the CIM XML model 
to OpenDSS and GridLab-D file formats.  

It also can compare the power flow solution results (if OpenDSS and 
GridLab-D are installed on your local machine) 

To run the conversion and power flow solution script, using the archived 
CIM XML files, follow the instructions below: 

1. Clone the feature/cimext branch of the CIMHub repository: 
   *git clone https://github.com/GRIDAPPSD/CIMHub.git -b feature/cimext*
2. Install the CIMHub Python package. From your home directory, run 
   *python3 -m pip install -e CIMHub*
3. Build the CIMHub java libraries by changing directories into cimhub library 
   with *cd CIMHub/cimhub*. Build the java library with *mvn clean install*
4. Return to the main CIMHub directory with *cd ..* and install the Blazegraph database engine:

   - Install the [Docker Engine](https://docs.docker.com/install/)
   - Install the Blazegraph engine with *docker pull lyrasis/blazegraph:2.1.5*
   - Install the CIMHub docker package with *docker pull gridappsd/cimhub:1.0.1*
   - Start the Blazegraph engine by running *./start.sh*
   - Exit the docker terminal with *exit*

5. Change directories into the 9500 node folder with *cd ieee9500*
6. Edit the python script test9500bal.py or test9500unbal.py and change the file path 
   in line 41 and 45 to your local directory */your/local/path/CIMHub/ieee9500/base*
7. Run *python3 test9500bal.py* or *python3 test9500unbal.py* to convert the CIM XML model
8. Run *./zipall.sh* to create downloadable archives

To build the CIM XML files from the original DSS source files:

1. Download the `cimext branch of OpenDSScmd <https://github.com/GRIDAPPSD/GOSS-GridAPPS-D/tree/feature/cimext/opendss>`_

   - Clone the GOSS-GridAPPSD repo with *git clone https://github.com/GRIDAPPSD/GOSS-GridAPPS-D.git -b feature/cimext*
   - If OpenDSScmd is already installed, check its location with *which opendsscmnd*.
   - Move the opendsscmd executable with *sudo cp -i /YOUR_HOME_PATH/GOSS-GridAPPS-D/opendss/opendsscmd /usr/local/bin*

2. Uncomment lines 41 and 46 in test9500bal.py and test9500unbal.py. Now, the script will read 
   from the original_dss directory and build the CIM XML files
3. Re-run *python3 test9500bal.py* or *python3 test9500unbal.py* to re-build the XML files and 
   solve the power flow solution.

