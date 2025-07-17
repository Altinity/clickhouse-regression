# Running clickhouse-sqlalchemy tests locally

clickhouse-sqlalchemy: `https://github.com/xzkostyan/clickhouse-sqlalchemy/`

To run clickhouse-sqlalchemy tests specify clickhouse docker image that you want to test in Dockerfile.

then execute commands:

```bash
docker build . -t sqlalchemy

docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=0.3.0 sqlalchemy
```

Patch is needed to change clickhouse version check in tests.

