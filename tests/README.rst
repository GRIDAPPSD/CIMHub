CIMHub Test Cases for IEEE 13-Bus System
========================================

Copyright (c) 2017-2022, Battelle Memorial Institute

Process
-------

The test cases in *cases.json* and *name\_cases.json* are configured as decribed in 
`Test Case Configuration <../README.rst#Test-Case-Configuration>`_. The
`Command-Line Reference <../README.rst#Command-Line-Reference>`_ describes available
**export\_options** for each case.

The first set of test cases is executed with *python3 
onestep.py*.  They cover the IEEE 13-bus system with photovoltaic, 
storage, and single-phase centertap secondary transformer added.  The 
options for assets-based line and transformer modeling are also covered.  

The second set of test cases is executed with *python3 naming.py*. They show use
of CIM's IdentifiedObject.mRID instead of IdentifiedObject.name to identify circuit elements.

Results
-------

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on interpreting the results.

Datasheet and ZIP coefficient variations on the IEEE 13-bus circuit: `Results <onestep.inc>`_.

Use of mRID naming option on the IEEE 13-bus circuit: `Results <naming.inc>`_.

..
    literalinclude:: onestep.inc
   :language: none
   However, GitHub README will not support include files


