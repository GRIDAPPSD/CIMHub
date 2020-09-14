## CIMHub: IEEE 9500-Node Test Case Files

Copyright (c) 2017-2020, Battelle Memorial Institute

This directory helps convert the IEEE 9500-node test case from source
files into GridLAB-D, OpenDSS and CSV file format. Follow these steps: 

1. Install and run the Blazegraph engine as described one directory above.
2. Clone the Powergrid-Models repository from GridAPPS-D into a sibling directory. For example, if you cloned this repository to ~/src/CIMHub, then clone the other to ~/src/Powergrid-Models
3. Run the convert9500.sh script
4. Use "gridlabd test\_ieee9500.glm" to check the converted GridLAB-D file. Results in test\_curr.csv and test\_volt.csv
5. Use "opendsscmd ieee9500\_base.dss" to check the converted OpenDSS file
6. the comma-separated files are named like "ieee9500*.csv" 
7. Run zipall.sh to create 3 downloadable archives


