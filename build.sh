# mvn clean install

docker ps -a | awk '{ print $1,$2 }' | grep temcderm/cimhub:0.0.1 | awk '{print $1 }' | xargs -I {} docker rm {}

docker rmi temcderm/cimhub:0.0.1

sudo docker build -t="temcderm/cimhub:0.0.1" .
