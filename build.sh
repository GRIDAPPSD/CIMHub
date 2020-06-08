mvn clean install

# opendsscmd build product from fpc
rm -rf distrib
mkdir distrib
cp ../OpenDSS/Source/CMD/test/opendsscmd distrib
cp ../linenoise-ng/build/liblinenoise.so distrib

./stop.sh
docker rmi temcderm/cimhub:0.0.1
sudo docker build -t="temcderm/cimhub:0.0.1" .
