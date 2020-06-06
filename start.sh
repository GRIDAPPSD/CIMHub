# docker run --name cimhub -it --mount type=bind,source=/home/tom/src/CIMHub/model_output_tests,destination=/data temcderm/cimhub:0.0.1

docker run --name cimhub --entrypoint bash -it --mount type=bind,source=/home/tom/src/CIMHub/model_output_tests,destination=/data temcderm/cimhub:0.0.1

