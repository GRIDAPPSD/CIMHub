# CIMHub

Copyright &copy; 2017-2022, Battelle Memorial Institute

This is a tool set for translating electric power distribution system models between
various formats, using the IEC Standard 61970/61968 Common Information Model (CIM) as the "Hub".
The CIM data is stored in an open-source triple-store called Blazegraph.
Python 3 scripts depend on SPARQLWrapper.

## Installation and Examples

Please see the [documentation](https://cimhub.readthedocs.io/en/latest/) or the 
[repository](https://github.com/GRIDAPPSD/CIMHub) for details.

* There are Docker and Java runtime options for Blazegraph installation.
* Examples include the [IEEE test feeders](https://cmte.ieee.org/pes-testfeeders/resources/), a [PNNL taxonomy feeder](https://doi.org/10.1109/PES.2009.5275900), and many others.
* The proposed IEEE 9500-node test feeder is maintained here.
* Voltage control functions from IEEE 1547-2018 are supported through CIM Dynamics, 61970-302, 2nd ed.
* Features include scripts to add houses, distributed energy resources, and measurements to a CIM model.
* Export formats include OpenDSS, GridLAB-D&trade;, comma-separated values, ePHASORSIM, and Alternative Transients Program.
* CIMHub is a component of the [GridAPPS-D project](https://doi.org/10.1109/ACCESS.2018.2851186).


## License

<div>
Copyright &copy; 2017-2022, Battelle Memorial Institute All rights reserved.
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
