# Change log
2.0: Added pandas
3.0: Added parquet-tools. ONLY FOR AMD64
4.0: Added flask. ONLY FOR AMD64

# Building

This image is used in both x86_amd and arrch64, when building please use command:


```
docker buildx create --use
docker buildx build --push --platform linux/arm64/v8,linux/amd64 --tag registry.gitlab.com/altinity-public/container-images/test/clickhouse-intergration-test-pyarrow:TAG
```
