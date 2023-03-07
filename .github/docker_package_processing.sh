#!/bin/bash

set -x
echo "clickhouse_binary_path=$clickhouse_binary_path:$version" >> $GITHUB_ENV
echo "get specific ClickHouse version $version"
docker_image=${{ env.clickhouse_binary_path }}
echo $docker_image
docker pull $docker_image
if [[ $version == 'latest' ]]; then
    pid=$(docker run -d $(echo ${{ env.clickhouse_binary_path }}))
    echo $pid
    ../retry.sh 60 2 "docker exec $pid clickhouse-client -q \"SELECT version()\""
    echo "version=$(docker exec $pid clickhouse-client -q 'SELECT version()')" >> $GITHUB_ENV
    docker stop $pid
fi
