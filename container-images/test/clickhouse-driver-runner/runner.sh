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
git clone --branch "${RELEASE}" --depth 1 --single-branch "https://github.com/mymarilyn/clickhouse-driver.git"
cd clickhouse-driver

# if [ ${RELEASE} == 0.2.3 ]
# then
# git apply /diff-0.2.3.patch
# fi
# git apply /clickhouse-driver.patch

apt install python3-pip -y
python3 testsrequire.py && python3 setup.py develop

pip3 install cython lz4

py.test -v
