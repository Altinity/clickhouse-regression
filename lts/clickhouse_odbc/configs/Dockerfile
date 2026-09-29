ARG CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest

# Build the driver on the same base as the ClickHouse image (Ubuntu 22.04), but
# in a stage that does not depend on the ClickHouse image, so the build is
# cached across ClickHouse releases and only redone for a new ODBC_RELEASE.
FROM ubuntu:22.04 AS build

ARG ODBC_RELEASE=v1.2.1.20220905

# test/CMakeLists.txt registers the pyodbc (test.py, parametrized), Perl
# (test.pl) and isql/iusql tests only if it finds these tools when configuring.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates git clang-12 cmake make build-essential libssl-dev \
        libpoco-dev libicu-dev unixodbc-dev unixodbc odbcinst \
        python3 python3-pip python3-dev perl libdbd-odbc-perl \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pyodbc

# GitHub refuses git protocol v2 from Ubuntu 22.04's git 2.34 ("could not
# read Username for 'https://github.com'") and serves protocol v0.
RUN git config --system protocol.version 0

COPY diff.patch /diff.patch

# The clone and the many nested submodule clones are retried, as a single
# failed request fails the whole build.
RUN retry() { for attempt in 1 2 3 4 5; do "$@" && return 0; sleep 30; done; return 1; } \
    && retry sh -c "rm -rf /clickhouse-odbc && git clone https://github.com/ClickHouse/clickhouse-odbc /clickhouse-odbc" \
    && cd /clickhouse-odbc \
    && git checkout "${ODBC_RELEASE}" \
    && retry git submodule update --init --recursive \
    && git apply /diff.patch \
    # Fix the relative include in FindUnixODBC.cmake, which breaks when
    # nanodbc's CMakeLists.txt calls find_package(ODBC) from a subdirectory.
    && sed -i 's|include(cmake/extract_flags.cmake)|include(${CMAKE_CURRENT_LIST_DIR}/../extract_flags.cmake)|' \
        cmake/Modules/FindUnixODBC.cmake

RUN mkdir /clickhouse-odbc/build \
    && cd /clickhouse-odbc/build \
    && CC=clang-12 CXX=clang++-12 cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo .. \
    && cmake --build . --config RelWithDebInfo -j "$(nproc)"


FROM ${CLICKHOUSE_IMAGE}

# Runtime: the unixODBC driver manager and its isql/iusql tools, the libraries
# the driver links against, ctest, and pyodbc/testflows for the Python tests.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        cmake unixodbc odbcinst unixodbc-dev libpoco-dev libicu-dev libssl-dev \
        python3 python3-pip python3-dev build-essential perl libdbd-odbc-perl \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pyodbc testflows

# ctest runs from the build tree and the tests use paths in the source tree, so
# both are copied to the same location as in the build stage.
COPY --from=build /clickhouse-odbc /clickhouse-odbc

RUN mkdir -p /usr/local/lib64 \
    && cp /clickhouse-odbc/build/driver/libclickhouseodbc.so /clickhouse-odbc/build/driver/libclickhouseodbcw.so /usr/local/lib64/ \
    && odbcinst -i -d -f /clickhouse-odbc/packaging/odbcinst.ini.sample \
    && odbcinst -i -s -l -f /clickhouse-odbc/packaging/odbc.ini.sample

COPY runner.sh /runner.sh

ENTRYPOINT ["/bin/bash", "/runner.sh"]
