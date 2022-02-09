# CIMHub Test Cases for S2G CPYDAR

Copyright (c) 2017-2022, Battelle Memorial Institute

## Contents

The model files are versioned in subdirectories _ieee13x_, _ieee123x_, and _j1red_, each of which includes:

1. The original OpenDSS models files are in _*.dss_, with _Master.dss_ at the top level.
2. The CIM XML is in _*.xml_
3. The UUID values are persisted in _*_uuids.dat_.
4. Base case power flow solution is in _*_?.csv_.

## Process

The test case conversion is executed with ```python3 test_CPYDAR.py```. The steps cover:

1. Solve the original cases in OpenDSS, then create CIM XML
2. Upload the CIM XML to Blazegraph
3. Export CSV, DSS, and GridLAB-D (GLM) files from Blazegraph
4. Solve the exported models in OpenDSS and GridLAB-D
5. Compare the original OpenDSS power flow results with exported OpenDSS and GridLAB-D power flow results

The test cases are configured by entries in the ```cases``` array near the top of ```test_CPYDAR.py```.
Each array element is a dictionary with the following keys:

- **root** is used to generate file names for converted files
- **mRID** is a UUID4 to make the test case feeder unique. For a new test case, generate a random new mRID with this Python script: ```import uuid;idNew=uuid.uuid4();print(str(idNew).upper())```'
- **glmvsrc** is the substation source line-to-neutral voltage for GridLAB-D
- **bases** is an array of voltage bases to use for interpretation of the voltage outputs. Specify line-to-line voltages, in ascending order, leaving out 208 and 480.
- **export_options** is a string of command-line options to the CIMImporter Java program. ```-e=carson``` keeps the OpenDSS line constants model compatible with GridLAB-D's
- **skip_gld** specify as ```True``` when you know that GridLAB-D won't support this test case
- **check_branches** an array of branches in the model to compare power flows and line-to-line voltages. Each element contains:
    - **dss_link** is the name of an OpenDSS branch for power and current flow; power delivery or power conversion components may be used
    - **dss_bus** is the name of an OpenDSS bus attached to **dss_link**. Line-to-line voltages are calculated here, and this bus establishes flow polarity into the branch at this bus.
    - **gld_link** is the name of a GridLAB-D branch for power and current flow; only links, e.g., line or transformer, may be used. Do not use this when **skip_gld** is ```True```
    - **gld_bus** is the name of a GridLAB-D bus attached to **gld_link**. Do not use this when **skip_gld** is ```True```

The script outputs include the comparisons requested from **check_branches**, and summary information:

- **Nbus** is the number of buses found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **Nlink** is the number of links found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **MAEv** is the mean absolute voltage error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in per-unit. This is based on line-to-neutral voltages.
In an ungrounded system, MAEv can be large. Use the line-to-line voltage comparisons from **check_branches** for ungrounded systems.
- **MAEi** is the mean absolute link current error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in Amperes

## Results

```
  OpenDSS branch flow in LINE.650632 from RG60, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2551.89  0.0000      0.00  1.5741     -0.000 + j    -0.006     AB     4394.03  0.5202
    B   2521.87 -2.0944      0.00 -0.5185     -0.000 + j    -0.005     BC     4407.06 -1.5657
    C   2566.90  2.0944      0.00 -2.6201      0.000 + j    -0.007     CA     4433.01  2.6163
    Total S =    -0.000 + j    -0.018
  OpenDSS branch flow in LINE.650632 from RG60, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2551.13  0.0000    539.54 -0.5131   1199.173 + j   675.699     AB     4392.92  0.5202
    B   2521.35 -2.0944    404.35 -2.4775    945.609 + j   381.091     BC     4405.99 -1.5657
    C   2566.18  2.0944    565.01  1.6296   1296.121 + j   649.898     CA     4431.73  2.6163
    Total S =  3440.903 + j  1706.689
  GridLAB-D branch flow in LINE_650632 from RG60
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2561.72 -0.5236    537.47 -1.0351   1200.615 + j   673.977     AB     4407.92 -0.0038
    B   2528.06  3.6652    403.16  3.2844    946.193 + j   378.817     BC     4422.84 -2.0887
    C   2578.91  1.5708    562.72  1.1085   1298.879 + j   647.224     CA     4451.92  2.0925
    Total S =  3445.687 + j  1700.018
ieee13x          Nbus=[    53,    53,    90] Nlink=[    87,    87,    60] MAEv=[ 0.0385, 0.0195] MAEi=[ 120.3238, 186.7661]
  OpenDSS branch flow in TRANSFORMER.REG1A from 150, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2401.78  0.0000      0.02  1.5708      0.000 + j    -0.042     AB     4160.00  0.5236
    B   2401.78 -2.0944      0.02 -0.5236      0.000 + j    -0.037     BC     4160.00 -1.5708
    C   2401.78  2.0944      0.02 -2.6180     -0.000 + j    -0.043     CA     4160.00  2.6180
    Total S =    -0.000 + j    -0.122
  OpenDSS branch flow in TRANSFORMER.REG1A from 150, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2401.75  0.0000    233.30 -1.2753    163.168 + j   536.040     AB     4159.96  0.5236
    B   2401.76 -2.0944    229.45  1.7506   -420.302 + j   356.442     BC     4159.97 -1.5708
    C   2401.76  2.0944    253.99  1.4074    471.650 + j   386.866     CA     4159.96  2.6180
    Total S =   214.516 + j  1279.348
  GridLAB-D branch flow in REG_REG1A from 150
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2401.78  0.0000    233.32 -1.2752    163.262 + j   536.086     AB     4160.01  0.5236
    B   2401.78  4.1888    229.46  1.7509   -420.205 + j   356.570     BC     4160.00 -1.5708
    C   2401.78  2.0944    257.11  1.4102    478.548 + j   390.299     CA     4160.00  2.6180
    Total S =   221.604 + j  1282.954
ieee123x         Nbus=[   442,   442,   655] Nlink=[   564,   564,   639] MAEv=[ 0.0197, 0.0193] MAEi=[  33.5055,  49.3382]
  OpenDSS branch flow in LINE.FEEDER from FDR_BUS, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7444.05  0.0000      0.03  1.5708      0.000 + j    -0.230     AB    12893.47  0.5236
    B   7444.05 -2.0944      0.03 -0.5236      0.000 + j    -0.220     BC    12893.49 -1.5708
    C   7444.07  2.0944      0.04 -2.6180     -0.000 + j    -0.281     CA    12893.49  2.6180
    Total S =    -0.000 + j    -0.731
  OpenDSS branch flow in LINE.FEEDER from FDR_BUS, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7407.02 -0.1257    213.97 -0.1218   1584.883 + j    -6.086     AB    12830.67  0.3980
    B   7408.56 -2.2201    212.20 -2.2115   1572.009 + j   -13.444     BC    12852.81 -1.6944
    C   7440.06  1.9705    203.43  2.0593   1507.563 + j  -134.281     CA    12864.43  2.4919
    Total S =  4664.455 + j  -153.811
  GridLAB-D branch flow in SWT_FEEDER from FDR_BUS
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  40341.17  0.0000   1165.14  0.0038  47002.670 + j  -178.376     AB    69872.97  0.5236
    B  40341.18  4.1888   1155.53  4.1966  46614.105 + j  -362.945     BC    69872.99 -1.5708
    C  40341.18  2.0944   1102.93  2.1828  44319.701 + j -3930.288     CA    69872.95  2.6180
    Total S = 137936.476 + j -4471.609
j1red            Nbus=[   180,   180,   328] Nlink=[   452,   440,   240] MAEv=[ 0.0337, 0.0514] MAEi=[  24.9575, 332.8359]
```

