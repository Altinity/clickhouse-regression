#!/bin/bash
set -xe

# Go to your cloned repository
# git clone --recursive "https://github.com/ClickHouse/clickhouse-jdbc"
cd clickhouse-jdbc
# git checkout v0.9.0

Ensure dependencies
apt update
apt install -y maven openjdk-17-jdk

# for mac os
# brew update
# brew install maven openjdk@17

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 1. Build dependencies with tests skipped
# 2. Then run only clickhouse-jdbc tests
mvn -Dj8 clean install -DskipTests -am

# Now, run tests ONLY in clickhouse-jdbc
mvn -Dj8 verify -pl clickhouse-jdbc