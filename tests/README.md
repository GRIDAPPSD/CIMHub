# CIMHub Test Cases for IEEE 13-Bus System

Copyright (c) 2017-2021, Battelle Memorial Institute

## Process

The test cases are executed with ```python3 test13.py```. They cover the IEEE 13-bus system
with photovoltaic, storage, and single-phase centertap secondary transformer added. The option
for assets-based line and transformer modeling are also covered.

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
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2434.48 -0.0471     81.65 -0.6658    161.923 + j   115.285     AB     4233.08  0.4928
    B   2483.38 -2.1206     63.29 -2.7780    124.403 + j    96.045     BC     4292.51 -1.6086
    C   2450.93  2.0525     63.28  1.3957    122.823 + j    94.689     CA     4237.28  2.5716
    Total S =   409.148 + j   306.019
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2434.45 -0.0471     81.65 -0.6658    161.921 + j   115.284     AB     4233.03  0.4928
    B   2483.35 -2.1206     63.29 -2.7780    124.401 + j    96.044     BC     4292.45 -1.6086
    C   2450.89  2.0525     63.28  1.3957    122.821 + j    94.687     CA     4237.22  2.5716
    Total S =   409.142 + j   306.015
  GridLAB-D branch flow in XF_XFM1 from 633
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2445.54 -0.5702     80.84 -1.1842    161.590 + j   113.906     AB     4248.87 -0.0309
    B   2490.43  3.6393     62.45  2.9877    123.663 + j    94.333     BC     4309.15 -2.1307
    C   2464.21  1.5301     62.45  0.8783    122.353 + j    93.351     CA     4259.22  2.0485
    Total S =   407.605 + j   301.590
  OpenDSS branch flow in LINE.670671 from 670, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2415.78 -0.0628    466.90 -0.4740   1033.904 + j   450.842     AB     4206.13  0.4874
    B   2491.02 -2.1223    190.54 -2.3077    466.521 + j    87.476     BC     4287.47 -1.6184
    C   2425.27  2.0420    418.58  1.7722    978.444 + j   270.611     CA     4205.09  2.5593
    Total S =  2478.869 + j   808.929
  OpenDSS branch flow in LINE.670671 from 670, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2415.75 -0.0628    466.89 -0.4740   1033.880 + j   450.832     AB     4206.07  0.4874
    B   2490.98 -2.1223    190.55 -2.3077    466.516 + j    87.475     BC     4287.40 -1.6184
    C   2425.23  2.0420    418.58  1.7724    978.476 + j   270.436     CA     4205.03  2.5593
    Total S =  2478.871 + j   808.742
  GridLAB-D branch flow in LINE_670671 from 670
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2426.79 -0.5859    466.79 -0.9966   1038.629 + j   452.212     AB     4222.08 -0.0364
    B   2497.98  3.6373    190.46  3.4538    467.767 + j    86.851     BC     4304.99 -2.1412
    C   2438.54  1.5186    418.49  1.2508    984.143 + j   269.998     CA     4225.75  2.0358
    Total S =  2490.539 + j   809.060
IEEE13_Assets    Nbus=[    41,    41,    66] Nlink=[    64,    64,    45] MAEv=[ 0.0000, 0.0038] MAEi=[   0.0007,   0.2533]
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2458.42 -0.0471     65.57 -0.8238    114.968 + j   112.979     AB     4225.11  0.4895
    B   2457.89 -2.1153     47.96 -3.0058     74.153 + j    91.637     BC     4277.50 -1.5983
    C   2461.63  2.0595     47.89  1.1694     74.182 + j    91.607     CA     4275.84  2.5766
    Total S =   263.303 + j   296.223
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2458.42 -0.0471     65.57 -0.8238    114.968 + j   112.979     AB     4225.11  0.4895
    B   2457.89 -2.1153     47.96 -3.0058     74.153 + j    91.637     BC     4277.50 -1.5983
    C   2461.63  2.0595     47.89  1.1694     74.182 + j    91.607     CA     4275.84  2.5766
    Total S =   263.303 + j   296.223
  GridLAB-D branch flow in XF_XFM1 from 633
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2472.39 -0.5675     52.41  4.6526     62.995 + j   113.238     AB     4246.50 -0.0318
    B   2467.48  3.6466     38.53  2.3135     22.385 + j    92.389     BC     4299.39 -2.1190
    C   2476.92  1.5380     38.56  0.2089     22.855 + j    92.742     CA     4299.91  2.0556
    Total S =   108.235 + j   298.369
  OpenDSS branch flow in LINE.670671 from 670, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2442.42 -0.0628    469.52 -0.4691   1053.403 + j   453.231     AB     4192.50  0.4826
    B   2456.41 -2.1171    187.81 -2.3154    452.295 + j    90.870     BC     4266.73 -1.6080
    C   2436.23  2.0473    418.45  1.7843    984.376 + j   265.052     CA     4244.06  2.5637
    Total S =  2490.074 + j   809.153
  OpenDSS branch flow in LINE.670671 from 670, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2442.42 -0.0628    469.52 -0.4691   1053.403 + j   453.231     AB     4192.50  0.4826
    B   2456.41 -2.1171    187.81 -2.3154    452.295 + j    90.870     BC     4266.73 -1.6080
    C   2436.23  2.0473    418.45  1.7843    984.374 + j   265.052     CA     4244.06  2.5637
    Total S =  2490.072 + j   809.153
  GridLAB-D branch flow in LINE_670671 from 670
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2455.50 -0.5838    467.34 -0.9908   1053.783 + j   454.322     AB     4212.10 -0.0395
    B   2464.70  3.6441    189.54  3.4523    458.594 + j    89.055     BC     4285.13 -2.1289
    C   2450.18  1.5261    418.79  1.2630    990.797 + j   266.920     CA     4267.31  2.0426
    Total S =  2503.174 + j   810.297
IEEE13_CDPSM     Nbus=[    53,    53,    90] Nlink=[    87,    87,    60] MAEv=[ 0.0000, 0.0049] MAEi=[   0.0002,   5.1742]
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2459.16 -0.0454     66.12 -0.8215    116.037 + j   113.910     AB     4227.91  0.4891
    B   2455.31 -2.1171     48.87 -3.0025     75.945 + j    92.886     BC     4273.53 -1.5988
    C   2462.08  2.0595     49.07  1.1746     76.516 + j    93.485     CA     4274.74  2.5775
    Total S =   268.499 + j   300.281
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2459.16 -0.0454     66.12 -0.8215    116.037 + j   113.910     AB     4227.91  0.4891
    B   2455.31 -2.1171     48.87 -3.0025     75.945 + j    92.885     BC     4273.53 -1.5988
    C   2462.08  2.0595     49.07  1.1746     76.516 + j    93.485     CA     4274.74  2.5775
    Total S =   268.499 + j   300.281
  GridLAB-D branch flow in XF_XFM1 from 633
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2472.21 -0.5672     53.26  4.6604     64.883 + j   114.575     AB     4245.87 -0.0322
    B   2465.73  3.6460     39.20  2.3262     24.008 + j    93.627     BC     4296.99 -2.1194
    C   2476.11  1.5376     39.45  0.2261     25.043 + j    94.411     CA     4298.22  2.0555
    Total S =   113.934 + j   302.613
  OpenDSS branch flow in LINE.670671 from 670, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2443.38 -0.0611    464.60 -0.4714   1040.951 + j   452.835     AB     4195.24  0.4821
    B   2453.49 -2.1188    191.47 -2.3084    461.368 + j    88.512     BC     4262.72 -1.6085
    C   2436.95  2.0473    418.76  1.7813    984.600 + j   268.248     CA     4243.42  2.5646
    Total S =  2486.920 + j   809.594
  OpenDSS branch flow in LINE.670671 from 670, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2443.38 -0.0611    464.60 -0.4714   1040.951 + j   452.835     AB     4195.24  0.4821
    B   2453.49 -2.1188    191.47 -2.3084    461.368 + j    88.512     BC     4262.72 -1.6085
    C   2436.95  2.0473    418.76  1.7813    984.603 + j   268.249     CA     4243.42  2.5646
    Total S =  2486.922 + j   809.595
  GridLAB-D branch flow in LINE_670671 from 670
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2455.38 -0.5834    466.85 -0.9932   1051.392 + j   456.690     AB     4211.61 -0.0399
    B   2462.75  3.6435    192.26  3.4535    464.975 + j    89.398     BC     4282.55 -2.1294
    C   2449.36  1.5256    420.93  1.2598    994.824 + j   270.779     CA     4265.45  2.0426
    Total S =  2511.190 + j   816.868
IEEE13_CDPSM_Z   Nbus=[    53,    53,    90] Nlink=[    87,    87,    60] MAEv=[ 0.0000, 0.0047] MAEi=[   0.0002,   4.9501]
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2458.66 -0.0471     65.84 -0.8227    115.573 + j   113.336     AB     4226.50  0.4885
    B   2456.72 -2.1171     48.45 -3.0037     75.233 + j    92.245     BC     4274.73 -1.5990
    C   2462.06  2.0595     48.48  1.1720     75.358 + j    92.563     CA     4276.42  2.5766
    Total S =   266.164 + j   298.144
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2458.66 -0.0471     65.84 -0.8227    115.573 + j   113.336     AB     4226.50  0.4885
    B   2456.72 -2.1171     48.45 -3.0037     75.233 + j    92.245     BC     4274.73 -1.5990
    C   2462.06  2.0595     48.48  1.1720     75.358 + j    92.563     CA     4276.42  2.5766
    Total S =   266.164 + j   298.144
  GridLAB-D branch flow in XF_XFM1 from 633
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2472.39 -0.5675     52.41  4.6526     62.995 + j   113.238     AB     4246.50 -0.0318
    B   2467.48  3.6466     38.53  2.3135     22.385 + j    92.389     BC     4299.39 -2.1190
    C   2476.92  1.5380     38.56  0.2089     22.855 + j    92.742     CA     4299.91  2.0556
    Total S =   108.235 + j   298.369
  OpenDSS branch flow in LINE.670671 from 670, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2442.74 -0.0628    467.48 -0.4705   1048.339 + j   452.788     AB     4193.86  0.4815
    B   2455.09 -2.1188    189.65 -2.3117    456.978 + j    89.241     BC     4263.96 -1.6087
    C   2436.77  2.0473    418.89  1.7825    985.174 + j   267.112     CA     4244.81  2.5637
    Total S =  2490.491 + j   809.142
  OpenDSS branch flow in LINE.670671 from 670, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2442.74 -0.0628    467.48 -0.4705   1048.339 + j   452.788     AB     4193.86  0.4815
    B   2455.09 -2.1188    189.65 -2.3117    456.978 + j    89.241     BC     4263.96 -1.6087
    C   2436.77  2.0473    418.89  1.7827    985.219 + j   266.940     CA     4244.81  2.5637
    Total S =  2490.535 + j   808.969
  GridLAB-D branch flow in LINE_670671 from 670
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2455.50 -0.5838    467.34 -0.9908   1053.783 + j   454.322     AB     4212.10 -0.0395
    B   2464.70  3.6441    189.54  3.4523    458.594 + j    89.055     BC     4285.13 -2.1289
    C   2450.18  1.5261    418.79  1.2630    990.797 + j   266.920     CA     4267.31  2.0426
    Total S =  2503.174 + j   810.297
IEEE13_CDPSM_I   Nbus=[    53,    53,    90] Nlink=[    87,    87,    60] MAEv=[ 0.0000, 0.0050] MAEi=[   0.0002,   5.0233]
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2458.08 -0.0471     65.58 -0.8240    114.948 + j   112.999     AB     4225.13  0.4896
    B   2458.26 -2.1153     47.95 -3.0055     74.185 + j    91.611     BC     4278.12 -1.5983
    C   2461.97  2.0595     47.88  1.1694     74.182 + j    91.607     CA     4275.84  2.5765
    Total S =   263.315 + j   296.217
  OpenDSS branch flow in TRANSFORMER.XFM1 from 633, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2458.08 -0.0471     65.58 -0.8240    114.948 + j   112.999     AB     4225.13  0.4896
    B   2458.26 -2.1153     47.95 -3.0055     74.185 + j    91.611     BC     4278.12 -1.5983
    C   2461.97  2.0595     47.88  1.1694     74.182 + j    91.607     CA     4275.84  2.5765
    Total S =   263.315 + j   296.217
  GridLAB-D branch flow in XF_XFM1 from 633
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2472.60 -0.5677     51.52  4.6441     61.016 + j   111.838     AB     4247.24 -0.0314
    B   2469.37  3.6472     37.77  2.2985     20.548 + j    90.988     BC     4301.97 -2.1185
    C   2477.83  1.5385     37.64  0.1898     20.544 + j    90.981     CA     4301.76  2.0556
    Total S =   102.108 + j   293.806
  OpenDSS branch flow in LINE.670671 from 670, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2442.00 -0.0628    470.71 -0.4695   1055.735 + j   454.671     AB     4192.50  0.4827
    B   2456.83 -2.1171    187.78 -2.3152    452.331 + j    90.795     BC     4267.33 -1.6080
    C   2436.49  2.0473    419.10  1.7837    985.867 + j   266.007     CA     4243.92  2.5637
    Total S =  2493.932 + j   811.474
  OpenDSS branch flow in LINE.670671 from 670, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2442.00 -0.0628    470.71 -0.4695   1055.735 + j   454.671     AB     4192.50  0.4827
    B   2456.83 -2.1171    187.78 -2.3152    452.331 + j    90.795     BC     4267.33 -1.6080
    C   2436.49  2.0473    419.09  1.7837    985.857 + j   266.005     CA     4243.92  2.5637
    Total S =  2493.922 + j   811.471
  GridLAB-D branch flow in LINE_670671 from 670
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2455.66 -0.5841    467.64 -0.9882   1055.880 + j   451.508     AB     4212.73 -0.0390
    B   2466.78  3.6448    186.66  3.4513    451.853 + j    88.561     BC     4287.90 -2.1284
    C   2451.11  1.5267    416.24  1.2665    985.892 + j   262.524     CA     4269.37  2.0426
    Total S =  2493.625 + j   802.593
IEEE13_CDPSM_P   Nbus=[    53,    53,    90] Nlink=[    87,    87,    60] MAEv=[ 0.0000, 0.0053] MAEi=[   0.0004,   6.2046]
```

## Limitations on Validation

GridLAB-D has assumptions and component models that differ from those in OpenDSS, which may affect
the comparison of solutions between them:

1. There is no neutral impedance for transformer connections in GridLAB-D.
2. The ```shunt_impedance``` is only implemented for WYE-WYE or SINGLE_PHASE transfromers in GridLAB-D.
3. GridLAB-D transformers only have two windings.
4. The regulator impedance is modeled differently.
5. Capacitor banks are always on in the converted GridLAB-D model; control parameters are translated but not activated.
6. In a constant-current load model, the angle rotations are not exactly correct, especially for unbalanced loads or loads connected in Delta. See [GridLAB-D Issue 1312](https://github.com/gridlab-d/gridlab-d/issues/1312)
7. GridLAB-D calculates line parameters with Carson's equations, as simplified in Kersting's book. OpenDSS defaults to Deri's method, but it offers Full Carson and Carson options. Specify ```Carson``` for compatibility. (Deri is the OpenDSS default because it's easy to calculate, and it closely matches Full Carson.)
8. In GridLAB-D, wye/delta transformers have to be converted to delta/wye, swapping primary and secondary windings. With **check_branches**, choose an adjacent branch for proper comparisons.
9. In GridLAB-D, the IEEE13 results are affected by a bug in default solar insolation.  See [GridLAB-D Issue 1333] (https://github.com/gridlab-d/gridlab-d/issues/1333)

If these effects cannot be mitigated, one could either remove the unsupported feature from the test case, or
use **skip_gld** for the test case.

Some other limitations on the validation process include:

1. MAEv is limited to the line-to-neutral voltages. Using **check_branches** can partially mitigate this, but it does not implement a systematic comparison of line-to-line voltages.
2. MAEi misses the regulators; it captures lines, transformers and switches.
3. MAEi misses the shunt components, e.g., loads, capacitors, DER.
