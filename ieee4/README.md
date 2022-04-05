# CIMHub Test Cases for Transformers

Copyright (c) 2017-2021, Battelle Memorial Institute

## Process

The test cases are executed with ```python3 test_xfmr.py```. They cover:

1. Step-down, balanced and unbalanced load IEEE 4-bus test cases for YY, DD, grounded YD, ungrounded YD, and DY three-phase transformers
2. Single-phase, centertapped secondary transformer with balanced or unbalanced load
3. Single-phase, wye connected transformer
4. Open Wye/Open Delta stepdown transformer
5. 3-winding substation transformer, with tank modeling and neutral reactance options
6. YD, Open Wye/Open Delta lagging, and Open Wye/Open Delta leading service to induction motor and plug/lighting loads
7. 3-winding autotransformers

Items 1, 2, 4, and 6 are based on IEEE test cases. Items 4-7 are not supported in GridLAB-D.

The test cases are configured by entries in the ```cases``` array near the top of ```test_xfmr.py```.
Each array element is a dictionary with the following keys:

- **dssname** is the root file name of the original OpenDSS base case
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
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7138.21 -0.0035    240.51 -0.5543   1462.888 + j   898.567     AB    12380.91  0.5197
    B   7150.84 -2.0996    246.37 -2.6557   1496.297 + j   929.914     BC    12380.69 -1.5763
    C   7145.15  2.0892    243.91  1.5235   1471.340 + j   934.101     CA    12363.52  2.6133
    Total S =  4430.525 + j  2762.582
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7138.18 -0.0035    240.68 -0.5547   1463.565 + j   899.687     AB    12380.86  0.5197
    B   7150.81 -2.0996    246.54 -2.6562   1496.872 + j   931.359     BC    12380.64 -1.5763
    C   7145.12  2.0892    244.08  1.5231   1471.996 + j   935.239     CA    12363.46  2.6133
    Total S =  4432.434 + j  2766.285
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7138.78 -0.0041    240.53 -0.5543   1463.683 + j   897.788     AB    12377.91  0.5197
    B   7151.42  4.1841    246.38  3.6274   1495.995 + j   930.928     BC    12384.07 -1.5761
    C   7145.73  2.0890    243.93  1.5235   1471.758 + j   933.953     CA    12366.13  2.6130
    Total S =  4431.436 + j  2762.669
YYBal            Nbus=[    12,    12,    15] Nlink=[    15,    15,     9] MAEv=[ 0.0002, 0.0001] MAEi=[   0.3023,   0.0316]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7162.30 -0.0017    189.44 -0.6137   1110.625 + j   779.403     AB    12391.63  0.5200
    B   7139.11 -2.0979    240.80 -2.6384   1474.030 + j   884.636     BC    12378.00 -1.5772
    C   7132.25  2.0857    298.66  1.5869   1870.544 + j  1019.007     CA    12354.43  2.6140
    Total S =  4455.200 + j  2683.046
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7162.32 -0.0017    189.41 -0.6137   1110.488 + j   779.306     AB    12391.67  0.5200
    B   7139.14 -2.0979    240.77 -2.6384   1473.865 + j   884.537     BC    12378.05 -1.5772
    C   7132.28  2.0857    298.63  1.5869   1870.358 + j  1018.905     CA    12354.47  2.6140
    Total S =  4454.710 + j  2682.749
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7162.85 -0.0020    189.46 -0.6136   1111.051 + j   779.190     AB    12391.29  0.5200
    B   7139.68  4.1854    240.82  3.6447   1474.114 + j   885.071     BC    12381.14 -1.5773
    C   7132.85  2.0852    298.69  1.5870   1871.442 + j  1018.171     CA    12354.58  2.6136
    Total S =  4456.607 + j  2682.432
YYUnBal          Nbus=[    12,    12,    15] Nlink=[    15,    15,     9] MAEv=[ 0.0000, 0.0001] MAEi=[   0.0499,   0.0383]
  OpenDSS branch flow in LINE.LINE2 from N3, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2301.43 -0.6336    723.50 -1.0800   1501.872 + j   718.932     AB     3984.95 -0.0462
    B   2430.67 -2.6354    737.28  3.1079   1537.245 + j   921.116     BC     3986.67 -2.1411
    C   2177.38  1.5586    729.87  0.9976   1345.653 + j   845.436     CA     3983.93  2.0475
    Total S =  4384.770 + j  2485.484
  OpenDSS branch flow in LINE.LINE2 from N3, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2301.43 -0.6336    723.52 -1.0800   1501.916 + j   718.953     AB     3984.96 -0.0462
    B   2430.68 -2.6354    737.30  3.1079   1537.297 + j   921.147     BC     3986.68 -2.1411
    C   2177.38  1.5586    729.89  0.9976   1345.691 + j   845.460     CA     3983.93  2.0475
    Total S =  4384.904 + j  2485.560
  GridLAB-D branch flow in LINE_LINE2 from N3
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2300.53 -0.5703    723.55 -1.0799   1453.084 + j   811.977     AB     3984.24 -0.0465
    B   2300.75  3.6190    737.34  3.1079   1479.667 + j   829.733     BC     3986.18 -2.1407
    C   2301.65  1.5242    729.92  0.9976   1452.424 + j   844.372     CA     3985.81  2.0476
    Total S =  4385.176 + j  2486.082
YDBal            Nbus=[    12,    12,    15] Nlink=[    16,    16,     9] MAEv=[ 0.0000, 0.0181] MAEi=[   0.0120, 162.4784]
  OpenDSS branch flow in LINE.LINE2 from N3, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2321.37 -0.6213    532.41 -1.1437   1071.097 + j   616.654     AB     4036.69 -0.0276
    B   2479.89 -2.6180    443.51 -3.0981    975.498 + j   508.028     BC     4069.47 -2.1290
    C   2211.88  1.5673    550.83  1.1549   1116.207 + j   488.355     CA     4028.64  2.0562
    Total S =  3162.802 + j  1613.038
  OpenDSS branch flow in LINE.LINE2 from N3, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2321.37 -0.6213    532.42 -1.1437   1071.121 + j   616.668     AB     4036.70 -0.0276
    B   2479.90 -2.6180    443.52 -3.0981    975.519 + j   508.040     BC     4069.48 -2.1290
    C   2211.88  1.5673    550.84  1.1549   1116.235 + j   488.367     CA     4028.64  2.0562
    Total S =  3162.876 + j  1613.075
  GridLAB-D branch flow in LINE_LINE2 from N3
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2321.74 -0.5556    532.45 -1.1437   1028.546 + j   685.799     AB     4038.73 -0.0276
    B   2345.56  3.6360    443.54  3.1851    936.375 + j   453.358     BC     4069.22 -2.1294
    C   2339.42  1.5314    550.87  1.1549   1198.454 + j   473.794     CA     4028.04  2.0565
    Total S =  3163.375 + j  1612.952
YDUnBal          Nbus=[    12,    12,    15] Nlink=[    19,    19,     9] MAEv=[ 0.0000, 0.0185] MAEi=[   0.0055, 113.2593]
  OpenDSS branch flow in LINE.LINE2 from N3, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2301.44 -0.6336    723.50 -1.0800   1501.883 + j   718.937     AB     3984.96 -0.0462
    B   2430.67 -2.6354    737.28  3.1079   1537.245 + j   921.116     BC     3986.67 -2.1411
    C   2177.38  1.5586    729.87  0.9976   1345.653 + j   845.436     CA     3983.94  2.0475
    Total S =  4384.780 + j  2485.489
  OpenDSS branch flow in LINE.LINE2 from N3, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2301.44 -0.6336    723.52 -1.0800   1501.927 + j   718.958     AB     3984.97 -0.0462
    B   2430.68 -2.6354    737.30  3.1079   1537.297 + j   921.147     BC     3986.68 -2.1411
    C   2177.38  1.5586    729.89  0.9976   1345.691 + j   845.460     CA     3983.94  2.0475
    Total S =  4384.915 + j  2485.565
  GridLAB-D branch flow in LINE_LINE2 from N3
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2300.53 -0.5703    723.55 -1.0799   1453.084 + j   811.977     AB     3984.24 -0.0465
    B   2300.75  3.6190    737.34  3.1079   1479.667 + j   829.733     BC     3986.18 -2.1407
    C   2301.65  1.5242    729.92  0.9976   1452.424 + j   844.372     CA     3985.81  2.0476
    Total S =  4385.176 + j  2486.082
GYDBal           Nbus=[    12,    12,    15] Nlink=[    15,    15,     9] MAEv=[ 0.0000, 0.0181] MAEi=[   0.0128, 162.2470]
  OpenDSS branch flow in LINE.LINE2 from N3, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2321.37 -0.6213    532.41 -1.1437   1071.099 + j   616.656     AB     4036.69 -0.0276
    B   2479.89 -2.6180    443.51 -3.0981    975.498 + j   508.028     BC     4069.47 -2.1290
    C   2211.88  1.5673    550.83  1.1549   1116.207 + j   488.355     CA     4028.64  2.0562
    Total S =  3162.804 + j  1613.039
  OpenDSS branch flow in LINE.LINE2 from N3, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2321.37 -0.6213    532.42 -1.1437   1071.123 + j   616.670     AB     4036.70 -0.0276
    B   2479.90 -2.6180    443.52 -3.0981    975.519 + j   508.040     BC     4069.48 -2.1290
    C   2211.88  1.5673    550.84  1.1549   1116.235 + j   488.367     CA     4028.64  2.0562
    Total S =  3162.878 + j  1613.077
  GridLAB-D branch flow in LINE_LINE2 from N3
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2321.74 -0.5556    532.45 -1.1437   1028.546 + j   685.799     AB     4038.73 -0.0276
    B   2345.56  3.6360    443.54  3.1851    936.375 + j   453.358     BC     4069.22 -2.1294
    C   2339.42  1.5314    550.87  1.1549   1198.454 + j   473.794     CA     4028.04  2.0565
    Total S =  3163.375 + j  1612.952
GYDUnBal         Nbus=[    12,    12,    15] Nlink=[    18,    18,     9] MAEv=[ 0.0000, 0.0185] MAEi=[   0.0059, 113.0694]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7137.13 -0.0035    241.39 -0.5554   1467.049 + j   903.241     AB    12379.75  0.5198
    B   7150.58 -2.0996    246.14 -2.6522   1498.086 + j   923.792     BC    12381.63 -1.5762
    C   7146.50  2.0892    243.28  1.5209   1465.312 + j   935.665     CA    12363.75  2.6133
    Total S =  4430.446 + j  2762.698
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7137.14 -0.0035    241.39 -0.5554   1467.093 + j   903.268     AB    12379.77  0.5198
    B   7150.59 -2.0996    246.14 -2.6522   1498.137 + j   923.824     BC    12381.65 -1.5762
    C   7146.51  2.0892    243.28  1.5209   1465.362 + j   935.697     CA    12363.77  2.6133
    Total S =  4430.592 + j  2762.789
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7137.70 -0.0040    241.41 -0.5554   1467.703 + j   902.694     AB    12377.91  0.5197
    B   7151.15  4.1839    246.16  3.6309   1498.004 + j   924.463     BC    12384.06 -1.5761
    C   7147.07  2.0891    243.29  1.5209   1465.613 + j   935.707     CA    12366.14  2.6130
    Total S =  4431.320 + j  2762.864
DDBal            Nbus=[    12,    12,    15] Nlink=[    15,    15,     9] MAEv=[ 0.0000, 0.0182] MAEi=[   0.0129,   0.0315]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7152.14 -0.0035    177.60 -0.6196   1036.698 + j   734.023     AB    12405.65  0.5209
    B   7172.67 -2.0979    148.04 -2.5751    943.218 + j   487.665     BC    12421.98 -1.5755
    C   7163.78  2.0892    183.65  1.6781   1206.052 + j   525.658     CA    12391.70  2.6132
    Total S =  3185.968 + j  1747.346
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7152.15 -0.0035    177.61 -0.6196   1036.722 + j   734.040     AB    12405.67  0.5209
    B   7172.68 -2.0979    148.04 -2.5751    943.239 + j   487.676     BC    12422.00 -1.5755
    C   7163.79  2.0892    183.66  1.6781   1206.086 + j   525.673     CA    12391.72  2.6132
    Total S =  3186.047 + j  1747.390
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7152.68 -0.0028    177.62 -0.6195   1036.350 + j   734.840     AB    12408.67  0.5214
    B   7173.19  4.1854    148.05  3.7082    943.320 + j   487.798     BC    12422.13 -1.5753
    C   7164.31  2.0895    183.66  1.6782   1206.091 + j   526.051     CA    12391.29  2.6137
    Total S =  3185.761 + j  1748.689
DDUnBal          Nbus=[    12,    12,    15] Nlink=[    18,    18,     9] MAEv=[ 0.0000, 0.0185] MAEi=[   0.0058,   0.0201]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7136.85 -0.0035    243.73 -0.5513   1484.886 + j   906.022     AB    12379.31  0.5198
    B   7150.35 -2.0996    245.84 -2.6625   1486.632 + j   937.995     BC    12382.06 -1.5762
    C   7147.22  2.0892    241.23  1.5272   1458.948 + j   918.749     CA    12364.13  2.6132
    Total S =  4430.465 + j  2762.766
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7136.86 -0.0035    243.74 -0.5513   1484.936 + j   906.053     AB    12379.34  0.5198
    B   7150.37 -2.0996    245.84 -2.6625   1486.684 + j   938.028     BC    12382.08 -1.5762
    C   7147.23  2.0892    241.24  1.5272   1458.992 + j   918.776     CA    12364.15  2.6132
    Total S =  4430.613 + j  2762.858
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7138.65 -0.0041    243.75 -0.5513   1486.007 + j   905.292     AB    12376.86  0.5197
    B   7150.90  4.1842    245.86  3.6207   1486.341 + j   938.964     BC    12384.86 -1.5760
    C   7146.61  2.0890    241.25  1.5271   1459.085 + j   918.519     CA    12366.79  2.6129
    Total S =  4431.433 + j  2762.775
DYBal            Nbus=[    12,    12,    15] Nlink=[    15,    15,     9] MAEv=[ 0.0000, 0.0001] MAEi=[   0.0129,   0.2826]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7144.51 -0.0035    211.16 -0.5046   1323.173 + j   724.716     AB    12391.01  0.5185
    B   7149.02 -2.1014    267.40 -2.5545   1718.795 + j   836.827     BC    12369.21 -1.5772
    C   7140.92  2.0892    253.06  1.4210   1418.562 + j  1119.509     CA    12365.31  2.6138
    Total S =  4460.530 + j  2681.053
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7144.53 -0.0035    211.13 -0.5046   1323.014 + j   724.629     AB    12391.06  0.5185
    B   7149.05 -2.1014    267.38 -2.5545   1718.615 + j   836.740     BC    12369.26 -1.5772
    C   7140.94  2.0892    253.03  1.4210   1418.409 + j  1119.388     CA    12365.34  2.6138
    Total S =  4460.038 + j  2680.757
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7146.42 -0.0037    211.18 -0.5046   1323.816 + j   724.662     AB    12388.43  0.5189
    B   7149.59  4.1829    267.43  3.7288   1718.225 + j   838.763     BC    12371.11 -1.5765
    C   7140.16  2.0897    253.09  1.4210   1417.895 + j  1120.329     CA    12369.01  2.6140
    Total S =  4459.936 + j  2683.754
DYUnBal          Nbus=[    12,    12,    15] Nlink=[    15,    15,     9] MAEv=[ 0.0000, 0.0001] MAEi=[   0.0498,   0.3248]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    C   7107.90  2.0839    270.35  1.6193   1717.938 + j   861.029     CA        0.00  0.0000
    Total S =  1717.938 + j   861.029
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    C   7107.92  2.0839    270.35  1.6193   1717.949 + j   861.035     CA        0.00  0.0000
    Total S =  1717.949 + j   861.035
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7240.10 -0.0019      0.00  0.0000      0.000 + j    -0.000     AB    12467.46  0.5238
    B   7190.27  4.1951      0.00  0.0000     -0.000 + j    -0.000     BC    12443.13 -1.5762
    C   7108.60  2.0838    270.00  1.6193   1715.914 + j   859.870     CA    12395.24  2.6171
    Total S =  1715.914 + j   859.870
SCTBal           Nbus=[     8,     8,    10] Nlink=[     9,     9,     6] MAEv=[ 0.0000, 0.0003] MAEi=[   0.0048,   0.1771]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    C   7107.91  2.0839    270.33  1.6193   1717.788 + j   860.954     CA        0.00  0.0000
    Total S =  1717.788 + j   860.954
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    C   7107.93  2.0839    270.33  1.6193   1717.799 + j   860.960     CA        0.00  0.0000
    Total S =  1717.799 + j   860.960
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7240.09 -0.0019      0.00  0.0000      0.000 + j    -0.000     AB    12467.46  0.5238
    B   7190.28  4.1951      0.00  0.0000     -0.000 + j    -0.000     BC    12443.13 -1.5762
    C   7108.61  2.0838    269.98  1.6193   1715.772 + j   859.809     CA    12395.24  2.6171
    Total S =  1715.772 + j   859.809
SCTUnBal         Nbus=[     8,     8,    10] Nlink=[     9,     9,     6] MAEv=[ 0.0000, 0.0003] MAEi=[   0.0026,   0.1761]
  OpenDSS branch flow in LINE.LINE2 from N3, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2137.01 -0.5794    460.69 -1.0673    869.660 + j   461.434     AB     3843.92 -0.0153
    B   2336.50 -2.6459    511.40  3.1405   1050.478 + j   569.414     BC     4091.64 -2.1771
    C   2267.87  1.4486    495.94  0.9484    986.923 + j   539.429     CA     3740.26  1.9869
    Total S =  2907.062 + j  1570.277
  OpenDSS branch flow in LINE.LINE2 from N3, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2137.01 -0.5794    460.70 -1.0673    869.675 + j   461.442     AB     3843.93 -0.0153
    B   2336.51 -2.6459    511.41  3.1405   1050.505 + j   569.428     BC     4091.65 -2.1771
    C   2267.87  1.4486    495.95  0.9484    986.943 + j   539.440     CA     3740.26  1.9869
    Total S =  2907.124 + j  1570.310
OYODBal          Nbus=[    12,    12,     0] Nlink=[    17,    17,     0] MAEv=[ 0.3027,-1.0000] MAEi=[   0.0054,  -1.0000]
  OpenDSS branch flow in LINE.LINE2 from N3, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2116.21 -0.6318    481.27 -1.1826    867.824 + j   533.054     AB     3816.61 -0.0072
    B   2437.51 -2.6162    446.49 -3.1041    961.385 + j   510.102     BC     4119.25 -2.1845
    C   2161.29  1.4486    532.31  1.0517   1061.046 + j   444.716     CA     3689.47  1.9730
    Total S =  2890.255 + j  1487.872
  OpenDSS branch flow in LINE.LINE2 from N3, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2104.47 -0.6475    481.27 -1.1826    871.229 + j   516.476     AB     3818.86 -0.0075
    B   2473.86 -2.6162    446.49 -3.1041    975.722 + j   517.709     BC     4118.63 -2.1854
    C   2137.27  1.4608    532.31  1.0517   1043.803 + j   452.559     CA     3688.21  1.9731
    Total S =  2890.754 + j  1486.744
OYODUnBal        Nbus=[    12,    12,     0] Nlink=[    17,    17,     0] MAEv=[ 0.3017,-1.0000] MAEi=[   0.0000,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7113.31 -0.0070    230.04 -0.6069   1350.661 + j   923.778     AB        0.00  0.0000
    Total S =  1350.661 + j   923.778
  OpenDSS branch flow in TRANSFORMER.T1 from N2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7113.32 -0.0070    230.05 -0.6069   1350.721 + j   923.820     AB        0.00  0.0000
    Total S =  1350.721 + j   923.820
  GridLAB-D branch flow in XF_T1 from N2
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7113.88 -0.0077    230.06 -0.6069   1351.454 + j   923.077     AB    12414.13  0.5238
    B   7242.46  4.1864      0.00  0.0000     -0.000 + j    -0.000     BC    12479.00 -1.5713
    C   7197.89  2.0994      0.00  0.0000     -0.000 + j     0.000     CA    12439.47  2.6133
    Total S =  1351.454 + j   923.077
OnePh            Nbus=[    12,    12,    15] Nlink=[    11,    11,     9] MAEv=[ 0.0000, 0.0001] MAEi=[   0.0086,   0.0130]
  OpenDSS branch flow in LINE.DLINE3-4 from B4, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.13 -0.0401    184.16 -0.4211   1249.539 + j   500.539     AB    12699.02  0.4725
    B   7274.27 -2.1537    230.53 -2.6166   1500.462 + j   748.757     BC    12712.86 -1.6156
    C   7464.62  2.0490    138.08  1.8052   1000.221 + j   248.827     CA    12775.30  2.5691
    Total S =  3750.222 + j  1498.123
  OpenDSS branch flow in LINE.DLINE3-4 from B4, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.19 -0.0401    184.16 -0.4211   1249.536 + j   500.538     AB    12699.12  0.4725
    B   7274.33 -2.1537    230.52 -2.6166   1500.461 + j   748.756     BC    12712.95 -1.6156
    C   7464.67  2.0490    138.08  1.8052   1000.221 + j   248.827     CA    12775.39  2.5691
    Total S =  3750.218 + j  1498.121
YYD              Nbus=[    18,    18,     0] Nlink=[    21,    21,     0] MAEv=[ 0.0116,-1.0000] MAEi=[   0.0013,  -1.0000]
  OpenDSS branch flow in LINE.DLINE3-4 from B4, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7285.83 -0.0384    184.75 -0.4178   1250.324 + j   498.576     AB    12687.89  0.4721
    B   7263.34 -2.1572    230.87 -2.6210   1499.802 + j   750.063     BC    12712.74 -1.6146
    C   7497.91  2.0508    137.47  1.8064   1000.091 + j   249.351     CA    12784.14  2.5686
    Total S =  3750.218 + j  1497.990
  OpenDSS branch flow in LINE.DLINE3-4 from B4, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7285.89 -0.0384    184.75 -0.4178   1250.328 + j   498.577     AB    12687.99  0.4721
    B   7263.40 -2.1572    230.87 -2.6210   1499.801 + j   750.063     BC    12712.83 -1.6147
    C   7497.96  2.0508    137.47  1.8064   1000.091 + j   249.351     CA    12784.24  2.5686
    Total S =  3750.220 + j  1497.991
YYDXn            Nbus=[    18,    18,     0] Nlink=[    21,    21,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0013,  -1.0000]
  OpenDSS branch flow in LINE.DLINE3-4 from B4, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7308.77 -0.0401    184.17 -0.4211   1249.539 + j   500.539     AB    12698.37  0.4725
    B   7273.89 -2.1537    230.54 -2.6166   1500.461 + j   748.757     BC    12712.23 -1.6156
    C   7464.27  2.0490    138.09  1.8052   1000.218 + j   248.826     CA    12774.68  2.5691
    Total S =  3750.218 + j  1498.122
  OpenDSS branch flow in LINE.DLINE3-4 from B4, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7308.83 -0.0401    184.17 -0.4211   1249.542 + j   500.540     AB    12698.48  0.4725
    B   7273.95 -2.1537    230.54 -2.6166   1500.461 + j   748.756     BC    12712.32 -1.6156
    C   7464.32  2.0490    138.08  1.8052   1000.217 + j   248.826     CA    12774.78  2.5691
    Total S =  3750.220 + j  1498.123
YYD1Tank         Nbus=[    18,    18,     0] Nlink=[    21,    21,     0] MAEv=[ 0.0119,-1.0000] MAEi=[   0.0013,  -1.0000]
  OpenDSS branch flow in LOAD.MOTOR from LOADBUS, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    116.19 -0.0017     54.43 -1.0957      2.903 + j     5.619     AB      232.01 -0.0052
    B    115.81  3.1329     54.71  3.0973      6.332 + j     0.226     BC      234.32 -2.0913
    C    204.30  1.5673     54.77  0.9964      9.415 + j     6.047     CA      234.86  2.0848
    Total S =    18.650 + j    11.891
  OpenDSS branch flow in LOAD.MOTOR from LOADBUS, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    116.19 -0.0017     54.43 -1.0957      2.903 + j     5.619     AB      232.01 -0.0052
    B    115.81  3.1329     54.71  3.0973      6.332 + j     0.226     BC      234.32 -2.0913
    C    204.30  1.5673     54.77  0.9964      9.415 + j     6.047     CA      234.86  2.0848
    Total S =    18.650 + j    11.891
IMYD             Nbus=[    12,    12,     0] Nlink=[    24,    24,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0002,  -1.0000]
  OpenDSS branch flow in LOAD.MOTOR from LOADBUS, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    115.60 -0.0122     55.19 -1.0851      3.047 + j     5.605     AB      230.82 -0.0157
    B    115.22  3.1224     56.04  3.0912      6.454 + j     0.202     BC      226.71 -2.0950
    C    198.49  1.5795     55.02  0.9896      9.075 + j     6.075     CA      231.78  2.1016
    Total S =    18.576 + j    11.882
  OpenDSS branch flow in LOAD.MOTOR from LOADBUS, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    115.66 -0.0105     55.18 -1.0858      3.035 + j     5.615     AB      230.96 -0.0148
    B    115.30  3.1224     54.52  3.1056      6.285 + j     0.105     BC      226.99 -2.0964
    C    198.57  1.5778     54.98  1.0203      9.264 + j     5.775     CA      231.54  2.1008
    Total S =    18.584 + j    11.495
IMOYODlag        Nbus=[    12,    12,     0] Nlink=[    19,    19,     0] MAEv=[ 0.0003,-1.0000] MAEi=[   0.1838,  -1.0000]
  OpenDSS branch flow in LOAD.MOTOR from LOADBUS, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    115.16  0.0070     54.82 -1.1167      2.730 + j     5.692     AB      229.92  0.0026
    B    114.76  3.1398     55.40  3.0939      6.351 + j     0.292     BC      234.17 -2.1141
    C    200.75  1.5394     56.14  0.9798      9.552 + j     5.983     CA      227.57  2.0696
    Total S =    18.633 + j    11.967
  OpenDSS branch flow in LOAD.MOTOR from LOADBUS, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    115.13  0.0070     54.79 -1.0852      2.905 + j     5.600     AB      229.87  0.0026
    B    114.75  3.1398     55.39  3.0932      6.349 + j     0.296     BC      234.42 -2.1135
    C    201.04  1.5394     54.60  0.9945      9.388 + j     5.690     CA      227.81  2.0688
    Total S =    18.643 + j    11.586
IMOYODlead       Nbus=[    12,    12,     0] Nlink=[    19,    19,     0] MAEv=[ 0.0004,-1.0000] MAEi=[   0.2013,  -1.0000]
  OpenDSS branch flow in LOAD.TEST from LOW, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  88192.10 -0.0750   1463.41 -0.6304  109664.425 + j 68047.832     AB   152753.20  0.4485
    B  88192.10 -2.1694   1463.41 -2.7248  109664.425 + j 68047.832     BC   152753.20 -1.6458
    C  88192.10  2.0193   1463.41  1.4640  109664.425 + j 68047.832     CA   152753.20  2.5429
    Total S = 328993.276 + j 204143.496
  OpenDSS branch flow in LOAD.TEST from LOW, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  88192.10 -0.0750   1463.41 -0.6304  109664.425 + j 68047.832     AB   152753.20  0.4485
    B  88192.10 -2.1694   1463.41 -2.7248  109664.425 + j 68047.832     BC   152753.20 -1.6458
    C  88192.10  2.0193   1463.41  1.4640  109664.425 + j 68047.832     CA   152753.20  2.5429
    Total S = 328993.276 + j 204143.496
AutoHLT          Nbus=[    12,    12,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0000,  -1.0000]
  OpenDSS branch flow in LOAD.TEST from LOW, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  88193.90 -0.0750   1463.44 -0.6302  109680.787 + j 68031.474     AB   152756.32  0.4485
    B  88193.90 -2.1694   1463.44 -2.7246  109680.787 + j 68031.474     BC   152756.32 -1.6458
    C  88193.90  2.0193   1463.44  1.4642  109680.787 + j 68031.474     CA   152756.32  2.5429
    Total S = 329042.361 + j 204094.422
  OpenDSS branch flow in LOAD.TEST from LOW, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    Total S =     0.000 + j     0.000
Auto1bus         Nbus=[    15,     9,     0] Nlink=[    24,    18,     0] MAEv=[ 0.0719,-1.0000] MAEi=[137260.1296,  -1.0000]
  OpenDSS branch flow in LOAD.TEST from LOW, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  88193.90 -0.0750   1463.44 -0.6302  109680.787 + j 68031.474     AB   152756.32  0.4485
    B  88193.90 -2.1694   1463.44 -2.7246  109680.787 + j 68031.474     BC   152756.32 -1.6458
    C  88193.90  2.0193   1463.44  1.4642  109680.787 + j 68031.474     CA   152756.32  2.5429
    Total S = 329042.361 + j 204094.422
  OpenDSS branch flow in LOAD.TEST from LOW, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 149052.00 -0.1972   2024.90 -0.7517  256593.938 + j 158909.041     AB   258165.64  0.3264
    B 149052.00 -2.2916   2024.90 -2.8461  256593.938 + j 158909.041     BC   258165.64 -1.7680
    C 149052.00  1.8972   2024.90  1.3427  256593.938 + j 158909.041     CA   258165.64  2.4208
    Total S = 769781.815 + j 476727.123
Auto3bus         Nbus=[    12,    12,     0] Nlink=[    18,    15,     0] MAEv=[ 0.0670,-1.0000] MAEi=[ 967.4582,  -1.0000]
  OpenDSS branch flow in LOAD.TEST from LOW, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  88192.10 -0.0750   1463.41 -0.6304  109664.425 + j 68047.832     AB   152753.20  0.4485
    B  88192.10 -2.1694   1463.41 -2.7248  109664.425 + j 68047.832     BC   152753.20 -1.6458
    C  88192.10  2.0193   1463.41  1.4640  109664.425 + j 68047.832     CA   152753.20  2.5429
    Total S = 328993.276 + j 204143.496
  OpenDSS branch flow in LOAD.TEST from LOW, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A  88192.10 -0.0750   1463.41 -0.6304  109664.425 + j 68047.832     AB   152753.20  0.4485
    B  88192.10 -2.1694   1463.41 -2.7248  109664.425 + j 68047.832     BC   152753.20 -1.6458
    C  88192.10  2.0193   1463.41  1.4640  109664.425 + j 68047.832     CA   152753.20  2.5429
    Total S = 328993.276 + j 204143.496
AutoAuto         Nbus=[    12,    12,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0000,  -1.0000]
```

## AutoTransformers

The three-winding autotransformer test cases were derived from a whitepaper on CIM transformer modeling, which
included an actual test report from a 345/161/13.8 kV, 330/330/72 MVA, YNad1 autotransformer. The test data is
archived in the OpenDSS repository, with scripts that verify losses, short-circuit currents and voltage
regulation for the modeling options available in OpenDSS. GridLAB-D does not support 3-winding transformers, nor
autotransformers, so GridLAB-D validation is skipped. The CIM support for autotransformers is incomplete, so only
two of the four variants work properly for round-trip validation in OpenDSS.

- **AutoHLT.dss** represents the autotransformer as a non-auto Yyd1. It replicates test data, except for the split of load losses between HT and LT tests. It also fails to show the MVA size reduction inherent in the autotransformer.
- **Auto1bus.dss** represents the autotransformer as a bank of three single-phase, reduced-MVA tanks, connected YNad1. This is accurate, but does not translate through CIM because it uses a "9-phase bus" to represent the common node, which causes errors in connections and voltage ratings. This is "option 1" from the OpenDSS Tech Note on modeling autotransformers.
- **Auto3bus.dss** represents the autotransformer as a bank of three single-phase, reduced-MVA tanks, connected YNad1. This is accurate, but does not translate through CIM because it uses a "6-phase bus" with jumper to represent the common node, which causes errors in connections and voltage ratings. This is "option 2" from the OpenDSS Tech Note on modeling autotransformers.
- **AutoAuto.dss** uses the built-in "autotrans" component in OpenDSS. It uses test results directly as input, making the series-common winding connection internally. 
CIM can support this by recognizing the vector group YNa or YNad1. OpenDSS uses the PowerTransformer.vectorGroup to determine whether it's an autotransformer. 
The choices of WindingConnectionKind include Y, Yn, and A for windings 1 and 2. A applies to winding 2 and Y can work for winding 1. A new enumeration should be considered
for winding 1, i.e., S for series.



