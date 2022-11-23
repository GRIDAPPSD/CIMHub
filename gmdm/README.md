# Scripts for EPRI/UCA GMDM Interoperability Tests

Copyright (c) 2017-2022, Battelle Memorial Institute

These scripts and data files were used to support PNNL's participation in the Grid Model Data Management (GMDM)
interoperability tests at EPRI's Charlotte, NC office in June 2022.

## Process

The base ("golden") planning assembly is invoked with _python adapt\_gmdm.py_. This calls _step2.py_
to perform part of the processing. Expected output is shown in the next section. Furthermore:

- The Blazegraph database engine must already be started.
- A GridLAB-D model is created, but power flow solution fails because GridLAB-D does not report secondary switches or some of the regulator connections in the GMDM model.
- To run the test on a vendor's exported planning assembly, supply a directory on the command line, e.g., _python adapt\_gmdm.py vendor1_.
- Use _python summarize\_db.py_ or _python list\_db.py_ to examine the full contents of Blazegraph, after CIM XML has been uploaded.
- These scripts have only been tested on Windows.

## Results

The export model's power flow report is shown below. For more detail, compare 
_dss/*.csv_ to the archived results in _base/dss/*.csv_.

```
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
  OpenDSS branch flow in TRANSFORMER.XF3_1 from J1
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  39837.20  0.0000      3.47  0.7810     98.079 + j   -97.227     AB    69000.05  0.5236
    B  39837.20 -2.0944      4.04 -1.5985    141.608 + j   -76.599     BC    69000.05 -1.5708
    C  39837.20  2.0944      4.41  2.4688    163.646 + j   -64.297     CA    69000.05  2.6180
    Total S =   403.334 + j  -238.123
  OpenDSS branch flow in LINE.FBKR_A from J
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7210.13 -0.0017     25.76  1.1058     82.990 + j  -166.162     AB    12486.11  0.5218
    B   7207.59 -2.0961     26.76 -1.2415    126.630 + j  -145.517     BC    12488.90 -1.5735
    C   7206.09  2.0909     27.70  2.8231    148.475 + j  -133.453     CA    12478.52  2.6155
    Total S =   358.095 + j  -445.132
  OpenDSS branch flow in STORAGE.INDIV_RES_BATTERY from E1
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    120.16 -2.0996     42.43  0.8453     -5.001 + j    -0.997     AB      240.33 -2.0996
    B    120.17  1.0420     42.43 -2.2963     -5.001 + j    -0.997     BC        0.00  0.0000
    Total S =   -10.001 + j    -1.993
  OpenDSS branch flow in CAPACITOR.CAP_A1 from I1
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7226.94 -0.0035     28.91  1.5673      0.000 + j  -208.913     AB    12507.40  0.5196
    B   7215.36 -2.0979     28.86 -0.5280      0.182 + j  -208.245     BC    12504.25 -1.5751
    C   7216.04  2.0892     28.86 -2.6236      0.073 + j  -208.284     CA    12501.68  2.6141
    Total S =     0.254 + j  -625.442
  OpenDSS branch flow in LOAD.AGGREGATE_A_PH_LOAD from G1
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    120.30 -0.0052    260.89 -0.3969     29.008 + j    11.980     AB      240.60 -0.0052
    B    120.31  3.1364    260.88  2.7447     29.008 + j    11.980     BC        0.00  0.0000
    Total S =    58.016 + j    23.960
  OpenDSS branch flow in LOAD.AGGREGATE_B_PH_LOAD from G2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    120.00 -2.0996    340.44 -2.4757     37.998 + j    15.006     AB      240.01 -2.0996
    B    120.01  1.0420    340.42  0.6658     37.998 + j    15.006     BC        0.00  0.0000
    Total S =    75.995 + j    30.012
  OpenDSS branch flow in LOAD.AGGREGATE_C_PH_LOAD from G3
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    119.94  2.0857    520.23  1.7085     58.008 + j    22.979     AB      239.88  2.0857
    B    119.94 -1.0559    520.20 -1.4331     58.008 + j    22.979     BC        0.00  0.0000
    Total S =   116.016 + j    45.958
  OpenDSS branch flow in LOAD.BOX_STORE_LOAD from B1
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    272.31 -0.0140     47.28 -0.3845     12.002 + j     4.662     AB      471.43  0.5093
    B    272.04 -2.1084     47.33 -2.4796     11.998 + j     4.671     BC      471.41 -1.5856
    C    272.02  2.0787     47.33  1.7083     12.002 + j     4.660     CA      471.17  2.6035
    Total S =    36.003 + j    13.993
  OpenDSS branch flow in LOAD.G_AND_G_COMM_LOAD from D2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    198.33 -0.0017     67.13 -0.3929     12.308 + j     5.076     AB      232.39  0.5209
    B    116.04 -1.5987     67.42 -2.4899      4.917 + j     6.085     BC      232.08 -1.5987
    C    116.04  1.5429     67.12  1.6965      7.697 + j    -1.192     CA      227.15  2.6039
    Total S =    24.922 + j     9.969
  OpenDSS branch flow in LOAD.G_AND_G_RES_LOAD from D2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    B    116.04 -1.5987     88.17 -1.9801      9.497 + j     3.808     BC      232.08 -1.5987
    C    116.04  1.5429     88.17  1.1615      9.497 + j     3.808     CA        0.00  0.0000
    Total S =    18.994 + j     7.616
  OpenDSS branch flow in LOAD.INDIV_RES_120/240_LOAD from E1
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    120.16 -2.0996     85.92 -2.4759      9.602 + j     3.794     AB      240.33 -2.0996
    B    120.17  1.0420     85.92  0.6657      9.602 + j     3.794     BC        0.00  0.0000
    Total S =    19.205 + j     7.588
Accumulated Load P=349.15 kW   Q=139.10 kVAR
```

## Limitations on Validation

GridLAB-D has assumptions and component models that differ from those in OpenDSS, which may affect
the comparison of solutions between them:

1. There is no neutral impedance for transformer connections in GridLAB-D.
2. The ```shunt_impedance``` is only implemented for WYE-WYE or SINGLE_PHASE transfromers in GridLAB-D.
3. GridLAB-D transformers only have two windings.
4. The regulator impedance is modeled differently.
5. Capacitor banks are always on in the converted GridLAB-D model; control parameters are translated but not activated.
6. In a constant-current load model, the angle rotations are not exactly correct, especially for unbalanced loads or loads connected in Delta. See [GridLAB-D Issue 1312](https://github.com/gridlab-d/gridlab-d/issues/1312). This has been corrected in GridLAB-D version 5.
7. GridLAB-D calculates line parameters with Carson's equations, as simplified in Kersting's book. OpenDSS defaults to Deri's method, but it offers Full Carson and Carson options. Specify ```Carson``` for compatibility. (Deri is the OpenDSS default because it's easy to calculate, and it closely matches Full Carson.)
8. In GridLAB-D, wye/delta transformers have to be converted to delta/wye, swapping primary and secondary windings. With **check_branches**, choose an adjacent branch for proper comparisons.
9. In GridLAB-D, the IEEE13 results are affected by a bug in default solar insolation.  See [GridLAB-D Issue 1333] (https://github.com/gridlab-d/gridlab-d/issues/1333)

If these effects cannot be mitigated, one could either remove the unsupported feature from the test case, or
use **skip_gld** for the test case.

Some other limitations on the validation process include:

1. MAEv is limited to the line-to-neutral voltages. Using **check_branches** can partially mitigate this, but it does not implement a systematic comparison of line-to-line voltages.
2. MAEi misses the regulators; it captures lines, transformers and switches.
3. MAEi misses the shunt components, e.g., loads, capacitors, DER.
