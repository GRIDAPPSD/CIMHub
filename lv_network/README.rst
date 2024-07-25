CIMHub Test Cases for Low-Voltage Distribution
==============================================

Copyright (c) 2021-2022, Battelle Memorial Institute

Process
-------

The test cases in *cases.json* are configured as decribed in 
`Test Case Configuration <../README.rst#Test-Case-Configuration>`_. The
`Command-Line Reference <../README.rst#Command-Line-Reference>`_ describes available
**export\_options** for each case.

The test cases are executed with ``python3 test_lvn.py``. They cover:

1. IEEE Low-voltage secondary network distribution, with parallel secondary lines retained
2. IEEE Low-voltage secondary network distribution, with secondary lines reduced from 
   5 or 6 in parallel, to 1 equivalent line
3. European Low-voltage radial distribution

Load Flow Comparisons
---------------------

For the IEEE 390-bus low-voltage network, the branch comparisons comprise two transformers, each
serving 4 radial primary feeders. For the European-style radial low-voltage circuit, the branch
comparison is at the feeder head.

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on 
interpreting the `Results <onestep.inc>`_.

..
    literalinclude:: onestep.inc
   :language: none
   However, GitHub README will not support include files

Notes on GridLAB-D Conversion
-----------------------------

For the IEEE 390-bus network, the secondary parallel lines have to be reduced for GridLAB-D. The model that
retains these parallel lines will not solve.

