# CIMHub Test Cases for OEDI

Copyright (c) 2017-2021, Battelle Memorial Institute

## Contents

The archived files include:

1. The CIM XML and UUID files are in _IEEE123_PV.xml_ and ieee123_pv_uuids.dat_. The CIM measurement UUID values are maintained in _IEEE123_PV_msid.json_
2. The exported OpenDSS model files are in _dss_files.zip_
3. The exported GridLAB-D model files are in _glm_files.zip_
4. The exported comma-separated value (CSV) files are in _csv_files.zip_
5. A sample exported dictionary of CIM objects and measurements is in _IEEE123_PV_dict.json_

## Process

The test case conversion is executed with ```python3 test_OEDI.py```. The steps cover:

1. Solve the original GridAPPS-D case in OpenDSS, then create CIM XML
2. Upload the CIM XML to Blazegraph
3. List and insert CIM measurement points on the feeder
4. Export CSV, DSS, and GridLAB-D (GLM) files from Blazegraph
5. Solve the exported models in OpenDSS and GridLAB-D
6. Compare the original OpenDSS power flow result with exported OpenDSS and GridLAB-D power flow results

The test cases are configured by entries in the ```cases``` array near the top of ```test_OEDI.py```.
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
  OpenDSS branch flow in LINE.L114 from 135, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2433.24 -0.0105    136.66 -0.5327    288.217 + j   165.866     AB     4167.23  0.5395
    B   2448.98 -2.0560    189.32  1.5432   -415.934 + j   204.845     BC     4229.20 -1.5705
    C   2358.60  2.0769     99.35  1.5088    197.515 + j   126.074     CA     4141.64  2.6131
    Total S =    69.798 + j   496.785
  OpenDSS branch flow in LINE.L114 from 135, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2433.25 -0.0105    136.66 -0.5327    288.218 + j   165.867     AB     4167.24  0.5395
    B   2448.98 -2.0560    189.32  1.5432   -415.932 + j   204.844     BC     4229.20 -1.5705
    C   2358.60  2.0769     99.35  1.5088    197.516 + j   126.074     CA     4141.65  2.6131
    Total S =    69.802 + j   496.785
  GridLAB-D branch flow in LINE_L114 from 135
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2429.57 -0.0110    136.39 -0.5327    287.298 + j   165.134     AB     4163.40  0.5388
    B   2446.97  4.2259    189.03  1.5459   -414.148 + j   206.012     BC     4225.95 -1.5698
    C   2360.97  2.0787     94.50  1.5076    187.714 + j   120.600     CA     4143.25  2.6130
    Total S =    60.864 + j   491.746
IEEE123_PV       Nbus=[   442,   442,   655] Nlink=[   564,   564,   639] MAEv=[ 0.0000, 0.0015] MAEi=[   0.0028,   1.0437]
```

