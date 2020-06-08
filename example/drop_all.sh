if (($# > 0)) 
then
  declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"
else
  declare -r DB_URL="http://blazegraph:8080/bigdata/namespace/kb/sparql"
fi

curl -D- -X POST $DB_URL --data-urlencode "update=drop all"
