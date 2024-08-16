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

| Suite                         | Utilized image(s)                                                        |
|-------------------------------|--------------------------------------------------------------------------|
| aes_encryption                | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | mysql:5.7.30                                                             |
|                               | zookeeper:3.8.4                                                          |
| aggregate_functions           | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| alter                         | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | altinityinfra/s3-proxy:265-ea7abf434d5f99618d1e188b8284cf43835724f3      |
|                               | altinityinfra/python-bottle:265-ea7abf434d5f99618d1e188b8284cf43835724f3 |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-07-17T15-43-14Z                                 |
|                               | mysql:8.0.34                                                             |
|                               | postgres:15.0-bullseye                                                   |
|                               | zookeeper:3.8.4                                                          |
| atomic_insert                 | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| attach                        | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| base_58                       | clickhouse/clickhouse-integration-test:28741                             |
|                               | zookeeper:3.8.4                                                          |
| base_58                       | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.2                                                          |
| clickhouse/functional         | altinityinfra/clickhouse-functional-test:1.0                             |
|                               | bitnami/zookeeper:3.7.1-debian-11-r90                                    |
| clickhouse_keeper             | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | clickhouse/clickhouse-server:22.8.12.45                                  |
|                               | zookeeper:3.8.4                                                          |
|                               | zookeeper:3.4.12                                                         |
|                               | altinity/zookeeper-fips:3.7.1-1                                          |
|                               | altinityinfra/bash-tools:1.0                                             |
| clickhouse_keeper_failout     | clickhouse/clickhouse-keeper:latest                                      |
| data_types                    | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| datetime64_extended_range     | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| disk_level_encryption         | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| dns                           | altinityinfra/clickhouse-regression-multiarch:1.0                        |
| engines                       | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| example                       | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| extended_precision_data_types | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | mysql:5.7.30                                                             |
| functions                     | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| kafka                         | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | confluentinc/cp-kafka:5.2.0                                              |
|                               | zookeeper:3.4.12                                                         |
| kerberos                      | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | altinityinfra/docker-krb5-server:1.0                                     |
|                               | zookeeper:3.8.4                                                          |
| key_value                     | clickhouse/clickhouse-integration-test:28741                             |
|                               | zookeeper:3.8.4                                                          |
|                               |                                                                          |
|                               | zookeeper:3.6.2                                                          |
| key_value                     | clickhouse/clickhouse-integration-test:28741                             |
|                               | zookeeper:3.6.2                                                          |
|                               | zookeeper:3.6.2                                                          |
| key_value                     | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.6.2                                                          |
| ldap                          | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | osixia/openldap:1.4.0                                                    |
|                               | zookeeper:3.8.4                                                          |
| lightweight_delete            | altinityinfra/clickhouse-regression-multiarch-ontime:1.0                 |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-07-17T15-43-14Z                                 |
|                               | zookeeper:3.8.4                                                          |
| map_type                      | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| ontime_benchmark              | altinityinfra/clickhouse-regression-multiarch-ontime:1.0                 |
|                               | zookeeper:3.8.4                                                          |
| memory                        | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| ontime_benchmark              | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | altinityinfra/s3-proxy:265-ea7abf434d5f99618d1e188b8284cf43835724f3      |
|                               | altinityinfra/python-bottle:265-ea7abf434d5f99618d1e188b8284cf43835724f3 |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-06-11T19-55-32Z                                 |
|                               | zookeeper:3.8.4                                                          |
| parquet                       | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-07-17T15-43-14Z                                 |
|                               | mysql:8.0.34                                                             |
|                               | postgres:15.0-bullseye                                                   |
|                               | zookeeper:3.8.4                                                          |
| part_moves_between_shards     | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.4.12                                                         |
| rbac                          | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | mysql:5.7.30                                                             |
|                               | zookeeper:3.8.4                                                          |
|                               | mysql:8.0.34                                                             |
|                               | zookeeper:3.8.4                                                          |
| s3                            | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-06-11T19-55-32Z                                 |
|                               | zookeeper:3.8.4                                                          |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-06-11T19-55-32Z                                 |
|                               | zookeeper:3.8.4                                                          |
| selects                       | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| ssl_server                    | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| session_timezone              | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |
| ssl_keeper                    | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | altinityinfra/bash-tools:1.0                                             |
| ssl_server                    | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | clickhouse/clickhouse-server:22.8.12.45                                  |
|                               | zookeeper:3.8.4                                                          |
|                               | altinity/zookeeper-fips:3.7.1-1                                          |
| tiered_storage                | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-07-17T15-43-14Z                                 |
|                               | zookeeper:3.8.4                                                          |
| vfs                           | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | minio/mc:RELEASE.2022-06-11T21-10-36Z                                    |
|                               | minio/minio:RELEASE.2022-07-17T15-43-14Z                                 |
|                               | zookeeper:3.8.4                                                          |
| window_functions              | altinityinfra/clickhouse-regression-multiarch:1.0                        |
|                               | zookeeper:3.8.4                                                          |

## Check online runners

Provide which Altinity repository you want to check runners for, and it will provide the currently online runners.
 
