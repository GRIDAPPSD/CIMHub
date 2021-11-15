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


### Results

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
    A   7373.13 -0.5532    139.12 -0.5573   1025.714 + j     4.184     AB    12768.53 -0.0297
    B   7370.93  3.6356    131.26  3.6571    967.310 + j   -20.791     BC    12765.64 -2.1241
    C   7368.95  1.5411    150.63  1.5200   1109.743 + j    23.394     CA    12766.69  2.0649
    Total S =  3102.768 + j     6.787
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
    A   7367.67 -0.5602    123.19 -0.5111    906.513 + j   -44.580     AB    12773.97 -0.0385
    B   7367.01  3.6249    124.20  3.6842    913.391 + j   -54.244     BC    12714.39 -2.1325
    C   7341.70  1.5370    123.87  1.5584    909.178 + j   -19.493     CA    12748.98  2.0602
    Total S =  2729.083 + j  -118.317
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
    A   7373.98 -0.5609    171.05 -0.9306   1176.111 + j   455.780     AB    12787.57 -0.0386
    B   7379.48  3.6250    179.05  3.2592   1233.868 + j   472.560     BC    12779.70 -2.1300
    C   7407.54  1.5377    143.28  1.1616    987.180 + j   389.827     CA    12816.58  2.0579
    Total S =  3397.159 + j  1318.168
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
    A   7307.68 -0.5705     84.38 -0.8712    588.992 + j   182.613     AB    12668.42 -0.0464
    B   7320.61  3.6183     89.95  3.3356    632.346 + j   183.658     BC    12685.60 -2.1397
    C   7336.42  1.5260     78.52  1.2347    551.784 + j   165.413     CA    12689.95  2.0474
    Total S =  1773.122 + j   531.685
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
    A   7263.91 -0.5751     47.87 -0.8695    332.775 + j   100.883     AB    12586.48 -0.0550
    B   7246.58  3.6081     63.94  3.3355    446.196 + j   124.772     BC    12541.59 -2.1477
    C   7261.61  1.5200     25.61  1.2125    177.267 + j    56.293     CA    12582.22  2.0433
    Total S =   956.238 + j   281.948
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7135.42 -0.5672     33.40 -0.8275    230.281 + j    61.316     AB    12427.77 -0.0463
    B   7178.99 -2.6704     31.43 -2.9274    218.244 + j    57.377     BC    12456.86 -2.1363
    C   7263.43  1.5324     25.26  1.2737    177.367 + j    46.929     CA    12488.74  2.0483
    Total S =   625.892 + j   165.622
  OpenDSS branch flow in LINE.LN6350537-1 from M1026907, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7133.67 -0.5672     33.41 -0.8271    230.367 + j    61.253     AB    12418.62 -0.0454
    B   7177.34 -2.6686     31.44 -2.9271    218.182 + j    57.687     BC    12459.98 -2.1355
    C   7261.31  1.5324     25.27  1.2739    177.407 + j    46.906     CA    12485.38  2.0483
    Total S =   625.956 + j   165.846
  GridLAB-D branch flow in LINE_LN6350537-1 from M1026907
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7126.49 -0.5677     33.60 -0.8334    231.066 + j    62.869     AB    12414.97 -0.0455
    B   7180.16  3.6141     31.29  3.3551    217.195 + j    57.545     BC    12447.95 -2.1360
    C   7249.39  1.5330     25.44  1.2672    177.956 + j    48.462     CA    12472.75  2.0486

ieee9500bal      Nbus=[  9549,  9549, 12524] Nlink=[ 11252, 11252, 12156] MAEv=[ 0.0002, 0.0051] MAEi=[   0.0087,   0.1406]
```

