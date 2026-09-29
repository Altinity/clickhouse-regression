#!/bin/bash
# Run the clickhouse-sqlalchemy test suite at tag $RELEASE against the
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

git clone --branch "${RELEASE}" --depth 1 --single-branch "https://github.com/xzkostyan/clickhouse-sqlalchemy.git"
cd clickhouse-sqlalchemy

# patches/<release>.series lists the patches to apply, in order. A release
# without its own series uses the series of its minor line (0.3.2 -> 0.3).
series="/patches/${RELEASE}.series"
[ -f "$series" ] || series="/patches/${RELEASE%.*}.series"
if [ -f "$series" ]; then
    while read -r patch; do
        [ -n "$patch" ] && git apply "/patches/$patch"
    done < "$series"
else
    echo "WARNING: no patch series for ${RELEASE}, running the tests unpatched"
fi

pip3 install --upgrade pip
# asynch 0.2.5 and alembic 1.11.1 are the versions the patched tests work with.
pip3 install "asynch==0.2.5" "alembic==1.11.1" "pytest-asyncio==1.4.0"
python3 testsrequire.py && python3 setup.py develop

set +e
python3 -m pytest -v --junitxml=/results/junit.xml -o junit_family=xunit2
rc=$?
echo "pytest exited with code $rc"
exit $rc
