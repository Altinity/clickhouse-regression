# QA-STP009 ClickHouse 25.8 Long-Term Support Release  
# Software Test Plan

(c) 2025 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** [TBD]

## Execution Summary

**Completed:** [TBD]

**Test Results:**

* [TBD]

**Build Report:**

* [TBD]

**Summary:**

Approved for release.

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
            * 6.1.5.1 [AES Encryption](#aes-encryption)
            * 6.1.5.2 [Aggregate Functions](#aggregate-functions)
            * 6.1.5.3 [Alter](#alter)
            * 6.1.5.4 [Atomic Insert](#atomic-insert)
            * 6.1.5.5 [Attach](#attach)
            * 6.1.5.6 [Base58](#base58)
            * 6.1.5.7 [Ontime Benchmark](#ontime-benchmark)
            * 6.1.5.8 [ClickHouse Keeper](#clickhouse-keeper)
            * 6.1.5.9 [ClickHouse Keeper Failover](#clickhouse-keeper-failover)
            * 6.1.5.10 [Data Types](#data-types)
            * 6.1.5.11 [DateTime64 Extended Range](#datetime64-extended-range)
            * 6.1.5.12 [Disk Level Encryption](#disk-level-encryption)
            * 6.1.5.13 [DNS](#dns)
            * 6.1.5.14 [Engines](#engines)
            * 6.1.5.15 [Example](#example)
            * 6.1.5.16 [Extended Precision Data Types](#extended-precision-data-types)
            * 6.1.5.17 [Functions](#functions)
            * 6.1.5.18 [Hive Partitioning](#hive-partitioning)
            * 6.1.5.19 [Iceberg](#iceberg)
            * 6.1.5.20 [JWT Authentication](#jwt-authentication)
            * 6.1.5.21 [Kafka](#kafka)
            * 6.1.5.22 [Kerberos](#kerberos)
            * 6.1.5.23 [Key Value](#key-value)
            * 6.1.5.24 [LDAP](#ldap)
            * 6.1.5.25 [Lightweight Delete](#lightweight-delete)
            * 6.1.5.26 [Memory](#memory)
            * 6.1.5.27 [Parquet](#parquet)
            * 6.1.5.28 [Part Moves Between Shards](#part-moves-between-shards)
            * 6.1.5.29 [RBAC](#rbac)
            * 6.1.5.30 [S3](#s3)
            * 6.1.5.31 [Selects](#selects)
            * 6.1.5.32 [Session Timezone](#session-timezone)
            * 6.1.5.33 [Settings](#settings)
            * 6.1.5.34 [SSL Server](#ssl-server)
            * 6.1.5.35 [Swarms](#swarms)
            * 6.1.5.36 [Tiered Storage](#tiered-storage)
            * 6.1.5.37 [Version](#version)
            * 6.1.5.38 [Window Functions](#window-functions)
    * 6.2 [Regression Tests with Sanitizers](#regression-tests-with-sanitizers)
        * 6.2.1 [ASAN](#asan)
        * 6.2.2 [MSAN](#msan)
        * 6.2.3 [UBSAN](#ubsan)
        * 6.2.4 [TSAN](#tsan)
    * 6.3 [Compatibility with Client Drivers](#compatibility-with-client-drivers)
        * 6.3.1 [Python `clickhouse_driver`](#python-clickhouse_driver)
        * 6.3.2 [ODBC `clickhouse-odbc`](#odbc-clickhouse-odbc)
        * 6.3.3 [SQLAlchemy](#sqlalchemy)
        * 6.3.4 [Java `clickhouse-jdbc`](#java-clickhouse-jdbc)
    * 6.4 [Backup `clickhouse-backup`](#backup-clickhouse-backup)
    * 6.5 [Compatibility With Operation on Kubernetes](#compatibility-with-operation-on-kubernetes)
        * 6.5.1 [Kubernetes `clickhouse-operator`](#kubernetes-clickhouse-operator)
        * 6.5.2 [Altinity.Cloud](#altinitycloud)
    * 6.6 [Production Cluster Operation](#production-cluster-operation)
    * 6.7 [Upgrade and Downgrade](#upgrade-and-downgrade)
        * 6.7.1 [Upgrade](#upgrade)
        * 6.7.2 [Downgrade](#downgrade)
    * 6.8 [Compatibility With BI Tools](#compatibility-with-bi-tools)
        * 6.8.1 [Grafana](#grafana)
        * 6.8.2 [Tableau](#tableau)
        * 6.8.3 [Superset](#superset)
    * 6.9 [Docker Image Vulnerability Scanning](#docker-image-vulnerability-scanning)
        * 6.9.1 [Grype](#grype)


## Introduction

This test plan covers testing of ClickHouse 25.8 LTS (long-term support) Altinity Stable release.

## Timeline

The testing of 25.8.x binaries SHALL be started on [TBD] and be completed by [TBD].

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager)
* Davit Mnatobishvili (regression, clickhouse-odbc, grafana, superset, DBeaver)
* Alsu Giliazova (regression, clickhouse-jdbc, sqlalchemy, clickhouse-driver)
* Saba Momtselidze (clickhouse-operator)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup)
* Dima Borovstov (Tableau)
* Eugene Klimov (Superset)
* Mikhail Filimonov (production clusters, support team feedback)

### Release Notes

* [TBD]

## Known Issues

[TBD]

### Open Issues

[TBD]

### Summary
Build report: [TBD]

> [!NOTE]
> **\*Pass** - tests passed with known fails

| Test Suite  | Result                                        | Comments |
| --- |-----------------------------------------------| --- |
| Stateless | [*TBD](#stateless)                     |   |
| Stateful | [TBD](#stateful)                      |   |
| Stress | [TBD](#stress)                        |  Not executed  |
| Integration | [*TBD](#integration)                   |   |
| AES Encryption | [TBD](#aes-encryption)                |   |
| Aggregate Functions | [TBD](#aggregate-functions)           |   |
| Alter | [TBD](#alter)                 |   |
| Atomic Insert | [TBD](#atomic-insert)                 |   |
| Attach | [TBD](#attach)                        |   |
| Base58 | [TBD](#base58)                        |   |
| Ontime Benchmark | [TBD](#ontime-benchmark)              |   |
| ClickHouse Keeper | [TBD](#clickhouse-keeper)             |   |
| ClickHouse Keeper Failover | [TBD](#clickhouse-keeper-failover)   |   |
| Data Types | [TBD](#data-types)                    |   |
| DateTime64 Extended Range | [TBD](#datetime64-extended-range)     |   |
| Disk Level Encryption | [TBD](#disk-level-encryption)         |   |
| DNS | [TBD](#dns)                           |   |
| Engines  | [TBD](#engines)                       | Not executed  |
| Example | [TBD](#example)                       |   |
| Extended Precision Data Types | [TBD](#extended-precision-data-types) |   |
| Functions | [TBD](#functions)                     |   |
| Hive Partitioning | [TBD](#hive-partitioning)           |   |
| Iceberg | [TBD](#iceberg)                       |   |
| JWT Authentication | [TBD](#jwt-authentication)           |   |
| Kafka | [TBD](#kafka)                         |   |
| Kerberos | [TBD](#kerberos)                      |   |
| Key Value | [TBD](#key-value)                     |   |
| LDAP | [TBD](#ldap)                          |   |
| Lightweight Delete | [TBD](#lightweight-delete)            |    |
| Memory | [TBD](#memory)                       |   |
| Parquet | [TBD](#parquet)                       |   |
| Part Moves Between Shards | [TBD](#part-moves-between-shards)     |   |
| RBAC | [TBD](#rbac)                          |   |
| S3 | [TBD](#s3)                           |  |
| Selects | [TBD](#selects)                       |   |
| Session Timezone | [TBD](#session-timezone)              |   |
| Settings | [TBD](#settings)                      |   |
| SSL Server | [TBD](#ssl-server)                    |   |
| Swarms | [TBD](#swarms)                        |   |
| Tiered Storage | [TBD](#tiered-storage)                |   |
| Version | [TBD](#version)                       |   |
| Window Functions | [TBD](#window-functions)             |   |
| Python `clickhouse_driver` | [TBD*](#python-clickhouse_driver)            |   |
| ODBC `clickhouse-odbc` | [TBD](#odbc-clickhouse-odbc)                 |  |
| SQLAlchemy | [TBD](#sqlalchemy)                           |    |
| Java `clickhouse-jdbc` | [TBD](#java-clickhouse-jdbc)                 |   |
| Java `clickhouse-jdbc` (DBeaver) | [TBD](#java-clickhouse-jdbc)          |   |
| Backup `clickhouse-backup` | [TBD](#backup-clickhouse-backup)             |   |
| Kubernetes `clickhouse-operator` | [TBD](#kubernetes-clickhouse-operator)       |   |
| Altinity.Cloud | [TBD](#altinitycloud)                        |   |
| Production Cluster Operation | [TBD](#production-cluster-operation)         |   |
| Upgrade And Downgrade | [TBD](#upgrade-and-downgrade)                |   |
| Grafana | [TBD](#grafana)                              |   |
| Tableau | [TBD](#tableau)                       |   |
| Superset | [TBD](#superset)                             |   |
| Grype | [TBD](#grype)                         |   |

## Scope

The scope of testing ClickHouse 25.8 Altinity Stable LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

* [TBD]

The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.

#### Stress

Results:

* [TBD]

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

* [TBD]

The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### AES Encryption

Results:

* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html

Altinity AES Encryption tests.

##### Aggregate Functions

Results:

* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions/report.html
  
Altinity Aggregate Functions integration tests.

##### Alter

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter/attach_partition/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter/move_partition/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter/replace_partition/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter/attach_partition/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter/move_partition/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter/replace_partition/report.html

Altinity Alter tests.

##### Atomic Insert

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html

Altinity Atomic Insert integration tests.

##### Attach

Results:

* [TBD]16570234845/job/46860218565
* [TBD]16570238894/job/46860234499

Altinity Attach tests.

##### Base58

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html

Altinity Base58 encode and decode functions integration tests.

##### Ontime Benchmark

Results:

* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/gcs/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/minio/report.html

Altinity OnTime Benchmark tests.

##### ClickHouse Keeper

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper/ssl/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper/ssl/report.html

Altinity ClickHouse Keeper integration tests.

##### ClickHouse Keeper Failover

Results:

* [TBD]16570238894/job/46860235299
* [TBD]16570234845/job/46860219117

Altinity ClickHouse Keeper Failover integration tests.

##### Data Types

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html

Altinity data types integration tests.

##### DateTime64 Extended Range

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html

Altinity DateTime64 extended range integration tests.

##### Disk Level Encryption

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html

Altinity Disk Level Encryption integration tests.

##### DNS

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html

Altinity DNS integration tests.

##### Engines

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html

Altinity Engines tests.

##### Example

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/example/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/example/report.html

Altinity Example tests.

##### Extended Precision Data Types

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html

Altinity Extended Precision Data Types integration tests.

##### Functions

Results:

* [TBD]16570234845/job/46860219119
* [TBD]16570238894/job/46860235351

Altinity Functions tests.

##### Iceberg

Results:

* [TBD]16570234845/job/46860219005
* [TBD]16570234845/job/46860219153
* [TBD]16570238894/job/46860235361
* [TBD]16570238894/job/46860235373

Altinity Iceberg tests.


##### JWT Authentication

Results:

* [TBD]16570238894/job/46860235180
* [TBD]16570234845/job/46860219008

Altinity JWT Authentication tests.

##### Kafka

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html

Altinity Kafka integration tests.

##### Kerberos

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html

Altinity Kerberos integration tests.

##### Key Value

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html

Altinity Key Value function tests.

##### LDAP

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/authentication/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/external_user_directory/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/role_mapping/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/authentication/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/external_user_directory/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/role_mapping/report.html

Altinity LDAP integration tests.

##### Lightweight Delete

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html

Altinity Lightweight Delete integration tests.

##### Memory

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/memory/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/memory/report.html

Altinity Memory tests.

##### Parquet

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html
* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html

Altinity Parquet format integration tests.

##### Part Moves Between Shards

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html

Altinity Part Moves Between Shards integration tests.

##### RBAC

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac/report.html

Altinity RBAC integration tests.

##### S3

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html

Altinity S3 integration tests.

##### Selects

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html

Altinity Selects tests.

##### Session Timezone

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html

Altinity Session Timezone tests.

##### Settings

Results:

* [TBD]16570238894/job/46860235336
* [TBD]16570234845/job/46860219192

Altinity Settings tests.

##### SSL Server

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server/report.html

Altinity basic SSL server integration tests.

##### Swarms

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/swarms/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/swarms/report.html

Altinity Swarms tests.

##### Tiered Storage

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/report.html

Altinity Tiered-Storage tests.

##### Version

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/version/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/version/report.html

Altinity Version tests.

##### Window Functions

Results:

* [TBD]regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html
* [TBD]regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html

Altinity Window Functions integration tests.

### Regression Tests with Sanitizers

#### ASAN
Results:
* [TBD]

#### MSAN
Results:
* [TBD]

Known issues:
* [TBD]
* [TBD]

#### UBSAN
Results:
* [TBD]

#### TSAN
Results:
* [TBD]


### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

clickhouse-driver version: 
* 0.2.9

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8-lts/clickhouse-driver/

Created Patched for version 0.2.9:
* https://github.com/Altinity/clickhouse-regression/blob/main/container-images/test/clickhouse-driver-runner/diff-0.2.9-cert.patch
* https://github.com/Altinity/clickhouse-regression/blob/main/container-images/test/clickhouse-driver-runner/diff-0.2.9-json.patch
* https://github.com/Altinity/clickhouse-regression/blob/main/container-images/test/clickhouse-driver-runner/diff-0.2.9-progress.patch
* https://github.com/Altinity/clickhouse-regression/blob/main/container-images/test/clickhouse-driver-runner/diff-0.2.9-totals.patch
* https://github.com/Altinity/clickhouse-regression/blob/main/container-images/test/clickhouse-driver-runner/diff-0.2.9.patch
  
The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

Compatibility with the [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

#### ODBC `clickhouse-odbc`

clickhouse-odbc version: 
* v1.3.0.20241018

Results: 
* [TBD]clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.

#### SQLAlchemy

clickhouse-sqlalchemy version: 
* 0.2.9

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.

#### Java `clickhouse-jdbc`

clickhouse-jdbc version: 
* 0.9.0

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8-lts/clickhouse-jdbc/

Results (DBeaver): 
* [TBD]clickhouse-jdbc/DBeaver/

The  [clickhouse-jdbc](https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results: 
* [TBD]clickhouse-backup/

Results (ACM):
* [TBD]clickhouse-backup-acm/

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

clickhouse-operator version: 
* 0.25.2

Results: 
* [TBD]clickhouse-operator/


Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).

#### Altinity.Cloud

Results: 
[TBD]

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: OK

Approved by Mikhail Filimonov. 

### Upgrade and Downgrade

Results: 
[TBD]

The upgrade and downgrade.

#### Upgrade

* from 24.8 to 25.8

#### Downgrade

* from 25.8 to 24.3

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results: 
* [TBD]grafana/

Compatibility with [Grafana].

#### Tableau

Results: [TBD]tableau/

Compatibility with [Tableau].

#### Superset

Results: [TBD]superset/

Compatibility with [Superset].

The tests were run against Superset version `4.1.1`. Currently, there is an issue with establishing a connection to ClickHouse in Superset `5.0.0 (latest)`, due to the absence of the `clickhouse-connect` library in the default setup. This default setup follows the same test procedure we used previously with version `4.1.1`.

### Docker Image Vulnerability Scanning

#### Grype

Results:

[TBD]
[TBD]
[TBD]

[Grype](https://github.com/anchore/grype) Docker image vulnerability scanner.


[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub]: https://github.com
