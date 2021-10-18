FROM python:3.8-slim-buster
LABEL maintainer="Thomas.McDermott@pnnl.gov"

RUN apt-get update;apt-get dist-upgrade -y

ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /usr/share/man/man1/
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y openjdk-11-jre-headless python3-pip curl nano
RUN apt-get clean
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install cimhub

COPY distrib/opendsscmd /usr/local/bin/opendsscmd
COPY distrib/liblinenoise.so /usr/local/lib/liblinenoise.so
COPY distrib/libklusolve.so /usr/local/lib/libklusolve.so
RUN ldconfig

WORKDIR /app
COPY example example
COPY cimhub/target target

VOLUME /data

CMD []
ENTRYPOINT ["/bin/bash"]


