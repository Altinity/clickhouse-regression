# Running clickhouse-odbc tests locally

clickhouse-odbc: `https://github.com/ClickHouse/clickhouse-odbc`

To run clickhouse-odbc tests manually you need `clickhouse-common.deb` and the `clickhouse-client.deb` in your machine.

Then execute command
```bash
docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=v1.2.1.20220905 registry.gitlab.com/altinity-public/container-images/test/clickhouse-odbc-runner:v1.0
```
Where `$(pwd)/PACKAGES` is the folder to the clickhouse*.deb packages and `RELEASE=v1.2.1.20220905` is the clickhouse-odbc version you want to test.
Test log you need is $(pwd)/PACKAGES/test.log

Make sure you have access to gitlab registry, if you don't then build the image manually with file in `https://gitlab.com/altinity-public/container-images/-/tree/main/test/clickhouse-odbc-runner` and change the previous command with
```bash
docker build . -t clickhouse-odbc

docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=v1.2.1.20220905 clickhouse-odbc
```
Where `clickhouse-odbc` is the name of created docker image.

Patches are needed to make tests work with clickhouse 22.3-lts.

Script `runner.sh` is run in the container.
This script runs:
1. Instalation clickhouse deb packages
2. Instalation clang-12
3. Instalation cmake
4. Building clickhouse-odbc
5. Testing clickhouse-odbc

So it may take a long time.

