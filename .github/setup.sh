#!/bin/bash

set -x

export RUNNER_IP=$(hostname -I | cut -d ' ' -f 1)
export RUNNER_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$RUNNER_IP"
uname -i

echo "::group::Print env"
env
echo "::endgroup::"

echo "::group::Python Setup"
echo "Install Python modules..."
sudo apt-get install -y python3.12-venv

echo "Create and activate Python virtual environment..."
if [ ! -f venv/bin/activate ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "PATH=$PATH" >> "$GITHUB_ENV"
echo "Pre-installing Python packages from requirements.txt..."
./retry.sh 60 2 "pip install -r requirements.txt"
echo "::endgroup::"

echo "::group::Set up ZRAM"
sudo apt-get install -y linux-modules-extra-$(uname -r)
sudo modprobe zram
MemTotal=$(grep -Po "(?<=MemTotal:)\s+\d+" /proc/meminfo) # KiB
Percent=200
ZRAM_SIZE=$(($MemTotal / 1024 / 1024 * $Percent / 100)) # Convert to GiB
./retry.sh 30 2 sudo zramctl --size ${ZRAM_SIZE}GiB --algorithm zstd /dev/zram0
sudo mkswap /dev/zram0 && sudo swapon -p 100 /dev/zram0
sudo sysctl vm.swappiness=100 # optional, makes zram usage more aggressive
echo "::endgroup::"

echo "::group::Install docker-compose"
COMPOSE_VERSION="v2.23.1"
COMPOSE_BIN_NAME="docker-compose-linux-$(uname -m)"
COMPOSE_URL="https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/${COMPOSE_BIN_NAME}"
CACHE_PATH="/mnt/cache/docker-compose/${COMPOSE_VERSION}"
TARGET_PATH="/usr/local/bin/docker-compose"

if [ -d "/mnt/cache" ]; then
    echo "Using cached docker-compose if available"
    sudo mkdir -p "$CACHE_PATH"
    if [ ! -f "$CACHE_PATH/docker-compose" ]; then
        echo "Downloading docker-compose ${COMPOSE_VERSION}..."
        sudo curl -SL "$COMPOSE_URL" -o "$CACHE_PATH/docker-compose"
        sudo chmod +x "$CACHE_PATH/docker-compose"
    else
        echo "docker-compose ${COMPOSE_VERSION} already cached"
    fi

    echo "Linking cached docker-compose to ${TARGET_PATH}"
    sudo ln -sf "$CACHE_PATH/docker-compose" "$TARGET_PATH"
else
    echo "No cache available, downloading docker-compose directly"
    sudo curl -SL "$COMPOSE_URL" -o "$TARGET_PATH"
    sudo chmod +x "$TARGET_PATH"
fi

docker-compose --version
echo "::endgroup::"

echo "::group::Docker Setup"
mkdir $SUITE/_instances

echo "Login to docker..."
./retry.sh 60 2 "docker login -u $DOCKER_USERNAME --password $DOCKER_PASSWORD"

if [[ $clickhouse_path == "docker"* ]]; then
  echo "clickhouse_path=$clickhouse_path" >>$GITHUB_ENV
  echo "Get specific ClickHouse package $clickhouse_path..."
  docker_image=$(echo $clickhouse_path | cut -c10-)
  docker pull $docker_image
  if [[ $version == 'latest' || $version == '' ]]; then
    pid=$(docker run -d $docker_image)
    echo $pid
    ./retry.sh 60 2 "docker exec $pid clickhouse-client -q \"SELECT version()\""
    export version=$(docker exec $pid clickhouse-client -q 'SELECT version()')
    echo "version=$version" >>$GITHUB_ENV
    docker stop $pid
  fi
fi
echo "::endgroup::"

echo "::group::Generate upload paths..."
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
    artifact_s3_dir="PRs/$pr_number/$build_sha/regression"
  else # release, push, workflow_dispatch
    artifact_s3_dir="REFs/$GITHUB_REF_NAME/$build_sha/regression"
  fi

fi

if [[ $args == *'--with-analyzer'* ]]; then
  analyzer="with_analyzer"
else
  analyzer="without_analyzer"
fi

if [ "$enable_thread_fuzzer" == "true" ]; then
  thread_fuzzer="with_thread_fuzzer"
else
  thread_fuzzer="without_thread_fuzzer"
fi

if [[ $args == *'--use-keeper'* ]]; then
  keeper_or_zookeeper="keeper"
else
  keeper_or_zookeeper="zookeeper"
fi


if [[ -z "$S3_ENDPOINT" ]]; then 
  JOB_BUCKET_URL=https://$artifact_s3_bucket_path.s3.amazonaws.com
else
  JOB_BUCKET_URL=https://$S3_ENDPOINT/$artifact_s3_bucket_path
fi

echo "confidential=$confidential" >>$GITHUB_ENV

JOB_REPORT_INDEX=$JOB_BUCKET_URL/index.html#$artifact_s3_dir/
echo "JOB_REPORT_INDEX=$JOB_REPORT_INDEX" >>$GITHUB_ENV

JOB_S3_ROOT=s3://$artifact_s3_bucket_path/$artifact_s3_dir
echo "JOB_S3_ROOT=$JOB_S3_ROOT" >>$GITHUB_ENV

SUITE_REPORT_INDEX_URL=$JOB_REPORT_INDEX$(uname -i)/$analyzer/$keeper_or_zookeeper/$thread_fuzzer/$SUITE$PART$STORAGE/
echo "SUITE_REPORT_INDEX_URL=$SUITE_REPORT_INDEX_URL" >>$GITHUB_ENV

SUITE_LOG_FILE_PREFIX_URL=$JOB_BUCKET_URL/$artifact_s3_dir/$(uname -i)/$analyzer/$keeper_or_zookeeper/$thread_fuzzer/$SUITE$PART$STORAGE
echo "SUITE_LOG_FILE_PREFIX_URL=$SUITE_LOG_FILE_PREFIX_URL" >>$GITHUB_ENV

SUITE_REPORT_BUCKET_PATH=$JOB_S3_ROOT/$(uname -i)/$analyzer/$keeper_or_zookeeper/$thread_fuzzer/$SUITE$PART$STORAGE
echo "SUITE_REPORT_BUCKET_PATH=$SUITE_REPORT_BUCKET_PATH" >>$GITHUB_ENV

echo "::endgroup::"

echo "Browse results at $SUITE_REPORT_INDEX_URL"
