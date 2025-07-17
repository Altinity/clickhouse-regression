#!/bin/bash
set -xe

#install clickhouse-jdbc
git clone --recursive "https://github.com/ClickHouse/clickhouse-jdbc"
cd clickhouse-jdbc
git checkout v0.4.6 #specify clickhouse-jdbc version

apt install -y maven
apt install -y openjdk-8-jdk

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre

mvn -Dj8 -DskipITs -DclickhouseVersion=23.3 clean verify > ../test.log #specify clickhouse version
