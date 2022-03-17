# CIMHub Test Cases for IEEE 1547-2018 Inverter Models

Copyright (c) 2021-2022, Battelle Memorial Institute

These test cases are based on a 6-MW photovoltaic system, connected through a delta-wye transformer
to a 13.2-kV distribution circuit. The point of common coupling (PCC) is on the high side of the
transformer. When the photovoltaic system generates a full 6 MW and the grid source voltage is
1.05 per-unit, the PCC voltage will rise to 1.08 per-unit, which is into the B Range defined
in ANSI/IEEE C84.1. However, the smart inverter functions can mitigate the voltage rise. See 
IEEE P1547.2/D6.2 for more background on how the smarter inverter functions work, including
how settings are determined. IEEE 1547-2018 defines Category A and Category B for the reactive
power and control capabilities of distributed energy resources. Ultimately, these CIMHub test cases will 
encompass all functionality specified in IEEE 1547-2018, but some necessary features are currently 
missing in OpenDSS and/or CIM.

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
    A   8340.75  0.1586    434.09  3.3693  -3612.001 + j   249.967     AB    14446.60  0.6822
    B   8340.75  4.3474    434.09  1.2749  -3612.001 + j   249.968     BC    14446.60 -1.4122
    C   8340.75  2.2530    434.09 -0.8195  -3612.001 + j   249.968     CA    14446.60  2.7766
    Total S = -10836.004 + j   749.903
local_unity_a    Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0068] MAEi=[   0.1145, 192.2415]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7994.83  0.1030    265.86 -2.6780  -1988.801 + j   749.919     AB    13847.45  0.6266
    B   7994.83 -1.9914    265.86  1.5108  -1988.801 + j   749.919     BC    13847.45 -1.4678
    C   7994.83  2.1974    265.86 -0.5836  -1988.801 + j   749.919     CA    13847.45  2.7210
    Total S = -5966.402 + j  2249.756
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7994.79  0.1030    265.88 -2.6779  -1988.817 + j   750.321     AB    13847.38  0.6266
    B   7994.79 -1.9914    265.88  1.5109  -1988.817 + j   750.321     BC    13847.38 -1.4678
    C   7994.79  2.1974    265.88 -0.5835  -1988.817 + j   750.321     CA    13847.38  2.7210
    Total S = -5966.450 + j  2250.964
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8743.84  0.1302    427.39  3.0134  -3612.940 + j  -954.970     AB    15144.78  0.6538
    B   8743.84  4.3190    427.39  0.9190  -3612.941 + j  -954.969     BC    15144.78 -1.4406
    C   8743.84  2.2246    427.39 -1.1754  -3612.941 + j  -954.969     CA    15144.78  2.7482
    Total S = -10838.822 + j -2864.908
local_optpf_a    Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.1083, 161.5305]
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
    A   8852.63  0.1226    433.73  2.9181  -3612.054 + j -1302.209     AB    15333.20  0.6462
    B   8852.63  4.3114    433.73  0.8237  -3612.052 + j -1302.215     BC    15333.20 -1.4482
    C   8852.63  2.2170    433.73 -1.2706  -3612.052 + j -1302.215     CA    15333.20  2.7406
    Total S = -10836.157 + j -3906.638
local_optpf_b    Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.2335, 155.2136]
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
    A   8117.39  0.0947    250.44  3.4427  -1989.800 + j   416.535     AB    14059.73  0.6183
    B   8117.39  4.2835    250.44  1.3483  -1989.800 + j   416.536     BC    14059.73 -1.4761
    C   8117.39  2.1891    250.44 -0.7461  -1989.800 + j   416.536     CA    14059.73  2.7127
    Total S = -5969.400 + j  1249.607
local_fixq_a     Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.0008,   0.0004]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8018.09  0.0401    103.01 -2.7688   -780.663 + j   269.719     AB    13887.74  0.5637
    B   8018.09 -2.0543    103.01  1.4200   -780.663 + j   269.719     BC    13887.74 -1.5307
    C   8018.09  2.1345    103.01 -0.6744   -780.663 + j   269.719     CA    13887.74  2.6581
    Total S = -2341.989 + j   809.156
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8016.86  0.0384    100.71 -2.7663   -762.019 + j   266.855     AB    13885.61  0.5620
    B   8016.86 -2.0560    100.71  1.4224   -762.019 + j   266.855     BC    13885.61 -1.5324
    C   8016.86  2.1328    100.71 -0.6720   -762.019 + j   266.855     CA    13885.61  2.6564
    Total S = -2286.058 + j   800.566
local_combo_a    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0001,-1.0000] MAEi=[  20.7335,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8056.04  0.0977    255.16 -2.7578  -1972.086 + j   580.042     AB    13953.47  0.6213
    B   8056.04 -1.9967    255.16  1.4310  -1972.086 + j   580.042     BC    13953.47 -1.4731
    C   8056.04  2.1921    255.16 -0.6634  -1972.086 + j   580.042     CA    13953.47  2.7157
    Total S = -5916.257 + j  1740.127
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8055.96  0.0977    254.92 -2.7578  -1970.157 + j   579.475     AB    13953.33  0.6213
    B   8055.96 -1.9967    254.92  1.4310  -1970.157 + j   579.475     BC    13953.33 -1.4731
    C   8055.96  2.1921    254.92 -0.6634  -1970.157 + j   579.475     CA    13953.33  2.7157
    Total S = -5910.472 + j  1738.426
local_combo_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   2.2252,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8119.02  0.0942    250.28 -2.8428  -1989.665 + j   412.764     AB    14062.56  0.6178
    B   8119.02 -2.0001    250.28  1.3460  -1989.665 + j   412.764     BC    14062.56 -1.4765
    C   8119.02  2.1886    250.28 -0.7484  -1989.665 + j   412.764     CA    14062.56  2.7122
    Total S = -5968.994 + j  1238.292
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8119.09  0.0942    250.27 -2.8430  -1989.690 + j   412.407     AB    14062.68  0.6178
    B   8119.09 -2.0001    250.27  1.3458  -1989.690 + j   412.407     BC    14062.68 -1.4765
    C   8119.09  2.1886    250.27 -0.7486  -1989.690 + j   412.407     CA    14062.68  2.7122
    Total S = -5969.070 + j  1237.222
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   9301.50  0.0912    492.95  2.5660  -3603.128 + j -2835.655     AB    16110.67  0.6148
    B   9301.50  4.2800    492.95  0.4717  -3603.129 + j -2835.654     BC    16110.67 -1.4796
    C   9301.50  2.1856    492.95  4.6604  -3603.128 + j -2835.655     CA    16110.67  2.7092
    Total S = -10809.384 + j -8506.965
local_vvar_a     Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0001, 0.0000] MAEi=[   0.0660, 242.6660]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8056.70  0.0977    257.31 -2.7576  -1988.748 + j   585.320     AB    13954.61  0.6213
    B   8056.70 -1.9967    257.31  1.4312  -1988.748 + j   585.320     BC    13954.61 -1.4731
    C   8056.70  2.1921    257.31 -0.6632  -1988.748 + j   585.320     CA    13954.61  2.7157
    Total S = -5966.243 + j  1755.961
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8056.72  0.0977    257.31 -2.7576  -1988.722 + j   585.313     AB    13954.65  0.6213
    B   8056.72 -1.9967    257.31  1.4312  -1988.722 + j   585.313     BC    13954.65 -1.4731
    C   8056.72  2.1921    257.31 -0.6632  -1988.722 + j   585.313     CA    13954.65  2.7157
    Total S = -5966.165 + j  1755.938
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   9337.38  0.0887    499.67  2.5416  -3602.044 + j -2965.303     AB    16172.82  0.6123
    B   9337.38  4.2775    499.67  0.4472  -3602.045 + j -2965.302     BC    16172.82 -1.4821
    C   9337.38  2.1831    499.67  4.6360  -3602.044 + j -2965.303     CA    16172.82  2.7067
    Total S = -10806.132 + j -8895.907
local_vvar_b     Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.0305, 242.3550]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8013.71  0.1012    263.10 -2.7018  -1988.712 + j   700.336     AB    13880.15  0.6248
    B   8013.71 -1.9932    263.10  1.4870  -1988.712 + j   700.336     BC    13880.15 -1.4696
    C   8013.71  2.1956    263.10 -0.6074  -1988.712 + j   700.336     CA    13880.15  2.7192
    Total S = -5966.137 + j  2101.009
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8095.32  0.0960    252.75 -2.8098  -1989.514 + j   478.007     AB    14021.51  0.6196
    B   8095.32 -1.9984    252.75  1.3790  -1989.514 + j   478.007     BC    14021.51 -1.4748
    C   8095.32  2.1904    252.75 -0.7154  -1989.514 + j   478.007     CA    14021.51  2.7140
    Total S = -5968.543 + j  1434.022
local_avr_b      Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0087,-1.0000] MAEi=[  93.1228,  -1.0000]
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
    A   9337.38  0.0887    499.67  2.5416  -3602.044 + j -2965.303     AB    16172.82  0.6123
    B   9337.38  4.2775    499.67  0.4472  -3602.045 + j -2965.302     BC    16172.82 -1.4821
    C   9337.38  2.1831    499.67  4.6360  -3602.044 + j -2965.303     CA    16172.82  2.7067
    Total S = -10806.132 + j -8895.907
local_vwatt_b    Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   2.8117, 332.6620]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8115.08  0.0942    250.68 -2.8372  -1989.507 + j   424.335     AB    14055.73  0.6178
    B   8115.08 -2.0001    250.68  1.3516  -1989.507 + j   424.335     BC    14055.73 -1.4765
    C   8115.08  2.1886    250.68 -0.7428  -1989.507 + j   424.335     CA    14055.73  2.7122
    Total S = -5968.520 + j  1273.004
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8115.18  0.0942    250.66 -2.8374  -1989.510 + j   423.972     AB    14055.90  0.6178
    B   8115.18 -2.0001    250.66  1.3514  -1989.510 + j   423.972     BC    14055.90 -1.4765
    C   8115.18  2.1886    250.66 -0.7430  -1989.510 + j   423.972     CA    14055.90  2.7122
    Total S = -5968.530 + j  1271.917
remote_vvar_a    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0965,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8035.05  0.0995    260.14 -2.7292  -1988.699 + j   643.482     AB    13917.11  0.6231
    B   8035.05 -1.9949    260.14  1.4596  -1988.699 + j   643.482     BC    13917.11 -1.4713
    C   8035.05  2.1939    260.14 -0.6348  -1988.699 + j   643.482     CA    13917.11  2.7175
    Total S = -5966.097 + j  1930.447
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8035.17  0.0995    260.12 -2.7293  -1988.711 + j   643.103     AB    13917.32  0.6231
    B   8035.17 -1.9949    260.12  1.4594  -1988.711 + j   643.103     BC    13917.32 -1.4713
    C   8035.17  2.1939    260.12 -0.6350  -1988.711 + j   643.103     CA    13917.32  2.7175
    Total S = -5966.133 + j  1929.309
remote_vvar_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.1477,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.33  0.0873    241.83 -3.0154  -1990.508 + j    77.511     AB    14267.47  0.6109
    B   8237.33 -2.0071    241.83  1.1734  -1990.508 + j    77.511     BC    14267.47 -1.4835
    C   8237.33  2.1817    241.83 -0.9210  -1990.508 + j    77.511     CA    14267.47  2.7053
    Total S = -5971.525 + j   232.534
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8095.32  0.0960    252.75 -2.8098  -1989.514 + j   478.007     AB    14021.51  0.6196
    B   8095.32 -1.9984    252.75  1.3790  -1989.514 + j   478.007     BC    14021.51 -1.4748
    C   8095.32  2.1904    252.75 -0.7154  -1989.514 + j   478.007     CA    14021.51  2.7140
    Total S = -5968.543 + j  1434.022
remote_avr_b     Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0153,-1.0000] MAEi=[  98.3502,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8185.55  0.0628    176.88 -3.0494  -1447.279 + j    42.449     AB    14177.79  0.5864
    B   8185.55 -2.0316    176.88  1.1394  -1447.279 + j    42.449     BC    14177.79 -1.5080
    C   8185.55  2.1572    176.88 -0.9550  -1447.279 + j    42.449     CA    14177.79  2.6808
    Total S = -4341.836 + j   127.346
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8185.56  0.0628    176.89 -3.0494  -1447.338 + j    42.450     AB    14177.81  0.5864
    B   8185.56 -2.0316    176.89  1.1394  -1447.338 + j    42.450     BC    14177.81 -1.5080
    C   8185.56  2.1572    176.89 -0.9550  -1447.338 + j    42.450     CA    14177.81  2.6808
    Total S = -4342.013 + j   127.351
remote_vwatt_b   Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0327,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8034.35  0.0995    257.83 -2.7292  -1970.914 + j   637.728     AB    13915.90  0.6231
    B   8034.35 -1.9949    257.83  1.4596  -1970.914 + j   637.728     BC    13915.90 -1.4713
    C   8034.35  2.1939    257.83 -0.6348  -1970.914 + j   637.728     CA    13915.90  2.7175
    Total S = -5912.741 + j  1913.183
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8034.39  0.0995    257.96 -2.7292  -1971.887 + j   638.042     AB    13915.97  0.6231
    B   8034.39 -1.9949    257.96  1.4596  -1971.887 + j   638.042     BC    13915.97 -1.4713
    C   8034.39  2.1939    257.96 -0.6348  -1971.887 + j   638.042     CA    13915.97  2.7175
    Total S = -5915.660 + j  1914.127
remote_combo_b   Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   1.1320,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.92  0.0593    167.01 -3.0547  -1365.076 + j    37.653     AB    14162.84  0.5829
    B   8176.92 -2.0351    167.01  1.1341  -1365.076 + j    37.653     BC    14162.84 -1.5115
    C   8176.92  2.1537    167.01 -0.9603  -1365.076 + j    37.653     CA    14162.84  2.6773
    Total S = -4095.227 + j   112.959
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.92  0.0593    167.00 -3.0547  -1365.043 + j    37.652     AB    14162.84  0.5829
    B   8176.92 -2.0351    167.00  1.1341  -1365.043 + j    37.652     BC    14162.84 -1.5115
    C   8176.92  2.1537    167.00 -0.9603  -1365.043 + j    37.652     CA    14162.84  2.6773
    Total S = -4095.128 + j   112.957
local_chcurve_b  Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0705,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8092.37  0.0960    253.08 -2.8058  -1989.418 + j   486.439     AB    14016.40  0.6196
    B   8092.37 -1.9984    253.08  1.3830  -1989.418 + j   486.439     BC    14016.40 -1.4748
    C   8092.37  2.1904    253.08 -0.7114  -1989.418 + j   486.439     CA    14016.40  2.7140
    Total S = -5968.254 + j  1459.318
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8092.37  0.0960    253.08 -2.8058  -1989.418 + j   486.439     AB    14016.40  0.6196
    B   8092.37 -1.9984    253.08  1.3830  -1989.418 + j   486.439     BC    14016.40 -1.4748
    C   8092.37  2.1904    253.08 -0.7114  -1989.418 + j   486.439     CA    14016.40  2.7140
    Total S = -5968.254 + j  1459.318
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   9337.38  0.0887    499.67  2.5416  -3602.044 + j -2965.303     AB    16172.82  0.6123
    B   9337.38  4.2775    499.67  0.4472  -3602.045 + j -2965.302     BC    16172.82 -1.4821
    C   9337.38  2.1831    499.67  4.6360  -3602.044 + j -2965.303     CA    16172.82  2.7067
    Total S = -10806.132 + j -8895.907
local_wvar_b     Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.0000, 246.5870]
  OpenDSS branch flow in REACTOR.THEV from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8029.67  0.1047    273.97 -2.7180  -2088.984 + j   689.652     AB    13907.80  0.6283
    B   8029.67 -1.9897    273.97  1.4708  -2088.984 + j   689.652     BC    13907.80 -1.4661
    C   8029.67  2.1991    273.97 -0.6236  -2088.984 + j   689.652     CA    13907.80  2.7227
    Total S = -6266.952 + j  2068.957
  OpenDSS branch flow in REACTOR.THEV from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8030.13  0.1047    273.20 -2.7189  -2083.870 + j   685.948     AB    13908.59  0.6283
    B   8030.13 -1.9897    273.20  1.4699  -2083.870 + j   685.948     BC    13908.59 -1.4661
    C   8030.13  2.1991    273.20 -0.6245  -2083.870 + j   685.948     CA    13908.59  2.7227
    Total S = -6251.609 + j  2057.843
remote_1phase_b  Nbus=[    21,    21,     0] Nlink=[    27,    27,     0] MAEv=[ 0.0002,-1.0000] MAEi=[  11.0416,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8095.32  0.0960    252.75 -2.8098  -1989.514 + j   478.007     AB    14021.51  0.6196
    B   8095.32 -1.9984    252.75  1.3790  -1989.514 + j   478.007     BC    14021.51 -1.4748
    C   8095.32  2.1904    252.75 -0.7154  -1989.514 + j   478.007     CA    14021.51  2.7140
    Total S = -5968.543 + j  1434.022
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8095.31  0.0960    252.76 -2.8098  -1989.528 + j   478.011     AB    14021.49  0.6196
    B   8095.31 -1.9984    252.76  1.3790  -1989.528 + j   478.011     BC    14021.49 -1.4748
    C   8095.31  2.1904    252.76 -0.7154  -1989.528 + j   478.011     CA    14021.49  2.7140
    Total S = -5968.583 + j  1434.032
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

