## CIMHub: IEEE 9500-Node Test Case Files

Copyright (c) 2017-2022, Battelle Memorial Institute

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
    A   7367.39 -0.5533    139.04 -0.5515   1024.382 + j    -1.788     AB    12758.50 -0.0298
    B   7364.86 -2.6477    132.93 -2.6253    978.759 + j   -21.869     BC    12751.43 -2.1243
    C   7359.22  1.5411    160.57  1.5038   1180.846 + j    44.125     CA    12753.62  2.0650
    Total S =  3183.987 + j    20.468
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7367.28 -0.5533    139.06 -0.5515   1024.522 + j    -1.788     AB    12758.60 -0.0298
    B   7365.08 -2.6477    132.95 -2.6253    978.928 + j   -21.873     BC    12751.64 -2.1243
    C   7359.25  1.5411    160.60  1.5036   1181.056 + j    44.339     CA    12753.55  2.0650
    Total S =  3184.506 + j    20.678
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7369.50 -0.5530    137.94 -0.5531   1016.554 + j     0.125     AB    12762.86 -0.0296
    B   7367.02  3.6356    131.40  3.6555    967.835 + j   -19.304     BC    12758.79 -2.1247
    C   7361.68  1.5403    159.43  1.5042   1172.880 + j    42.377     CA    12753.55  2.0647
    Total S =  3157.269 + j    23.198
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7351.93 -0.5585    123.50 -0.5058    906.717 + j   -47.836     AB    12747.60 -0.0366
    B   7352.94 -2.6564    125.08 -2.6044    918.477 + j   -47.814     BC    12726.80 -2.1285
    C   7372.46  1.5394    122.92  1.5678    905.827 + j   -25.777     CA    12764.53  2.0604
    Total S =  2731.020 + j  -121.427
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7351.61 -0.5585    123.52 -0.5058    906.832 + j   -47.842     AB    12747.47 -0.0366
    B   7353.10 -2.6564    125.11 -2.6044    918.717 + j   -47.826     BC    12726.45 -2.1286
    C   7371.90  1.5394    122.95  1.5678    906.023 + j   -25.782     CA    12763.77  2.0604
    Total S =  2731.572 + j  -121.451
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7349.86 -0.5596    122.63 -0.5116    900.290 + j   -43.268     AB    12747.41 -0.0380
    B   7351.94  3.6250    124.36  3.6775    913.027 + j   -48.008     BC    12725.33 -2.1304
    C   7371.31  1.5375    122.25  1.5656    900.780 + j   -25.342     CA    12758.86  2.0589
    Total S =  2714.096 + j  -116.618
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7371.60 -0.5603    168.91 -0.9070   1170.975 + j   423.194     AB    12784.27 -0.0382
    B   7375.56 -2.6581    179.64 -3.0095   1244.024 + j   455.987     BC    12776.01 -2.1298
    C   7406.78  1.5376    141.31  1.2008    987.824 + j   345.931     CA    12811.34  2.0581
    Total S =  3402.823 + j  1225.112
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7371.28 -0.5603    168.95 -0.9072   1171.169 + j   423.495     AB    12784.75 -0.0382
    B   7376.44 -2.6581    177.86 -3.0088   1232.139 + j   450.655     BC    12776.15 -2.1299
    C   7406.06  1.5376    141.44  1.2003    988.483 + j   346.743     CA    12810.44  2.0581
    Total S =  3391.791 + j  1220.893
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7370.20 -0.5604    167.74 -0.9104   1161.378 + j   423.855     AB    12782.59 -0.0384
    B   7375.17  3.6249    178.14  3.2716   1232.627 + j   454.595     BC    12773.28 -2.1298
    C   7405.88  1.5379    138.96  1.1909    967.788 + j   349.999     CA    12811.08  2.0582
    Total S =  3361.792 + j  1228.449
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7312.31 -0.5707     84.09 -0.8611    589.175 + j   176.089     AB    12656.79 -0.0463
    B   7309.87 -2.6634     91.18 -2.9372    641.684 + j   180.248     BC    12672.80 -2.1404
    C   7316.06  1.5237     88.80  1.2388    623.463 + j   182.550     CA    12668.54  2.0471
    Total S =  1854.322 + j   538.887
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7311.40 -0.5707     84.11 -0.8611    589.216 + j   176.101     AB    12655.50 -0.0463
    B   7309.28 -2.6634     91.20 -2.9370    641.783 + j   180.155     BC    12671.55 -2.1404
    C   7315.20  1.5237     88.81  1.2388    623.513 + j   182.564     CA    12667.01  2.0471
    Total S =  1854.512 + j   538.821
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7314.32 -0.5702     83.48 -0.8669    583.901 + j   178.474     AB    12663.23 -0.0463
    B   7311.38  3.6194     90.08  3.3380    632.701 + j   182.870     BC    12676.82 -2.1410
    C   7317.99  1.5230     88.11  1.2369    618.562 + j   181.939     CA    12667.51  2.0470
    Total S =  1835.164 + j   543.283
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7249.36 -0.5725     47.93 -0.8493    334.210 + j    94.950     AB    12565.85 -0.0531
    B   7231.34 -2.6738     64.42 -2.9454    448.790 + j   124.967     BC    12556.26 -2.1441
    C   7296.70  1.5219     25.32  1.2298    176.889 + j    53.204     CA    12597.28  2.0436
    Total S =   959.889 + j   273.121
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7247.64 -0.5725     47.94 -0.8493    334.214 + j    94.951     AB    12563.11 -0.0531
    B   7229.90 -2.6738     64.45 -2.9452    448.881 + j   124.908     BC    12553.30 -2.1442
    C   7294.71  1.5219     25.32  1.2298    176.896 + j    53.206     CA    12594.07  2.0437
    Total S =   959.992 + j   273.065
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7244.98 -0.5742     47.65 -0.8660    330.657 + j    99.315     AB    12559.25 -0.0545
    B   7229.63  3.6080     64.06  3.3356    446.067 + j   124.607     BC    12551.99 -2.1454
    C   7294.81  1.5209     25.23  1.2188    175.708 + j    54.760     CA    12594.33  2.0422
    Total S =   952.432 + j   278.683
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7135.15 -0.5672     33.40 -0.8268    230.324 + j    61.155     AB    12425.51 -0.0463
    B   7176.66 -2.6704     31.44 -2.9280    218.216 + j    57.492     BC    12456.44 -2.1362
    C   7265.27  1.5324     25.25  1.2737    177.366 + j    46.928     CA    12490.10  2.0482
    Total S =   625.906 + j   165.576
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7134.27 -0.5672     33.41 -0.8268    230.386 + j    61.172     AB    12421.43 -0.0453
    B   7179.98 -2.6686     31.43 -2.9269    218.190 + j    57.648     BC    12461.37 -2.1356
    C   7260.29  1.5324     25.28  1.2741    177.416 + j    46.875     CA    12485.01  2.0484
    Total S =   625.993 + j   165.696
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7132.19 -0.5671     33.26 -0.8275    229.189 + j    61.060     AB    12424.33 -0.0460
    B   7178.39  3.6130     31.27  3.3546    217.048 + j    57.365     BC    12455.43 -2.1360
    C   7263.29  1.5328     25.11  1.2738    176.271 + j    46.697     CA    12486.72  2.0484
    Total S =   622.509 + j   165.122
ieee9500bal      Nbus=[  9549,  9549, 12528] Nlink=[ 11254, 11254, 12159] MAEv=[ 0.0002, 0.0018] MAEi=[   0.0485,   0.6354]
```

## Unbalanced Load Results

```
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.50 -0.5533    139.56 -0.5538   1027.951 + j     0.538     AB    12755.24 -0.0298
    B   7362.98 -2.6477    133.73 -2.6293    984.515 + j   -18.044     BC    12748.05 -2.1243
    C   7357.20  1.5411    161.36  1.5010   1186.209 + j    47.643     CA    12750.23  2.0650
    Total S =  3198.675 + j    30.137
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.41 -0.5533    139.59 -0.5540   1028.101 + j     0.718     AB    12755.31 -0.0298
    B   7363.15 -2.6477    133.75 -2.6293    984.693 + j   -18.047     BC    12748.21 -2.1243
    C   7357.22  1.5411    161.39  1.5010   1186.440 + j    47.652     CA    12750.17  2.0650
    Total S =  3199.233 + j    30.323
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7368.11 -0.5530    138.10 -0.5538   1017.515 + j     0.829     AB    12760.78 -0.0296
    B   7366.09  3.6356    131.22  3.6562    966.378 + j   -19.902     BC    12756.94 -2.1247
    C   7360.22  1.5403    159.69  1.5032   1174.567 + j    43.595     CA    12750.94  2.0647
    Total S =  3158.460 + j    24.523
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7348.90 -0.5585    124.03 -0.5088    910.393 + j   -45.322     AB    12742.92 -0.0366
    B   7350.57 -2.6564    125.51 -2.6068    921.422 + j   -45.710     BC    12722.44 -2.1285
    C   7369.79  1.5394    123.28  1.5659    908.206 + j   -24.099     CA    12759.59  2.0604
    Total S =  2740.022 + j  -115.131
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7348.58 -0.5585    124.06 -0.5088    910.508 + j   -45.328     AB    12742.66 -0.0366
    B   7350.59 -2.6564    125.54 -2.6068    921.660 + j   -45.722     BC    12722.00 -2.1286
    C   7369.26  1.5394    123.31  1.5659    908.406 + j   -24.105     CA    12758.85  2.0604
    Total S =  2740.573 + j  -115.154
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7347.83 -0.5596    122.49 -0.5112    899.012 + j   -43.499     AB    12744.48 -0.0380
    B   7350.47  3.6250    124.38  3.6773    913.008 + j   -47.807     BC    12722.32 -2.1304
    C   7369.18  1.5375    122.33  1.5651    901.144 + j   -24.885     CA    12755.08  2.0589
    Total S =  2713.164 + j  -116.191
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.72 -0.5603    171.28 -0.9297   1176.493 + j   455.623     AB    12815.45 -0.0364
    B   7417.38 -2.6581    180.58 -3.0262   1249.683 + j   481.962     BC    12807.38 -2.1317
    C   7401.26  1.5376    143.66  1.1741    993.735 + j   378.080     CA    12801.46  2.0581
    Total S =  3419.911 + j  1315.665
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.41 -0.5603    171.32 -0.9299   1176.618 + j   455.908     AB    12815.68 -0.0364
    B   7417.96 -2.6581    179.21 -3.0257   1240.570 + j   477.701     BC    12807.31 -2.1317
    C   7400.60  1.5376    143.78  1.1737    994.365 + j   378.717     CA    12800.62  2.0581
    Total S =  3411.553 + j  1312.326
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.31 -0.5604    169.43 -0.9324   1162.547 + j   453.639     AB    12815.39 -0.0365
    B   7417.75  3.6250    178.31  3.2558   1233.563 + j   477.282     BC    12805.91 -2.1316
    C   7401.00  1.5380    140.87  1.1649    970.829 + j   380.019     CA    12802.44  2.0582
    Total S =  3366.939 + j  1310.939
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.91 -0.5707     84.51 -0.8622    591.715 + j   177.523     AB    12652.20 -0.0464
    B   7306.96 -2.6634     91.88 -2.9393    645.947 + j   182.906     BC    12668.23 -2.1404
    C   7313.69  1.5237     89.23  1.2374    626.025 + j   184.249     CA    12664.41  2.0471
    Total S =  1863.687 + j   544.678
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.01 -0.5707     84.53 -0.8622    591.759 + j   177.536     AB    12650.86 -0.0464
    B   7306.31 -2.6634     91.89 -2.9391    646.045 + j   182.812     BC    12666.91 -2.1404
    C   7312.82  1.5237     89.24  1.2374    626.074 + j   184.264     CA    12662.88  2.0471
    Total S =  1863.877 + j   544.612
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7312.72 -0.5703     83.66 -0.8672    585.026 + j   179.026     AB    12660.96 -0.0463
    B   7310.75  3.6194     90.10  3.3379    632.801 + j   183.007     BC    12675.04 -2.1410
    C   7316.25  1.5229     88.07  1.2369    618.161 + j   181.773     CA    12664.71  2.0470
    Total S =  1835.987 + j   543.807
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7245.13 -0.5725     48.32 -0.8514    336.550 + j    96.377     AB    12559.89 -0.0530
    B   7228.70 -2.6738     64.61 -2.9463    449.807 + j   125.673     BC    12551.33 -2.1442
    C   7293.63  1.5219     25.41  1.2289    177.421 + j    53.533     CA    12590.96  2.0436
    Total S =   963.778 + j   275.583
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7243.40 -0.5725     48.33 -0.8514    336.555 + j    96.378     AB    12557.02 -0.0530
    B   7227.12 -2.6738     64.63 -2.9459    449.918 + j   125.535     BC    12548.28 -2.1442
    C   7291.69  1.5219     25.42  1.2289    177.429 + j    53.535     CA    12587.78  2.0436
    Total S =   963.902 + j   275.448
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7243.61 -0.5741     47.40 -0.8657    328.836 + j    98.713     AB    12556.67 -0.0545
    B   7227.62  3.6080     64.18  3.3353    446.704 + j   124.906     BC    12548.76 -2.1454
    C   7292.69  1.5208     25.25  1.2185    175.781 + j    54.819     CA    12590.62  2.0422
    Total S =   951.322 + j   278.438
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7117.47 -0.5655     33.55 -0.8268    230.701 + j    61.687     AB    12441.40 -0.0425
    B   7212.56 -2.6686     31.37 -2.9278    218.695 + j    57.986     BC    12479.02 -2.1375
    C   7248.23  1.5324     25.43  1.2736    178.159 + j    47.171     CA    12453.75  2.0490
    Total S =   627.554 + j   166.844
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7116.42 -0.5655     33.55 -0.8266    230.663 + j    61.633     AB    12442.37 -0.0423
    B   7214.71 -2.6686     31.36 -2.9269    218.759 + j    57.799     BC    12477.16 -2.1377
    C   7243.93  1.5324     25.45  1.2737    178.201 + j    47.149     CA    12449.10  2.0491
    Total S =   627.623 + j   166.581
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7116.61 -0.5663     33.30 -0.8267    229.021 + j    61.009     AB    12442.39 -0.0430
    B   7215.89  3.6141     31.10  3.3557    216.951 + j    57.336     BC    12474.30 -2.1372
    C   7247.42  1.5338     25.23  1.2743    176.709 + j    46.903     CA    12460.22  2.0493
    Total S =   622.681 + j   165.248
ieee9500unbal    Nbus=[  9549,  9549, 12528] Nlink=[ 11254, 11254, 12159] MAEv=[ 0.0002, 0.0020] MAEi=[   0.0388,   0.7034]
```
