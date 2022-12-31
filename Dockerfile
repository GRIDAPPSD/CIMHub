FROM python:3.8.10-slim-buster
LABEL maintainer="Thomas.McDermott@pnnl.gov"

RUN apt-get update;apt-get dist-upgrade -y

ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /usr/share/man/man1/
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y openjdk-11-jre-headless python3-pip curl nano
RUN apt-get clean
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install lxml numpy pandas scipy SPARQLWrapper
# RUN python3 -m pip install cimhub

COPY opendsscmd/linux/opendsscmd /usr/local/bin/opendsscmd
COPY opendsscmd/linux/liblinenoise.so /usr/local/lib/liblinenoise.so
COPY opendsscmd/linux/libklusolve.so /usr/local/lib/libklusolve.so
RUN ldconfig

WORKDIR /app
COPY blazegraph blazegraph
COPY example example
COPY releases releases
COPY tests tests
COPY queries/cimhubconfig.json queries/
COPY queries/q100.xml queries/

COPY setup.py setup.py
COPY setup.cfg setup.cfg
COPY src_python src_python
RUN python3 -m pip install -e /app

VOLUME /data

CMD []
ENTRYPOINT ["/bin/bash"]


