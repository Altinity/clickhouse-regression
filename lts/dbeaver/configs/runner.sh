#!/bin/bash
# Run the DBeaver smoke checks (Smoke.java) through the ClickHouse JDBC driver
# that DBeaver bundles, com.clickhouse:clickhouse-jdbc:$DRIVER_VERSION with
# httpclient5 $HTTPCLIENT_VERSION, against the ClickHouse server in this image.
# JUnit XML is written to /results/junit.xml.
set -xe

: "${DRIVER_VERSION:?}" "${HTTPCLIENT_VERSION:?}"

trap 'chown -R "${HOST_UID:-0}:${HOST_GID:-0}" /results || true' EXIT

# Start the server the way the image does, so that its /etc/clickhouse-server
# configuration is used. A bare `clickhouse server` ignores it and runs with
# the built-in defaults.
/entrypoint.sh > /results/logs/clickhouse-server.log 2>&1 &
for i in $(seq 1 60); do
    clickhouse-client -q "SELECT 1" && break
    sleep 1
done
clickhouse-client -q "SELECT version()"

mkdir -p /drivers /resolve
cat > /resolve/pom.xml <<EOF
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>lts</groupId>
  <artifactId>dbeaver-driver</artifactId>
  <version>1</version>
  <dependencies>
    <dependency>
      <groupId>com.clickhouse</groupId>
      <artifactId>clickhouse-jdbc</artifactId>
      <version>${DRIVER_VERSION}</version>
    </dependency>
    <dependency>
      <groupId>org.apache.httpcomponents.client5</groupId>
      <artifactId>httpclient5</artifactId>
      <version>${HTTPCLIENT_VERSION}</version>
    </dependency>
  </dependencies>
</project>
EOF
mvn -B -q -f /resolve/pom.xml dependency:copy-dependencies -DoutputDirectory=/drivers
ls /drivers

java -cp "/drivers/*" /Smoke.java /results/junit.xml
