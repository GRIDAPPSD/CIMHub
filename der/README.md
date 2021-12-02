# CIMHub Test Cases for IEEE 1547-2018 Inverter Models

Copyright (c) 2021, Battelle Memorial Institute

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
    A   8237.43  0.0871    241.82  3.2677  -1990.490 + j    77.573     AB    14267.64  0.6107
    B   8237.43  4.2759    241.82  1.1733  -1990.490 + j    77.574     BC    14267.64 -1.4837
    C   8237.43  2.1815    241.82 -0.9211  -1990.490 + j    77.574     CA    14267.64  2.7051
    Total S = -5971.470 + j   232.722
local_unity_a    Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.1145,   0.0258]
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
    A   7994.79  0.1025    265.88  3.6052  -1988.504 + j   751.144     AB    13847.38  0.6261
    B   7994.79  4.2913    265.88  1.5108  -1988.504 + j   751.144     BC    13847.38 -1.4683
    C   7994.79  2.1969    265.88 -0.5836  -1988.504 + j   751.144     CA    13847.38  2.7205
    Total S = -5965.511 + j  2253.432
local_optpf_a    Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.1083,   0.0208]
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
    A   7917.97  0.1073    278.46  3.6968  -1987.390 + j   954.860     AB    13714.32  0.6309
    B   7917.97  4.2961    278.46  1.6024  -1987.389 + j   954.861     BC    13714.32 -1.4635
    C   7917.97  2.2017    278.46 -0.4920  -1987.389 + j   954.861     CA    13714.32  2.7253
    Total S = -5962.169 + j  2864.582
local_optpf_b    Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.2335,   0.0482]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8117.38  0.0942    250.44 -2.8405  -1989.600 + j   417.462     AB    14059.71  0.6178
    B   8117.38 -2.0001    250.44  1.3483  -1989.600 + j   417.462     BC    14059.71 -1.4765
    C   8117.38  2.1886    250.44 -0.7461  -1989.600 + j   417.462     CA    14059.71  2.7122
    Total S = -5968.801 + j  1252.385
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8117.42  0.0942    250.44 -2.8405  -1989.594 + j   417.460     AB    14059.78  0.6178
    B   8117.42 -2.0001    250.44  1.3483  -1989.594 + j   417.460     BC    14059.78 -1.4765
    C   8117.42  2.1886    250.44 -0.7461  -1989.594 + j   417.460     CA    14059.78  2.7122
    Total S = -5968.782 + j  1252.381
  GridLAB-D branch flow in XF_DER from HIGH
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8117.39  0.0947    250.44  3.4427  -1989.800 + j   416.535     AB    14059.73  0.6183
    B   8117.39  4.2835    250.44  1.3483  -1989.800 + j   416.536     BC    14059.73 -1.4761
    C   8117.39  2.1891    250.44 -0.7461  -1989.800 + j   416.536     CA    14059.73  2.7127
    Total S = -5969.400 + j  1249.607
local_fixq_a     Nbus=[     9,     9,    12] Nlink=[    12,    12,     3] MAEv=[ 0.0000, 0.0000] MAEi=[   0.0240,   0.0004]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7984.81  0.0716    184.34 -2.6721  -1356.872 + j   570.376     AB    13830.10  0.5952
    B   7984.81 -2.0228    184.34  1.5167  -1356.872 + j   570.376     BC    13830.10 -1.4992
    C   7984.81  2.1660    184.34 -0.5777  -1356.872 + j   570.376     CA    13830.10  2.6896
    Total S = -4070.616 + j  1711.129
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7984.84  0.0716    184.31 -2.6723  -1356.807 + j   570.071     AB    13830.15  0.5952
    B   7984.84 -2.0228    184.31  1.5165  -1356.807 + j   570.071     BC    13830.15 -1.4992
    C   7984.84  2.1660    184.31 -0.5779  -1356.807 + j   570.071     CA    13830.15  2.6896
    Total S = -4070.422 + j  1710.212
local_combo_a    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.1998,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8056.04  0.0977    255.16 -2.7578  -1972.086 + j   580.042     AB    13953.47  0.6213
    B   8056.04 -1.9967    255.16  1.4310  -1972.086 + j   580.042     BC    13953.47 -1.4731
    C   8056.04  2.1921    255.16 -0.6634  -1972.086 + j   580.042     CA    13953.47  2.7157
    Total S = -5916.257 + j  1740.127
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8056.13  0.0977    255.07 -2.7580  -1971.444 + j   579.480     AB    13953.63  0.6213
    B   8056.13 -1.9967    255.07  1.4308  -1971.444 + j   579.480     BC    13953.63 -1.4731
    C   8056.13  2.1921    255.07 -0.6636  -1971.444 + j   579.480     CA    13953.63  2.7157
    Total S = -5914.331 + j  1738.439
local_combo_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.8893,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8045.85  0.0995    258.71 -2.7433  -1989.279 + j   612.742     AB    13935.82  0.6231
    B   8045.85 -1.9949    258.71  1.4455  -1989.279 + j   612.742     BC    13935.82 -1.4713
    C   8045.85  2.1939    258.71 -0.6489  -1989.279 + j   612.742     CA    13935.82  2.7175
    Total S = -5967.836 + j  1838.227
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8045.85  0.0995    258.70 -2.7433  -1989.263 + j   612.737     AB    13935.82  0.6231
    B   8045.85 -1.9949    258.70  1.4455  -1989.263 + j   612.737     BC    13935.82 -1.4713
    C   8045.85  2.1939    258.70 -0.6489  -1989.263 + j   612.737     CA    13935.82  2.7175
    Total S = -5967.790 + j  1838.212
local_vvar_a     Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0065,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8056.70  0.0977    257.31 -2.7576  -1988.748 + j   585.320     AB    13954.61  0.6213
    B   8056.70 -1.9967    257.31  1.4312  -1988.748 + j   585.320     BC    13954.61 -1.4731
    C   8056.70  2.1921    257.31 -0.6632  -1988.748 + j   585.320     CA    13954.61  2.7157
    Total S = -5966.243 + j  1755.961
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8056.63  0.0977    257.32 -2.7576  -1988.785 + j   585.331     AB    13954.49  0.6213
    B   8056.63 -1.9967    257.32  1.4312  -1988.785 + j   585.331     BC    13954.49 -1.4731
    C   8056.63  2.1921    257.32 -0.6632  -1988.785 + j   585.331     CA    13954.49  2.7157
    Total S = -5966.354 + j  1755.993
local_vvar_b     Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0703,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.29  0.0873    241.83 -3.0152  -1990.502 + j    77.859     AB    14267.40  0.6109
    B   8237.29 -2.0071    241.83  1.1736  -1990.502 + j    77.859     BC    14267.40 -1.4835
    C   8237.29  2.1817    241.83 -0.9208  -1990.502 + j    77.859     CA    14267.40  2.7053
    Total S = -5971.505 + j   233.577
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.43  0.0873    241.82 -3.0156  -1990.505 + j    77.163     AB    14267.65  0.6109
    B   8237.43 -2.0071    241.82  1.1732  -1990.505 + j    77.163     BC    14267.65 -1.4835
    C   8237.43  2.1817    241.82 -0.9212  -1990.505 + j    77.163     CA    14267.65  2.7053
    Total S = -5971.515 + j   231.490
local_avr_b      Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0552,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.92  0.0593    167.01 -3.0547  -1365.076 + j    37.653     AB    14162.84  0.5829
    B   8176.92 -2.0351    167.01  1.1341  -1365.076 + j    37.653     BC    14162.84 -1.5115
    C   8176.92  2.1537    167.01 -0.9603  -1365.076 + j    37.653     CA    14162.84  2.6773
    Total S = -4095.227 + j   112.959
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8176.97  0.0593    167.05 -3.0547  -1365.444 + j    37.663     AB    14162.93  0.5829
    B   8176.97 -2.0351    167.05  1.1341  -1365.444 + j    37.663     BC    14162.93 -1.5115
    C   8176.97  2.1537    167.05 -0.9603  -1365.444 + j    37.663     CA    14162.93  2.6773
    Total S = -4096.331 + j   112.990
local_vwatt_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.3630,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8045.85  0.0995    258.71 -2.7433  -1989.279 + j   612.742     AB    13935.82  0.6231
    B   8045.85 -1.9949    258.71  1.4455  -1989.279 + j   612.742     BC    13935.82 -1.4713
    C   8045.85  2.1939    258.71 -0.6489  -1989.279 + j   612.742     CA    13935.82  2.7175
    Total S = -5967.836 + j  1838.227
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8045.85  0.0995    258.70 -2.7433  -1989.263 + j   612.737     AB    13935.82  0.6231
    B   8045.85 -1.9949    258.70  1.4455  -1989.263 + j   612.737     BC    13935.82 -1.4713
    C   8045.85  2.1939    258.70 -0.6489  -1989.263 + j   612.737     CA    13935.82  2.7175
    Total S = -5967.790 + j  1838.212
remote_vvar_a    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0065,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8035.05  0.0995    260.14 -2.7292  -1988.699 + j   643.482     AB    13917.11  0.6231
    B   8035.05 -1.9949    260.14  1.4596  -1988.699 + j   643.482     BC    13917.11 -1.4713
    C   8035.05  2.1939    260.14 -0.6348  -1988.699 + j   643.482     CA    13917.11  2.7175
    Total S = -5966.097 + j  1930.447
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8035.16  0.0995    260.12 -2.7293  -1988.716 + j   643.105     AB    13917.31  0.6231
    B   8035.16 -1.9949    260.12  1.4594  -1988.716 + j   643.105     BC    13917.31 -1.4713
    C   8035.16  2.1939    260.12 -0.6350  -1988.716 + j   643.105     CA    13917.31  2.7175
    Total S = -5966.149 + j  1929.314
remote_vvar_b    Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.1395,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.33  0.0873    241.83 -3.0154  -1990.508 + j    77.511     AB    14267.47  0.6109
    B   8237.33 -2.0071    241.83  1.1734  -1990.508 + j    77.511     BC    14267.47 -1.4835
    C   8237.33  2.1817    241.83 -0.9210  -1990.508 + j    77.511     CA    14267.47  2.7053
    Total S = -5971.525 + j   232.534
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.43  0.0873    241.82 -3.0156  -1990.505 + j    77.163     AB    14267.65  0.6109
    B   8237.43 -2.0071    241.82  1.1732  -1990.505 + j    77.163     BC    14267.65 -1.4835
    C   8237.43  2.1817    241.82 -0.9212  -1990.505 + j    77.163     CA    14267.65  2.7053
    Total S = -5971.515 + j   231.490
remote_avr_b     Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0000,-1.0000] MAEi=[   0.0363,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8185.55  0.0628    176.88 -3.0494  -1447.279 + j    42.449     AB    14177.79  0.5864
    B   8185.55 -2.0316    176.88  1.1394  -1447.279 + j    42.449     BC    14177.79 -1.5080
    C   8185.55  2.1572    176.88 -0.9550  -1447.279 + j    42.449     CA    14177.79  2.6808
    Total S = -4341.836 + j   127.346
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.43  0.0873    241.82 -3.0156  -1990.505 + j    77.163     AB    14267.65  0.6109
    B   8237.43 -2.0071    241.82  1.1732  -1990.505 + j    77.163     BC    14267.65 -1.4835
    C   8237.43  2.1817    241.82 -0.9212  -1990.505 + j    77.163     CA    14267.65  2.7053
    Total S = -5971.515 + j   231.490
remote_vwatt_b   Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0049,-1.0000] MAEi=[ 584.4135,  -1.0000]
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8034.35  0.0995    257.83 -2.7292  -1970.914 + j   637.728     AB    13915.90  0.6231
    B   8034.35 -1.9949    257.83  1.4596  -1970.914 + j   637.728     BC    13915.90 -1.4713
    C   8034.35  2.1939    257.83 -0.6348  -1970.914 + j   637.728     CA    13915.90  2.7175
    Total S = -5912.741 + j  1913.183
  OpenDSS branch flow in TRANSFORMER.DER from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8237.43  0.0873    241.82 -3.0156  -1990.505 + j    77.163     AB    14267.65  0.6109
    B   8237.43 -2.0071    241.82  1.1732  -1990.505 + j    77.163     BC    14267.65 -1.4835
    C   8237.43  2.1817    241.82 -0.9212  -1990.505 + j    77.163     CA    14267.65  2.7053
    Total S = -5971.515 + j   231.490
remote_combo_b   Nbus=[     9,     9,     0] Nlink=[    12,    12,     0] MAEv=[ 0.0218,-1.0000] MAEi=[ 144.0900,  -1.0000]
  OpenDSS branch flow in REACTOR.THEV from HIGH, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8029.67  0.1047    273.97 -2.7180  -2088.984 + j   689.652     AB    13907.80  0.6283
    B   8029.67 -1.9897    273.97  1.4708  -2088.984 + j   689.652     BC    13907.80 -1.4661
    C   8029.67  2.1991    273.97 -0.6236  -2088.984 + j   689.652     CA    13907.80  2.7227
    Total S = -6266.952 + j  2068.957
  OpenDSS branch flow in REACTOR.THEV from HIGH, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   8030.13  0.1047    273.20 -2.7189  -2083.855 + j   685.943     AB    13908.59  0.6283
    B   8030.13 -1.9897    273.20  1.4699  -2083.855 + j   685.943     BC    13908.59 -1.4661
    C   8030.13  2.1991    273.20 -0.6245  -2083.855 + j   685.943     CA    13908.59  2.7227
    Total S = -6251.564 + j  2057.828
remote_1phase_b  Nbus=[    21,    21,     0] Nlink=[    27,    27,     0] MAEv=[ 0.0003,-1.0000] MAEi=[  10.7562,  -1.0000]
```

## Notes on GridLAB-D Conversion

Unsupported features were removed from the model, to improve GridLAB-D comparisons:

- Transformer core losses and magnetizing currents were removed
- The positive-sequence grid impedance at the PCC is represented in a series reactor, instead of built in to the source.

