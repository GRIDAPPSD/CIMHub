## CIMHub: IEEE 9500-Node Test Case Files

Copyright (c) 2017-2021, Battelle Memorial Institute

This directory helps convert the IEEE 9500-node test case from source
files into GridLAB-D, OpenDSS and CSV file format. Follow these steps: 

1. Install and run the Blazegraph engine as described one directory above
2. Install the Python support with ```pip3 install cimhub --upgrade```
3. Run ```python3 test9500.py``` to check the results
4. Run zipall.sh to create 3 downloadable archives

### Results

```
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7380.77 -0.5463    131.75 -0.5273    972.255 + j   -18.499     AB    12780.87 -0.0228
    B   7377.31 -2.6407    127.19 -2.6051    937.711 + j   -33.401     BC    12777.46 -2.1183
    C   7369.40  1.5464    154.02  1.5205   1134.664 + j    29.316     CA    12767.58  2.0713
    Total S =  3044.630 + j   -22.584
  OpenDSS branch flow in LINE.LN5815900-1 from E192860, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7380.74 -0.5463    131.77 -0.5273    972.377 + j   -18.501     AB    12780.80 -0.0228
    B   7377.26 -2.6407    127.21 -2.6053    937.880 + j   -33.243     BC    12777.38 -2.1183
    C   7369.36  1.5464    154.05  1.5204   1134.873 + j    29.519     CA    12767.52  2.0713
    Total S =  3045.130 + j   -22.224
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7383.27 -0.5460    130.70 -0.5283    964.854 + j   -17.041     AB    12787.82 -0.0228
    B   7379.98  3.6422    125.69  3.6764    927.020 + j   -31.754     BC    12778.11 -2.1181
    C   7371.98  1.5471    153.00  1.5214   1127.520 + j    28.980     CA    12773.41  2.0718
    Total S =  3019.394 + j   -19.814
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7394.48 -0.5463     81.96  2.8526   -586.086 + j   154.194     AB    12778.02 -0.0287
    B   7330.68 -2.6477    111.76  0.6002   -814.631 + j    86.915     BC    12687.34 -2.1222
    C   7334.20  1.5446    143.20 -1.6261  -1049.804 + j   -30.607     CA    12742.57  2.0723
    Total S = -2450.521 + j   210.502
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7394.33 -0.5463     81.96  2.8524   -586.145 + j   154.100     AB    12777.61 -0.0287
    B   7330.35 -2.6477    111.78  0.6002   -814.784 + j    86.931     BC    12686.83 -2.1222
    C   7333.94  1.5446    143.24 -1.6261  -1050.097 + j   -30.616     CA    12742.22  2.0723
    Total S = -2451.026 + j   210.416
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7395.34 -0.5461     81.52  2.8509   -583.328 + j   152.273     AB    12781.49 -0.0283
    B   7334.23  3.6358    111.07  0.6017   -809.928 + j    87.359     BC    12692.06 -2.1220
    C   7335.82  1.5449    142.19  4.6546  -1042.566 + j   -33.206     CA    12744.84  2.0725
    Total S = -2435.822 + j   206.426
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7408.46 -0.5411     79.83  1.7856   -405.674 + j  -430.340     AB    12814.15 -0.0206
    B   7373.16 -2.6389     70.74 -0.3817   -330.561 + j  -403.436     BC    12757.23 -2.1078
    C   7410.02  1.5621     44.10  2.3499    230.481 + j  -231.610     CA    12865.39  2.0812
    Total S =  -505.754 + j -1065.387
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7408.35 -0.5411     79.86  1.7862   -406.058 + j  -430.296     AB    12813.74 -0.0206
    B   7372.80 -2.6389     70.83 -0.3810   -331.237 + j  -403.686     BC    12756.77 -2.1078
    C   7409.85  1.5621     44.07  2.3504    230.216 + j  -231.587     CA    12865.14  2.0812
    Total S =  -507.079 + j -1065.568
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7408.84 -0.5414     79.09  1.7757   -397.839 + j  -430.174     AB    12813.30 -0.0205
    B   7375.23  3.6447     69.82 -0.3915   -322.289 + j  -401.654     BC    12761.66 -2.1078
    C   7410.14  1.5618     45.37  2.3477    237.582 + j  -237.822     CA    12866.27  2.0809
    Total S =  -482.546 + j -1069.649
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7328.71 -0.5620     81.07 -0.8545    568.879 + j   171.321     AB    12699.58 -0.0393
    B   7328.12 -2.6581     88.14 -2.9308    622.029 + j   173.908     BC    12696.54 -2.1344
    C   7332.58  1.5307     83.20  1.2455    585.406 + j   171.628     CA    12690.65  2.0550
    Total S =  1776.314 + j   516.858
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7327.94 -0.5620     81.08 -0.8545    568.917 + j   171.333     AB    12698.18 -0.0393
    B   7327.28 -2.6581     88.16 -2.9308    622.096 + j   173.926     BC    12695.06 -2.1344
    C   7331.71  1.5307     83.21  1.2455    585.451 + j   171.642     CA    12689.23  2.0550
    Total S =  1776.464 + j   516.901
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7331.21 -0.5624     80.45 -0.8599    563.886 + j   172.896     AB    12696.71 -0.0388
    B   7330.12  3.6265     87.02  3.3446    612.723 + j   177.436     BC    12704.08 -2.1335
    C   7334.55  1.5310     82.59  1.2440    580.985 + j   171.434     CA    12697.18  2.0549
    Total S =  1757.593 + j   521.766
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7426.31 -0.5515     20.47  2.3140   -146.284 + j   -41.449     AB    12673.08 -0.0435
    B   7162.62 -2.6564     57.68  0.2136   -398.027 + j  -110.832     BC    12506.73 -2.1409
    C   7199.95  1.5132     47.52 -1.9158   -328.112 + j   -97.004     CA    12557.37  2.0609
    Total S =  -872.423 + j  -249.285
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7425.25 -0.5515     20.48  2.3140   -146.286 + j   -41.450     AB    12670.92 -0.0435
    B   7161.19 -2.6564     57.70  0.2136   -398.084 + j  -110.848     BC    12503.54 -2.1410
    C   7197.72  1.5132     47.54 -1.9158   -328.123 + j   -97.008     CA    12554.55  2.0609
    Total S =  -872.493 + j  -249.305
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7425.06 -0.5508     20.46  2.2991   -145.492 + j   -43.678     AB    12674.50 -0.0423
    B   7167.24  3.6279     57.34  0.2134   -395.746 + j  -110.752     BC    12512.00 -2.1403
    C   7199.30  1.5138     47.19  4.3541   -324.438 + j  -100.803     CA    12555.32  2.0615
    Total S =  -865.676 + j  -255.232
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7129.14 -0.5341     30.64 -0.7945    211.063 + j    56.238     AB    12552.20 -0.0070
    B   7328.16 -2.6372     27.54 -2.8953    195.149 + j    51.524     BC    12593.30 -2.0887
    C   7402.30  1.5952     22.90  1.3380    163.961 + j    43.137     CA    12710.17  2.0910
    Total S =   570.173 + j   150.899
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7128.65 -0.5341     30.65 -0.7941    211.140 + j    56.180     AB    12550.90 -0.0070
    B   7327.16 -2.6372     27.55 -2.8950    195.184 + j    51.460     BC    12586.23 -2.0878
    C   7402.83  1.5970     22.91  1.3381    163.920 + j    43.401     CA    12716.35  2.0918
    Total S =   570.244 + j   151.042
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7130.55 -0.5342     30.50 -0.7944    210.167 + j    55.956     AB    12555.06 -0.0068
    B   7331.88  3.6463     27.41  3.3882    194.288 + j    51.286     BC    12590.99 -2.0880
    C   7401.22  1.5968     22.78  1.3382    163.006 + j    43.117     CA    12716.23  2.0918
    Total S =   567.461 + j   150.360
ieee9500bal      Nbus=[  9493,  9493, 12463] Nlink=[ 11191, 11191, 12132] MAEv=[ 0.0002, 0.0018] MAEi=[   0.0057,   0.1214]
```

