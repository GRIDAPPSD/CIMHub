## CIMHub Requirements

Copyright (c) 2020, Battelle Memorial Institute

CIMHub will support model conversions for the [GridAPPS-D](https://gridappsd.readthedocs.io/en/latest/) project, 
provide open-source tools to faciliate adoption of [CIM](https://gridappsd.readthedocs.io/en/latest/developer_resources/index.html#cim-documentation), including 
participation in [CIM interoperability tests](https://cimug.ucaiug.org/), and provide 
model conversions for selected open-source analysis software.

1. Containerization for use within GridAPPS-D and also standalone use.
2. Output model conversions:
  * CIM to [GridLAB-D](https://github.com/gridlab-d/gridlab-d)
  * CIM to [GridPACK](https://github.com/GridOPTICS/GridPACK)
  * CIM to [OpenDSS](https://sourceforge.net/projects/electricdss/)
3. Input model conversions:
  * OpenDSS to CIM
  * GridLAB-D to OpenDSS
4. Compare power flow solutions from GridLAB-D and OpenDSS
5. Manage addition, removal and updates of components attached to the power system network model, with persistent IdentifiedObject.mRID attributes:
  * [Houses](http://gridlab-d.shoutwiki.com/wiki/Residential_module_user%27s_guide), comprising controlled Heating, Ventilating and Air Conditioning (HVAC) Models attached to CIM EnergyConsumer
  * Distributed Energy Resources (DER), including photovoltaic, storage and synchronous generator, attached to CIM ConnectivityNode
  * Measurements, attached to measurable components like ACLineSegment, EnergyConsumer, PowerElectronicsConnection, LinearShuntCompensator, PowerTransformer and Switch
6. Support different CIM versions through [SPARQL](https://www.w3.org/TR/sparql11-query/) queries stored in separate XML files



