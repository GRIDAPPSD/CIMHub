FROM python:3.8.16-bullseye
LABEL maintainer="Thomas.McDermott@pnnl.gov"

RUN apt-get update;apt-get dist-upgrade -y

ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /usr/share/man/man1/
RUN apt-get update
RUN apt-get install -y --no-install-recommends apt
RUN apt-get install -y openjdk-11-jre-headless python3-pip curl nano
RUN apt-get clean
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install lxml numpy pandas scipy SPARQLWrapper
# RUN python3 -m pip install cimhub

# install GridLAB-D for testing
COPY gridlabd/bin/gridlabd /usr/local/bin/gridlabd
COPY gridlabd/bin/gridlabd.sh /usr/local/bin/gridlabd.sh
COPY gridlabd/lib/assert.so /usr/local/lib/assert.so
COPY gridlabd/lib/climate.so /usr/local/lib/climate.so
COPY gridlabd/lib/commercial.so /usr/local/lib/commercial.so
COPY gridlabd/lib/connection.so /usr/local/lib/connection.so
COPY gridlabd/lib/generators.so /usr/local/lib/generators.so
COPY gridlabd/lib/glsolvers.so /usr/local/lib/glsolvers.so
COPY gridlabd/lib/glxengine.so /usr/local/lib/glxengine.so
COPY gridlabd/lib/market.so /usr/local/lib/market.so
COPY gridlabd/lib/mysql.so /usr/local/lib/mysql.so
COPY gridlabd/lib/optimize.so /usr/local/lib/optimize.so
COPY gridlabd/lib/powerflow.so /usr/local/lib/powerflow.so
COPY gridlabd/lib/reliability.so /usr/local/lib/reliability.so
COPY gridlabd/lib/residential.so /usr/local/lib/residential.so
COPY gridlabd/lib/tape.so /usr/local/lib/tape.so
COPY gridlabd/lib/tape_file.so /usr/local/lib/tape_file.so
COPY gridlabd/lib/tape_plot.so /usr/local/lib/tape_plot.so
COPY gridlabd/lib/static/libjsoncpp.a /usr/local/lib/static/libjsoncpp.a
COPY gridlabd/lib/static/superlu_lib.a /usr/local/lib/static/superlu_lib.a
COPY gridlabd/share/tzinfo.txt /usr/local/share/tzinfo.txt
COPY gridlabd/share/unitfile.txt /usr/local/share/unitfile.txt

# install OpenDSS for testing
RUN mkdir -p ~/Documents/OpenDSSCmd
COPY opendsscmd/linux/opendsscmd /usr/local/bin/opendsscmd
COPY opendsscmd/linux/liblinenoise.so /usr/local/lib/liblinenoise.so
COPY opendsscmd/linux/libklusolve.so /usr/local/lib/libklusolve.so
RUN ldconfig

# Java application, DB engine, base examples and queries
WORKDIR /app
COPY blazegraph /data
COPY example example
COPY releases releases
COPY tests tests
COPY model_output_tests model_output_tests
COPY support support
COPY queries/cimhubconfig.json queries/
COPY queries/q100.xml queries/

# extra examples and autotest
COPY CPYDAR CPYDAR
COPY der der
COPY ecp ecp
COPY gmdm gmdm
COPY ieee4 ieee4
COPY ieee9500 ieee9500
COPY line_constants line_constants
COPY lv_network lv_network
COPY OEDI OEDI
COPY tutorial tutorial
COPY batch_tests.py batch_tests.py

# local installation of CIMHub Python
COPY setup.py setup.py
COPY setup.cfg setup.cfg
COPY src_python src_python
RUN python3 -m pip install -e /app

VOLUME /data

CMD []
ENTRYPOINT ["/bin/bash"]


