# Running clickhouse-odbc tests locally

clickhouse-odbc: `https://github.com/ClickHouse/clickhouse-odbc`

To run clickhouse-sqlalchemy tests specify clickhouse docker image that you want to test in Dockerfile.

then execute commands:

```bash
docker build . -t clickhouse-odbc

docker run --rm -e RELEASE=v1.2.1.20220905 clickhouse-odbc
```

Patches are needed to make tests work with latest clickhouse versions.

Script `runner.sh` is run in the container.
This script runs:
1. Instalation clickhouse deb packages
2. Instalation clang-12
3. Instalation cmake
4. Building clickhouse-odbc
5. Testing clickhouse-odbc

So it may take a long time.
