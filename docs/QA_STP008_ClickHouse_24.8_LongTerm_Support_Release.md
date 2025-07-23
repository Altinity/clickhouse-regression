# QA-STP008 ClickHouse 24.8 Long-Term Support Release
# Software Test Plan

(c) 2025 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** December 16, 2024

## Execution Summary

**Completed:** January 13, 2025

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/

**Build Report:**

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/report.html

**Summary:**

Started to execute test plan on December 16, 2024 and ended on January 13, 2025.

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Timeline](#timeline)
* 3 [Human Resources And Assignments](#human-resources-and-assignments)
* 4 [End User Recommendations](#end-user-recommendations)
    * 4.1 [Release Notes](#release-notes)
* 5 [Known Issues](#known-issues)
    * 5.1 [Open Issues](#open-issues)
    * 5.2 [Summary](#summary)
* 6 [Scope](#scope)
    * 6.1 [Automated Regression Tests](#automated-regression-tests)
        * 6.1.1 [Stateless](#stateless)
        * 6.1.2 [Stateful](#stateful)
        * 6.1.3 [Stress](#stress)
        * 6.1.4 [Integration](#integration)
        * 6.1.5 [Altinity TestFlows Integration](#altinity-testflows-integration)
            * 6.1.5.1 [Key Value](#key-value)
            * 6.1.5.2 [Engines](#engines)
            * 6.1.5.3 [Selects](#selects)
            * 6.1.5.4 [Session Timezone](#session-timezone)
            * 6.1.5.5 [AES Encryption](#aes-encryption)
            * 6.1.5.6 [Tiered-storage](#tiered-storage)
            * 6.1.5.7 [S3](#s3)
            * 6.1.5.8 [Kafka](#kafka)
            * 6.1.5.9 [Kerberos](#kerberos)
            * 6.1.5.10 [DateTime64 Extended Range](#datetime64-extended-range)
            * 6.1.5.11 [Extended Precision Data Types](#extended-precision-data-types)
            * 6.1.5.12 [LDAP](#ldap)
            * 6.1.5.13 [RBAC](#rbac)
            * 6.1.5.14 [Window Functions](#window-functions)
            * 6.1.5.15 [SSL Server](#ssl-server)
            * 6.1.5.16 [Disk Level Encryption](#disk-level-encryption)
            * 6.1.5.17 [ClickHouse Keeper](#clickhouse-keeper)
            * 6.1.5.18 [Data Types](#data-types)
            * 6.1.5.19 [Part Moves Between Shards](#part-moves-between-shards)
            * 6.1.5.20 [Lightweight Delete](#lightweight-delete)
            * 6.1.5.21 [Base58](#base58)
            * 6.1.5.22 [Parquet](#parquet)
            * 6.1.5.23 [Atomic Insert](#atomic-insert)
            * 6.1.5.24 [Aggregate Functions](#aggregate-functions)
            * 6.1.5.25 [DNS](#dns)
        * 6.1.6 [Benchmark](#benchmark)
    * 6.2 [Compatibility with Client Drivers](#compatibility-with-client-drivers)
        * 6.2.1 [Python `clickhouse_driver`](#python-clickhouse_driver)
        * 6.2.2 [ODBC `clickhouse-odbc`](#odbc-clickhouse-odbc)
        * 6.2.3 [SQLAlchemy](#sqlalchemy)
        * 6.2.4 [Java `clickhouse-jdbc`](#java-clickhouse-jdbc)
    * 6.3 [Backup `clickhouse-backup`](#backup-clickhouse-backup)
    * 6.4 [Compatibility With Operation on Kubernetes](#compatibility-with-operation-on-kubernetes)
        * 6.4.1 [Kubernetes `clickhouse-operator`](#kubernetes-clickhouse-operator)
        * 6.4.2 [Altinity.Cloud](#altinitycloud)
    * 6.5 [Production Cluster Operation](#production-cluster-operation)
    * 6.6 [Upgrade and Downgrade](#upgrade-and-downgrade)
        * 6.6.1 [Upgrade](#upgrade)
        * 6.6.2 [Downgrade](#downgrade)
    * 6.7 [Compatibility With BI Tools](#compatibility-with-bi-tools)
        * 6.7.1 [Grafana](#grafana)
        * 6.7.2 [Tableau](#tableau)
        * 6.7.3 [Superset](#superset)
    * 6.8 [Docker Image Vulnerability Scanning](#docker-image-vulnerability-scanning)
        * 6.8.1 [Grype](#grype)

## Introduction

This test plan covers testing of ClickHouse 24.8 LTS (long-term support) Altinity Stable release.

## Timeline

The testing of 24.8.8.17 binaries SHALL be started on December 16, 2024 and be completed
by January 13, 2025.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager, regression)
* Davit Mnatobishvili (parquet, LDAP, benchmarks, alter, extended precision data types)
* Alsu Giliazova (aggregate functions, selects, lightweight_delete)
* Stuart Gibb (clickhouse-keeper, RBAC, S3, tiered_storage)
* Andrey Antipov (clickhouse-operator, disk level encryption, Python clickhouse-driver, JDBC driver, ODBC driver, clickhouse-sqlalchemy, Grafana)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup)
* Dima Borovstov (Tableau)
* Eugene Klimov (Superset)
* Tatiana Saltykova (production cluster, upgrade and downgrade)

## End User Recommendations

### Release Notes

* https://docs.altinity.com/releasenotes/altinity-stable-release-notes/24.8/

## Known Issues

* Analyzer issues https://github.com/ClickHouse/ClickHouse/labels/analyzer
* https://github.com/ClickHouse/ClickHouse/issues/71456 issue with concurrent mutations. workaround: avoid concurrent mutations.
* https://github.com/ClickHouse/ClickHouse/issues/71479 corner case with push down of arrayAll conditions into joins. Workaround: rewrite the query.
* https://github.com/ClickHouse/ClickHouse/issues/71218 issue with array join and partition pruning. Workaround: rewrite query.
* https://github.com/ClickHouse/ClickHouse/issues/64652 issue with memory accounting in cgroups env.
* https://github.com/ClickHouse/ClickHouse/issues/65402 columns for parametrized views are not shown. Workaround: EXPLAIN (SELECT … FROM view(a=1,b=2) WHERE 0)
* https://github.com/ClickHouse/ClickHouse/issues/71895 “Optimized trivial count” can give wrong results in certain corner cases. Workaround: optimize_use_implicit_projection=0, optimize_trivial_count_query=0
* https://github.com/ClickHouse/ClickHouse/issues/71511 issue with memory tracking (fix https://github.com/ClickHouse/ClickHouse/pull/73081 )
* https://github.com/ClickHouse/ClickHouse/issues/69730 Unexpected literal type in function when using toDecimal256. Workaround: disable analyzer, or upgrade to a newer version.

### Open Issues

[GitHub is:issue is:open label:v24.8-affected](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+is%3Aopen+label%3Av24.8-affected+) 

* https://github.com/ClickHouse/ClickHouse/issues/81045 (SerializationString Crash after DROP/ADD the same column)
* https://github.com/ClickHouse/ClickHouse/issues/69518 (Inconsistent handling of maps with LowCardinality(Nullable) between 24.3 and 24.8)

### Summary

Build report: https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/report.html

> [!NOTE]
> **Pass\*** - tests passed with known fails

| Test Suite  | Result                                        | Comments |
| --- |-----------------------------------------------| --- |
| Stateless | [*Pass](#stateless)                     |   |
| Stateful | [Pass](#stateful)                      |   |
| Stress | [Pass](#stress)                        |  Not executed  |
| Integration | [*Pass](#integration)                   |   |
| Key Value | [Pass](#key-value)                     |   |
| Engines  | [Pass](#engines)                       | Not executed  |
| Parquet | [Pass](#parquet)                       |   |
| Parquet (AWS) | [Pass](#parquet)                       |   |
| Parquet (Minio)| [Pass](#parquet)                       |   |
| Memory | [Pass](#memory)                       |   |
| Tiered Storage (Local) | [Pass](#tiered-storage)                |   |
| Tiered Storage (MinIO) | [Pass](#tiered-storage)                |   |
| Tiered Storage (AWS) | [Pass](#tiered-storage)                |   |
| Tiered Storage (GCS) | [Pass](#tiered-storage)                |   |
| S3 (AWS) | [Pass](#s3)                           |  |
| S3 (MinIO) | [Pass](#s3)                            |   |
| S3 (GCS) | [Pass](#s3)                            |   |
| Selects | [Pass](#selects)                       |   |
[ Session Timezone | [Pass](#session-timezone)              |   |
| AES Encryption | [Pass](#aes-encryption)                |   |
| Alter | [Pass](#alter)                 |   |
| Atomic Insert | [Pass](#atomic-insert)                 |   |
| Base58 | [Pass](#base58)                        |   |
| DNS | [Pass](#dns)                           |   |
| Kafka | [Pass](#kafka)                         |   |
| Kerberos | [Pass](#kerberos)                      |   |
| DateTime64 Extended Range | [Pass](#datetime64-extended-range)     |   |
| Extended Precision Data Types | [Pass](#extended-precision-data-types) |   |
| LDAP | [Pass](#ldap)                          |   |
| RBAC | [Pass](#rbac)                          |   |
| Window Functions | [Pass](#window-functions)             |   |
| SSL Server | [Pass](#ssl-server)                    |   |
| Disk Level Encryption | [Pass](#disk-level-encryption)         |   |
| ClickHouse Keeper | [Pass](#clickhouse-keeper)             |   |
| Data Types | [Pass](#data-types)                    |   |
| Benchmark | [Pass](#benchmark)              
| Part Moves Between Shards | [Pass](#part-moves-between-shards)     |   |
| Lightweight Delete | [Pass](#lightweight-delete)            |    |
| Aggregate Functions | [Pass](#aggregate-functions)           |   |
| Python `clickhouse_driver` | [Pass*](#python-clickhouse_driver)            |   |
| ODBC `clickhouse-odbc` | [Pass](#odbc-clickhouse-odbc)                 |  |
| SQLAlchemy | [Pass](#sqlalchemy)                           |    |
| Java `clickhouse-jdbc` | [Pass](#java-clickhouse-jdbc)                 |   |
| Java `clickhouse-jdbc` (DBeaver) | [Pass](#java-clickhouse-jdbc)          |   |
| Backup `clickhouse-backup` | [Pass](#backup-clickhouse-backup)             |   |
| Kubernetes `clickhouse-operator` | [Pass](#kubernetes-clickhouse-operator)       |   |
| Altinity.Cloud | [Pass](#altinitycloud)                        |   |
| Production Cluster Operation | [Pass](#production-cluster-operation)         |   |
| Upgrade And Downgrade | [Pass](#upgrade-and-downgrade)                |   |
| Grafana | [Pass](#grafana)                              |   |
| Tableau | [Pass](#tableau)                       |   |
| Superset | [Pass](#superset)                             |   |
| Gripe | [Pass](#gripe)                         |   |

## Scope

The scope of testing ClickHouse 24.8 Altinity Stable LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.14.10459.altinitystable/2025-03-27T02-26-35.852/stateless/amd64/stateless_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/stateless/aarch64/stateless_results.html

The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.

#### Stateful

Results:

* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.14.10459.altinitystable/2025-03-27T02-26-35.852/stateful/amd64/stateful_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/stateful/aarch64/stateful_results.html

The standard `stateful` suite that consists of running SQL scripts executed against a predefined database schema.

#### Stress

Results:

* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/stress/asan/stress_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/stateful/msan/stateful_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/stress/tsan/stress_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/stress/ubsan/stress_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/stress/debug/stress_results.html

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/integration/release/integration_results_1.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/integration/release/integration_results_2.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/integration/release/integration_results_3.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/integration/release/integration_results_4.html


The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### Key Value

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html

Altinity Key Value function tests.

##### Engines

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html

Altinity Engines tests.

##### Selects

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html

Altinity Selects tests.

##### Session Timezone

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html

Altinity Session Timezone tests.

##### AES Encryption

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html

Altinity AES Encryption tests.

##### Tiered-storage

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/report.html

Altinity Tiered-Storage tests.

##### S3

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s3/report.html

Altinity S3 integration tests.

##### Kafka

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html

Altinity Kafka integration tests.

##### Kerberos

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html

Altinity Kerberos integration tests.

##### DateTime64 Extended Range

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html

Altinity DateTime64 extended range integration tests.

##### Extended Precision Data Types

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html

Altinity Extended Precision Data Types integration tests.

##### LDAP

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/report.html

Altinity LDAP integration tests.

##### RBAC

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac/report.html

Altinity RBAC integration tests.

##### Window Functions

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html

Altinity Window Functions integration tests.

##### SSL Server

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server/report.html

Altinity basic SSL server integration tests.

##### Disk Level Encryption

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html

Altinity Disk Level Encryption integration tests.

##### ClickHouse Keeper

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper/report.html

Altinity ClickHouse Keeper integration tests.

##### Data Types

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html

Altinity data types integration tests.

##### Part Moves Between Shards

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html

Altinity Part Moves Between Shards integration tests.

##### Lightweight Delete

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html

Altinity Lightweight Delete integration tests.

##### Base58

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html

Altinity Base58 encode and decode functions integration tests.

##### Parquet

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html

Altinity Parquet format integration tests.


##### Atomic Insert

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html

Altinity Atomic Insert integration tests.

##### Aggregate Functions

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions/report.html
  
Altinity Aggregate Functions integration tests.

##### DNS

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html

Altinity DNS integration tests.

#### Benchmark

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/gcs/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/gcs/report.html

Altinity OnTime Benchmark tests.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

clickhouse-driver version: 0.2.9

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-driver/

* https://github.com/mymarilyn/clickhouse-driver/issues/470 (Clickhouse drivers tests for JSON type fails)
* https://github.com/mymarilyn/clickhouse-driver/issues/470 (Clickhouse drivers test for client with no cert validations fails)
  
The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

Compatibility with the [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

#### ODBC `clickhouse-odbc`

clickhouse-odbc version: v1.3.0.20241018

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.

#### SQLAlchemy

clickhouse-sqlalchemy version: 0.3.2

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.

#### Java `clickhouse-jdbc`

clickhouse-jdbc version: v0.7.2

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-jdbc/

Results (DBeaver): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-jdbc/DBeaver/

The (https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-backup/
Results (ACM): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-backup-acm/

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/clickhouse-operator/

clickhouse-operator version: 0.24.2

Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).

#### Altinity.Cloud

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/acm-launch-and-upgrade/launch_with_24.8.8.17/

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: 

Operation on a production clusters.

### Upgrade and Downgrade

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/acm-launch-and-upgrade/upgrade_downgrade_from_24.3.12.76.altinitystable_to_24.8.8.17/

The upgrade and downgrade.

#### Upgrade

* from 24.3 to 24.8

#### Downgrade

* from 24.8 to 24.2

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/grafana/

Compatibility with [Grafana].

#### Tableau

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/tableau/

Compatibility with [Tableau].

#### Superset

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.8-lts/superset/

Compatibility with [Superset].

### Docker Image Vulnerability Scanning

#### Grype

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/staging-docker-grype-ubuntu-server-amd64/results.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.8.11.51285.altinitystable/2025-01-30T18-01-41.627/staging-docker-grype-ubuntu-server-arm64/results.html

[Grype](https://github.com/anchore/grype) Docker image vulnerability scanner.


[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub]: https://github.com
