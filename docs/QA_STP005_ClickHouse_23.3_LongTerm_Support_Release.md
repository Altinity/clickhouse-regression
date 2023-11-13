# QA-STP005 ClickHouse 23.3 Long-Term Support Release
# Software Test Plan

(c) 2022 Altinity Inc. All Rights Reserved.

**Document status:** Confidential

**Author:** vzakaznikov

**Date:** June 26, 2023

## Execution Summary

**Completed:** July 13, 2023

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/

**Summary:**

Started to execute test plan on June 26, 2023.

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Timeline](#timeline)
* 4 [Human Resources And Assignments](#human-resources-and-assignments)
* 5 [End User Recommendations](#end-user-recommendations)
    * 5.1 [Summary of Main Regressions](#summary-of-main-regressions)
* 6 [Known Issues](#known-issues)
* 7 [New Features](#new-features)
    * 7.1 [Altinity Stable Backports](#altinity-stable-backports)
    * 7.2 [Changelog](#changelog)
    * 7.3 [Summary](#summary)
* 8 [Scope](#scope)
    * 8.1 [Automated Regression Tests](#automated-regression-tests)
        * 8.1.1 [Stateless](#stateless)
        * 8.1.2 [Stateful](#stateful)
        * 8.1.3 [Stress](#stress)
        * 8.1.4 [Integration](#integration)
        * 8.1.5 [Altinity TestFlows Integration](#altinity-testflows-integration)
            * 8.1.5.1 [Key Value](#key-value)
            * 8.1.5.2 [Engines](#engines)
            * 8.1.5.3 [Selects](#selects)
            * 8.1.5.4 [AES Encryption](#aes-encryption)
            * 8.1.5.5 [Tiered-storage](#tiered-storage)
            * 8.1.5.6 [S3](#s3)
            * 8.1.5.7 [Kafka](#kafka)
            * 8.1.5.8 [Kerberos](#kerberos)
            * 8.1.5.9 [DateTime64 Extended Range](#datetime64-extended-range)
            * 8.1.5.10 [Extended Precision Data Types](#extended-precision-data-types)
            * 8.1.5.11 [LDAP](#ldap)
            * 8.1.5.12 [RBAC](#rbac)
            * 8.1.5.13 [Window Functions](#window-functions)
            * 8.1.5.14 [SSL Server](#ssl-server)
            * 8.1.5.15 [Disk Level Encryption](#disk-level-encryption)
            * 8.1.5.16 [ClickHouse Keeper](#clickhouse-keeper)
            * 8.1.5.17 [Map Type](#map-type)
            * 8.1.5.18 [Part Moves Between Shards](#part-moves-between-shards)
            * 8.1.5.19 [Lightweight Delete](#lightweight-delete)
            * 8.1.5.20 [Base58](#base58)
            * 8.1.5.21 [Parquet](#parquet)
            * 8.1.5.22 [Atomic Insert](#atomic-insert)
            * 8.1.5.23 [Aggregate Functions](#aggregate-functions)
            * 8.1.5.24 [DNS](#dns)
        * 8.1.6 [Ontime Benchmark](#ontime-benchmark)
    * 8.2 [Compatibility with Client Drivers](#compatibility-with-client-drivers)
        * 8.2.1 [Python `clickhouse_driver`](#python-clickhouse_driver)
        * 8.2.2 [ODBC `clickhouse-odbc`](#odbc-clickhouse-odbc)
        * 8.2.3 [SQLAlchemy](#sqlalchemy)
        * 8.2.4 [Java `clickhouse-jdbc`](#java-clickhouse-jdbc)
    * 8.3 [Backup `clickhouse-backup`](#backup-clickhouse-backup)
    * 8.4 [Compatibility With Operation on Kubernetes](#compatibility-with-operation-on-kubernetes)
        * 8.4.1 [Kubernetes `clickhouse-operator`](#kubernetes-clickhouse-operator)
        * 8.4.2 [Altinity.Cloud](#altinitycloud)
    * 8.5 [Production Cluster Operation](#production-cluster-operation)
    * 8.6 [Upgrade and Downgrade](#upgrade-and-downgrade)
        * 8.6.1 [Upgrade](#upgrade)
        * 8.6.2 [Downgrade](#downgrade)
    * 8.7 [Compatibility With BI Tools](#compatibility-with-bi-tools)
        * 8.7.1 [Grafana](#grafana)
        * 8.7.2 [Tableau](#tableau)
        * 8.7.3 [Superset](#superset)
    * 8.8 [Docker Image Vulnerability Scanning](#docker-image-vulnerability-scanning)
        * 8.8.1 [Trivy](#trivy)
        * 8.8.2 [Scout](#scout)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitLab Repository].
All the updates are tracked using the [Revision History].

## Introduction

This test plan covers testing of ClickHouse 23.3 LTS (long-term support) release.

## Timeline

The testing of pre-stable binaries SHALL be started on June 26, 2023 and be completed
by July 28, 2022.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager, regression)
* Myroslav Tkachenko (automated regression tests)
* Andrey Antipov (clickhouse-operator, disk level encryption, Python clickhouse-driver, JDBC driver, ODBC driver, clickhouse-sqlalchemy)
* Davit Mnatobishvili (parquet)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup)
* Ivan Sidorov (clickhouse-keeper, part-moves-between-shards)
* Dima Borovstov (Tableau)
* Eugene Klimov (Grafana, Superset)
* Tatiana Saltykova (production cluster, upgrade and downgrade)

## End User Recommendations

### Summary of Main Regressions

Regressions between the latest `23.3.8` vs `22.8` are the following:

* Wrong result - Count over Nullable LowCardinality column
  https://github.com/ClickHouse/ClickHouse/issues/52055

* Performance - PREWHERE
  https://github.com/ClickHouse/ClickHouse/issues/51849

* B Compatibility - Ipv4 is not supported as a dictionary attribute anymore
  https://github.com/ClickHouse/ClickHouse/issues/51083

* Minor - Mutation cannot finish if parts are not byte-identical
  https://github.com/ClickHouse/ClickHouse/issues/48801

## Known Issues

[GitHub is:issue is:open label:v23.3-affected](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+is%3Aopen+label%3Av23.3-affected+) as of July 13, 2023

* Count over Nullable LowCardinality column bug Confirmed user-visible misbehaviour
  https://github.com/ClickHouse/ClickHouse/issues/52055

* Problem with query plan optimizer yielding incorrect results
  https://github.com/ClickHouse/ClickHouse/issues/51901

* Query performance between 23.x and 22.x
  https://github.com/ClickHouse/ClickHouse/issues/51849

* Incorrect sort result after join
  https://github.com/ClickHouse/ClickHouse/issues/51660

* ASOF JOIN and force_index_by_date
  https://github.com/ClickHouse/ClickHouse/issues/51659

* JIT compiler issue / Cannot convert column because it is non constant in source stream but must be constant in result
  https://github.com/ClickHouse/ClickHouse/issues/51090

* Ipv4 is not supported as a dictionary attribute anymore
  https://github.com/ClickHouse/ClickHouse/issues/51083

* Querying ReplicatedSummingMergeTree table through Distribution table with condition on DateTime64 column with lesser/greater than subquery result returns results only from single shard
  https://github.com/ClickHouse/ClickHouse/issues/50868

* DB::Exception: Memory limit (total) exceeded: While executing MergeTreeThread. (MEMORY_LIMIT_EXCEEDED)
  https://github.com/ClickHouse/ClickHouse/issues/50223

* Example of projection from documentations is not work
  https://github.com/ClickHouse/ClickHouse/issues/50093

* Query with offset on order field produces incorrect results
  https://github.com/ClickHouse/ClickHouse/issues/48881

* Mutation cannot finish if parts are not byte-identical
  https://github.com/ClickHouse/ClickHouse/issues/48801

Reported By Altinity:

* Caching of successful LDAP authentication requests (verification cooldown) broken since 22.12
  https://github.com/ClickHouse/ClickHouse/issues/50864

* singleValueOrNullState with Array(Nullable(UInt32)) argument throws exception. version 23.2.1
  https://github.com/ClickHouse/ClickHouse/issues/47142

* Disk appears as active after TTL delete triggers
  https://github.com/ClickHouse/ClickHouse/issues/50060

* 23.2 - mannWhitneyUTest function returns all numbers in both samples are identical exception, worked previously
  https://github.com/ClickHouse/ClickHouse/issues/48917

* RBAC access_management config does not grant ACCESS MANAGEMENT
  https://github.com/ClickHouse/ClickHouse/issues/47092

* Clickhouse-client successfully connects to the server using TLS when all protocols are disabled in clickhouse-client config
  https://github.com/ClickHouse/ClickHouse/issues/45445

* Adding valid openSSL config causes CertificateReloader error in the clickhouse-server log
  https://github.com/ClickHouse/ClickHouse/issues/45255

* Clickhouse Keeper's secure <raft_configuration> port doesn't use openSSL server config settings
  https://github.com/ClickHouse/ClickHouse/issues/51188

* Incorrect values insertion into the is_deleted column of new ReplacingMergeTree engine
  https://github.com/ClickHouse/ClickHouse/issues/47579


## New Features

### Altinity Stable Backports

### Changelog

### Summary

| Test Suite  | Result | Comments |
| --- | --- | --- |
| Stateless | [Pass*](#stateless) |   |
| Stateful | [Pass](#stateful)  |   |
| Stress | Not executed  |   |
| Integration | [Pass*](#integration)  |   |
| Key Value | [Skipped](#key-value)  |   |
| Engines  | [Pass](#engines)  |   |
| Parquet | [Pass*](#parquet)  |   |
| Tiered Storage (Local) | [Pass](#tiered-storage)  |   |
| Tiered Storage (MinIO) | [Pass](#tiered-storage)  |   |
| Tiered Storage (AWS) | [Pass](#tiered-storage)  |   |
| Tiered Storage (GCS) | [Pass](#tiered-storage)  |   |
| S3 (AWS) | [Pass](#s3)  |  |
| S3 (MinIO) | [Pass](#s3)  |   |
| S3 (GCS) | [Pass](#s3) |   |
| Selects | [Pass](#selects) |   |
| AES Encryption | [Pass](#aes-encryption)  |   |
| Atomic Insert | [Pass](#atomic-insert) |   |
| Base58 | [Pass](#base58) |   |
| DNS | [Pass](#dns) |   |
| Kafka | [Pass](#kafka) |   |
| Kerberos | [Pass](#kerberos)  |   |
| DateTime64 Extended Range | [Pass](#datetime64-extended-range)  |   |
| Extended Precision Data Types | [Pass](#extended-precision-data-types) |   |
| LDAP | [Pass](#ldap)  |   |
| RBAC | [Pass](#rbac) |   |
| Window Functions | [Pass](#window-functions)  |   |
| SSL Server | [Pass](#ssl-server)  |   |
| Disk Level Encryption | [Pass](#disk-level-encryption)  |   |
| ClickHouse Keeper | [Pass](#clickhouse-keeper)  |   |
| Map Type | [Pass](#map-type) |   |
| Ontime Bechmark | [Pass](#ontime-benchmark)
| Part Moves Between Shards | [Pass](#part-moves-between-shards) |   |
| Lightweight Delete | [Pass](#lightweight-delete) |    |
| Aggregate Functions | [Pass](#aggregate-functions) |  |
| Python `clickhouse_driver` | [Pass](#python-clickhouse_driver)  |   |
| ODBC `clickhouse-odbc` | [Pass](#odbc-clickhouse-odbc)  |  |
| SQLAlchemy | [Pass](#sqlalchemy) |    |
| Java `clickhouse-jdbc` | [Pass](#java-clickhouse-jdbc)  |   |
| Java `clickhouse-jdbc` (DBeaver) | [Pass](#java-clickhouse-jdbc)  |   |
| Backup `clickhouse-backup` | [Pass](#backup-clickhouse-backup)  |   |
| Kubernetes `clickhouse-operator` | [Pass*](#kubernetes-clickhouse-operator) |   |
| Altinity.Cloud | [Pass](#altinitycloud)  |   |
| Production Cluster Operation | [Pass](#production-cluster-operation) |   |
| Upgrade And Downgrade | [Pass](#upgrade-and-downgrade) |   |
| Grafana | [Pass](#grafana) |   |
| Tableau | [Pass](#tableau)  |   |
| Superset | [Pass](#superset)  |   |
| Trivy | [Pass](#trivy) |   |
| Scout | [Pass](#scout) |   |

## Scope

The scope of testing ClickHouse 23.3 LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/stateless/

The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.

```
Test: 01680_date_time_add_ubsan
Reason: Test has ubsan in its name and we do not produce sanitized builds.
Status: FAIL (OK to fail)
```

#### Stateful

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/stateful/

The standard `stateful` suite that consists of running SQL scripts executed against a predefined database schema.

#### Stress

Results: test suite was not executed

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/integration/

The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

```
Test: /integration/test_cgroup_limit/test.py::test_cgroup_cpu_limit
Reason: Misconfiguration: 1 CPU/hardware thread available to the CH instead of at least 2.
Status: FAIL (OK to fail)

Test: test_reverse_dns_query/test.py::test_reverse_dns_query
Reason: Reverse DNS function fails to get a response.
Status: FAIL
```

#### Altinity TestFlows Integration

##### Key Value

Results:

Altinity Key Value function tests.

```
Reason: not supported on <23.5
Status: Skipped
```

##### Engines

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/engines/

Altinity Engines tests.

##### Selects

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/selects/

Altinity Selects tests.

##### AES Encryption

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/aes_encryption/

Altinity AES Encryption tests.

##### Tiered-storage

Results: (Local) https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/tiered_storage/

Results: (MinIO) https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/tiered_storage/minio/

Results: (AWS) https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/tiered_storage/s3amazon/

Results (GCS) https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/tiered_storage/s3gcs/

Altinity Tiered-Storage tests.

##### S3

Results: (AWS S3) https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/s3/

Results: (MinIO) https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/s3/minio/

Results: (GCS) https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/s3/gcs/

Altinity S3 integration tests.

##### Kafka

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/kafka/

Altinity Kafka integration tests.

##### Kerberos

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/kerberos/

Altinity Kerberos integration tests.

##### DateTime64 Extended Range

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/datetime64_extended_range/

Altinity DateTime64 extended range integration tests.

##### Extended Precision Data Types

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/extended_precision_data_types/

Altinity Extended Precision Data Types integration tests.

##### LDAP

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/ldap/

Altinity LDAP integration tests.

##### RBAC

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/rbac/

Altinity RBAC integration tests.

##### Window Functions

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/window_functions/

Altinity Window Functions integration tests.

##### SSL Server

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/ssl_server/

Altinity basic SSL server integration tests.

##### Disk Level Encryption

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/disk_level_encryption/

Altinity Disk Level Encryption integration tests.

##### ClickHouse Keeper

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse_keeper/

Altinity ClickHouse Keeper integration tests.

##### Map Type

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/map_type/

Altinity Map data type integration tests.

##### Part Moves Between Shards

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/part_moves_between_shards/

Altinity Part Moves Between Shards integration tests.

##### Lightweight Delete

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/lightweight_delete/

Altinity Lightweight Delete integration tests.

##### Base58

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/base_58/

Altinity Base58 encode and decode functions integration tests.

##### Parquet

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/parquet/no_s3/
Results (AWS S3): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/parquet/aws_s3/
Results (MinIO S3): timeout


Altinity Parquet format integration tests.

```
Test: parquet/minio_s3
Reason: timeout
Status: Failed
```

##### Atomic Insert

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/atomic_insert/

Altinity Atomic Insert integration tests.

##### Aggregate Functions

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/aggregate_functions/

Altinity Aggregate Functions integration tests.

##### DNS

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/dns/

Altinity DNS integration tests.

#### Ontime Benchmark

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/ontime_benchmark/
Results AWS S3: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/testflows/ontime_benchmark/aws_s3/

Altinity OnTime Benchmark tests.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickchouse-driver/

The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.


#### ODBC `clickhouse-odbc`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.


#### SQLAlchemy

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.


#### Java `clickhouse-jdbc`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse-jdbc/v0.4.6/

Results (DBeaver): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse-jdbc/DBeaver/

The (https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse-backup/
Results (ACM): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse-backup-acm/

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/clickhouse-operator/

Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).

```
Test: /regression/e2e.test_operator/test_041. Secure zookeeper
Reason: known failing test that will be fixed
Status: Fail
```

#### Altinity.Cloud

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/acm-launch-and-upgrade/

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: OK (feedback from support team)

Operation on a production clusters.

### Upgrade and Downgrade

Results: OK (feedback from support team)

The upgrade and downgrade.

#### Upgrade

* from 22.8 to 23.3

#### Downgrade

* from 23.3 to 22.8

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/grafana/

Compatibility with [Grafana].

#### Tableau

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/tableau/

Compatibility with [Tableau].

#### Superset

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/superset/

Compatibility with [Superset].

### Docker Image Vulnerability Scanning

#### Trivy

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/trivy/

Trivy Docker image vulnerability scanner.


#### Scout

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.3-lts/scout/

Scout Docker image vulnerability scanner.

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[GitLab Repository]: https://gitlab.com/altinity-qa/documents/qa-stp005-clickhouse-23.3-long-term-support-release/
[Revision History]: https://gitlab.com/altinity-qa/documents/qa-stp005-clickhouse-23.3-long-term-support-release/-/commits/main/
[Git]: https://git-scm.com/
[GitLab]: https://gitlab.com
