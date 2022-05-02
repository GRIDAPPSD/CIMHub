# CIMHub Test Cases for IEEE 1547-2018 Inverter Models

Copyright (c) 2021-2022, Battelle Memorial Institute

These test cases are based on a 6-MW photovoltaic system, connected 
through a delta-wye transformer to a 13.2-kV distribution circuit.  The 
point of common coupling (PCC) is on the high side of the transformer.  
When the photovoltaic system generates a full 6 MW and the grid source 
voltage is 1.05 per-unit, the PCC voltage will rise to 1.08 per-unit, 
which is into the B Range defined in ANSI/IEEE C84.1.  However, the smart 
inverter functions can mitigate the voltage rise.  See IEEE P1547.2/D6.2 
for more background on how the smarter inverter functions work, including 
how settings are determined.  IEEE 1547-2018 defines Category A and 
Category B for the reactive power and control capabilities of distributed 
energy resources.  Ultimately, these CIMHub test cases will encompass all 
functionality specified in IEEE 1547-2018, but some necessary features are 
currently missing in OpenDSS and/or CIM.  

![DER_Circuit](der_ckt.png)

The category B reactive power capability requirement is 44% of nameplate 
apparent power, absorbing or injecting.  For category A, the requirement 
is 44% injecting and 25% absorbing.  For a real power rating of 6000 kW, 
the nameplate S=6000/sqrt(1-0.44^2) = 6682 kVA for category B.  The 
reactive power limits are 0.44*6682 = 2940 kVAR.  The minimum power factor 
is 6000/6682 = 0.8980.  The optimal power factor for the test circuit is 
0.92 absorbing, at which the voltage fluctuations are approximately zero 
when the real power fluctuates.  Category B allows the power factor to be 
0.92 absorbing.  

For category A, the nameplate rating is also 6682 kVA, but the reactive 
power absorption capability is 0.25*6682 = 1670 kVAR.  GridLAB-D doesn't 
have separate limits on reactive power injection and absorption.  To 
represent the limit on reactive power absorption, we set S = sqrt(6000^2 + 
1670^2) = 6228 kVA.  This has a side effect of limiting the reactive power 
injection to 1670 kVAR instead of 2940 kVAR, but it's more important to 
accurately represent the absorption capability.  For absorption, the 
minimum power factor is 6000/6228 = 0.9634.  Therefore, the optimal power 
factor is not 0.92 for category A; it must be limited to 0.9634.  

## Process

The test cases are executed with ```python3 test_1547.py```. They cover:

1. Operation at unity power factor.
2. Operation at fixed reactive power.
3. Operation at the optimal power factor that minimizes impact on voltage. The achievable optimal power factor differs for Category A and B, because their reactive power ratings are different.
4. Volt-var control, for Category A and B, including autonomously adjusting reference voltage.
5. Volt-watt control for Category B.
6. Coordinated Volt-var and Volt-watt control for Categories A and B.

The test cases are configured by entries in the ```cases``` array near the top of ```test_1547.py```.
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
- **MAEi** is the mean absolute link current error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in Amperes

The branch for comparison is the injection into the high side of the DER interconnection transformer.

## Results

CIM currently supports only the first 4 cases, which involve fixed power factor or fixed reactive power.
The other 6 cases involve smart inverter functions, to be implemented with CIM Dynamics profile. GridLAB-D
comparison has been skipped for those 6 cases, pending the implementation of CIM Dynamics. (Note: the apparent sgood
agreement in OpenDSS solution for those 6 cases is artificial, because the solved P and Q from the base
case is exported to the converted case as a fixed operating point.)

All test cases respond to voltage at the point of connection, on the low side of the transformer. OpenDSS
does not presently support inverter control sensing at other points in the network.

Notes: 

- At 1.05 per-unit, the high-side voltage should be 8002 volts
- The AVR-B case should do a better job of mitigating the voltage rise (to investigate)

```
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.43  0.0873    241.85 -3.0154  -1990.705 + j    77.519     AB    14267.65  0.6109
    B   8237.43 -2.0071    241.85  1.1734  -1990.705 + j    77.519     BC    14267.65 -1.4835
    C   8237.43  2.1817    241.85 -0.9210  -1990.705 + j    77.519     CA    14267.65  2.7053
    Total S = -5972.116 + j   232.557
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.43  0.0873    241.82 -3.0156  -1990.505 + j    77.163     AB    14267.65  0.6109
    B   8237.43 -2.0071    241.82  1.1732  -1990.505 + j    77.163     BC    14267.65 -1.4835
    C   8237.43  2.1817    241.82 -0.9212  -1990.505 + j    77.163     CA    14267.65  2.7053
    Total S = -5971.515 + j   231.490
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.42  0.0871    241.81  3.2677  -1990.397 + j    77.568     AB    14267.63  0.6107
    B   8237.42  4.2759    241.81  1.1733  -1990.397 + j    77.567     BC    14267.63 -1.4837
    C   8237.42  2.1815    241.81 -0.9211  -1990.397 + j    77.567     CA    14267.63  2.7051
    Total S = -5971.192 + j   232.701
local_unity_a    Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0000] MAEi=[   0.1145,   0.0368]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8033.62  0.0995    260.32 -2.7274  -1988.640 + j   647.300     AB    13914.64  0.6231
    B   8033.62 -1.9949    260.32  1.4614  -1988.640 + j   647.300     BC    13914.64 -1.4713
    C   8033.62  2.1939    260.32 -0.6330  -1988.640 + j   647.300     CA    13914.64  2.7175
    Total S = -5965.920 + j  1941.899
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8033.63  0.0995    260.33 -2.7274  -1988.688 + j   647.315     AB    13914.66  0.6231
    B   8033.63 -1.9949    260.33  1.4614  -1988.688 + j   647.315     BC    13914.66 -1.4713
    C   8033.63  2.1939    260.33 -0.6330  -1988.688 + j   647.315     CA    13914.66  2.7175
    Total S = -5966.065 + j  1941.946
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8426.14  0.0751    242.93  2.9809  -1990.309 + j  -478.193     AB    14594.50  0.5987
    B   8426.14  4.2639    242.93  0.8865  -1990.309 + j  -478.193     BC    14594.49 -1.4957
    C   8426.14  2.1695    242.93 -1.2078  -1990.309 + j  -478.193     CA    14594.49  2.6931
    Total S = -5970.928 + j -1434.579
local_optpf_a    Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0421] MAEi=[   0.0270,  17.3945]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7917.96  0.1082    278.51 -2.5864  -1988.604 + j   953.206     AB    13714.31  0.6318
    B   7917.96 -1.9862    278.51  1.6024  -1988.604 + j   953.206     BC    13714.31 -1.4626
    C   7917.96  2.2026    278.51 -0.4920  -1988.604 + j   953.206     CA    13714.31  2.7262
    Total S = -5965.812 + j  2859.619
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7917.97  0.1065    278.46 -2.5864  -1986.598 + j   956.512     AB    13714.33  0.6301
    B   7917.97 -1.9879    278.46  1.6024  -1986.598 + j   956.512     BC    13714.33 -1.4643
    C   7917.97  2.2009    278.46 -0.4920  -1986.598 + j   956.512     CA    13714.33  2.7245
    Total S = -5959.793 + j  2869.536
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8521.21  0.0691    250.33  2.8420  -1989.716 + j  -768.829     AB    14759.16  0.5927
    B   8521.21  4.2579    250.33  0.7476  -1989.716 + j  -768.830     BC    14759.17 -1.5017
    C   8521.21  2.1635    250.33 -1.3468  -1989.716 + j  -768.830     CA    14759.17  2.6871
    Total S = -5969.148 + j -2306.490
local_optpf_b    Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0647] MAEi=[   0.2335,  28.1860]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8117.38  0.0942    250.44 -2.8405  -1989.600 + j   417.462     AB    14059.71  0.6178
    B   8117.38 -2.0001    250.44  1.3483  -1989.600 + j   417.462     BC    14059.71 -1.4765
    C   8117.38  2.1886    250.44 -0.7461  -1989.600 + j   417.462     CA    14059.71  2.7122
    Total S = -5968.801 + j  1252.385
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8117.39  0.0942    250.44 -2.8405  -1989.611 + j   417.464     AB    14059.73  0.6178
    B   8117.39 -2.0001    250.44  1.3483  -1989.611 + j   417.464     BC    14059.73 -1.4765
    C   8117.39  2.1886    250.44 -0.7461  -1989.611 + j   417.464     CA    14059.73  2.7122
    Total S = -5968.832 + j  1252.391
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.42  0.0871    241.81  3.2677  -1990.397 + j    77.568     AB    14267.63  0.6107
    B   8237.42  4.2759    241.81  1.1733  -1990.397 + j    77.567     BC    14267.63 -1.4837
    C   8237.42  2.1815    241.81 -0.9211  -1990.397 + j    77.567     CA    14267.63  2.7051
    Total S = -5971.192 + j   232.701
local_fixq_a     Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0129] MAEi=[   0.0008,   8.6288]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8035.87  0.0192     53.37 -2.9349   -421.351 + j    79.920     AB    13918.54  0.5428
    B   8035.87 -2.0752     53.37  1.2538   -421.351 + j    79.920     BC    13918.54 -1.5516
    C   8035.87  2.1136     53.37 -0.8406   -421.351 + j    79.920     CA    13918.54  2.6372
    Total S = -1264.052 + j   239.759
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8034.45  0.0192     51.36 -2.9344   -405.357 + j    77.106     AB    13916.08  0.5428
    B   8034.45 -2.0752     51.36  1.2544   -405.357 + j    77.106     BC    13916.08 -1.5516
    C   8034.45  2.1136     51.36 -0.8400   -405.357 + j    77.106     CA    13916.08  2.6372
    Total S = -1216.071 + j   231.318
local_combo_a    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0001,-1.0000] MAEi=[  18.1787,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8116.82  0.0890    234.66 -2.8529  -1866.884 + j   377.786     AB    14058.74  0.6126
    B   8116.82 -2.0054    234.66  1.3359  -1866.884 + j   377.786     BC    14058.74 -1.4818
    C   8116.82  2.1834    234.66 -0.7585  -1866.884 + j   377.786     CA    14058.74  2.7070
    Total S = -5600.652 + j  1133.359
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8116.81  0.0890    234.70 -2.8529  -1867.192 + j   377.849     AB    14058.73  0.6126
    B   8116.81 -2.0054    234.70  1.3359  -1867.192 + j   377.849     BC    14058.73 -1.4818
    C   8116.81  2.1834    234.70 -0.7585  -1867.192 + j   377.849     CA    14058.73  2.7070
    Total S = -5601.576 + j  1133.546
local_combo_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.3617,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8199.40  0.0890    243.80 -2.9589  -1990.265 + j   187.084     AB    14201.78  0.6126
    B   8199.40 -2.0054    243.80  1.2299  -1990.265 + j   187.084     BC    14201.78 -1.4818
    C   8199.40  2.1834    243.80 -0.8645  -1990.265 + j   187.084     CA    14201.78  2.7070
    Total S = -5970.794 + j   561.252
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8199.42  0.0890    243.80 -2.9589  -1990.237 + j   187.081     AB    14201.81  0.6126
    B   8199.42 -2.0054    243.80  1.2299  -1990.237 + j   187.081     BC    14201.81 -1.4818
    C   8199.42  2.1834    243.80 -0.8645  -1990.237 + j   187.081     CA    14201.81  2.7070
    Total S = -5970.711 + j   561.244
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8413.84  0.0759    242.30  2.9994  -1990.359 + j  -441.119     AB    14573.20  0.5995
    B   8413.84  4.2647    242.30  0.9050  -1990.359 + j  -441.121     BC    14573.19 -1.4949
    C   8413.84  2.1703    242.30 -1.1894  -1990.359 + j  -441.121     CA    14573.19  2.6939
    Total S = -5971.078 + j -1323.361
local_vvar_a     Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0230] MAEi=[   0.0230,   1.5051]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8124.73  0.0942    249.72 -2.8508  -1989.870 + j   396.171     AB    14072.45  0.6178
    B   8124.73 -2.0001    249.72  1.3380  -1989.870 + j   396.171     BC    14072.45 -1.4765
    C   8124.73  2.1886    249.72 -0.7564  -1989.870 + j   396.171     CA    14072.45  2.7122
    Total S = -5969.609 + j  1188.512
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8124.80  0.0942    249.71 -2.8510  -1989.884 + j   395.813     AB    14072.57  0.6178
    B   8124.80 -2.0001    249.71  1.3378  -1989.884 + j   395.813     BC    14072.57 -1.4765
    C   8124.80  2.1886    249.71 -0.7566  -1989.884 + j   395.813     CA    14072.57  2.7122
    Total S = -5969.652 + j  1187.438
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8561.43  0.0666    254.74  2.7858  -1989.353 + j  -893.941     AB    14828.83  0.5902
    B   8561.43  4.2553    254.74  0.6914  -1989.352 + j  -893.942     BC    14828.83 -1.5042
    C   8561.43  2.1609    254.74 -1.4030  -1989.352 + j  -893.942     CA    14828.83  2.6845
    Total S = -5968.058 + j -2681.825
local_vvar_b     Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0469] MAEi=[   0.0642,   5.0224]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8013.01  0.1012    263.20 -2.7009  -1988.690 + j   702.280     AB    13878.94  0.6248
    B   8013.01 -1.9932    263.20  1.4879  -1988.690 + j   702.280     BC    13878.94 -1.4696
    C   8013.01  2.1956    263.20 -0.6065  -1988.690 + j   702.280     CA    13878.94  2.7192
    Total S = -5966.070 + j  2106.839
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8094.88  0.0960    252.80 -2.8093  -1989.541 + j   479.116     AB    14020.74  0.6196
    B   8094.88 -1.9984    252.80  1.3795  -1989.541 + j   479.116     BC    14020.74 -1.4748
    C   8094.88  2.1904    252.80 -0.7149  -1989.541 + j   479.116     CA    14020.74  2.7140
    Total S = -5968.624 + j  1437.348
local_avr_b      Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0088,-1.0000] MAEi=[  93.5943,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.92  0.0593    167.01 -3.0547  -1365.076 + j    37.653     AB    14162.84  0.5829
    B   8176.92 -2.0351    167.01  1.1341  -1365.076 + j    37.653     BC    14162.84 -1.5115
    C   8176.92  2.1537    167.01 -0.9603  -1365.076 + j    37.653     CA    14162.84  2.6773
    Total S = -4095.227 + j   112.959
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.66  0.0593    166.70 -3.0548  -1362.513 + j    37.344     AB    14162.39  0.5829
    B   8176.66 -2.0351    166.70  1.1339  -1362.513 + j    37.344     BC    14162.39 -1.5115
    C   8176.66  2.1537    166.70 -0.9605  -1362.513 + j    37.344     CA    14162.39  2.6773
    Total S = -4087.539 + j   112.033
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.42  0.0871    241.81  3.2677  -1990.397 + j    77.568     AB    14267.63  0.6107
    B   8237.42  4.2759    241.81  1.1733  -1990.397 + j    77.567     BC    14267.63 -1.4837
    C   8237.42  2.1815    241.81 -0.9211  -1990.397 + j    77.567     CA    14267.63  2.7051
    Total S = -5971.192 + j   232.701
local_vwatt_b    Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0057] MAEi=[   2.8117,  74.8062]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8200.74  0.0890    243.72 -2.9608  -1990.284 + j   183.232     AB    14204.10  0.6126
    B   8200.74 -2.0054    243.72  1.2280  -1990.284 + j   183.232     BC    14204.10 -1.4818
    C   8200.74  2.1834    243.72 -0.8664  -1990.284 + j   183.232     CA    14204.10  2.7070
    Total S = -5970.852 + j   549.695
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8200.78  0.0890    243.72 -2.9608  -1990.253 + j   183.229     AB    14204.17  0.6126
    B   8200.78 -2.0054    243.72  1.2280  -1990.253 + j   183.229     BC    14204.17 -1.4818
    C   8200.78  2.1834    243.72 -0.8664  -1990.253 + j   183.229     CA    14204.17  2.7070
    Total S = -5970.759 + j   549.687
remote_vvar_a    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0313,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8120.39  0.0942    250.15 -2.8447  -1989.731 + j   408.795     AB    14064.93  0.6178
    B   8120.39 -2.0001    250.15  1.3441  -1989.731 + j   408.795     BC    14064.93 -1.4765
    C   8120.39  2.1886    250.15 -0.7503  -1989.731 + j   408.795     CA    14064.93  2.7122
    Total S = -5969.194 + j  1226.385
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8120.17  0.0942    250.16 -2.8444  -1989.678 + j   409.508     AB    14064.55  0.6178
    B   8120.17 -2.0001    250.16  1.3444  -1989.678 + j   409.508     BC    14064.55 -1.4765
    C   8120.17  2.1886    250.16 -0.7500  -1989.678 + j   409.508     CA    14064.55  2.7122
    Total S = -5969.033 + j  1228.524
remote_vvar_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.1860,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.33  0.0873    241.83 -3.0154  -1990.508 + j    77.511     AB    14267.47  0.6109
    B   8237.33 -2.0071    241.83  1.1734  -1990.508 + j    77.511     BC    14267.47 -1.4835
    C   8237.33  2.1817    241.83 -0.9210  -1990.508 + j    77.511     CA    14267.47  2.7053
    Total S = -5971.525 + j   232.534
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8094.88  0.0960    252.80 -2.8093  -1989.541 + j   479.116     AB    14020.74  0.6196
    B   8094.88 -1.9984    252.80  1.3795  -1989.541 + j   479.116     BC    14020.74 -1.4748
    C   8094.88  2.1904    252.80 -0.7149  -1989.541 + j   479.116     CA    14020.74  2.7140
    Total S = -5968.624 + j  1437.348
remote_avr_b     Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0153,-1.0000] MAEi=[  98.7870,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8185.55  0.0628    176.88 -3.0494  -1447.279 + j    42.449     AB    14177.79  0.5864
    B   8185.55 -2.0316    176.88  1.1394  -1447.279 + j    42.449     BC    14177.79 -1.5080
    C   8185.55  2.1572    176.88 -0.9550  -1447.279 + j    42.449     CA    14177.79  2.6808
    Total S = -4341.836 + j   127.346
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8185.24  0.0628    176.52 -3.0496  -1444.229 + j    42.107     AB    14177.25  0.5864
    B   8185.24 -2.0316    176.52  1.1392  -1444.229 + j    42.107     BC    14177.25 -1.5080
    C   8185.24  2.1572    176.52 -0.9552  -1444.229 + j    42.107     CA    14177.25  2.6808
    Total S = -4332.686 + j   126.321
remote_vwatt_b   Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   3.3352,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8108.66  0.0873    228.95 -2.8463  -1816.462 + j   383.451     AB    14044.61  0.6109
    B   8108.66 -2.0071    228.95  1.3425  -1816.462 + j   383.451     BC    14044.61 -1.4835
    C   8108.66  2.1817    228.95 -0.7519  -1816.462 + j   383.451     CA    14044.61  2.7053
    Total S = -5449.387 + j  1150.353
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8108.64  0.0873    228.96 -2.8463  -1816.545 + j   383.468     AB    14044.58  0.6109
    B   8108.64 -2.0071    228.96  1.3425  -1816.545 + j   383.468     BC    14044.58 -1.4835
    C   8108.64  2.1817    228.96 -0.7519  -1816.545 + j   383.468     CA    14044.58  2.7053
    Total S = -5449.635 + j  1150.405
remote_combo_b   Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.1082,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.92  0.0593    167.01 -3.0547  -1365.076 + j    37.653     AB    14162.84  0.5829
    B   8176.92 -2.0351    167.01  1.1341  -1365.076 + j    37.653     BC    14162.84 -1.5115
    C   8176.92  2.1537    167.01 -0.9603  -1365.076 + j    37.653     CA    14162.84  2.6773
    Total S = -4095.227 + j   112.959
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.63  0.0593    166.66 -3.0548  -1362.246 + j    37.337     AB    14162.34  0.5829
    B   8176.63 -2.0351    166.66  1.1339  -1362.246 + j    37.337     BC    14162.34 -1.5115
    C   8176.63  2.1537    166.66 -0.9605  -1362.246 + j    37.337     CA    14162.34  2.6773
    Total S = -4086.739 + j   112.012
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8002.07 -0.0000      0.00  0.1220      0.000 + j    -0.000     AB    13860.00  0.5236
    B   8002.07  4.1888      0.00  4.0115      0.000 + j     0.000     BC    13860.00 -1.5708
    C   8002.07  2.0944      0.00  1.6928      0.000 + j     0.000     CA    13860.00  2.6180
    Total S =     0.000 + j     0.000
local_chcurve_b  Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0163] MAEi=[   3.1033, 167.0060]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8080.96  0.0977    254.38 -2.7903  -1989.857 + j   515.724     AB    13996.63  0.6213
    B   8080.96 -1.9967    254.38  1.3985  -1989.857 + j   515.724     BC    13996.63 -1.4731
    C   8080.96  2.1921    254.38 -0.6959  -1989.857 + j   515.724     CA    13996.63  2.7157
    Total S = -5969.570 + j  1547.171
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8080.96  0.0977    254.38 -2.7903  -1989.857 + j   515.724     AB    13996.63  0.6213
    B   8080.96 -1.9967    254.38  1.3985  -1989.857 + j   515.724     BC    13996.63 -1.4731
    C   8080.96  2.1921    254.38 -0.6959  -1989.857 + j   515.724     CA    13996.63  2.7157
    Total S = -5969.570 + j  1547.171
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8048.43  0.0991    258.36  3.5365  -1989.051 + j   606.162     AB    13940.28  0.6227
    B   8048.43  4.2879    258.36  1.4421  -1989.052 + j   606.161     BC    13940.29 -1.4717
    C   8048.43  2.1935    258.36 -0.6523  -1989.051 + j   606.163     CA    13940.28  2.7171
    Total S = -5967.154 + j  1818.486
local_wvar_b     Nbus=[     9,     9,    12] Nlink=[    12,    12,     6] MAEv=[ 0.0000, 0.0035] MAEi=[   0.0000,   3.9807]
  OpenDSS branch flow in REACTOR.THEV from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8121.61  0.0995    263.69 -2.8356  -2096.116 + j   439.047     AB    14067.04  0.6231
    B   8121.61 -1.9949    263.69  1.3532  -2096.116 + j   439.047     BC    14067.04 -1.4713
    C   8121.61  2.1939    263.69 -0.7412  -2096.116 + j   439.047     CA    14067.04  2.7175
    Total S = -6288.349 + j  1317.141
  OpenDSS branch flow in REACTOR.THEV from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8121.62  0.0995    262.44 -2.8367  -2086.599 + j   434.773     AB    14067.06  0.6231
    B   8121.62 -1.9949    262.44  1.3521  -2086.599 + j   434.773     BC    14067.06 -1.4713
    C   8121.62  2.1939    262.44 -0.7423  -2086.599 + j   434.773     CA    14067.06  2.7175
    Total S = -6259.798 + j  1304.320
  GridLAB-D branch flow in REAC_THEV from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8555.88  0.0716    263.15  2.8297  -2088.005 + j  -842.354     AB    14819.22  0.5952
    B   8555.88  4.2604    263.15  0.7353  -2088.005 + j  -842.353     BC    14819.22 -1.4992
    C   8555.88  2.1660    263.15 -1.3590  -2088.005 + j  -842.353     CA    14819.22  2.6896
    Total S = -6264.015 + j -2527.060
remote_1phase_b  Nbus=[    21,    21,    30] Nlink=[    27,    27,    15] MAEv=[ 0.0009, 0.3207] MAEi=[  17.1166,   2.6346]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8094.88  0.0960    252.80 -2.8093  -1989.533 + j   479.114     AB    14020.74  0.6196
    B   8094.88 -1.9984    252.80  1.3795  -1989.533 + j   479.114     BC    14020.74 -1.4748
    C   8094.88  2.1904    252.80 -0.7149  -1989.533 + j   479.114     CA    14020.74  2.7140
    Total S = -5968.600 + j  1437.342
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8094.87  0.0960    252.81 -2.8093  -1989.547 + j   479.117     AB    14020.73  0.6196
    B   8094.87 -1.9984    252.81  1.3795  -1989.547 + j   479.117     BC    14020.73 -1.4748
    C   8094.87  2.1904    252.81 -0.7149  -1989.547 + j   479.117     CA    14020.73  2.7140
    Total S = -5968.640 + j  1437.352
default_avr_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0140,  -1.0000]
```

## Notes on OpenDSS Conversion

The results for autonomously adjusting reference voltage (AVR) cannot be compared closely, because of variations used in the test cases:

- The baseline ```local_avr_b``` simulation had ```vregmax=1.03```, which is not supported in CIM. The exported case uses default ```vregmax=1.05```, which allows the terminal voltage to be higher.
- The baseline ```remote_avr_b``` was set up with dynamic reactive current mode, because the OpenDSS ExpControl does not support monitoring remote buses. The exported model uses ExpControl because the AVR implementation is better, but the remote monitoring signals are not exported.

In the last case, ```default_avr_b```, the base attribute values were set to facilitate a match.

## Notes on GridLAB-D Conversion

Unsupported features were removed from the model, to improve GridLAB-D comparisons:

- Transformer core losses and magnetizing currents were removed
- The positive-sequence grid impedance at the PCC is represented in a series reactor, instead of built in to the source.

Other notes:

- The default solar insolation in GridLAB-D is affecting the match for many comparisons, see [GridLAB-D Issue 1333](https://github.com/gridlab-d/gridlab-d/issues/1333)
- The fixed-Q case does not seem to absorb reactive power in GridLAB-D
- There is no provision for Q limits in GridLAB-D, only on the total apparent power

