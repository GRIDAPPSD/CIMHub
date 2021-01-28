docker ps | awk '{ print $1,$NF }' | grep cimhub | awk '{print $1 }' | xargs -I {} docker stop {}
docker ps -a | awk '{ print $1,$2 }' | grep gridappsd/cimhub | awk '{print $1 }' | xargs -I {} docker rm {}

