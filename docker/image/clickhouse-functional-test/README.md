# Source
Copy `ClickHouse/docker/tests/stateless/Dockerfile` without minio or the run.sh script.
Replace `FROM` with:
```
altinityinfra/clickhouse-regression-multiarch:1.0
```

Copy `ClickHouse/docker/tests/stateful/s3downloader`

To download the stateful datasets include:
```
RUN mkdir -p /var/lib/clickhouse
RUN s3downloader --dataset-names hits visits
```

# Building

This image is for x86_amd, when building please use command:

```
docker buildx create --use
docker buildx build --push --platform linux/amd64 --tag altinityinfra/clickhouse-functional-test:TAG
```
