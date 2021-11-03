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
    A   7420.55 -0.5463    138.86 -0.2096    972.576 + j  -340.401     AB    12856.22 -0.0237
    B   7417.06 -2.6424    135.22 -2.2789    937.403 + j  -356.648     BC    12839.86 -2.1191
    C   7409.13  1.5464    158.14  1.7975   1134.920 + j  -291.187     CA    12836.41  2.0713
    Total S =  3044.899 + j  -988.235
  GridLAB-D branch flow in LINE_LN5815900-1 from E192860
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7057.38 -0.5489    142.36 -0.2704    965.971 + j  -276.121     AB    12223.21 -0.0258
    B   7053.73  3.6392    137.85  3.9416    928.246 + j  -289.626     BC    12212.75 -2.1211
    C   7045.36  1.5440    163.46  1.7440   1128.672 + j  -228.751     CA    12208.10  2.0689
    Total S =  3022.888 + j  -794.498
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7394.48 -0.5463     81.96  2.8526   -586.086 + j   154.194     AB    12778.02 -0.0287
    B   7330.68 -2.6477    111.76  0.6002   -814.631 + j    86.915     BC    12687.34 -2.1222
    C   7334.20  1.5446    143.20 -1.6261  -1049.804 + j   -30.607     CA    12742.57  2.0723
    Total S = -2450.521 + j   210.502
  OpenDSS branch flow in LINE.LN6380847-1 from M1047303, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7408.24 -0.5463     81.85  2.8541   -586.172 + j   155.202     AB    12801.71 -0.0287
    B   7344.21 -2.6477    111.58  0.6016   -814.705 + j    88.074     BC    12710.80 -2.1222
    C   7347.79  1.5446    142.96 -1.6251  -1050.011 + j   -29.513     CA    12766.24  2.0723
    Total S = -2450.888 + j   213.763
  GridLAB-D branch flow in LINE_LN6380847-1 from M1047303
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7038.79 -0.5483     84.64  2.8000   -583.111 + j   122.245     AB    12166.41 -0.0310
    B   6978.79  3.6328    116.63  0.5606   -811.986 + j    56.435     BC    12075.70 -2.1248
    C   6980.31  1.5422    149.86  4.6199  -1043.958 + j   -66.854     CA    12127.30  2.0702
    Total S = -2439.056 + j   111.825
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7408.46 -0.5411     79.83  1.7856   -405.674 + j  -430.340     AB    12814.15 -0.0206
    B   7373.16 -2.6389     70.74 -0.3817   -330.561 + j  -403.436     BC    12757.23 -2.1078
    C   7410.02  1.5621     44.10  2.3499    230.481 + j  -231.610     CA    12865.39  2.0812
    Total S =  -505.754 + j -1065.387
  OpenDSS branch flow in LINE.LN6044631-1 from E203026, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7422.48 -0.5411     79.51  1.7881   -405.879 + j  -428.455     AB    12838.13 -0.0206
    B   7386.80 -2.6389     70.49 -0.3791   -331.064 + j  -401.899     BC    12780.86 -2.1078
    C   7423.76  1.5621     43.83  2.3462    230.371 + j  -229.808     CA    12889.49  2.0813
    Total S =  -506.572 + j -1060.162
  GridLAB-D branch flow in LINE_LN6044631-1 from E203026
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7046.49 -0.5432     88.48  1.7251   -400.444 + j  -477.876     AB    12189.18 -0.0223
    B   7016.00  3.6426     78.84 -0.4401   -325.777 + j  -447.066     BC    12139.13 -2.1091
    C   7053.11  1.5609     51.93  2.4343    235.226 + j  -280.741     CA    12244.67  2.0794
    Total S =  -490.995 + j -1205.683
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7328.71 -0.5620     81.07 -0.8545    568.879 + j   171.321     AB    12699.58 -0.0393
    B   7328.12 -2.6581     88.14 -2.9308    622.029 + j   173.908     BC    12696.54 -2.1344
    C   7332.58  1.5307     83.20  1.2455    585.406 + j   171.628     CA    12690.65  2.0550
    Total S =  1776.314 + j   516.858
  OpenDSS branch flow in LINE.LN6381853-1 from L2955077, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7376.70 -0.5637     80.53 -0.8554    568.928 + j   170.795     AB    12776.07 -0.0402
    B   7375.83 -2.6581     87.54 -2.9315    621.721 + j   174.290     BC    12778.84 -2.1344
    C   7379.90  1.5307     82.66  1.2448    585.246 + j   172.025     CA    12779.59  2.0541
    Total S =  1775.894 + j   517.110
  GridLAB-D branch flow in LINE_LN6381853-1 from L2955077
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7006.80 -0.5671     84.24 -0.8653    564.245 + j   173.380     AB    12134.32 -0.0436
    B   7005.10  3.6218     91.19  3.3384    613.335 + j   178.598     BC    12141.38 -2.1382
    C   7009.93  1.5262     86.45  1.2387    581.127 + j   171.831     CA    12135.18  2.0502
    Total S =  1758.706 + j   523.809
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7426.31 -0.5515     20.47  2.3140   -146.284 + j   -41.449     AB    12673.08 -0.0435
    B   7162.62 -2.6564     57.68  0.2136   -398.027 + j  -110.832     BC    12506.73 -2.1409
    C   7199.95  1.5132     47.52 -1.9158   -328.112 + j   -97.004     CA    12557.37  2.0609
    Total S =  -872.423 + j  -249.285
  OpenDSS branch flow in LINE.LN5486729-1 from M1069310, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7439.17 -0.5515     20.44  2.3140   -146.281 + j   -41.448     AB    12695.40 -0.0435
    B   7175.46 -2.6564     57.59  0.2136   -398.060 + j  -110.841     BC    12528.33 -2.1410
    C   7211.92  1.5132     47.44 -1.9157   -328.118 + j   -96.944     CA    12578.69  2.0609
    Total S =  -872.458 + j  -249.233
  GridLAB-D branch flow in LINE_LN5486729-1 from M1069310
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7068.41 -0.5534     21.49  2.2960   -145.487 + j   -43.761     AB    12050.46 -0.0464
    B   6800.84  3.6242     60.50  0.2093   -396.181 + j  -111.031     BC    11882.24 -2.1450
    C   6834.25  1.5079     49.73  4.3477   -324.494 + j  -101.021     CA    11924.07  2.0581
    Total S =  -866.162 + j  -255.813
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7129.14 -0.5341     30.64 -0.7945    211.063 + j    56.238     AB    12552.20 -0.0070
    B   7328.16 -2.6372     27.54 -2.8953    195.149 + j    51.524     BC    12593.30 -2.0887
    C   7402.30  1.5952     22.90  1.3380    163.961 + j    43.137     CA    12710.17  2.0910
    Total S =   570.173 + j   150.899
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7143.71 -0.5341     30.58 -0.7943    211.111 + j    56.212     AB    12576.49 -0.0070
    B   7341.58 -2.6372     27.49 -2.8952    195.169 + j    51.493     BC    12617.38 -2.0887
    C   7417.04  1.5952     22.86  1.3378    163.970 + j    43.170     CA    12735.81  2.0910
    Total S =   570.251 + j   150.875
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   6743.36 -0.5344     32.32 -0.7949    210.574 + j    56.131     AB    11901.69 -0.0065
    B   6961.32  3.6448     28.88  3.3867    194.368 + j    51.308     BC    11945.95 -2.0867
    C   7036.71  1.5999     23.99  1.3411    163.194 + j    43.201     CA    12069.82  2.0918
    Total S =   568.136 + j   150.640
ieee9500bal      Nbus=[  9493,  9493, 12463] Nlink=[ 11191, 11191, 12132] MAEv=[ 0.0030, 0.0484] MAEi=[   0.1257,   1.0415]
```

