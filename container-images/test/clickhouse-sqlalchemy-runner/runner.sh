#!/bin/bash
set -xe

# install clickhouse, make sure binaries for common and client in /clickhouse folder
# dpkg -i clickhouse/clickhouse-common-static*.deb
# dpkg -i clickhouse/clickhouse-client*.deb

clickhouse server --daemon
sleep 10
clickhouse-client -q "SELECT 1"

apt update

apt install git -y

git clone --branch "${RELEASE}" --depth 1 --single-branch "https://github.com/xzkostyan/clickhouse-sqlalchemy.git"
cd clickhouse-sqlalchemy
# git apply /sqlalchemy.patch
git apply /diff_0_2_9.patch

apt install python3-pip -y

pip install --upgrade pip
pip install "asynch==0.2.5" "alembic==1.11.1" "pytest-asyncio"
python3 testsrequire.py && python3 setup.py develop
pytest -v
