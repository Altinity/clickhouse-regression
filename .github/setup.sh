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
sudo apt-get install -y python3.12-venv

echo "Create and activate Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo PATH=$PATH >> $GITHUB_ENV

./retry.sh 60 2 "pip install -r requirements.txt"

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

echo "Generate upload paths..."
if [[ $artifacts == 'internal' ]]; then
    artifact_s3_bucket_path="altinity-internal-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential="--confidential"
elif [[ $artifacts == 'public' ]]; then
    artifact_s3_bucket_path="altinity-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential=""
elif [[ $artifacts == 'builds' ]]; then
    artifact_s3_bucket_path="altinity-build-artifacts"
    confidential=""
    if [[ $event_name == "pull_request" ]]; then
        artifact_s3_dir="$pr_number/$build_sha/regression"
    elif [[ $event_name == "release" || $event_name == "push" ]]; then
        artifact_s3_dir="0/$build_sha/regression"
    fi

fi

if [[ $args == *'--with-analyzer'* ]]; then
  analyzer="with_analyzer"
else
  analyzer="without_analyzer"
fi

if [[ $args == *'--use-keeper'* ]]; then
  keeper_or_zookeeper="keeper"
else
  keeper_or_zookeeper="zookeeper"
fi

JOB_BUCKET_URL=https://$artifact_s3_bucket_path.s3.amazonaws.com

echo "confidential=$confidential" >> $GITHUB_ENV

JOB_REPORT_INDEX=$JOB_BUCKET_URL/index.html#$artifact_s3_dir/
echo "JOB_REPORT_INDEX=$JOB_REPORT_INDEX" >> $GITHUB_ENV

JOB_S3_ROOT=s3://$artifact_s3_bucket_path/$artifact_s3_dir
echo "JOB_S3_ROOT=$JOB_S3_ROOT" >> $GITHUB_ENV

SUITE_REPORT_INDEX_URL=$JOB_REPORT_INDEX$(uname -i)/$analyzer/$keeper_or_zookeeper/$SUITE$STORAGE/
echo "SUITE_REPORT_INDEX_URL=$SUITE_REPORT_INDEX_URL" >> $GITHUB_ENV

SUITE_LOG_FILE_PREFIX_URL=$JOB_BUCKET_URL/$artifact_s3_dir/$(uname -i)/$analyzer/$keeper_or_zookeeper/$SUITE$STORAGE
echo "SUITE_LOG_FILE_PREFIX_URL=$SUITE_LOG_FILE_PREFIX_URL" >> $GITHUB_ENV

SUITE_REPORT_BUCKET_PATH=$JOB_S3_ROOT/$(uname -i)/$analyzer/$keeper_or_zookeeper/$SUITE$STORAGE
echo "SUITE_REPORT_BUCKET_PATH=$SUITE_REPORT_BUCKET_PATH" >> $GITHUB_ENV

