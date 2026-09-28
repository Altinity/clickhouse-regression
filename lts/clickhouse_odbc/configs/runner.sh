#!/bin/bash
# Run the clickhouse-odbc ctest targets, built into this image, against the
# ClickHouse server in this image. JUnit XML is written to /results/junit.xml.
set -xe

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

cd /clickhouse-odbc/build
ctest -N

set +e
ctest -C RelWithDebInfo --output-on-failure --output-junit /results/junit.xml
rc=$?
cp Testing/Temporary/LastTest.log /results/logs/ctest-detailed.log 2>/dev/null
echo "ctest exited with code $rc"
# ctest exits with 8 when tests fail; anything else means it did not run properly.
exit $rc
