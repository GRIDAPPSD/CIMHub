#!/bin/bash
declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"
#declare -r DB_URL="http://blazegraph:8080/bigdata/namespace/kb/sparql"
declare -r CIMHUB_PATH="../cimhub/target/libs/*:../cimhub/target/cimhub-0.0.2-SNAPSHOT.jar"
declare -r CIMHUB_PROG="gov.pnnl.gridappsd.cimhub.CIMImporter"

