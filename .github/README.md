## GitHub Actions

Overview of Actions available and how to run and maintain them.

## Regression

### Run CI/CD regression tests 
To run GitHub actions, navigate to `Actions`, select `Run CI/CD regression tests`. Inside `Run workflow` dropdown menu specify the package, version, suite and upload destination of artifacts.

Package: `docker://` or `https://` package specifier to use for tests. For example: 
* docker://altinity/clickhouse-server
* docker://clickhouse/clickhouse-server
* https://s3.amazonaws.com/altinity-build-artifacts/217/acf34c9fc6932aaf9af69425612070b50529f484/package_release/clickhouse-client_22.8.11.17.altinitystable_amd64.deb
 
Version: Version of clickhouse to use for tests. The test verifies that node version matches specified version. When package option uses `docker://` specifier then the version is the image tag. For example:
 * 22.3.9.19-alpine
 * 22.3.8.40.altinitystable
 * latest
 
Suite: Which suite to run. Default runs all suites.
 
Artifacts: Specify whether to upload to internal or public s3 bucket. 'altinity-internal-test-reports' for internal upload, 'altinity-test-reports' for public.

### Regression docker images

Table of which suites rely on what docker images.

| Suite | Utilized image(s) |
| ------| ----------------- |
| aes_encryption | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| mysql:5.7.30 |
|| zookeeper:3.6.2 |
| aggregate_functions | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| atomic_insert | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| base_58 | clickhouse/clickhouse-integration-test:28741 |
|| zookeeper:3.6.2 |
| clickhouse/functional | registry.gitlab.com/altinity-public/container-images/test/clickhouse-functional-test:1.0 |
|| bitnami/zookeeper:3.7.1-debian-11-r90 |
| clickhouse_keeper | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.7.0 |
|| zookeeper:3.4.12 |
| datetime64_extended_range | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| disk_level_encryption | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| dns | altinityinfra/clickhouse-regression-multiarch:1.0 |
| engines | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| example | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| extended_precision_data_types | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| mysql:5.7.30 |
| kafka | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| confluentinc/cp-kafka:5.2.0 |
|| zookeeper:3.4.12 |
| kerberos | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| registry.gitlab.com/altinity-public/container-images/docker-krb5-server:2.0 |
|| zookeeper:3.6.2 |
| key_value | clickhouse/clickhouse-integration-test:28741 |
|| zookeeper:3.6.2 |
| ldap | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| osixia/openldap:1.4.0 |
|| zookeeper:3.6.2 |
| lightweight_delete | registry.gitlab.com/altinity-public/container-images/benchmark/multiarch:22.8 |
|| minio/mc:RELEASE.2022-06-11T21-10-36Z |
|| minio/minio:RELEASE.2022-07-17T15-43-14Z |
|| zookeeper:3.6.2 |
| map_type | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| ontime_benchmark | registry.gitlab.com/altinity-public/container-images/benchmark/multiarch:22.8 |
|| registry.gitlab.com/altinity-public/container-images/s3-tools:2.0 |
|| minio/mc:RELEASE.2022-06-11T21-10-36Z |
|| minio/minio:RELEASE.2022-06-11T19-55-32Z |
|| zookeeper:3.6.2 |
| parquet | registry.gitlab.com/altinity-public/container-images/test/clickhouse-intergration-test-pyarrow:4.0 |
|| registry.gitlab.com/altinity-public/container-images/s3-tools:2.0 |
|| minio/mc:RELEASE.2022-06-11T21-10-36Z |
|| minio/minio:RELEASE.2022-07-17T15-43-14Z |
|| mysql:5.7.30 |
|| postgres:15.0-bullseye |
|| zookeeper:3.6.2 |
| part_moves_between_shards | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.4.12 |
| rbac | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| mysql:5.7.30 |
|| zookeeper:3.6.2 |
| s3 | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| registry.gitlab.com/altinity-public/container-images/s3-tools:2.0 |
|| minio/mc:RELEASE.2022-06-11T21-10-36Z |
|| minio/minio:RELEASE.2022-06-11T19-55-32Z |
|| zookeeper:3.6.2 |
| selects | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |
| ssl_server | registry.gitlab.com/altinity-public/container-images/test/clickhouse-intergration-test-pyarrow:4.0 |
|| clickhouse/clickhouse-server:22.8.12.45 |
|| zookeeper:3.6.2 |
| tiered_storage | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| minio/mc:RELEASE.2022-06-11T21-10-36Z |
|| minio/minio:RELEASE.2022-07-17T15-43-14Z |
|| zookeeper:3.6.2 |
| window_functions | altinityinfra/clickhouse-regression-multiarch:1.0 |
|| zookeeper:3.6.2 |


## Check online runners

Provide which Altinity repository you want to check runners for and it will provide the currently online runners.
 