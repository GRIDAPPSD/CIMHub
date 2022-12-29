CIMHub Test Cases for S2G CPYDAR
================================

Copyright (c) 2017-2022, Battelle Memorial Institute

Contents
--------

The model files are versioned in subdirectories *ieee13x*, *ieee123x*, and *j1red*, each of which includes:

1. The original OpenDSS models files are in *\*.dss*, with *Master.dss* at the top level.
2. The CIM XML is in *\*.xml*
3. The UUID values are persisted in *\*\_uuids.dat*.
4. Base case power flow solution is in *\*\_?.csv*.

Loading and Testing CIM Models
------------------------------

The test cases in *cases.json* are configured as decribed in 
`Test Case Configuration <../README.rst#Test-Case-Configuration>`_. The
`Command-Line Reference <../README.rst#Command-Line-Reference>`_ describes available
**export\_options** for each case.

The test case conversion to CIM XML is executed with ``python3 test_CPYDAR.py``. The steps cover:

1. Solve the original cases in OpenDSS, then create CIM XML
2. Upload the CIM XML to Blazegraph
3. Export CSV, DSS, and GridLAB-D (GLM) files from Blazegraph
4. Solve the exported models in OpenDSS and GridLAB-D
5. Compare the original OpenDSS power flow results with exported OpenDSS and GridLAB-D power flow results

Exporting ePHASORSIM Spreadsheets
---------------------------------

The test case conversion to ePHASORSIM is executed with ``python3 ePHASORSIM.py [0,1,2]``.
The numerical command-line argument converts *ieee13x*, *ieee123x*, and *j1red*, respectively.
If not provided, the script converts *ieee13x* by default.

The ePHASORSIM exporter adds prefixes to the component names, in the effort to make them unique:

- Voltage Source prefix is VS\_
- Line prefix is LN\_
- Load prefix is LD\_
- Shunt prefix is SH\_
- Transformer prefix is XF\_
- Switch prefix is SW\_
- There is no prefix on Bus names

The exporter writes distributed energy resources (DER) as Loads with negative power if generating,
or with positive power for storage that is charging.

Load Flow Comparisons
---------------------

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on 
interpreting the `Results <onestep.inc>`_.

..
    literalinclude:: onestep.inc
   :language: none
   However, GitHub README will not support include files


