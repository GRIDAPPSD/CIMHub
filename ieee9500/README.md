## CIMHub: IEEE 9500-Node Test Case Files

Copyright (c) 2017-2021, Battelle Memorial Institute

This directory contains the power system model files and scripts to help convert the CIM XML model to other formats and compare the power flow solutions.

## CIM XML Model Files

These are contained in the Base subdirectory. There are separate model versions for blanced and unbalanced load models.

------

## Exporting to DSS and GLM file formats

The CIMHub repo contains a set of scripts for converting the CIM XML model to OpenDSS and GridLab-D file formats. 

It also can compare the power flow solution results (if OpenDSS and GridLab-D are installed on your local machine)

To run the conversion and power flow solution script, follow the instructions below:


1. Clone the final9500node branch of the CIMHub repository: ```git clone https://github.com/GRIDAPPSD/CIMHub.git -b final9500node```

2. Install the CIMHub Python package. From your home directory, run ```python3 -m pip install -e CIMHub```

3. Build the CIMHub java libraries by changing directories into cimhub library with `cd CIMHub/cimhub`. Build the java library with `mvn clean install`

4. Return to the main CIMHub directory with `cd ..` and install the Blazegraph database engine:
   * Install the [Docker Engine](https://docs.docker.com/install/)
   * Install the Blazegraph engine with ```docker pull lyrasis/blazegraph:2.1.5```
   * Install the CIMHub docker package with ```docker pull gridappsd/cimhub:0.0.4```
   * Start the Blazegraph engine by running `./start.sh`
   * Exit the docker terminal with `exit`

5. Change directories into the 9500 node folder with `cd ieee9500`

6. Run `python3 test9500bal.py` or `python3 test9500unbal.py` to convert the CIM XML model

7. Run `./zipall.sh` and `./zipcomparisons.h` to create downloadable archives

------

## Building the CIM XML model from Original DSS Files

To build the CIM XML files from the original DSS source files:

1. Download the [cimext branch of OpenDSScmd](https://github.com/GRIDAPPSD/GOSS-GridAPPS-D/tree/feature/cimext/opendss)
   * Clone the GOSS-GridAPPSD repo with `git clone https://github.com/GRIDAPPSD/GOSS-GridAPPS-D.git -b feature/cimext`
   * If OpenDSScmd is already installed, check its location with `which opendsscmnd`. It 9s 
   * Move the opendsscmd executable with `sudo cp -i /YOUR_HOME_PATH/GOSS-GridAPPS-D/opendss/opendsscmd /usr/local/bin`

2. Uncomment lines 41 and 46 in test9500bal.py and test9500unbal.py. Now, the script will read from the original_dss directory and build the CIM XML files

3. Re-run `python3 test9500bal.py` or `python3 test9500unbal.py` to re-build the XML files and solve the power flow solution.


### Balanced Load Results

```

   OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7372.48 -0.5533    139.19 -0.5494   1026.131 + j    -3.940     AB    12766.47 -0.0298
    B   7368.97 -2.6477    132.71 -2.6236    977.645 + j   -23.552     BC    12763.14 -2.1241
    C   7368.64  1.5411    150.25  1.5275   1107.028 + j    15.072     CA    12766.18  2.0649
    Total S =  3110.804 + j   -12.420
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7372.44 -0.5533    139.20 -0.5494   1026.266 + j    -3.941     AB    12766.41 -0.0298
    B   7368.94 -2.6477    132.74 -2.6238    977.837 + j   -23.386     BC    12763.08 -2.1241
    C   7368.59  1.5411    150.28  1.5273   1107.210 + j    15.267     CA    12766.11  2.0649
    Total S =  3111.312 + j   -12.059
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7373.31 -0.5533    139.11 -0.5571   1025.705 + j     3.844     AB    12767.04 -0.0300
    B   7368.20  3.6353    132.61  3.6454    977.020 + j    -9.824     BC    12761.88 -2.1242
    C   7368.54  1.5411    150.61  1.5200   1109.491 + j    23.448     CA    12766.80  2.0649
    Total S =  3112.215 + j    17.468
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7368.29 -0.5603    123.26 -0.5007    906.593 + j   -54.020     AB    12773.98 -0.0384
    B   7367.00 -2.6581    124.88 -2.5995    918.432 + j   -53.921     BC    12713.65 -2.1320
    C   7343.19  1.5376    123.43  1.5685    905.937 + j   -27.995     CA    12753.34  2.0605
    Total S =  2730.962 + j  -135.937
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7367.96 -0.5603    123.28 -0.5009    906.716 + j   -53.869     AB    12773.28 -0.0385
    B   7366.53 -2.6581    124.92 -2.5995    918.674 + j   -53.936     BC    12712.87 -2.1320
    C   7342.76  1.5376    123.46  1.5685    906.134 + j   -28.001     CA    12752.68  2.0605
    Total S =  2731.524 + j  -135.806
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7367.92 -0.5602    123.19 -0.5109    906.516 + j   -44.765     AB    12771.93 -0.0388
    B   7362.75  3.6246    125.31  3.6740    921.463 + j   -45.641     BC    12709.58 -2.1325
    C   7341.82  1.5369    123.84  1.5584    909.006 + j   -19.496     CA    12749.10  2.0602
    Total S =  2736.984 + j  -109.902
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7376.83 -0.5603    169.65 -0.9212   1170.871 + j   441.968     AB    12792.76 -0.0383
    B   7380.13 -2.6581    178.68 -3.0222   1232.267 + j   469.572     BC    12785.17 -2.1298
    C   7412.80  1.5376    142.08  1.1846    988.254 + j   364.194     CA    12821.09  2.0581
    Total S =  3391.392 + j  1275.734
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7376.47 -0.5603    169.72 -0.9212   1171.297 + j   442.129     AB    12792.02 -0.0383
    B   7379.64 -2.6581    178.67 -3.0220   1232.184 + j   469.294     BC    12784.33 -2.1298
    C   7412.32  1.5376    142.16  1.1844    988.634 + j   364.530     CA    12820.37  2.0581
    Total S =  3392.115 + j  1275.953
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7374.30 -0.5609    171.03 -0.9300   1176.244 + j   455.069     AB    12784.63 -0.0390
    B   7373.61  3.6245    182.68  3.2484   1252.888 + j   494.774     BC    12773.32 -2.1300
    C   7407.84  1.5376    143.18  1.1617    986.596 + j   389.375     CA    12816.79  2.0579
    Total S =  3415.728 + j  1339.218
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7308.13 -0.5707     84.23 -0.8615    589.706 + j   176.472     AB    12667.16 -0.0467
    B   7318.65 -2.6651     91.01 -2.9398    641.116 + j   180.693     BC    12687.57 -2.1398
    C   7339.08  1.5254     78.31  1.2402    551.482 + j   161.683     CA    12691.25  2.0469
    Total S =  1782.304 + j   518.847
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7307.34 -0.5707     84.24 -0.8615    589.744 + j   176.483     AB    12665.70 -0.0467
    B   7317.75 -2.6651     91.03 -2.9398    641.188 + j   180.713     BC    12686.04 -2.1398
    C   7338.21  1.5254     78.32  1.2402    551.520 + j   161.694     CA    12689.81  2.0469
    Total S =  1782.452 + j   518.890
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7308.07 -0.5704     84.38 -0.8709    589.006 + j   182.520     AB    12665.62 -0.0468
    B   7314.28  3.6178     91.26  3.3266    639.376 + j   191.598     BC    12679.81 -2.1396
    C   7337.53  1.5259     78.50  1.2345    551.707 + j   165.430     CA    12690.19  2.0474
    Total S =  1780.090 + j   539.549
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7267.76 -0.5760     47.80 -0.8515    334.296 + j    94.533     AB    12588.54 -0.0558
    B   7246.34 -2.6756     64.28 -2.9473    448.734 + j   125.036     BC    12543.68 -2.1477
    C   7267.19  1.5202     25.42  1.2273    176.871 + j    53.333     CA    12593.97  2.0429
    Total S =   959.901 + j   272.902
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7266.03 -0.5760     47.81 -0.8515    334.301 + j    94.535     AB    12585.22 -0.0558
    B   7244.24 -2.6756     64.31 -2.9473    448.806 + j   125.056     BC    12540.27 -2.1477
    C   7265.34  1.5202     25.43  1.2273    176.878 + j    53.335     CA    12590.87  2.0429
    Total S =   959.985 + j   272.925
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7264.32 -0.5748     47.87 -0.8692    332.775 + j   100.879     AB    12582.83 -0.0554
    B   7238.55  3.6076     64.68  3.3289    450.138 + j   128.820     BC    12534.65 -2.1477
    C   7263.28  1.5199     25.61  1.2124    177.261 + j    56.291     CA    12582.46  2.0434
    Total S =   960.175 + j   285.990
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7135.42 -0.5672     33.40 -0.8275    230.281 + j    61.316     AB    12427.77 -0.0463
    B   7178.99 -2.6704     31.43 -2.9274    218.244 + j    57.377     BC    12456.86 -2.1363
    C   7263.43  1.5324     25.26  1.2737    177.367 + j    46.929     CA    12488.74  2.0483
    Total S =   625.892 + j   165.622
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7133.66 -0.5672     33.41 -0.8271    230.367 + j    61.253     AB    12418.61 -0.0454
    B   7177.34 -2.6686     31.44 -2.9271    218.182 + j    57.687     BC    12459.98 -2.1355
    C   7261.31  1.5324     25.27  1.2739    177.407 + j    46.906     CA    12485.37  2.0483
    Total S =   625.956 + j   165.846
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7127.66 -0.5670     33.60 -0.8326    231.065 + j    62.858     AB    12407.66 -0.0462
    B   7164.05  3.6132     31.69  3.3479    219.089 + j    59.529     BC    12436.36 -2.1359
    C   7253.86  1.5326     25.42  1.2667    177.942 + j    48.457     CA    12473.48  2.0485
    Total S =   628.096 + j   170.844
ieee9500bal      Nbus=[  9549,  9549, 12524] Nlink=[ 11252, 11252, 12156] MAEv=[ 0.0002, 0.0068] MAEi=[   0.0087,   0.1773]

```

----
## Unbalanced Load Results

```

  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7366.21 -0.5533    139.79 -0.5522   1029.744 + j    -1.078     AB    12755.64 -0.0298
    B   7362.73 -2.6477    133.59 -2.6281    983.407 + j   -19.226     BC    12751.96 -2.1241
    C   7361.96  1.5411    151.12  1.5240   1112.369 + j    19.028     CA    12754.97  2.0649
    Total S =  3125.520 + j    -1.276
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7366.11 -0.5533    139.81 -0.5522   1029.885 + j    -1.078     AB    12755.70 -0.0298
    B   7362.90 -2.6477    133.61 -2.6281    983.591 + j   -19.229     BC    12752.12 -2.1241
    C   7361.98  1.5411    151.15  1.5240   1112.564 + j    19.031     CA    12754.90  2.0649
    Total S =  3126.040 + j    -1.276
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7367.22 -0.5533    139.51 -0.5589   1027.788 + j     5.733     AB    12757.09 -0.0300
    B   7362.85  3.6353    132.68  3.6447    976.886 + j    -9.175     BC    12751.88 -2.1243
    C   7361.96  1.5410    151.29  1.5171   1113.444 + j    26.610     CA    12755.55  2.0648
    Total S =  3118.118 + j    23.168
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7348.16 -0.5603    124.08 -0.5051    910.395 + j   -50.261     AB    12740.89 -0.0384
    B   7348.97 -2.6581    125.57 -2.6033    921.425 + j   -50.548     BC    12721.31 -2.1302
    C   7370.08  1.5376    123.29  1.5701    908.193 + j   -29.493     CA    12759.20  2.0586
    Total S =  2740.013 + j  -130.302
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7347.83 -0.5603    124.11 -0.5053    910.525 + j   -50.109     AB    12740.62 -0.0384
    B   7348.98 -2.6581    125.60 -2.6033    921.668 + j   -50.561     BC    12720.85 -2.1302
    C   7369.54  1.5376    123.33  1.5699    908.390 + j   -29.341     CA    12758.44  2.0586
    Total S =  2740.582 + j  -130.011
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7348.81 -0.5600    123.47 -0.5128    906.323 + j   -42.795     AB    12740.42 -0.0385
    B   7345.78  3.6249    125.74  3.6716    922.649 + j   -43.140     BC    12716.27 -2.1306
    C   7366.27  1.5372    123.60  1.5603    910.208 + j   -21.032     CA    12753.72  2.0587
    Total S =  2739.180 + j  -106.967
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.54 -0.5603    171.26 -0.9303   1176.061 + j   456.164     AB    12814.38 -0.0364
    B   7416.33 -2.6581    180.59 -3.0267   1249.316 + j   482.572     BC    12807.19 -2.1316
    C   7402.09  1.5376    143.60  1.1741    993.466 + j   377.978     CA    12802.02  2.0581
    Total S =  3418.843 + j  1316.714
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.21 -0.5603    171.30 -0.9304   1176.190 + j   456.450     AB    12814.61 -0.0364
    B   7416.92 -2.6581    179.19 -3.0262   1240.049 + j   478.246     BC    12807.11 -2.1317
    C   7401.41  1.5376    143.72  1.1739    994.166 + j   378.443     CA    12801.15  2.0581
    Total S =  3410.405 + j  1313.139
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7363.77 -0.5608    172.24 -0.9389   1178.739 + j   468.210     AB    12808.34 -0.0370
    B   7411.52  3.6246    182.34  3.2453   1255.376 + j   500.387     BC    12796.40 -2.1318
    C   7396.53  1.5377    144.63  1.1515    990.954 + j   402.965     CA    12797.80  2.0580
    Total S =  3425.070 + j  1371.562
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7301.26 -0.5707     84.70 -0.8627    592.244 + j   178.020     AB    12654.84 -0.0467
    B   7311.29 -2.6651     91.77 -2.9421    645.355 + j   183.469     BC    12675.06 -2.1398
    C   7331.99  1.5254     78.78  1.2388    554.040 + j   163.273     CA    12679.16  2.0469
    Total S =  1791.639 + j   524.762
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7300.40 -0.5707     84.72 -0.8627    592.287 + j   178.033     AB    12653.51 -0.0467
    B   7310.61 -2.6651     91.78 -2.9419    645.457 + j   183.376     BC    12673.78 -2.1398
    C   7331.19  1.5254     78.79  1.2388    554.078 + j   163.284     CA    12677.72  2.0469
    Total S =  1791.821 + j   524.693
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7301.58 -0.5705     84.74 -0.8717    590.899 + j   183.573     AB    12655.02 -0.0468
    B   7308.95  3.6178     91.48  3.3260    640.377 + j   192.317     BC    12669.41 -2.1398
    C   7330.30  1.5257     78.68  1.2339    552.398 + j   165.924     CA    12678.20  2.0473
    Total S =  1783.674 + j   541.814
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7245.28 -0.5760     48.32 -0.8535    336.683 + j    95.907     AB    12553.08 -0.0557
    B   7227.94 -2.6756     64.62 -2.9482    449.787 + j   125.752     BC    12551.77 -2.1458
    C   7294.90  1.5202     25.40  1.2271    177.420 + j    53.533     CA    12598.53  2.0409
    Total S =   963.891 + j   275.191
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7243.54 -0.5760     48.33 -0.8533    336.707 + j    95.850     AB    12550.20 -0.0557
    B   7226.36 -2.6756     64.64 -2.9480    449.878 + j   125.693     BC    12548.71 -2.1458
    C   7292.94  1.5202     25.41  1.2271    177.428 + j    53.535     CA    12595.32  2.0409
    Total S =   964.012 + j   275.078
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7244.53 -0.5746     47.80 -0.8691    331.365 + j   100.531     AB    12550.74 -0.0552
    B   7220.66  3.6077     65.02  3.3283    451.294 + j   129.483     BC    12540.38 -2.1457
    C   7288.78  1.5202     25.56  1.2125    177.527 + j    56.434     CA    12587.72  2.0419
    Total S =   960.186 + j   286.449
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7117.47 -0.5672     33.55 -0.8276    230.754 + j    61.485     AB    12440.50 -0.0442
    B   7211.52 -2.6704     31.37 -2.9287    218.746 + j    57.795     BC    12472.76 -2.1382
    C   7249.40  1.5324     25.42  1.2729    178.124 + j    47.295     CA    12461.01  2.0481
    Total S =   627.624 + j   166.576
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7116.41 -0.5672     33.55 -0.8276    230.707 + j    61.473     AB    12435.29 -0.0432
    B   7213.72 -2.6686     31.37 -2.9278    218.709 + j    57.990     BC    12477.28 -2.1376
    C   7245.05  1.5324     25.44  1.2732    178.175 + j    47.242     CA    12456.31  2.0482
    Total S =   627.591 + j   166.704
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7111.80 -0.5669     33.68 -0.8328    231.092 + j    62.937     AB    12426.06 -0.0438
    B   7202.50  3.6136     31.54  3.3482    219.190 + j    59.579     BC    12454.43 -2.1376
    C   7236.66  1.5331     25.60  1.2661    178.716 + j    48.887     CA    12446.29  2.0489
    Total S =   628.999 + j   171.403
ieee9500unbal    Nbus=[  9549,  9549, 12524] Nlink=[ 11252, 11252, 12156] MAEv=[ 0.0002, 0.0072] MAEi=[   0.0394,   0.1431]
```
