mvn clean install

./stop.sh
docker rmi temcderm/cimhub:0.0.1
sudo docker build -t="temcderm/cimhub:0.0.1" .
