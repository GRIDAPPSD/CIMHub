CIMHub Test Cases for IEEE 13-Bus System
========================================

Copyright (c) 2017-2022, Battelle Memorial Institute

Process
-------

The test cases are executed with *python3 onestep.py*. They cover the IEEE 13-bus system
with photovoltaic, storage, and single-phase centertap secondary transformer added. The option
for assets-based line and transformer modeling are also covered.

The test cases are configured by entries in the *cases.json* file.
Each array element is a dictionary with the following keys:

- **dssname** is the root file name of the original OpenDSS base case
- **root** is used to generate file names for converted files
- **mRID** is a UUID4 to make the test case feeder unique. For a new test case, generate a random new mRID with this Python script: ``import uuid;idNew=uuid.uuid4();print(str(idNew).upper())``
- **glmvsrc** is the substation source line-to-neutral voltage for GridLAB-D
- **bases** is an array of voltage bases to use for interpretation of the voltage outputs. Specify line-to-line voltages, in ascending order, leaving out 208 and 480.
- **export_options** is a string of command-line options to the CIMImporter Java program. ``-e=carson`` keeps the OpenDSS line constants model compatible with GridLAB-D's
- **skip_gld** specify as ``True`` when you know that GridLAB-D won't support this test case
- **check_branches** is an array of branches in the model to compare power flows and line-to-line voltages. Each element contains:

    - **dss_link** is the name of an OpenDSS branch for power and current flow; power delivery or power conversion components may be used
    - **dss_bus** is the name of an OpenDSS bus attached to **dss_link**. Line-to-line voltages are calculated here, and this bus establishes flow polarity into the branch at this bus.
    - **gld_link** is the name of a GridLAB-D branch for power and current flow; only links, e.g., line or transformer, may be used. Do not use this when **skip_gld** is ``True``
    - **gld_bus** is the name of a GridLAB-D bus attached to **gld_link**. Do not use this when **skip_gld** is ``True``

The script outputs include the comparisons requested from **check_branches**, and summary information:

- **Nbus** is the number of buses found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **Nlink** is the number of links found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **MAEv** is the mean absolute voltage error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in per-unit. This is based on line-to-neutral voltages.
In an ungrounded system, MAEv can be large. Use the line-to-line voltage comparisons from **check_branches** for ungrounded systems.
- **MAEi** is the mean absolute link current error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in Amperes

Results
-------

.. literalinclude:: onestep.inc
   :language: none

GitHub README will not support include files, so check here: `Results <onestep.inc>`_.

Limitations on Validation
-------------------------

GridLAB-D has assumptions and component models that differ from those in OpenDSS, which may affect
the comparison of solutions between them:

1. There is no neutral impedance for transformer connections in GridLAB-D.
2. The ``shunt_impedance`` is only implemented for WYE-WYE or SINGLE_PHASE transfromers in GridLAB-D.
3. GridLAB-D transformers only have two windings.
4. The regulator impedance is modeled differently.
5. Capacitor banks are always on in the converted GridLAB-D model; control parameters are translated but not activated.
6. In a constant-current load model, the angle rotations are not exactly correct, especially for unbalanced loads or loads connected in Delta. See `GridLAB-D Issue 1312 <https://github.com/gridlab-d/gridlab-d/issues/1312>`_. This has been corrected in GridLAB-D version 5.
7. GridLAB-D calculates line parameters with Carson's equations, as simplified in Kersting's book. OpenDSS defaults to Deri's method, but it offers Full Carson and Carson options. Specify ``Carson`` for compatibility. (Deri is the OpenDSS default because it's easy to calculate, and it closely matches Full Carson.)
8. In GridLAB-D, wye/delta transformers have to be converted to delta/wye, swapping primary and secondary windings. With **check_branches**, choose an adjacent branch for proper comparisons.
9. In GridLAB-D, the IEEE13 results are affected by a bug in default solar insolation.  See `GridLAB-D Issue 1333 <https://github.com/gridlab-d/gridlab-d/issues/1333>`_

If these effects cannot be mitigated, one could either remove the unsupported feature from the test case, or
use **skip_gld** for the test case.

Some other limitations on the validation process include:

1. MAEv is limited to the line-to-neutral voltages. Using **check_branches** can partially mitigate this, but it does not implement a systematic comparison of line-to-line voltages.
2. MAEi misses the regulators; it captures lines, transformers and switches.
3. MAEi misses the shunt components, e.g., loads, capacitors, DER.
