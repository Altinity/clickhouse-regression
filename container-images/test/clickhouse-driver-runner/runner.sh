#!/bin/bash
set -xe

# install clickhouse, make sure binaries for common and client in /clickhouse folder
# dpkg -i clickhouse/clickhouse-common-static*.deb
# dpkg -i clickhouse/clickhouse-client*.deb

export TZ=Europe/Moscow
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

clickhouse server --daemon
sleep 10
clickhouse-client -q "SELECT 1"

apt update

apt install git -y
git clone --branch "${RELEASE}" --depth 1 --single-branch "https://github.com/mymarilyn/clickhouse-driver.git"
cd clickhouse-driver

if [ ${RELEASE} == 0.2.3 ]
then
git apply /diff-0.2.3.patch
fi
if [ ${RELEASE} == 0.2.9 ] || [ ${RELEASE} == 0.2.10 ]
then  
git apply /diff-0.2.9.patch
git apply /diff-0.2.9-totals.patch
git apply /diff-0.2.9-cert.patch
git apply /diff-0.2.9-progress.patch
fi

if [ ${RELEASE} == 0.2.9 ]
git apply /diff-0.2.9-json.patch
fi


apt install python3-pip -y
python3 testsrequire.py && python3 setup.py develop

pip3 install cython lz4

py.test -v
