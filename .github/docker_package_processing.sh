#!/bin/bash

set -x
export clickhouse_binary_path="$clickhouse_binary_path:$version"
echo "get specific ClickHouse version $version"
docker_image=$clickhouse_binary_path
docker pull $docker_image
if [[ $version == 'latest' ]];
then
    pid=$(docker run -d $(echo $clickhouse_binary_path))
    echo $pid
    ./retry.sh 60 2 "docker exec $pid clickhouse-client -q \"SELECT version()\""
    echo "version=$(docker exec $pid clickhouse-client -q 'SELECT version()')" >> $GITHUB_ENV
    docker stop $pid
fi
