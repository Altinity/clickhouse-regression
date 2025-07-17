# Running clickhouse-odbc tests locally

clickhouse-odbc: `https://github.com/ClickHouse/clickhouse-odbc`

If you have docker image for test:
    To run clickhouse-odbc tests specify clickhouse docker image that you want to test in Dockerfile.
    
If you don't have docker image for tests:
    Create PACKAGE directory in clickhouse-odbc-runner directory, and add deb packages into it.
    Add `dpkg -i clickhouse/clickhouse-common-static*.deb`
        `dpkg -i clickhouse/clickhouse-client*.deb` into runner.sh
        
Also you need to specify driver version in this commands.
You always need to specify `-v $(pwd)/PACKAGES:/clickhouse` since it saves logs into this directory.

```bash
docker build . -t clickhouse-odbc

docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=v1.2.1.20220905 clickhouse-odbc
```

Where `clickhouse-odbc` is the name of created docker image.


Test log you need is $(pwd)/PACKAGES/test.log

Patches are needed to make tests work with clickhouse 22.3-lts.

Script `runner.sh` is run in the container.
This script runs:
1. Instalation clickhouse deb packages
2. Instalation clang-12
3. Instalation cmake
4. Building clickhouse-odbc
5. Testing clickhouse-odbc

So it may take a long time.

