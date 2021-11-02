# CIMHub Test Cases

Copyright (c) 2017-2021, Battelle Memorial Institute

## Process

## Results

```
  OpenDSS branch flow in N3 from LINE.LINE2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2137.01 -0.5794    460.69 -1.0673    869.660 + j   461.434     AB     3843.92 -0.0153
    B   2336.50 -2.6459    511.40  3.1405   1050.478 + j   569.414     BC     4091.64 -2.1771
    C   2267.87  1.4486    495.94  0.9484    986.923 + j   539.429     CA     3740.26  1.9869
    Total S =  2907.062 + j  1570.277
  OpenDSS branch flow in N3 from LINE.LINE2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2136.87 -0.5794    460.89 -1.0674    869.904 + j   461.758     AB     3843.77 -0.0153
    B   2336.46 -2.6459    511.65  3.1402   1050.779 + j   570.051     BC     4091.49 -2.1771
    C   2267.74  1.4486    496.16  0.9482    987.220 + j   539.816     CA     3740.03  1.9869
    Total S =  2907.903 + j  1571.625
OYODBal          Nbus=[    12,    12,     0] Nlink=[    17,    17,     0] MAEv=[ 0.3027,-1.0000] MAEi=[   0.1235,  -1.0000]
  OpenDSS branch flow in N3 from LINE.LINE2, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2116.21 -0.6318    481.27 -1.1826    867.824 + j   533.054     AB     3816.61 -0.0072
    B   2437.51 -2.6162    446.49 -3.1041    961.385 + j   510.102     BC     4119.25 -2.1845
    C   2161.29  1.4486    532.31  1.0517   1061.046 + j   444.716     CA     3689.47  1.9730
    Total S =  2890.255 + j  1487.872
  OpenDSS branch flow in N3 from LINE.LINE2, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   2104.47 -0.6475    481.27 -1.1826    871.229 + j   516.476     AB     3818.86 -0.0075
    B   2473.86 -2.6162    446.49 -3.1041    975.722 + j   517.709     BC     4118.63 -2.1854
    C   2137.27  1.4608    532.31  1.0517   1043.803 + j   452.559     CA     3688.21  1.9731
    Total S =  2890.754 + j  1486.744
OYODUnBal        Nbus=[    12,    12,     0] Nlink=[    17,    17,     0] MAEv=[ 0.3017,-1.0000] MAEi=[   0.0000,  -1.0000]

```

## AutoTransformers

The three-winding autotransformer test cases were derived from a whitepaper on CIM transformer modeling, which
included an actual test report from a 345/161/13.8 kV, 330/330/72 MVA, YNad1 autotransformer. The test data is
archived in the OpenDSS repository, with scripts that verify losses, short-circuit currents and voltage
regulation for the modeling options available in OpenDSS. GridLAB-D does not support 3-winding transformers, nor
autotransformers, so GridLAB-D validation is skipped. The CIM support for autotransformers is incomplete, so only
one of the options works properly for round-trip validation in OpenDSS.

- **AutoHLT.dss** represents the autotransformer as a non-auto Yyd1. It replicates test data, except for the split of load losses between HT and LT tests. It also fails to show the MVA size reduction inherent in the autotransformer.
- **Auto1bus.dss** represents the autotransformer as a bank of three single-phase, reduced-MVA tanks, connected YNad1. This is accurate, but does not translate through CIM because it uses a "9-phase bus" to represent the common node, which causes errors in connections and voltage ratings. This is "option 1" from the OpenDSS Tech Note on modeling autotransformers.
- **Auto3bus.dss** represents the autotransformer as a bank of three single-phase, reduced-MVA tanks, connected YNad1. This is accurate, but does not translate through CIM because it uses a "6-phase bus" with jumper to represent the common node, which causes errors in connections and voltage ratings. This is "option 2" from the OpenDSS Tech Note on modeling autotransformers.
- **AutoAuto.dss** uses the built-in "autotrans" component in OpenDSS. It uses test results directly as input, making the series-common winding connection internally. There are some errors in the losses and HT short-circuit currents, to be corrected in OpenDSS. The CIM export for "autotrans" also has to be implemented in OpenDSS. **This model option could be supported in CIM, based on specifying the vector group as YNad1**. 



