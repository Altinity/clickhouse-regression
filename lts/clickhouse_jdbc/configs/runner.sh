#!/bin/bash
# Run the clickhouse-jdbc module tests of clickhouse-java at tag $RELEASE.
#
# The tests start ClickHouse from $CLICKHOUSE_IMAGE themselves with
# Testcontainers, through the host Docker socket. Testcontainers bind-mounts
# test resources and java.io.tmpdir into that container, and the host daemon
# resolves those paths, so everything lives in $WORK_DIR, which is mounted at
# the same path on the host and in this container.
#
# Surefire (unit) and failsafe (integration) JUnit XML is copied to
# /results/reports.
set -xe

: "${RELEASE:?}" "${CLICKHOUSE_IMAGE:?}" "${WORK_DIR:?}"

src="$WORK_DIR/clickhouse-java"

finish() {
    mkdir -p /results/reports
    for kind in surefire failsafe; do
        for report in "$src"/clickhouse-jdbc/target/"$kind"-reports/TEST-*.xml; do
            [ -f "$report" ] && cp "$report" "/results/reports/$kind-$(basename "$report")"
        done
    done
    rm -rf "$src"
    chown -R "${HOST_UID:-0}:${HOST_GID:-0}" /results "$WORK_DIR" || true
}
trap finish EXIT

# Testcontainers defaults to Docker API 1.32, which Docker Engine 29 and later
# reject, so use the API version of the host daemon.
if [ -n "${DOCKER_API_VERSION:-}" ]; then
    echo "api.version=${DOCKER_API_VERSION}" > ~/.docker-java.properties
fi

mkdir -p "$WORK_DIR/tmp"
export JAVA_TOOL_OPTIONS="-Djava.io.tmpdir=$WORK_DIR/tmp"

git clone --branch "$RELEASE" --depth 1 --recursive https://github.com/ClickHouse/clickhouse-java.git "$src"
cd "$src"

mvn -B -Dj8 install -DskipTests -pl clickhouse-jdbc -am

set +e
# JDBC_MAVEN_ARGS is left unquoted on purpose so it can carry several options,
# for example -Dtest=... -Dit.test=... to run a single class.
mvn -B -Dj8 verify -pl clickhouse-jdbc \
    -DclickhouseImage="$CLICKHOUSE_IMAGE" \
    -Dmaven.test.failure.ignore=true \
    ${JDBC_MAVEN_ARGS}
rc=$?
# Test failures are ignored above, so a non-zero exit means Maven itself
# failed, for example a crashed test JVM.
echo "mvn exited with code $rc"
exit $rc
