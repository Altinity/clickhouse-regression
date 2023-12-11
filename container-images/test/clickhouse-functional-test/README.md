# Source
Copy from ClickHouse/docker/tests/stateless/Dockerfile without minio or the run.sh script.
Replace `FROM` with:
```
FROM registry.gitlab.com/altinity-public/container-images/test/clickhouse-integration-test:21.12
```

Copy s3downloader from ClickHouse/docker/tests/stateful/s3downloader

Include the following to download the stateful datasets
```
RUN mkdir -p /var/lib/clickhouse
RUN s3downloader --dataset-names hits visits
```

# Building

This image is for x86_amd, when building please use command:

```
docker buildx create --use
docker buildx build --push --platform linux/amd64 --tag registry.gitlab.com/altinity-public/container-images/test/clickhouse-functional-test:TAG
```
