#!/bin/bash

set -x

export RUNNER_IP=$(hostname -I | cut -d ' ' -f 1)
export RUNNER_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$RUNNER_IP"
env
uname -i

sudo rm -rf /var/lib/apt/lists/*
sudo rm -rf /var/cache/debconf
sudo rm -rf /tmp/*

echo "Install Python modules..."
sudo apt-get clean
./retry.sh 60 2 "sudo pip install -r requirements.txt"
sudo apt-get update

echo "Install docker-compose..."
curl -SL https://github.com/docker/compose/releases/download/v2.23.1/docker-compose-linux-x86_64 -o ~/.local/bin/docker-compose

mkdir $SUITE/_instances

echo "Login to docker..."
./retry.sh 60 2 "docker login -u $DOCKER_USERNAME --password $DOCKER_PASSWORD"

if [[ $clickhouse_binary_path == "docker"* ]]; then
    echo "clickhouse_binary_path=$clickhouse_binary_path:$version" >> $GITHUB_ENV
    echo "Get specific ClickHouse version $version..."
    docker_image=$(echo $clickhouse_binary_path | cut -c10- | cut -d: -f1):$version
    docker pull $docker_image
    if [[ $version == 'latest' ]]; then
        pid=$(docker run -d $docker_image)
        echo $pid
        ./retry.sh 60 2 "docker exec $pid clickhouse-client -q \"SELECT version()\""
        echo "version=$(docker exec $pid clickhouse-client -q 'SELECT version()')" >> $GITHUB_ENV
        docker stop $pid
    fi
fi
