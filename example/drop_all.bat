set DB_URL="http://localhost:9999/blazegraph/namespace/kb/sparql"

curl -D- -X POST %DB_URL% --data-urlencode "update=drop all"
