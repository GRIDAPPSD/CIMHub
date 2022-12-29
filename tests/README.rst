CIMHub Test Cases for IEEE 13-Bus System
========================================

Copyright (c) 2017-2022, Battelle Memorial Institute

Process
-------

The test cases in *cases.json* are configured as decribed in `Test Case Configuration <../README.rst#Configuration>`_
These test cases are executed with *python3 onestep.py*. They cover the IEEE 13-bus system
with photovoltaic, storage, and single-phase centertap secondary transformer added. The options
for assets-based line and transformer modeling are also covered.

Results
-------

For datasheet and ZIP coefficient variations on the IEEE 13-bus circuit: `Results <onestep.inc>`_.

For use of mRID naming option on the IEEE 13-bus circuit: `Results <naming.inc>`_.

..
    literalinclude:: onestep.inc
   :language: none
   However, GitHub README will not support include files


