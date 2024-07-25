Scripts for EPRI/UCA GMDM Interoperability Tests
================================================

Copyright (c) 2017-2022, Battelle Memorial Institute

These scripts and data files were used to support PNNL's participation in 
the Grid Model Data Management (GMDM) interoperability tests at EPRI's 
Charlotte, NC office in June 2022.  

Process
-------

The base ("golden") planning assembly is invoked with *python 
adapt\_gmdm.py*.  This calls *step2.py* to perform part of the processing.  
Expected output is shown in the next section.  Furthermore: 

- The Blazegraph database engine must already be started.
- A GridLAB-D model is created, but power flow solution fails because GridLAB-D 
  does not report secondary switches or some of the regulator connections in the GMDM model.
- To run the test on a vendor's exported planning assembly, supply a directory on the 
  command line, e.g., *python adapt\_gmdm.py vendor1*.
- Use *python summarize\_db.py* or *python list\_db.py* to examine the full contents 
  of Blazegraph, after CIM XML has been uploaded.
- These scripts have only been tested on Windows.

Summary Results
---------------

The export model's summary power flow report for GMDM is shown below. 
For more detail, compare *dss/\*.csv* to the archived results in *base/dss/\*.csv*, 
or see the next section on *Load Flow Comparisons*.

``
OpenDSS solution from: dss/ SOLVED in 6 iterations
  Number of Devices=46 Buses=23 Nodes=60
  Line-Neutral Voltage min=0.9663    max=1.6516 pu
  Source P=403.33 kW    Q=-238.12 kVAR
  Loss   P=64.21 kW    Q=250.15 kVAR
Tap Changer     Position
  XF5_1            0
  XF5_2            0
  XF5_3            0
  XF3_1            0
  XF2_1            0
Object counts (with non-zero current flow):
  LINE               13
  VSOURCE             1
  STORAGE             1
  TRANSFORMER        11
  CAPACITOR           1
  LOAD                7
``
Load Flow Comparisons
---------------------

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on 
interpreting the `Results <adapt_gmdm.inc>`_.

..
    literalinclude:: adapt_gmdm.inc
   :language: none
   However, GitHub README will not support include files


