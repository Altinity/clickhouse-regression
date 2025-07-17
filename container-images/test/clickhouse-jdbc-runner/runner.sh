#!/bin/bash
set -xe

# install clickhouse, make sure binaries for common and client in /clickhouse folder
dpkg -i clickhouse/clickhouse-common-static*.deb
dpkg -i clickhouse/clickhouse-client*.deb

# run clickhouse
clickhouse server --daemon
sleep 10
clickhouse-client -q "SELECT 1"

apt update -y

apt-get install -y git 

#install clickhouse-jdbc
git clone --recursive "https://github.com/ClickHouse/clickhouse-jdbc"
cd clickhouse-jdbc
git checkout "${RELEASE}"

apt install -y maven
apt install -y openjdk-8-jdk

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre

mvn -Dj8 -DskipITs -DclickhouseVersion=23.3 clean verify > /clickhouse/test.log
