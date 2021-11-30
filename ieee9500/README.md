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

---

## Balanced Load Results

```

 OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7367.72 -0.5533    139.04 -0.5491   1024.406 + j    -4.291     AB    12759.05 -0.0298
    B   7365.16 -2.6477    132.93 -2.6229    978.780 + j   -24.263     BC    12758.41 -2.1252
    C   7359.57  1.5394    160.55  1.5059   1180.908 + j    39.587     CA    12747.78  2.0642
    Total S =  3184.094 + j    11.034
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7367.61 -0.5533    139.06 -0.5493   1024.546 + j    -4.113     AB    12759.14 -0.0298
    B   7365.38 -2.6477    132.95 -2.6229    978.956 + j   -24.267     BC    12758.64 -2.1252
    C   7359.61  1.5394    160.58  1.5057   1181.121 + j    39.801     CA    12747.72  2.0642
    Total S =  3184.623 + j    11.421
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7368.44 -0.5533    138.96 -0.5567   1023.945 + j     3.516     AB    12760.02 -0.0299
    B   7364.57  3.6353    132.83  3.6463    978.150 + j   -10.781     BC    12754.44 -2.1250
    C   7359.07  1.5400    161.01  1.4968   1183.792 + j    51.191     CA    12750.14  2.0645
    Total S =  3185.887 + j    43.926
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7350.68 -0.5603    123.56 -0.5021    906.716 + j   -52.757     AB    12745.60 -0.0384
    B   7351.88 -2.6581    125.14 -2.6009    918.478 + j   -52.637     BC    12725.05 -2.1303
    C   7371.50  1.5376    122.95  1.5715    905.836 + j   -30.683     CA    12762.61  2.0587
    Total S =  2731.030 + j  -136.077
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7350.35 -0.5603    123.58 -0.5023    906.839 + j   -52.606     AB    12745.44 -0.0383
    B   7352.02 -2.6581    125.17 -2.6009    918.715 + j   -52.651     BC    12724.68 -2.1303
    C   7370.93  1.5376    122.99  1.5713    906.036 + j   -30.531     CA    12761.83  2.0587
    Total S =  2731.591 + j  -135.788
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7350.61 -0.5600    123.49 -0.5125    906.692 + j   -43.082     AB    12744.11 -0.0385
    B   7348.14  3.6248    125.56  3.6727    921.557 + j   -44.137     BC    12720.20 -2.1308
    C   7367.39  1.5369    123.40  1.5610    908.885 + j   -21.945     CA    12755.26  2.0586
    Total S =  2737.134 + j  -109.164
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7370.99 -0.5603    168.85 -0.9067   1170.616 + j   422.602     AB    12783.40 -0.0382
    B   7375.17 -2.6581    179.58 -3.0093   1243.595 + j   455.583     BC    12775.38 -2.1298
    C   7406.44  1.5376    141.25  1.2011    987.452 + j   345.414     CA    12810.52  2.0581
    Total S =  3401.663 + j  1223.599
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7370.66 -0.5603    168.89 -0.9070   1170.742 + j   423.110     AB    12783.86 -0.0382
    B   7376.03 -2.6581    177.79 -3.0086   1231.685 + j   450.245     BC    12775.49 -2.1299
    C   7405.70  1.5376    141.38  1.2008    988.169 + j   346.052     CA    12809.59  2.0581
    Total S =  3390.596 + j  1219.407
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7368.61 -0.5608    170.17 -0.9161   1175.650 + j   436.127     AB    12776.59 -0.0389
    B   7369.99  3.6245    181.77  3.2617   1252.377 + j   475.532     BC    12764.96 -2.1302
    C   7400.56  1.5374    142.37  1.1777    986.185 + j   370.872     CA    12804.47  2.0578
    Total S =  3414.212 + j  1282.531
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7312.73 -0.5707     84.09 -0.8617    589.082 + j   176.397     AB    12663.89 -0.0472
    B   7310.27 -2.6651     91.18 -2.9377    641.901 + j   179.464     BC    12673.54 -2.1421
    C   7316.51  1.5219     88.79  1.2381    623.653 + j   181.896     CA    12662.91  2.0462
    Total S =  1854.636 + j   537.757
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7311.82 -0.5707     84.11 -0.8617    589.123 + j   176.409     AB    12662.59 -0.0472
    B   7309.68 -2.6651     91.19 -2.9377    641.970 + j   179.483     BC    12672.28 -2.1422
    C   7315.65  1.5219     88.81  1.2381    623.702 + j   181.911     CA    12661.37  2.0462
    Total S =  1854.795 + j   537.803
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7312.64 -0.5705     84.24 -0.8711    588.377 + j   182.356     AB    12657.70 -0.0468
    B   7306.31  3.6190     91.41  3.3288    639.972 + j   191.098     BC    12669.39 -2.1414
    C   7313.84  1.5224     89.13  1.2301    624.248 + j   187.874     CA    12661.61  2.0467
    Total S =  1852.596 + j   561.329
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7249.02 -0.5742     47.93 -0.8514    334.177 + j    95.067     AB    12565.41 -0.0548
    B   7231.17 -2.6756     64.42 -2.9475    448.746 + j   125.123     BC    12556.05 -2.1459
    C   7296.63  1.5202     25.32  1.2277    176.871 + j    53.266     CA    12596.92  2.0419
    Total S =   959.794 + j   273.456
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7247.29 -0.5742     47.94 -0.8514    334.182 + j    95.068     AB    12562.65 -0.0548
    B   7229.72 -2.6756     64.45 -2.9473    448.838 + j   125.065     BC    12553.07 -2.1459
    C   7294.63  1.5202     25.32  1.2277    176.878 + j    53.268     CA    12593.69  2.0419
    Total S =   959.898 + j   273.401
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7245.87 -0.5747     48.00 -0.8691    332.803 + j   100.931     AB    12554.41 -0.0552
    B   7223.88  3.6077     64.82  3.3289    450.188 + j   128.884     BC    12544.85 -2.1459
    C   7289.94  1.5200     25.51  1.2127    177.237 + j    56.245     CA    12589.46  2.0417
    Total S =   960.228 + j   286.060
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7135.01 -0.5672     33.40 -0.8276    230.270 + j    61.356     AB    12425.47 -0.0463
    B   7176.75 -2.6704     31.44 -2.9288    218.165 + j    57.682     BC    12463.01 -2.1371
    C   7265.40  1.5307     25.25  1.2729    177.406 + j    46.773     CA    12483.84  2.0473
    Total S =   625.841 + j   165.812
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7134.11 -0.5672     33.41 -0.8278    230.324 + j    61.414     AB    12427.57 -0.0462
    B   7180.06 -2.6704     31.43 -2.9278    218.240 + j    57.458     BC    12461.54 -2.1374
    C   7260.41  1.5307     25.27  1.2732    177.457 + j    46.720     CA    12478.72  2.0475
    Total S =   626.020 + j   165.592
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7128.23 -0.5677     33.59 -0.8333    231.064 + j    62.857     AB    12410.37 -0.0468
    B   7166.82  3.6126     31.68  3.3473    219.085 + j    59.524     BC    12437.95 -2.1367
    C   7252.23  1.5318     25.43  1.2659    177.945 + j    48.460     CA    12472.15  2.0479
    Total S =   628.094 + j   170.840
ieee9500bal      Nbus=[  9549,  9549, 12528] Nlink=[ 11256, 11256, 12156] MAEv=[ 0.0002, 0.0069] MAEi=[   0.0486,   0.1415]


```

----
## Unbalanced Load Results

```

  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.83 -0.5533    139.56 -0.5513   1027.973 + j    -1.974     AB    12755.78 -0.0298
    B   7363.28 -2.6477    133.74 -2.6267    984.534 + j   -20.623     BC    12755.03 -2.1252
    C   7357.55  1.5394    161.34  1.5031   1186.278 + j    43.084     CA    12744.39  2.0642
    Total S =  3198.785 + j    20.488
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.73 -0.5533    139.58 -0.5515   1028.122 + j    -1.794     AB    12755.84 -0.0298
    B   7363.45 -2.6477    133.76 -2.6267    984.712 + j   -20.627     BC    12755.20 -2.1252
    C   7357.57  1.5394    161.37  1.5029   1186.494 + j    43.299     CA    12744.32  2.0642
    Total S =  3199.327 + j    20.878
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7366.83 -0.5533    139.27 -0.5581   1025.986 + j     4.949     AB    12757.55 -0.0299
    B   7363.40  3.6353    132.82  3.6461    977.981 + j   -10.552     BC    12752.15 -2.1251
    C   7357.31  1.5399    161.55  1.4947   1187.329 + j    53.646     CA    12747.04  2.0645
    Total S =  3191.297 + j    48.043
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7347.65 -0.5603    124.09 -0.5053    910.400 + j   -50.102     AB    12740.91 -0.0383
    B   7349.50 -2.6581    125.56 -2.6033    921.418 + j   -50.547     BC    12720.69 -2.1303
    C   7368.83  1.5376    123.31  1.5696    908.216 + j   -29.018     CA    12757.67  2.0587
    Total S =  2740.034 + j  -129.668
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7347.32 -0.5603    124.11 -0.5053    910.520 + j   -50.109     AB    12740.63 -0.0383
    B   7349.51 -2.6581    125.59 -2.6033    921.661 + j   -50.561     BC    12720.23 -2.1303
    C   7368.29  1.5376    123.35  1.5694    908.420 + j   -28.866     CA    12756.92  2.0587
    Total S =  2740.601 + j  -129.535
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7348.26 -0.5600    123.48 -0.5128    906.323 + j   -42.736     AB    12740.63 -0.0385
    B   7346.32  3.6248    125.73  3.6716    922.640 + j   -43.203     BC    12716.58 -2.1308
    C   7364.97  1.5369    123.62  1.5598    910.226 + j   -20.900     CA    12750.93  2.0586
    Total S =  2739.189 + j  -106.838
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.11 -0.5603    171.22 -0.9296   1176.056 + j   455.218     AB    12814.56 -0.0364
    B   7416.97 -2.6581    180.51 -3.0261   1249.241 + j   481.541     BC    12806.72 -2.1317
    C   7400.91  1.5376    143.59  1.1744    993.349 + j   377.536     CA    12800.63  2.0581
    Total S =  3418.647 + j  1314.295
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.78 -0.5603    171.26 -0.9297   1176.185 + j   455.504     AB    12814.77 -0.0363
    B   7417.54 -2.6581    179.14 -3.0255   1240.119 + j   477.279     BC    12806.64 -2.1317
    C   7400.24  1.5376    143.71  1.1743    994.044 + j   377.999     CA    12799.76  2.0581
    Total S =  3410.349 + j  1310.782
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7363.31 -0.5608    172.20 -0.9383   1178.706 + j   467.334     AB    12808.72 -0.0370
    B   7412.16  3.6245    182.26  3.2460   1255.315 + j   499.294     BC    12796.87 -2.1321
    C   7395.29  1.5373    144.62  1.1518    990.964 + j   402.214     CA    12795.13  2.0578
    Total S =  3424.984 + j  1368.842
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7310.33 -0.5707     84.51 -0.8629    591.590 + j   177.936     AB    12659.29 -0.0472
    B   7307.36 -2.6651     91.87 -2.9398    646.168 + j   182.116     BC    12668.97 -2.1421
    C   7314.14  1.5219     89.22  1.2369    626.248 + j   183.484     CA    12658.78  2.0462
    Total S =  1864.005 + j   543.536
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.43 -0.5707     84.52 -0.8629    591.634 + j   177.949     AB    12657.95 -0.0472
    B   7306.71 -2.6651     91.89 -2.9398    646.234 + j   182.135     BC    12667.65 -2.1421
    C   7313.27  1.5219     89.24  1.2369    626.296 + j   183.498     CA    12657.24  2.0462
    Total S =  1864.165 + j   543.582
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7310.67 -0.5706     84.54 -0.8718    590.244 + j   183.375     AB    12654.75 -0.0468
    B   7305.25  3.6190     91.58  3.3283    640.952 + j   191.784     BC    12666.86 -2.1415
    C   7311.62  1.5223     89.21  1.2298    624.543 + j   188.128     CA    12658.00  2.0466
    Total S =  1855.739 + j   563.288
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7244.78 -0.5760     48.32 -0.8535    336.684 + j    95.907     AB    12553.16 -0.0556
    B   7228.53 -2.6756     64.61 -2.9482    449.786 + j   125.752     BC    12551.12 -2.1459
    C   7293.56  1.5202     25.41  1.2268    177.402 + j    53.595     CA    12596.93  2.0410
    Total S =   963.872 + j   275.253
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7243.04 -0.5760     48.33 -0.8535    336.691 + j    95.909     AB    12550.27 -0.0556
    B   7226.94 -2.6756     64.63 -2.9480    449.876 + j   125.692     BC    12548.05 -2.1459
    C   7291.60  1.5202     25.42  1.2268    177.410 + j    53.597     CA    12593.73  2.0410
    Total S =   963.977 + j   275.198
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7243.98 -0.5746     47.80 -0.8691    331.365 + j   100.533     AB    12550.93 -0.0552
    B   7221.26  3.6076     65.02  3.3282    451.291 + j   129.481     BC    12540.70 -2.1460
    C   7287.38  1.5199     25.56  1.2121    177.529 + j    56.437     CA    12584.89  2.0417
    Total S =   960.185 + j   286.450
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7117.32 -0.5672     33.55 -0.8276    230.754 + j    61.485     AB    12441.33 -0.0442
    B   7212.62 -2.6704     31.37 -2.9288    218.734 + j    57.833     BC    12472.80 -2.1383
    C   7248.35  1.5324     25.43  1.2725    178.109 + j    47.358     CA    12459.97  2.0481
    Total S =   627.597 + j   166.676
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7116.25 -0.5672     33.55 -0.8276    230.706 + j    61.472     AB    12436.06 -0.0432
    B   7214.77 -2.6686     31.36 -2.9278    218.708 + j    57.989     BC    12477.31 -2.1377
    C   7244.04  1.5324     25.45  1.2729    178.159 + j    47.305     CA    12455.29  2.0483
    Total S =   627.573 + j   166.766
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7111.62 -0.5670     33.68 -0.8329    231.092 + j    62.938     AB    12426.98 -0.0438
    B   7203.62  3.6136     31.53  3.3482    219.188 + j    59.576     BC    12455.37 -2.1379
    C   7235.54  1.5327     25.61  1.2657    178.719 + j    48.889     CA    12444.13  2.0487

```
