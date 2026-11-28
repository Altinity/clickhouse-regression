Unity Catalog built from source at commit `e64816917eca9f3185e47a2b96351b0ad3a82f28`, with writable Iceberg REST mounted at `/iceberg-rest` and static S3 credentials (`minio-static-credentials.patch`). Used by the `iceberg` suite.

The tag is the short Unity Catalog commit. Change `UC_REF` in the Dockerfile and the tag together, and update the digest in `iceberg/iceberg_env*/docker-compose.yml` to the new multi-arch index digest (`docker buildx imagetools inspect altinityinfra/unity-catalog:<tag>`).

docker buildx build --push -t altinityinfra/unity-catalog:e648169 --platform=linux/amd64,linux/arm64 .

The runtime image keeps the build's Coursier cache (`.cache`, about 1.4 GB of the 3.3 GB image). `bin/start-uc-server` runs `java -cp $(cat server/target/classpath)`, and that classpath points at the jars in the cache, so removing it breaks the server.
