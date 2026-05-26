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

artifacts="${artifacts:-hetzner}"

# Build HETZNER_S3_URI only when Hetzner is selected for reports or when this is
# an explicit hetzner suite job (e.g. s3_hetzner, tiered_storage_hetzner).
if [[ "$artifacts" == "hetzner" || "${GITHUB_JOB:-}" == *"hetzner"* ]]; then
  : "${HETZNER_S3_BUCKET:?HETZNER_S3_BUCKET must be set when Hetzner is used}"
  : "${HETZNER_S3_REGION:?HETZNER_S3_REGION must be set when Hetzner is used}"
  echo "HETZNER_S3_URI=https://${HETZNER_S3_REGION}.your-objectstorage.com/${HETZNER_S3_BUCKET}/" >>"$GITHUB_ENV"
fi

# For hetzner: override AWS_* credentials (workflow defaults them from AWS_REPORT_*)
# and set the Hetzner endpoint. AWS branch is a no-op.
# Secret values reach this script only via ${{ secrets.HETZNER_S3_* }}, so
# GitHub Actions auto-masks them; we still disable tracing for credential writes.
if [[ "$artifacts" == "hetzner" ]]; then
  : "${HETZNER_S3_BUCKET:?HETZNER_S3_BUCKET must be set when artifacts=hetzner}"
  : "${HETZNER_S3_REGION:?HETZNER_S3_REGION must be set when artifacts=hetzner (Hetzner location: fsn1, nbg1, hel1, ...)}"
  : "${HETZNER_S3_KEY_ID:?HETZNER_S3_KEY_ID must be set when artifacts=hetzner}"
  : "${HETZNER_S3_ACCESS_KEY:?HETZNER_S3_ACCESS_KEY must be set when artifacts=hetzner}"

  hetzner_endpoint="https://${HETZNER_S3_REGION}.your-objectstorage.com"
  export REPORT_S3_PUBLIC_ENDPOINT_URL="$hetzner_endpoint"
  export S3_CLI_ENDPOINT_URL="$hetzner_endpoint"

  { set +x; } 2>/dev/null
  {
    echo "AWS_ACCESS_KEY_ID=$HETZNER_S3_KEY_ID"
    echo "AWS_SECRET_ACCESS_KEY=$HETZNER_S3_ACCESS_KEY"
    echo "AWS_DEFAULT_REGION=$HETZNER_S3_REGION"
  } >>"$GITHUB_ENV"
  set -x
fi

# Bucket layout: hetzner reuses HETZNER_S3_BUCKET; AWS values use legacy buckets.
case "$artifacts" in
  hetzner)
    artifact_s3_bucket_path="$HETZNER_S3_BUCKET"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential="--confidential"
    ;;
  internal)
    artifact_s3_bucket_path="altinity-internal-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential="--confidential"
    ;;
  public)
    artifact_s3_bucket_path="altinity-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential=""
    ;;
  builds)
    artifact_s3_bucket_path="altinity-build-artifacts"
    confidential=""
    if [[ $event_name == "pull_request" ]]; then
      artifact_s3_dir="PRs/$pr_number/$build_sha/regression"
    else
      artifact_s3_dir="REFs/$GITHUB_REF_NAME/$build_sha/regression"
    fi
    ;;
  *)
    echo "::error::Unknown artifacts='$artifacts'"
    exit 1
    ;;
esac

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


report_public_endpoint_url="${REPORT_S3_PUBLIC_ENDPOINT_URL:-${S3_PUBLIC_ENDPOINT_URL:-}}"
report_endpoint="${REPORT_S3_ENDPOINT:-${S3_ENDPOINT:-}}"
report_cli_endpoint_url="${S3_CLI_ENDPOINT_URL:-${REPORT_S3_CLI_ENDPOINT_URL:-${AWS_ENDPOINT_URL_S3:-${AWS_ENDPOINT_URL:-}}}}"

report_public_endpoint_url="${report_public_endpoint_url%/}"
report_endpoint="${report_endpoint%/}"
report_cli_endpoint_url="${report_cli_endpoint_url%/}"

if [[ -n "$report_public_endpoint_url" ]]; then
  JOB_BUCKET_URL=$report_public_endpoint_url/$artifact_s3_bucket_path
elif [[ -n "$report_endpoint" ]]; then
  if [[ "$report_endpoint" == http://* || "$report_endpoint" == https://* ]]; then
    JOB_BUCKET_URL=$report_endpoint/$artifact_s3_bucket_path
  else
    JOB_BUCKET_URL=https://$report_endpoint/$artifact_s3_bucket_path
  fi
else
  JOB_BUCKET_URL=https://$artifact_s3_bucket_path.s3.amazonaws.com
fi

if [[ -n "$report_cli_endpoint_url" ]]; then
  echo "S3_CLI_ENDPOINT_URL=$report_cli_endpoint_url" >>$GITHUB_ENV
  echo "AWS_ENDPOINT_URL_S3=$report_cli_endpoint_url" >>$GITHUB_ENV
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
