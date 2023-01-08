#!/bin/bash
docker-compose up -d
docker exec -it cimhub_hub_1 /bin/bash

# docker run --name cimhub -it --mount type=bind,source=/home/tom/src/Powergrid-Models/platform,destination=/platform gridappsd/cimhub:1.1.0

# docker run --name cimhub --entrypoint bash -it --mount type=bind,source=/home/tom/src/Powergrid-Models/platform,destination=/platform gridappsd/cimhub:1.1.0

