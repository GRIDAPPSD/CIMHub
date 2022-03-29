# CIMHub Test Cases for S2G CPYDAR

Copyright (c) 2017-2022, Battelle Memorial Institute

## Contents

The model files are versioned in subdirectories _ieee13x_, _ieee123x_, and _j1red_, each of which includes:

1. The original OpenDSS models files are in _*.dss_, with _Master.dss_ at the top level.
2. The CIM XML is in _*.xml_
3. The UUID values are persisted in _*_uuids.dat_.
4. Base case power flow solution is in _*_?.csv_.

## Process

The test case conversion to CIM XML is executed with ```python3 test_CPYDAR.py```. The steps cover:

1. Solve the original cases in OpenDSS, then create CIM XML
2. Upload the CIM XML to Blazegraph
3. Export CSV, DSS, and GridLAB-D (GLM) files from Blazegraph
4. Solve the exported models in OpenDSS and GridLAB-D
5. Compare the original OpenDSS power flow results with exported OpenDSS and GridLAB-D power flow results

The test case conversion to ePHASORSIM is executed with ```python3 ePHASORSIM.py```. 
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
    A   2551.13  0.0000    540.01 -0.5133   1200.095 + j   676.495     AB     4392.91  0.5202
    B   2521.34 -2.0944    404.58 -2.4780    945.943 + j   381.802     BC     4392.95 -1.5674
    C   2551.17  2.0944    567.27  1.6272   1292.087 + j   651.831     CA     4418.72  2.6180
    Total S =  3438.125 + j  1710.128
  OpenDSS branch flow in LINE.650632 from RG60, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2551.13  0.0000    540.01 -0.5133   1200.088 + j   676.491     AB     4392.91  0.5202
    B   2521.34 -2.0944    404.58 -2.4780    945.950 + j   381.805     BC     4392.95 -1.5674
    C   2551.17  2.0944    567.28  1.6272   1292.123 + j   651.849     CA     4418.72  2.6180
    Total S =  3438.162 + j  1710.145
  GridLAB-D branch flow in LINE_650632 from RG60
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2561.73 -0.5236    518.00 -1.0513   1146.488 + j   668.137     AB     4407.93 -0.0038
    B   2528.07  3.6652    380.39  3.2648    885.586 + j   374.848     BC     4407.92 -2.0906
    C   2561.72  1.5708    545.26  1.0914   1239.363 + j   644.221     CA     4437.03  2.0944
    Total S =  3271.437 + j  1687.206
ieee13x          Nbus=[    53,    53,    90] Nlink=[    87,    87,    60] MAEv=[ 0.0000, 0.0079] MAEi=[   0.0024,   5.8458]
  OpenDSS branch flow in TRANSFORMER.REG1A from 150, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2401.76  0.0000    232.44 -1.2299    186.631 + j   526.155     AB     4159.97  0.5236
    B   2401.76 -2.0944    225.01  1.7574   -409.769 + j   352.332     BC     4159.97 -1.5708
    C   2401.76  2.0944    260.72  1.4313    493.505 + j   385.430     CA     4159.97  2.6180
    Total S =   270.368 + j  1263.918
  OpenDSS branch flow in TRANSFORMER.REG1A from 150, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2401.76  0.0000    232.41 -1.2298    186.697 + j   526.048     AB     4159.97  0.5236
    B   2401.76 -2.0944    224.98  1.7572   -409.787 + j   352.223     BC     4159.97 -1.5708
    C   2401.76  2.0944    260.70  1.4315    493.531 + j   385.311     CA     4159.97  2.6180
    Total S =   270.441 + j  1263.583
  GridLAB-D branch flow in REG_REG1A from 150
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2401.78  0.0000    232.45 -1.2288    187.233 + j   525.953     AB     4160.01  0.5236
    B   2401.78  4.1888    224.91  1.7570   -409.699 + j   352.041     BC     4160.00 -1.5708
    C   2401.78  2.0944    260.94  1.4340    494.964 + j   384.427     CA     4160.00  2.6180
    Total S =   272.498 + j  1262.421
ieee123x         Nbus=[   442,   442,   655] Nlink=[   564,   564,   639] MAEv=[ 0.0000, 0.0012] MAEi=[   0.0029,   0.0528]
  OpenDSS branch flow in LINE.FEEDER from FDR_BUS, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7450.65 -0.1082    137.52 -0.0667   1023.730 + j   -42.549     AB    12900.73  0.4164
    B   7453.34 -2.2009    135.28 -2.1488   1006.924 + j   -52.418     BC    12928.26 -1.6753
    C   7482.45  1.9897    128.27  2.1605    945.805 + j  -163.199     CA    12945.47  2.5103
    Total S =  2976.459 + j  -258.166
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
j1red            Nbus=[   180,   180,   328] Nlink=[   452,   440,   240] MAEv=[ 0.0170, 0.0331] MAEi=[   8.5782, 294.2931]
```

