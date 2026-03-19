#!/bin/bash
set -ueo pipefail
export SUPERSET_VERSION=${SUPERSET_VERSION:-4.1.1}
export CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest
export CLICKHOUSE_VERSION=25.8.16.10001
export DOCKER_COMPOSE_FILE=./superset/docker-compose-non-dev.yml
export CLICKHOUSE_PYTHON_DRIVER=${CLICKHOUSE_PYTHON_DRIVER:-clickhouse-connect}
if [[ ! -d superset ]]; then
  git clone --depth 1 --branch ${SUPERSET_VERSION} https://github.com/apache/superset.git
else
  cd superset
  git fetch origin
#  git checkout ${SUPERSET_VERSION}
  cd ../
fi
cp -fv ./Dockerfile.${CLICKHOUSE_PYTHON_DRIVER} ./superset/Dockerfile
mkdir -p ./superset/clickhouse/
cp -fv *.xml ./superset/clickhouse/
cp -fv server.* ./superset/clickhouse/
cp -fv *.pem ./superset/clickhouse/

# you need install latest version of https://mikefarah.gitbook.io/yq/
# Convert env_file from object syntax (path/required) to simple string format for older docker-compose compatibility
yq -i eval '(.services[] | select(has("env_file")) | .env_file) = ["docker/.env"]' ${DOCKER_COMPOSE_FILE}
yq -i eval '.services.superset.build.context = "./"' ${DOCKER_COMPOSE_FILE}
yq -i eval '.services.superset.build.dockerfile = "Dockerfile"' ${DOCKER_COMPOSE_FILE}
yq -i eval '.services.superset-init.build.dockerfile = "Dockerfile"' ${DOCKER_COMPOSE_FILE}
yq -i eval '.services.clickhouse.image = "altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest"' ${DOCKER_COMPOSE_FILE}
yq -i eval '.services.clickhouse.ports = ["8123:8123","9000:9000","8443:8443","9440:9440"]' ${DOCKER_COMPOSE_FILE}
yq -i eval '.services.clickhouse.volumes = ["./clickhouse/config.xml:/etc/clickhouse-server/config.d/config.xml","./clickhouse/default_user.xml:/etc/clickhouse-server/users.d/default_user.xml"]' ${DOCKER_COMPOSE_FILE}
yq -i eval '.services.clickhouse.volumes += ["./clickhouse/dhparam.pem:/etc/clickhouse-server/dhparam.pem","./clickhouse/server.key:/etc/clickhouse-server/server.key","./clickhouse/server.crt:/etc/clickhouse-server/server.crt"]' ${DOCKER_COMPOSE_FILE}

docker compose -f ${DOCKER_COMPOSE_FILE} build superset superset-init
docker compose -f ${DOCKER_COMPOSE_FILE} run --rm superset-init
docker compose -f ${DOCKER_COMPOSE_FILE} up -d clickhouse superset superset-worker
