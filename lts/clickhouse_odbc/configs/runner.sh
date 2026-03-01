#!/bin/bash
set -xe

# install clickhouse, make sure binaries for common and client in /clickhouse folder
# dpkg -i clickhouse/clickhouse-common-static*.deb
# dpkg -i clickhouse/clickhouse-client*.deb

clickhouse server --daemon
sleep 10
clickhouse-client -q "SELECT 1"

apt update -y

# install clang
apt install clang-12 -y
export CC=clang-12
export CXX=clang++-12

# install dependencies for cmake
apt install wget -y
apt install tar -y
apt update -y
apt install build-essential libssl-dev -y

# install cmake
apt update -y
wget https://github.com/Kitware/CMake/releases/download/v3.22.1/cmake-3.22.1.tar.gz
tar -zxvf cmake-3.22.1.tar.gz
cd cmake-3.22.1
./bootstrap
make
make install
cd /

# install dependencies for clickhouse-odbc
apt-get install -y git libpoco-dev libicu-dev unixodbc-dev
apt update -y

#install clickhouse-odbc
git clone "https://github.com/ClickHouse/clickhouse-odbc"
cd clickhouse-odbc
git checkout "${RELEASE}"
git submodule update --init --recursive
git apply /diff.patch

apt install odbcinst -y
apt-get install python3-pip -y
apt install unixodbc-dev -y
pip install pyodbc
pip install testflows
apt update -y

# configurating odbc
odbcinst -i -d -f /clickhouse-odbc/packaging/odbcinst.ini.sample
odbcinst -i -s -l -f /clickhouse-odbc/packaging/odbc.ini.sample

# Fix relative include path in FindUnixODBC.cmake so it resolves correctly
# when nanodbc's CMakeLists.txt triggers find_package(ODBC) from a subdirectory
sed -i 's|include(cmake/extract_flags.cmake)|include(${CMAKE_CURRENT_LIST_DIR}/../extract_flags.cmake)|' cmake/Modules/FindUnixODBC.cmake

mkdir build
cd build

# building clickhouse-odbc
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo ..
cmake --build . --config RelWithDebInfo
mkdir /usr/local/lib64
cp driver/libclickhouseodbcw.so /usr/local/lib64/libclickhouseodbcw.so
cp driver/libclickhouseodbc.so /usr/local/lib64/libclickhouseodbc.so

# testing clickhouse-odbc
ctest -C RelWithDebInfo -E "(nano|test\.py|parametrized)" --output-on-failure 2>&1 | tee /clickhouse/test.log
cp Testing/Temporary/LastTest.log /clickhouse/test_detailed.log 2>/dev/null || true
