## GridAPPS-D Feeder Models

Eleven feeder models are tested routinely for use in GridAPPS-D, summarized in the table below:

|Name|Features|Houses|Buses|Nodes|Branches|Load|Origin|
|----|--------|------|-----|-----|--------|----|------|
|ACEP_PSIL|480-volt microgrid with PV, wind and diesel|No|8|24|13|0.28|UAF|
|EPRI_DPV_J1|1800 kW PV in 11 locations|No|3434|4245|4901|9.69|EPRI DPV|
|IEEE13|Added CIM sampler|No|22|57|51|3.44|IEEE (mod)|
|IEEE13_Assets|Uses line spacings and wires|No|16|41|40|3.58|IEEE (mod)|
|IEEE37|Delta system|No|39|117|73|2.59|IEEE|
|IEEE123|Includes switches for reconfiguration|No|130|274|237|3.62|IEEE|
|IEEE123_PV|Added 3320 kW PV in 14 locations|Yes|214|442|334|0.27|IEEE/NREL|
|IEEE8500|Large model, balanced secondary loads|Yes|4876|8531|6103|11.98|IEEE|
|IEEE8500_3subs|Added 2 grid sources and DER|Yes|5294|9499|6823|9.14|GridAPPS-D|
|R2_12_47_2|Supports approximately 4000 houses|Yes|853|1631|1086|6.26|PNNL|
|Transactive|Added 1281 secondary loads to IEEE123|Yes|1516|3051|2812|3.92|GridAPPS-D|

Notes:

1. The "CIM Sampler" version of the IEEE 13-bus model added a single breaker, recloser, fuse, center-tap transformer, split-phase secondary load, PV and battery for the purpose of CIM conversion testing
2. All models originated with an OpenDSS version, except for Transactive, which originated from a hand-edited GridLAB-D model, then converted to OpenDSS. See code in directory ```blazegraph/test/glm/pnnl``` for details.
3. Model marked ```Yes``` for Houses have been tested with houses, but they don't require houses.
4. ```Load``` is the net OpenDSS source power injection, which is approximately load plus losses, less DER output

The CIM namespace is ***http://iec.ch/TC57/CIM100#*** and the CIM class counts for each circuit are tabulated below:

[Class Count Table](class_counts.md)

Copyright (c) 2017-2022, Battelle Memorial Institute



