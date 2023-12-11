# Running clickhouse-jdbc tests locally

clickhouse-jdbc: `https://github.com/ClickHouse/clickhouse-jdbc`

To run clickhouse-jdbc tests specify clickhouse docker image that you want to test in Dockerfile.

then execute commands:

```bash
docker build . -t clickhouse-jdbc

docker run --rm -e RELEASE=v0.3.2 clickhouse-jdbc
```
Where `clickhouse-jdbc` is the name of created docker image.

Starting clickhouse-jdbc v0.4.0 running in docker not supported becouse of using docker inside the test.
to test version after or equal v0.4.0 use runner_without_docker.sh:

1. Specify clickhouse-jdbc version in runner_without_docker.sh
2. Specify clickhouse version runner_without_docker.sh
3. Run runner_without_docker.sh (sudo ./runner_without_docker.sh)
