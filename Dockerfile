FROM python:3.8-slim-buster
LABEL maintainer="Thomas.McDermott@pnnl.gov"

RUN apt-get update;apt-get dist-upgrade -y

ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /usr/share/man/man1/
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y openjdk-11-jre-headless python3-pip
RUN apt-get clean
RUN pip3 install SPARQLWrapper --upgrade

COPY distrib/opendsscmd /usr/local/bin/opendsscmd
COPY distrib/liblinenoise.so /usr/local/lib/liblinenoise.so
WORKDIR /app
COPY distrib/example example
COPY target/*.jar .

RUN ldconfig

CMD []
ENTRYPOINT [/bin/bash]

