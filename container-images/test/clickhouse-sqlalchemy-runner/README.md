# Running clickhouse-sqlalchemy tests locally

clickhouse-sqlalchemy: `https://github.com/xzkostyan/clickhouse-sqlalchemy/`

If you have docker image for test:
    To run clickhouse-sqlalchecmy tests specify clickhouse docker image that you want to test in Dockerfile.
    Also you need to specify driver version in this commands.
    Then execute commands:

```bash
docker build . -t sqlalchemy

docker run --rm -e RELEASE=0.3.0 sqlalchemy
```

If you don't have docker image for tests:
    Create PACKAGE directory in clickhouse-sqlalchemy-runner directory, and add deb packages into it.
    Add `dpkg -i clickhouse/clickhouse-common-static*.deb`
        `dpkg -i clickhouse/clickhouse-client*.deb` into runner.sh
    Also you need to specify driver version in this commands.
    Then execute commands:


```bash
docker build . -t sqlalchemy

docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=0.3.0 sqlalchemy
```

Patch is needed to change clickhouse version check in tests.

