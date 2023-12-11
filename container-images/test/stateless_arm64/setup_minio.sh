#!/bin/bash

# Usage for local run:
#
# ./docker/test/stateless/setup_minio.sh ./tests/
#

set -e -x -a -u

ls -lha

mkdir -p ./minio_data

if [ ! -f ./minio ]; then
  echo 'MinIO binary not found, downloading...'

  BINARY_TYPE=$(uname -s | tr '[:upper:]' '[:lower:]')

  wget "https://dl.min.io/server/minio/release/${BINARY_TYPE}-arm64/minio" \
    && chmod +x ./minio \
    && wget "https://dl.min.io/client/mc/release/${BINARY_TYPE}-arm64/mc" \
    && chmod +x ./mc
fi

MINIO_ROOT_USER=${MINIO_ROOT_USER:-clickhouse}
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-clickhouse}

./minio server --address ":11111" ./minio_data &

while ! curl -v --silent http://localhost:11111 2>&1 | grep AccessDenied
do
  echo "Trying to connect to minio"
  sleep 1
done

lsof -i :11111

sleep 5

./mc alias set clickminio http://localhost:11111 clickhouse clickhouse > /dev/null 2>&1 # This output freezes testflows wrapper utils
./mc admin user add clickminio test testtest > /dev/null 2>&1 # This output freezes testflows wrapper utils
./mc admin policy set clickminio readwrite user=test > /dev/null 2>&1 # This output freezes testflows wrapper utils
./mc mb clickminio/test > /dev/null 2>&1 # This output freezes testflows wrapper utils


# Upload data to Minio. By default after unpacking all tests will in
# /usr/share/clickhouse-test/queries

TEST_PATH=${1:-/usr/share/clickhouse-test}
MINIO_DATA_PATH=${TEST_PATH}/queries/0_stateless/data_minio

# Iterating over globs will cause redudant FILE variale to be a path to a file, not a filename
# shellcheck disable=SC2045
for FILE in $(ls "${MINIO_DATA_PATH}"); do
    echo "$FILE";
    ./mc cp "${MINIO_DATA_PATH}"/"$FILE" clickminio/test/"$FILE" > /dev/null 2>&1 # This output freezes testflows wrapper utils;
done
