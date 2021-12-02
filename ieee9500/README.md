## CIMHub: IEEE 9500-Node Test Case Files

Copyright (c) 2017-2021, Battelle Memorial Institute

This directory contains the power system model files and scripts to help convert the CIM XML model to other formats and compare the power flow solutions.

## CIM XML Model Files

These are contained in the Base subdirectory. There are separate model versions for balanced and unbalanced load models.

## Original DSS Source Files

These are the original files used to derive the model from IEEE 8500 Node model and contain in-line comments explaining the model changes. There are separate model versions for balanced and unbalanced load models. These files are located in the original_dss subdirectory.

------
## Model Semi-Geographic Rendering

![9500 node model](https://github.com/GRIDAPPSD/CIMHub/blob/final9500/ieee9500/9500%20Node%20Test%20Feeder%401x_overlay.png)

------

## Exporting to DSS and GLM file formats

The CIMHub repo contains a set of scripts for converting the CIM XML model to OpenDSS and GridLab-D file formats. 

It also can compare the power flow solution results (if OpenDSS and GridLab-D are installed on your local machine)

To run the conversion and power flow solution script, follow the instructions below:


1. Clone the final9500node branch of the CIMHub repository: ```git clone https://github.com/GRIDAPPSD/CIMHub.git -b final9500```

2. Install the CIMHub Python package. From your home directory, run ```python3 -m pip install -e CIMHub```

3. Build the CIMHub java libraries by changing directories into cimhub library with `cd CIMHub/cimhub`. Build the java library with `mvn clean install`

4. Return to the main CIMHub directory with `cd ..` and install the Blazegraph database engine:
   * Install the [Docker Engine](https://docs.docker.com/install/)
   * Install the Blazegraph engine with ```docker pull lyrasis/blazegraph:2.1.5```
   * Install the CIMHub docker package with ```docker pull gridappsd/cimhub:0.0.4```
   * Start the Blazegraph engine by running `./start.sh`
   * Exit the docker terminal with `exit`

5. Change directories into the 9500 node folder with `cd ieee9500`

6. Edit the python script test9500bal.py or test9500unbal.py and change the file path in line 41 and 45 to your local directory `/your/local/path/CIMHub/ieee9500/base`

7. Run `python3 test9500bal.py` or `python3 test9500unbal.py` to convert the CIM XML model

8. Run `./zipall.sh` and `./zipcomparisons.h` to create downloadable archives

------

## Building the CIM XML model from Original DSS Files

To build the CIM XML files from the original DSS source files:

1. Download the [cimext branch of OpenDSScmd](https://github.com/GRIDAPPSD/GOSS-GridAPPS-D/tree/feature/cimext/opendss)
   * Clone the GOSS-GridAPPSD repo with `git clone https://github.com/GRIDAPPSD/GOSS-GridAPPS-D.git -b feature/cimext`
   * If OpenDSScmd is already installed, check its location with `which opendsscmnd`. It 9s 
   * Move the opendsscmd executable with `sudo cp -i /YOUR_HOME_PATH/GOSS-GridAPPS-D/opendss/opendsscmd /usr/local/bin`

2. Uncomment lines 41 and 46 in test9500bal.py and test9500unbal.py. Now, the script will read from the original_dss directory and build the CIM XML files

3. Re-run `python3 test9500bal.py` or `python3 test9500unbal.py` to re-build the XML files and solve the power flow solution.

---

## Balanced Load Results

```

  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.59 -0.5533    139.08 -0.5522   1024.391 + j    -1.073     AB    12755.59 -0.0298
    B   7363.30 -2.6477    132.96 -2.6260    978.780 + j   -21.186     BC    12755.00 -2.1252
    C   7357.49  1.5394    160.61  1.5031   1180.908 + j    42.889     CA    12744.13  2.0642
    Total S =  3184.079 + j    20.630
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.52 -0.5533    139.10 -0.5524   1024.536 + j    -0.894     AB    12755.60 -0.0298
    B   7363.38 -2.6477    132.98 -2.6262    978.957 + j   -21.019     BC    12755.06 -2.1252
    C   7357.48  1.5394    160.64  1.5029   1181.119 + j    43.103     CA    12744.06  2.0642
    Total S =  3184.612 + j    21.190
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7366.05 -0.5533    139.01 -0.5599   1023.942 + j     6.802     AB    12756.51 -0.0299
    B   7362.79  3.6353    132.86  3.6430    978.156 + j    -7.539     BC    12751.12 -2.1250
    C   7357.16  1.5400    161.07  1.4940   1183.799 + j    54.459     CA    12746.45  2.0645
    Total S =  3185.898 + j    53.722
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7347.04 -0.5603    123.58 -0.5082    906.749 + j   -47.203     AB    12739.95 -0.0383
    B   7349.00 -2.6581    125.15 -2.6068    918.517 + j   -47.173     BC    12719.61 -2.1303
    C   7368.08  1.5376    122.98  1.5656    905.773 + j   -25.301     CA    12756.49  2.0587
    Total S =  2731.039 + j  -119.677
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7346.71 -0.5603    123.61 -0.5082    906.862 + j   -47.209     AB    12739.50 -0.0383
    B   7348.81 -2.6581    125.19 -2.6068    918.757 + j   -47.185     BC    12719.00 -2.1303
    C   7367.57  1.5376    123.01  1.5654    905.965 + j   -25.148     CA    12755.77  2.0587
    Total S =  2731.585 + j  -119.542
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7344.89 -0.5599    123.56 -0.5187    906.746 + j   -37.374     AB    12738.34 -0.0384
    B   7345.96  3.6246    125.57  3.6666    921.596 + j   -38.740     BC    12714.84 -2.1307
    C   7365.35  1.5372    123.41  1.5556    908.774 + j   -16.748     CA    12749.16  2.0586
    Total S =  2737.116 + j   -92.861
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.95 -0.5603    170.68 -0.9308   1171.705 + j   455.180     AB    12814.55 -0.0364
    B   7417.11 -2.6581    179.70 -3.0267   1243.324 + j   480.257     BC    12806.70 -2.1317
    C   7400.74  1.5376    142.98  1.1730    988.629 + j   377.323     CA    12800.34  2.0581
    Total S =  3403.658 + j  1312.761
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.61 -0.5603    170.73 -0.9310   1171.976 + j   455.521     AB    12814.37 -0.0363
    B   7417.25 -2.6581    178.87 -3.0264   1237.764 + j   477.614     BC    12806.29 -2.1317
    C   7400.13  1.5376    143.09  1.1729    989.208 + j   377.742     CA    12799.52  2.0581
    Total S =  3398.949 + j  1310.876
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7361.44 -0.5607    172.10 -0.9401   1176.841 + j   469.172     AB    12807.42 -0.0369
    B   7412.00  3.6245    181.85  3.2447   1251.814 + j   499.657     BC    12796.07 -2.1320
    C   7395.63  1.5376    144.20  1.1501    987.427 + j   402.949     CA    12794.28  2.0579
    Total S =  3416.082 + j  1371.777
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7310.47 -0.5707     84.12 -0.8617    589.089 + j   176.399     AB    12660.22 -0.0472
    B   7308.29 -2.6651     91.20 -2.9377    641.913 + j   179.467     BC    12669.91 -2.1422
    C   7314.30  1.5219     88.82  1.2381    623.659 + j   181.898     CA    12659.04  2.0462
    Total S =  1854.660 + j   537.764
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.60 -0.5707     84.13 -0.8617    589.129 + j   176.411     AB    12658.82 -0.0472
    B   7307.55 -2.6651     91.22 -2.9377    641.981 + j   179.486     BC    12668.49 -2.1422
    C   7313.40  1.5219     88.84  1.2381    623.709 + j   181.913     CA    12657.50  2.0462
    Total S =  1854.819 + j   537.810
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7310.10 -0.5705     84.27 -0.8711    588.386 + j   182.371     AB    12653.95 -0.0468
    B   7304.42  3.6190     91.44  3.3288    639.981 + j   191.115     BC    12665.86 -2.1414
    C   7311.80  1.5225     89.16  1.2301    624.256 + j   187.886     CA    12657.68  2.0467
    Total S =  1852.623 + j   561.373
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7244.35 -0.5742     47.96 -0.8514    334.184 + j    95.069     AB    12558.02 -0.0548
    B   7227.32 -2.6756     64.46 -2.9473    448.778 + j   125.048     BC    12548.95 -2.1459
    C   7292.26  1.5202     25.33  1.2277    176.874 + j    53.267     CA    12589.10  2.0419
    Total S =   959.835 + j   273.383
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7242.62 -0.5742     47.97 -0.8514    334.189 + j    95.070     AB    12554.95 -0.0548
    B   7225.52 -2.6756     64.49 -2.9472    448.871 + j   124.989     BC    12545.73 -2.1459
    C   7290.34  1.5202     25.34  1.2277    176.881 + j    53.269     CA    12585.94  2.0419
    Total S =   959.941 + j   273.328
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7239.05 -0.5745     48.04 -0.8690    332.814 + j   100.950     AB    12546.82 -0.0550
    B   7220.73  3.6076     64.85  3.3287    450.199 + j   128.898     BC    12537.94 -2.1458
    C   7287.02  1.5204     25.52  1.2130    177.239 + j    56.250     CA    12581.64  2.0418
    Total S =   960.252 + j   286.098
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7117.24 -0.5672     33.49 -0.8269    230.339 + j    61.202     AB    12441.85 -0.0442
    B   7213.30 -2.6704     31.28 -2.9276    218.208 + j    57.409     BC    12473.00 -2.1384
    C   7247.91  1.5324     25.32  1.2741    177.403 + j    46.872     CA    12459.52  2.0482
    Total S =   625.950 + j   165.483
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7115.88 -0.5672     33.50 -0.8268    230.411 + j    61.178     AB    12435.01 -0.0432
    B   7213.93 -2.6686     31.28 -2.9269    218.164 + j    57.641     BC    12476.94 -2.1377
    C   7244.45  1.5324     25.33  1.2743    177.445 + j    46.850     CA    12455.33  2.0482
    Total S =   626.020 + j   165.670
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7109.08 -0.5668     33.69 -0.8325    231.102 + j    62.902     AB    12425.07 -0.0436
    B   7203.77  3.6137     31.51  3.3486    219.034 + j    59.455     BC    12454.44 -2.1377
    C   7235.42  1.5331     25.49  1.2671    177.974 + j    48.487     CA    12442.59  2.0489
    Total S =   628.110 + j   170.844
ieee9500bal      Nbus=[  9549,  9549, 12528] Nlink=[ 11254, 11254, 12156] MAEv=[ 0.0002, 0.0069] MAEi=[   0.0269,   0.1315]



```

----
## Unbalanced Load Results

```
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.16 -0.5533    139.57 -0.5545   1027.955 + j     1.256     AB    12754.62 -0.0298
    B   7362.61 -2.6477    133.74 -2.6300    984.530 + j   -17.357     BC    12753.87 -2.1252
    C   7356.88  1.5394    161.37  1.5003   1186.265 + j    46.401     CA    12743.23  2.0642
    Total S =  3198.750 + j    30.300
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.07 -0.5533    139.59 -0.5545   1028.104 + j     1.256     AB    12754.69 -0.0298
    B   7362.78 -2.6477    133.76 -2.6300    984.707 + j   -17.360     BC    12754.03 -2.1252
    C   7356.90  1.5394    161.40  1.5003   1186.489 + j    46.410     CA    12743.17  2.0642
    Total S =  3199.300 + j    30.306
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.91 -0.5533    139.29 -0.5612   1025.973 + j     8.088     AB    12756.34 -0.0299
    B   7362.80  3.6353    132.83  3.6428    977.978 + j    -7.428     BC    12751.01 -2.1250
    C   7356.82  1.5399    161.58  1.4921   1187.324 + j    56.768     CA    12745.90  2.0645
    Total S =  3191.275 + j    57.428
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7346.40 -0.5603    124.08 -0.5109    910.415 + j   -45.005     AB    12738.75 -0.0383
    B   7348.26 -2.6581    125.55 -2.6091    921.450 + j   -45.228     BC    12718.54 -2.1303
    C   7367.59  1.5376    123.31  1.5638    908.223 + j   -23.783     CA    12755.51  2.0587
    Total S =  2740.088 + j  -114.015
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7346.06 -0.5603    124.10 -0.5110    910.535 + j   -44.851     AB    12738.47 -0.0383
    B   7348.27 -2.6581    125.58 -2.6091    921.694 + j   -45.240     BC    12718.08 -2.1303
    C   7367.05  1.5376    123.35  1.5636    908.426 + j   -23.629     CA    12754.75  2.0587
    Total S =  2740.654 + j  -113.720
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7344.94 -0.5599    123.50 -0.5188    906.359 + j   -37.259     AB    12738.31 -0.0384
    B   7345.74  3.6246    125.71  3.6657    922.668 + j   -37.965     BC    12714.54 -2.1308
    C   7365.11  1.5371    123.60  1.5544    910.228 + j   -15.737     CA    12748.77  2.0586
    Total S =  2739.254 + j   -90.961
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.65 -0.5603    171.17 -0.9287   1175.988 + j   454.012     AB    12813.77 -0.0364
    B   7416.52 -2.6581    180.46 -3.0252   1249.211 + j   480.278     BC    12805.95 -2.1317
    C   7400.47  1.5376    143.53  1.1757    993.363 + j   376.153     CA    12799.85  2.0581
    Total S =  3418.563 + j  1310.443
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.32 -0.5603    171.20 -0.9289   1176.103 + j   454.292     AB    12813.99 -0.0363
    B   7417.10 -2.6581    179.08 -3.0247   1240.053 + j   476.012     BC    12805.87 -2.1317
    C   7399.79  1.5376    143.65  1.1753    993.992 + j   376.788     CA    12798.97  2.0581
    Total S =  3410.148 + j  1307.092
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7361.76 -0.5608    172.18 -0.9374   1178.691 + j   466.225     AB    12807.81 -0.0370
    B   7411.99  3.6244    182.20  3.2467   1255.274 + j   497.987     BC    12796.18 -2.1321
    C   7395.64  1.5375    144.53  1.1531    990.916 + j   400.824     CA    12794.35  2.0578
    Total S =  3424.881 + j  1365.036
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.56 -0.5707     84.52 -0.8629    591.592 + j   177.937     AB    12657.96 -0.0472
    B   7306.59 -2.6651     91.88 -2.9398    646.173 + j   182.118     BC    12667.63 -2.1421
    C   7313.37  1.5219     89.23  1.2369    626.251 + j   183.485     CA    12657.44  2.0462
    Total S =  1864.017 + j   543.539
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7308.66 -0.5707     84.53 -0.8629    591.636 + j   177.950     AB    12656.61 -0.0472
    B   7305.94 -2.6651     91.90 -2.9398    646.239 + j   182.136     BC    12666.31 -2.1421
    C   7312.50  1.5219     89.25  1.2369    626.300 + j   183.499     CA    12655.91  2.0462
    Total S =  1864.175 + j   543.585
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.64 -0.5706     84.56 -0.8718    590.248 + j   183.382     AB    12653.34 -0.0468
    B   7304.55  3.6190     91.59  3.3282    640.956 + j   191.791     BC    12665.57 -2.1415
    C   7311.03  1.5224     89.22  1.2298    624.545 + j   188.131     CA    12656.68  2.0466
    Total S =  1855.749 + j   563.304
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7242.56 -0.5742     48.34 -0.8533    336.539 + j    96.437     AB    12555.61 -0.0547
    B   7226.34 -2.6756     64.63 -2.9482    449.791 + j   125.753     BC    12547.36 -2.1459
    C   7291.40  1.5202     25.42  1.2268    177.404 + j    53.595     CA    12586.80  2.0418
    Total S =   963.734 + j   275.786
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7240.82 -0.5742     48.35 -0.8533    336.545 + j    96.439     AB    12552.72 -0.0547
    B   7224.75 -2.6756     64.65 -2.9480    449.881 + j   125.694     BC    12544.29 -2.1459
    C   7289.44  1.5202     25.42  1.2268    177.412 + j    53.598     CA    12583.60  2.0418
    Total S =   963.838 + j   275.730
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7239.64 -0.5745     47.83 -0.8690    331.370 + j   100.544     AB    12546.88 -0.0551
    B   7219.74  3.6075     65.03  3.3281    451.297 + j   129.488     BC    12537.14 -2.1459
    C   7286.65  1.5202     25.57  1.2124    177.529 + j    56.438     CA    12581.06  2.0418
    Total S =   960.197 + j   286.470
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7117.29 -0.5672     33.55 -0.8278    230.744 + j    61.526     AB    12441.27 -0.0442
    B   7212.58 -2.6704     31.37 -2.9288    218.735 + j    57.833     BC    12472.73 -2.1383
    C   7248.31  1.5324     25.43  1.2725    178.109 + j    47.358     CA    12459.91  2.0481
    Total S =   627.588 + j   166.717
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7116.23 -0.5672     33.55 -0.8276    230.705 + j    61.472     AB    12436.02 -0.0432
    B   7214.74 -2.6686     31.36 -2.9278    218.709 + j    57.990     BC    12477.23 -2.1377
    C   7243.98  1.5324     25.45  1.2729    178.160 + j    47.305     CA    12455.22  2.0483
    Total S =   627.573 + j   166.766
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7110.39 -0.5670     33.68 -0.8329    231.095 + j    62.941     AB    12426.73 -0.0439
    B   7203.87  3.6134     31.53  3.3480    219.188 + j    59.576     BC    12455.41 -2.1380
    C   7236.37  1.5328     25.60  1.2658    178.717 + j    48.887     CA    12444.07  2.0487
    Total S =   629.001 + j   171.403
ieee9500unbal    Nbus=[  9549,  9549, 12528] Nlink=[ 11254, 11254, 12156] MAEv=[ 0.0002, 0.0072] MAEi=[   0.0390,   0.1292]


```
