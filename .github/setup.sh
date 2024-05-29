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
sudo apt-get update
sudo apt-get install python3.12-venv

echo "Create and activate Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo PATH=$PATH >> $GITHUB_ENV

./retry.sh 60 2 "sudo pip install -r requirements.txt"

echo "Install docker-compose..."
sudo curl -SL https://github.com/docker/compose/releases/download/v2.23.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

mkdir $SUITE/_instances

echo "Login to docker..."
./retry.sh 60 2 "docker login -u $DOCKER_USERNAME --password $DOCKER_PASSWORD"

if [[ $clickhouse_binary_path == "docker"* ]]; then
    echo "clickhouse_binary_path=$clickhouse_binary_path" >> $GITHUB_ENV
    echo "Get specific ClickHouse package $clickhouse_binary_path..."
    docker_image=$(echo $clickhouse_binary_path | cut -c10-)
    docker pull $docker_image
    if [[ $version == 'latest' || $version == '' ]]; then
        pid=$(docker run -d $docker_image)
        echo $pid
        ./retry.sh 60 2 "docker exec $pid clickhouse-client -q \"SELECT version()\""
        echo "version=$(docker exec $pid clickhouse-client -q 'SELECT version()')" >> $GITHUB_ENV
        docker stop $pid
    fi
fi
