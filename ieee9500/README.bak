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

## Test Procedure (CIMHub Installed)

The purpose of this test is to verify the model after changes to the CIM 
schema or CIMHub code, and package the model files for distribution.  It 
assumes you already have CIMHub installed, including Blazegraph, the 
Python package, and the Java program.  If not, please see directions at 
the bottom of this page.
  
1. Invoke ```python3 test9500.py```. Check the new results against those below.  Also use ```git diff``` to identify any changes to the XML or UUID files.
2. Invoke ```./zipall.sh``` to update the downloadable archives.  

------

## Balanced Load Results

```
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.58 -0.5533    139.08 -0.5522   1024.390 + j    -1.073     AB    12755.58 -0.0298
    B   7363.29 -2.6477    132.96 -2.6262    978.783 + j   -21.015     BC    12754.98 -2.1252
    C   7357.48  1.5394    160.61  1.5031   1180.906 + j    42.889     CA    12744.12  2.0642
    Total S =  3184.079 + j    20.801
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.51 -0.5533    139.10 -0.5524   1024.535 + j    -0.894     AB    12755.58 -0.0298
    B   7363.37 -2.6477    132.98 -2.6262    978.955 + j   -21.019     BC    12755.04 -2.1252
    C   7357.47  1.5394    160.64  1.5029   1181.125 + j    43.103     CA    12744.05  2.0642
    Total S =  3184.615 + j    21.190
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7368.17 -0.5530    137.97 -0.5532   1016.558 + j     0.249     AB    12760.80 -0.0296
    B   7365.96  3.6356    131.42  3.6554    967.839 + j   -19.204     BC    12756.79 -2.1247
    C   7360.40  1.5403    159.46  1.5041   1172.885 + j    42.497     CA    12751.24  2.0647
    Total S =  3157.281 + j    23.542
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7346.99 -0.5603    123.58 -0.5082    906.750 + j   -47.203     AB    12739.86 -0.0383
    B   7348.95 -2.6581    125.15 -2.6068    918.511 + j   -47.173     BC    12719.52 -2.1303
    C   7368.03  1.5376    122.98  1.5656    905.767 + j   -25.300     CA    12756.41  2.0587
    Total S =  2731.028 + j  -119.676
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7346.66 -0.5603    123.61 -0.5082    906.863 + j   -47.209     AB    12739.41 -0.0383
    B   7348.76 -2.6581    125.19 -2.6068    918.751 + j   -47.185     BC    12718.92 -2.1303
    C   7367.53  1.5376    123.02  1.5654    905.968 + j   -25.148     CA    12755.69  2.0587
    Total S =  2731.582 + j  -119.542
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7347.69 -0.5596    122.67 -0.5118    900.296 + j   -43.073     AB    12744.30 -0.0380
    B   7350.49  3.6250    124.38  3.6774    913.031 + j   -47.876     BC    12722.31 -2.1304
    C   7369.32  1.5375    122.28  1.5655    900.738 + j   -25.209     CA    12755.28  2.0589
    Total S =  2714.065 + j  -116.158
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.93 -0.5603    170.67 -0.9308   1171.681 + j   455.171     AB    12814.51 -0.0364
    B   7417.09 -2.6581    179.70 -3.0267   1243.307 + j   480.251     BC    12806.66 -2.1317
    C   7400.72  1.5376    142.98  1.1732    988.679 + j   377.144     CA    12800.31  2.0581
    Total S =  3403.666 + j  1312.566
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.59 -0.5603    170.73 -0.9310   1171.959 + j   455.515     AB    12814.34 -0.0363
    B   7417.23 -2.6581    178.87 -3.0264   1237.747 + j   477.607     BC    12806.26 -2.1317
    C   7400.11  1.5376    143.09  1.1729    989.191 + j   377.735     CA    12799.48  2.0581
    Total S =  3398.898 + j  1310.857
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.11 -0.5604    169.47 -0.9333   1162.368 + j   454.769     AB    12815.15 -0.0364
    B   7417.73  3.6250    178.19  3.2552   1232.441 + j   477.723     BC    12805.83 -2.1315
    C   7401.11  1.5380    140.63  1.1640    968.843 + j   380.262     CA    12802.57  2.0582
    Total S =  3363.652 + j  1312.754
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7310.46 -0.5707     84.12 -0.8617    589.089 + j   176.399     AB    12660.20 -0.0472
    B   7308.28 -2.6651     91.20 -2.9377    641.912 + j   179.467     BC    12669.89 -2.1422
    C   7314.29  1.5219     88.82  1.2381    623.658 + j   181.898     CA    12659.02  2.0462
    Total S =  1854.660 + j   537.764
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.59 -0.5707     84.13 -0.8617    589.129 + j   176.411     AB    12658.81 -0.0472
    B   7307.54 -2.6651     91.22 -2.9377    641.981 + j   179.486     BC    12668.47 -2.1422
    C   7313.39  1.5219     88.84  1.2381    623.709 + j   181.913     CA    12657.49  2.0462
    Total S =  1854.818 + j   537.809
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7312.96 -0.5702     83.49 -0.8669    583.902 + j   178.477     AB    12661.12 -0.0463
    B   7310.29  3.6194     90.09  3.3380    632.703 + j   182.873     BC    12674.79 -2.1410
    C   7316.68  1.5229     88.12  1.2369    618.563 + j   181.941     CA    12665.15  2.0470
    Total S =  1835.168 + j   543.291
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7244.30 -0.5742     47.96 -0.8514    334.184 + j    95.069     AB    12557.93 -0.0548
    B   7227.27 -2.6756     64.46 -2.9473    448.778 + j   125.048     BC    12548.86 -2.1459
    C   7292.21  1.5202     25.33  1.2277    176.874 + j    53.267     CA    12589.01  2.0419
    Total S =   959.836 + j   273.383
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7242.57 -0.5742     47.97 -0.8514    334.189 + j    95.070     AB    12554.87 -0.0548
    B   7225.47 -2.6756     64.49 -2.9472    448.870 + j   124.989     BC    12545.65 -2.1459
    C   7290.29  1.5202     25.34  1.2277    176.881 + j    53.269     CA    12585.85  2.0419
    Total S =   959.940 + j   273.328
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7242.76 -0.5742     47.67 -0.8660    330.657 + j    99.316     AB    12556.07 -0.0545
    B   7228.16  3.6080     64.08  3.3356    446.069 + j   124.609     BC    12548.92 -2.1454
    C   7292.80  1.5209     25.24  1.2188    175.708 + j    54.761     CA    12590.69  2.0422
    Total S =   952.435 + j   278.686
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7117.23 -0.5672     33.49 -0.8269    230.338 + j    61.202     AB    12441.84 -0.0442
    B   7213.30 -2.6704     31.28 -2.9276    218.208 + j    57.409     BC    12473.00 -2.1384
    C   7247.91  1.5324     25.32  1.2741    177.403 + j    46.872     CA    12459.51  2.0482
    Total S =   625.950 + j   165.483
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7115.87 -0.5672     33.50 -0.8268    230.411 + j    61.178     AB    12435.00 -0.0432
    B   7213.93 -2.6686     31.28 -2.9269    218.164 + j    57.641     BC    12476.94 -2.1377
    C   7244.45  1.5324     25.33  1.2743    177.445 + j    46.850     CA    12455.32  2.0482
    Total S =   626.020 + j   165.670
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7115.95 -0.5663     33.33 -0.8267    229.204 + j    61.072     AB    12441.73 -0.0429
    B   7216.05  3.6142     31.11  3.3558    217.033 + j    57.356     BC    12474.13 -2.1371
    C   7247.34  1.5339     25.16  1.2750    176.286 + j    46.702     CA    12460.03  2.0494
    Total S =   622.523 + j   165.129
ieee9500bal      Nbus=[  9549,  9549, 12528] Nlink=[ 11254, 11254, 12159] MAEv=[ 0.0002, 0.0018] MAEi=[   0.0269,   0.1664]
```

## Unbalanced Load Results

```
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.15 -0.5533    139.57 -0.5545   1027.953 + j     1.256     AB    12754.61 -0.0298
    B   7362.60 -2.6477    133.74 -2.6300    984.529 + j   -17.357     BC    12753.85 -2.1252
    C   7356.87  1.5394    161.37  1.5003   1186.264 + j    46.401     CA    12743.22  2.0642
    Total S =  3198.745 + j    30.300
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.06 -0.5533    139.59 -0.5545   1028.103 + j     1.256     AB    12754.67 -0.0298
    B   7362.77 -2.6477    133.76 -2.6300    984.706 + j   -17.360     BC    12754.02 -2.1252
    C   7356.89  1.5394    161.40  1.5003   1186.487 + j    46.410     CA    12743.15  2.0642
    Total S =  3199.296 + j    30.306
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7368.24 -0.5530    138.09 -0.5538   1017.515 + j     0.817     AB    12761.01 -0.0296
    B   7366.22  3.6356    131.22  3.6562    966.378 + j   -19.914     BC    12757.16 -2.1247
    C   7360.35  1.5403    159.69  1.5032   1174.567 + j    43.583     CA    12751.17  2.0647
    Total S =  3158.459 + j    24.486
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7346.34 -0.5603    124.08 -0.5110    910.415 + j   -44.845     AB    12738.66 -0.0383
    B   7348.21 -2.6581    125.55 -2.6091    921.451 + j   -45.228     BC    12718.46 -2.1303
    C   7367.54  1.5376    123.32  1.5636    908.228 + j   -23.624     CA    12755.42  2.0587
    Total S =  2740.095 + j  -113.697
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7346.01 -0.5603    124.10 -0.5110    910.536 + j   -44.851     AB    12738.38 -0.0383
    B   7348.22 -2.6581    125.58 -2.6091    921.695 + j   -45.240     BC    12718.00 -2.1303
    C   7367.00  1.5376    123.35  1.5636    908.420 + j   -23.629     CA    12754.66  2.0587
    Total S =  2740.650 + j  -113.720
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7348.04 -0.5596    122.49 -0.5112    899.012 + j   -43.517     AB    12744.82 -0.0380
    B   7350.67  3.6250    124.38  3.6774    913.007 + j   -47.825     BC    12722.66 -2.1304
    C   7369.38  1.5375    122.33  1.5651    901.144 + j   -24.903     CA    12755.43  2.0589
    Total S =  2713.162 + j  -116.245
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.63 -0.5603    171.16 -0.9287   1175.964 + j   454.003     AB    12813.75 -0.0364
    B   7416.51 -2.6581    180.45 -3.0252   1249.196 + j   480.272     BC    12805.93 -2.1317
    C   7400.45  1.5376    143.53  1.1757    993.347 + j   376.147     CA    12799.81  2.0581
    Total S =  3418.507 + j  1310.422
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7364.30 -0.5603    171.20 -0.9289   1176.086 + j   454.286     AB    12813.96 -0.0363
    B   7417.08 -2.6581    179.08 -3.0247   1240.029 + j   476.002     BC    12805.83 -2.1317
    C   7399.77  1.5376    143.65  1.1753    993.975 + j   376.782     CA    12798.94  2.0581
    Total S =  3410.091 + j  1307.070
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7365.80 -0.5604    169.26 -0.9302   1162.443 + j   450.659     AB    12816.22 -0.0365
    B   7418.22  3.6249    178.15  3.2578   1233.471 + j   474.307     BC    12806.72 -2.1316
    C   7401.46  1.5379    140.70  1.1674    970.748 + j   377.080     CA    12803.26  2.0582
    Total S =  3366.661 + j  1302.046
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7309.55 -0.5707     84.52 -0.8629    591.592 + j   177.936     AB    12657.94 -0.0472
    B   7306.58 -2.6651     91.88 -2.9398    646.173 + j   182.118     BC    12667.61 -2.1421
    C   7313.36  1.5219     89.23  1.2369    626.251 + j   183.485     CA    12657.43  2.0462
    Total S =  1864.016 + j   543.539
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7308.65 -0.5707     84.53 -0.8629    591.636 + j   177.950     AB    12656.60 -0.0472
    B   7305.93 -2.6651     91.90 -2.9398    646.239 + j   182.136     BC    12666.30 -2.1421
    C   7312.49  1.5219     89.25  1.2369    626.300 + j   183.499     CA    12655.89  2.0462
    Total S =  1864.175 + j   543.585
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7312.85 -0.5703     83.66 -0.8672    585.025 + j   179.026     AB    12661.19 -0.0463
    B   7310.89  3.6194     90.10  3.3379    632.800 + j   183.007     BC    12675.26 -2.1410
    C   7316.38  1.5229     88.07  1.2369    618.161 + j   181.774     CA    12664.94  2.0470
    Total S =  1835.986 + j   543.807
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7242.51 -0.5760     48.34 -0.8533    336.706 + j    95.850     AB    12549.25 -0.0556
    B   7226.29 -2.6756     64.63 -2.9482    449.792 + j   125.753     BC    12547.27 -2.1459
    C   7291.35  1.5202     25.42  1.2268    177.404 + j    53.595     CA    12593.05  2.0410
    Total S =   963.903 + j   275.199
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7240.76 -0.5760     48.35 -0.8533    336.713 + j    95.852     AB    12546.35 -0.0556
    B   7224.70 -2.6756     64.65 -2.9480    449.882 + j   125.694     BC    12544.20 -2.1459
    C   7289.39  1.5202     25.42  1.2268    177.411 + j    53.597     CA    12589.84  2.0410
    Total S =   964.006 + j   275.143
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7243.81 -0.5741     47.40 -0.8657    328.836 + j    98.712     AB    12557.02 -0.0545
    B   7227.82  3.6080     64.17  3.3353    446.704 + j   124.906     BC    12549.10 -2.1454
    C   7292.89  1.5208     25.25  1.2185    175.781 + j    54.819     CA    12590.98  2.0422
    Total S =   951.321 + j   278.437
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7117.28 -0.5672     33.55 -0.8278    230.744 + j    61.526     AB    12441.26 -0.0442
    B   7212.58 -2.6704     31.37 -2.9288    218.735 + j    57.833     BC    12472.73 -2.1383
    C   7248.31  1.5324     25.43  1.2725    178.109 + j    47.358     CA    12459.90  2.0481
    Total S =   627.588 + j   166.717
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7116.22 -0.5672     33.55 -0.8276    230.704 + j    61.472     AB    12436.01 -0.0432
    B   7214.74 -2.6686     31.36 -2.9278    218.709 + j    57.990     BC    12477.23 -2.1377
    C   7243.98  1.5324     25.45  1.2729    178.160 + j    47.305     CA    12455.22  2.0483
    Total S =   627.573 + j   166.766
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7118.11 -0.5664     33.30 -0.8268    229.019 + j    61.008     AB    12444.90 -0.0431
    B   7217.32  3.6140     31.09  3.3556    216.951 + j    57.336     BC    12476.69 -2.1373
    C   7248.81  1.5337     25.22  1.2743    176.708 + j    46.902     CA    12462.79  2.0492
    Total S =   622.678 + j   165.247
ieee9500unbal    Nbus=[  9549,  9549, 12528] Nlink=[ 11254, 11254, 12159] MAEv=[ 0.0002, 0.0021] MAEi=[   0.0390,   0.2416]
```

## Test Procedure (Building CIMHub)

The CIMHub repo contains a set of scripts for converting the CIM XML model to OpenDSS and GridLab-D file formats. 

It also can compare the power flow solution results (if OpenDSS and GridLab-D are installed on your local machine)

To run the conversion and power flow solution script, using the archived CIM XML files, follow the instructions below:

1. Clone the feature/cimext branch of the CIMHub repository: ```git clone https://github.com/GRIDAPPSD/CIMHub.git -b feature/cimext```

2. Install the CIMHub Python package. From your home directory, run ```python3 -m pip install -e CIMHub```

3. Build the CIMHub java libraries by changing directories into cimhub library with `cd CIMHub/cimhub`. Build the java library with `mvn clean install`

4. Return to the main CIMHub directory with `cd ..` and install the Blazegraph database engine:
   * Install the [Docker Engine](https://docs.docker.com/install/)
   * Install the Blazegraph engine with ```docker pull lyrasis/blazegraph:2.1.5```
   * Install the CIMHub docker package with ```docker pull gridappsd/cimhub:1.0.1```
   * Start the Blazegraph engine by running `./start.sh`
   * Exit the docker terminal with `exit`

5. Change directories into the 9500 node folder with `cd ieee9500`

6. Edit the python script test9500bal.py or test9500unbal.py and change the file path in line 41 and 45 to your local directory `/your/local/path/CIMHub/ieee9500/base`

7. Run `python3 test9500bal.py` or `python3 test9500unbal.py` to convert the CIM XML model

8. Run `./zipall.sh` to create downloadable archives

To build the CIM XML files from the original DSS source files:

1. Download the [cimext branch of OpenDSScmd](https://github.com/GRIDAPPSD/GOSS-GridAPPS-D/tree/feature/cimext/opendss)
   * Clone the GOSS-GridAPPSD repo with `git clone https://github.com/GRIDAPPSD/GOSS-GridAPPS-D.git -b feature/cimext`
   * If OpenDSScmd is already installed, check its location with `which opendsscmnd`. It 9s 
   * Move the opendsscmd executable with `sudo cp -i /YOUR_HOME_PATH/GOSS-GridAPPS-D/opendss/opendsscmd /usr/local/bin`

2. Uncomment lines 41 and 46 in test9500bal.py and test9500unbal.py. Now, the script will read from the original_dss directory and build the CIM XML files

3. Re-run `python3 test9500bal.py` or `python3 test9500unbal.py` to re-build the XML files and solve the power flow solution.

---

