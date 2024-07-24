CIMHub Test Cases for OEDI
==========================

Copyright (c) 2017-2022, Battelle Memorial Institute

Contents
--------

The archived files for a 123-bus system include:

1. The CIM XML and UUID files are in *IEEE123\_PV.xml* and *ieee123\_pv\_uuids.dat*. 
   The CIM measurement UUID values are maintained in *IEEE123\_PV\_msid.json*
2. The exported OpenDSS model files are in *dss\_files.zip*
3. The exported GridLAB-D model files are in *glm\_files.zip*
4. The exported comma-separated value (CSV) files are in *csv\_files.zip*
5. A sample exported dictionary of CIM objects and measurements is in *IEEE123\_PV\_dict.json*

Process
-------

The test cases in *cases.json* are configured as decribed in 
`Test Case Configuration <../README.rst#Test-Case-Configuration>`_. The
`Command-Line Reference <../README.rst#Command-Line-Reference>`_ describes available
**export\_options** for each case.

The test case conversion is executed with ``python3 onestep.py``. The steps cover:

1. Solve the original GridAPPS-D case in OpenDSS, then create CIM XML
2. Upload the CIM XML to Blazegraph
3. List and insert CIM measurement points on the feeder
4. Export CSV, DSS, and GridLAB-D (GLM) files from Blazegraph
5. Solve the exported models in OpenDSS and GridLAB-D
6. Compare the original OpenDSS power flow result with exported OpenDSS and GridLAB-D power flow results

Load Flow Comparisons
---------------------

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on 
interpreting the `Results <onestep.inc>`_.

..
    literalinclude:: onestep.inc
   :language: none
   However, GitHub README will not support include files


Supplemental Files
------------------

The file *convert\_extra.dss* creates modified versions of two IEEE test systems, for the OEDI project:

- *IEEE13\_PV* is based on the 13-bus test case with solar and storage added. For use with ATP, 
  switches were also added to separate solar and storage inverters that were connected to the same 
  bus in the load flow model.
- *IEEE390\_PV* is based on the North American Low-Voltage test system, with 390 buses and the 
  secondary cables in parallel. Eight 1-MW PV systems have been added to 480-Volt load buses.
