# Running clickhouse-driver tests locally

clickhouse-driver: `https://github.com/mymarilyn/clickhouse-driver`

To run clickhouse-driver tests specify clickhouse docker image that you want to test in Dockerfile.

then execute commands:

```bash
docker build . -t clickhouse-driver

docker run --rm -e RELEASE=0.2.6 clickhouse-driver
```

Where `clickhouse-driver` is the name of created docker image.

Link to the instruction how to run tests on local machine `https://clickhouse-driver.readthedocs.io/en/latest/development.html`

Patches are needed to make tests work with latest clickhouse versions.

Lin to the github issue about failing test: `https://github.com/mymarilyn/clickhouse-driver/issues/403`

