# Building

This image is used in both x86_amd and arrch64, when building please use command:


```
docker buildx create --use
docker buildx build --push --platform linux/arm64/v8,linux/amd64 --tag registry.gitlab.com/altinity-public/container-images/test/clickhouse-integration-test:TAG
```
