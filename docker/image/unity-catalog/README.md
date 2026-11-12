Unity Catalog built from source at commit `e64816917eca9f3185e47a2b96351b0ad3a82f28`, with writable Iceberg REST mounted at `/iceberg-rest` and static S3 credentials (`minio-static-credentials.patch`). Used by the `iceberg` suite.

The tag is the short Unity Catalog commit. Change `UC_REF` in the Dockerfile and the tag together.

docker buildx build --push -t altinityinfra/unity-catalog:e648169 --platform=linux/amd64,linux/arm64 .
