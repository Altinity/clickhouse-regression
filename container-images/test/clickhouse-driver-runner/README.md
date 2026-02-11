# Running clickhouse-driver tests locally

clickhouse-driver: `https://github.com/mymarilyn/clickhouse-driver`

If you have docker image for test (get it from https://hub.docker.com/r/altinityinfra/clickhouse-server/tags):
    To run clickhouse-driver tests specify clickhouse docker image that you want to test in Dockerfile.
    Also you need to specify driver version in this commands.
    Then execute commands:

```bash
docker build . -t clickhouse-driver

docker run --rm -e RELEASE=0.2.10 clickhouse-driver
```

If you don't have docker image for tests:
    Create PACKAGE directory in clickhouse-driver-runner directory, and add deb packages into it.
    Add `dpkg -i clickhouse/clickhouse-common-static*.deb`
        `dpkg -i clickhouse/clickhouse-client*.deb` into runner.sh
    Also you need to specify driver version in this commands.
    Then execute commands:

```bash
docker build . -t clickhouse-driver

docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=0.2.9 clickhouse-driver
```

Link to the instruction how to run tests on local machine `https://clickhouse-driver.readthedocs.io/en/latest/development.html`

Patches are needed to make tests work with latest clickhouse versions.

Link to the github issue about failing test: `https://github.com/mymarilyn/clickhouse-driver/issues/403`

