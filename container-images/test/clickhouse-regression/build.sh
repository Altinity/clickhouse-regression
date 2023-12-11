#!/bin/bash
set -e
echo "Pre-pull images for docker-compose"
docker pull library/hello-world
docker pull zookeeper:3.7.0
docker pull zookeeper:3.6.2
docker pull zookeeper:3.4.12
docker pull clickhouse/clickhouse-integration-test:28741
docker pull osixia/openldap:1.4.0
docker pull osixia/phpldapadmin:0.9.0
docker pull mysql:5.7.30
docker pull confluentinc/cp-kafka:5.2.0
docker pull yandex/clickhouse-s3-proxy:21495
docker pull yandex/clickhouse-python-bottle:21495
docker pull minio/minio:RELEASE.2022-04-09T15-09-52Z
docker pull minio/mc:RELEASE.2022-05-09T04-08-26Z
echo "Save images"
docker save library/hello-world -o hello-world.dockerimage
docker save zookeeper:3.7.0 -o zookeeper.3.7.0.dockerimage
docker save zookeeper:3.6.2 -o zookeeper.3.6.2.dockerimage
docker save zookeeper:3.4.12 -o zookeeper.3.4.12.dockerimage
docker save clickhouse/clickhouse-integration-test:28741 -o clickhouse-integration-test.28741.dockerimage
docker save osixia/phpldapadmin:0.9.0 -o phpldapadmin.0.9.0.dockerimage
docker save osixia/openldap:1.4.0 -o openldap.1.4.0.dockerimage
docker save mysql:5.7.30 -o mysql.5.7.30.dockerimage
docker save confluentinc/cp-kafka:5.2.0 -o cp-kafka.5.2.0.dockerimage
docker save yandex/clickhouse-s3-proxy:21495 -o clickhouse-s3-proxy.21495.dockerimage
docker save yandex/clickhouse-python-bottle:21495 -o clickhouse-python-bottle.21495.dockerimage
docker save minio/minio:RELEASE.2022-04-09T15-09-52Z -o minio.RELEASE.2022-04-09T15-09-52Z.dockerimage
docker save minio/mc:RELEASE.2022-05-09T04-08-26Z -o mc:RELEASE.2022-05-09T04-08-26Z.dockerimage
echo "Build image"
docker build -t registry.gitlab.com/altinity-qa/clickhouse/cicd/regression/image .
