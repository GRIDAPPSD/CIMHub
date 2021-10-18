# CIMHub

Copyright (c) 2017-2021, Battelle Memorial Institute

This is a tool set for translating electric power distribution system models between
various formats, using the IEC Standard 61970/61968 Common Information Model (CIM) as the "Hub".
The CIM data is stored in an open-source triple-store called Blazegraph.
Python 3 scripts depend on SPARQLWrapper.

## Installation Instructions

CIMHub requires Docker for the database engine, and it runs on Linux (best), Windows or Mac OS X.
The database engine (Blazegraph) requires Java 8, which is no longer widely available for new installations.  Blazegraph isn't 
compatible with Java 9 or newer versions. Therefore, we recommend using Blazegraph in a Docker container: 

1. Install the [Docker Engine](https://docs.docker.com/install/)
2. Install the Blazegraph engine with _docker pull lyrasis/blazegraph:2.1.5_
3. Install the CIMHub Java-based extensions with _docker pull gridappsd/cimhub_

## Examples

See the README file and example files at [the repository](https://github.com/GRIDAPPSD/CIMHub)

1. An example shell script (in the _example_ folder) runs inside the CIMHub Docker container, converting two versions of the IEEE 13-Bus circuit from OpenDSS to CIM XML, and then to OpenDSS and GridLAB-D. One version of the circuit, labeled _CDPSM_ uses phase impedance matrices for line segments. It also has two batteries and two solar installations, plus a single-phase center-tapped transformer. The other version,
labeled _Assets_, uses wire and spacing data for the line segments, and transformer code data for the transformers.
2. Example Python scripts (in the _tests_ folder) illustrate several operations:
    * Listing feeders and component counts in the database
    * Loading circuit models into the database
    * Extracting OpenDSS and GridLAB-D models from the database
    * Adding and removing distributed energy resources (DER) to a circuit 
    * Adding and removing Houses to a circuit, for GridLAB-D simulations
    * Adding and removing CIM Measurements to a circuit, for GridAPPS-D simulations
    * Systematically comparing OpenDSS and GridLAB-D power flow solutions, before and after the conversion process
    
See the [GridAPPS-D documentation](https://gridappsd.readthedocs.io/en/latest/developer_resources/index.html#cim-documentation) for more information about the CIM.

## License

<div>
Copyright &copy; 2017-2021, Battelle Memorial Institute All rights reserved.
</div>
    

1. Battelle Memorial Institute (hereinafter Battelle) hereby grants permission to any person or entity lawfully obtaining a copy of this software and associated documentation files (hereinafter the Software) to redistribute and use the Software in source and binary forms, with or without modification. Such person or entity may use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and may permit others to do so, subject to the following conditions:
    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimers.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Other than as used herein, neither the name Battelle Memorial Institute or Battelle may be used in any form whatsoever without the express written consent of Battelle.

2. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BATTELLE OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

General disclaimer for use with open source software licenses:

* This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the United States Government nor the United States Department of Energy, nor Battelle, nor any of their employees, nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe privately owned rights.
* Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United States Government or any agency thereof, or Battelle Memorial Institute. The views and opinions of authors expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

```
    PACIFIC NORTHWEST NATIONAL LABORATORY
                 operated by
                 BATTELLE
                  for the
     UNITED STATES DEPARTMENT OF ENERGY
      under Contract DE-AC05-76RL01830
```
