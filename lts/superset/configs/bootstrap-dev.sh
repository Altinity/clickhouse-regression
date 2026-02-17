#!/bin/bash
export SUPERSET_VERSION=${SUPERSET_VERSION:-4.0.2}
export CLICKHOUSE_PYTHON_DRIVER=${CLICKHOUSE_PYTHON_DRIVER:-clickhouse-connect}

if [[ ! -d superset ]]; then
  git clone --depth 1 --branch ${SUPERSET_VERSION} https://github.com/apache/superset.git
else
  cd superset
  git fetch origin
  git checkout ${SUPERSET_VERSION}
fi
if [[ "clickhouse-sqlalchemy" == "${CLICKHOUSE_PYTHON_DRIVER}" ]]; then
  echo "clickhouse-sqlalchemy<0.2.0" > ./docker/requirements-local.txt
else
  echo "clickhouse-connect" > ./docker/requirements-local.txt
fi
for id in $(docker ps -a -q); do docker stop $id; docker rm -f $id; done
docker-compose down --remove-orphan
docker-compose up -d db
docker-compose run superset-init
docker-compose up -d superset-node
docker-compose up -d superset-worker-beat
docker-compose up -d superset-worker
docker-compose up -d superset
docker run -d --name=clickhouse --network=superset_default ${CLICKHOUSE_IMAGE:-clickouse}/clickhouse-server:${CLICKHOUSE_VERSION:-latest}
cd ../
