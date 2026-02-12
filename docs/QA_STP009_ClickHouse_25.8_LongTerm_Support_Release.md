# QA-STP009 ClickHouse 25.8 Long-Term Support Release  
# Software Test Plan

(c) 2025 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** [TBD]

## Execution Summary

**Completed:** [TBD]

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/

**Build Report:**

* https://s3.amazonaws.com/altinity-build-artifacts/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/21752809609/ci_run_report.html

**Summary:**

Not approved for release.

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
* Downgrade from 25.8 to 25.3 fails with error `Code: 79` (`Unknown mark file extension: '4'`) while loading `system.*_log` tables.

### Open Issues

* [distributed_ddl replicas_path mismatch causing ON CLUSTER DDL to hang](https://github.com/Altinity/ClickHouse/issues/1391) - results in 12 scenario failures


### Summary
Build report: [TBD]

> [!NOTE]
> **\*Pass** - tests passed with known fails

| Test Suite  | Result                                        | Comments |
| --- |-----------------------------------------------| --- |
| Stateless | [Pass](#stateless)                     |   |
| Stateful | [Pass](#stateful)                      |   |
| Stress | [Pass](#stress)                        |   |
| Integration | [*Pass](#integration)                   | 1 CI Error with ASAN |
| AES Encryption | [Pass](#aes-encryption)                |   |
| Aggregate Functions | [Pass](#aggregate-functions)           |   |
| Alter | [Pass](#alter)                 |   |
| Atomic Insert | [Pass](#atomic-insert)                 |   |
| Attach | [Pass](#attach)                        |   |
| Base58 | [Pass](#base58)                        |   |
| Ontime Benchmark | [Pass](#ontime-benchmark)              |   |
| ClickHouse Keeper | [Pass](#clickhouse-keeper)             |   |
| ClickHouse Keeper Failover | [Pass](#clickhouse-keeper-failover)   |   |
| Data Types | [Pass](#data-types)                    |   |
| DateTime64 Extended Range | [Pass](#datetime64-extended-range)     |   |
| Disk Level Encryption | [Pass](#disk-level-encryption)         |   |
| DNS | [Pass](#dns)                           |   |
| Engines  | [Pass](#engines)                       |  |
| Example | [Pass](#example)                       |   |
| Extended Precision Data Types | [Pass](#extended-precision-data-types) |   |
| Functions | [Pass](#functions)                     |   |
| Hive Partitioning | [Pass](#hive-partitioning)           |   |
| Iceberg | [Pass](#iceberg)                       |   |
| JWT Authentication | [Pass](#jwt-authentication)           |   |
| Kafka | [Pass](#kafka)                         |   |
| Kerberos | [Pass](#kerberos)                      |   |
| Key Value | [Pass](#key-value)                     |   |
| LDAP | [Pass](#ldap)                          |   |
| Lightweight Delete | [Pass](#lightweight-delete)            |    |
| Memory | [Pass](#memory)                       |   |
| Parquet | [Pass](#parquet)                       |   |
| Part Moves Between Shards | [Pass](#part-moves-between-shards)     |   |
| RBAC | [Pass](#rbac)                          |   |
| S3 | [Pass](#s3)                           |  |
| Selects | [Pass](#selects)                       |   |
| Session Timezone | [Pass](#session-timezone)              |   |
| Settings | [Pass](#settings)                      |   |
| SSL Server | [Pass](#ssl-server)                    |   |
| Swarms | [Pass](#swarms)                        |   |
| Tiered Storage | [Pass](#tiered-storage)                |   |
| Version | [Pass](#version)                       |   |
| Window Functions | [Pass](#window-functions)             |   |
| Python `clickhouse_driver` | [Pass](#python-clickhouse_driver)            | 377 passed, 109 skipped  |
| ODBC `clickhouse-odbc` | [Pass](#odbc-clickhouse-odbc)                 |  |
| SQLAlchemy | [Pass](#sqlalchemy)                           | 388 passed, 27 warnings   |
| Java `clickhouse-jdbc` | [Pass](#java-clickhouse-jdbc)                 |  Tests run: 232, Failures: 0, Errors: 0, Skipped: 0 |
| Java `clickhouse-jdbc` (DBeaver) | [Pass](#java-clickhouse-jdbc)          |   |
| Backup `clickhouse-backup` | [Pass](#backup-clickhouse-backup)             |   |
| Kubernetes `clickhouse-operator` | [Fail](#kubernetes-clickhouse-operator)       | 12 Fails, related to: [issue](https://github.com/Altinity/ClickHouse/issues/1391)  |
| Altinity.Cloud | [Pass](#altinitycloud)                        |   |
| Production Cluster Operation | [TBD](#production-cluster-operation)         |   |
| Upgrade And Downgrade | [Pass](#upgrade-and-downgrade)                | Downgrade to 25.3 failed due to `Unknown mark file extension: '4'` when loading `system.*_log` tables.  |
| Grafana | [Pass](#grafana)                              |   |
| Tableau | [*Pass](#tableau)                     | 849 passed, 24 failed (97%). Expected fails. |
| Superset | [Pass](#superset)                             |   |
| Grype | [Pass](#grype)                         |   |

## Scope

The scope of testing ClickHouse 25.8 Altinity Stable LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

* ARM Binary
  * [Stateless tests (arm_binary, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28arm_binary%2C+parallel%29&name_2=Tests) 
  * [Stateless tests (arm_binary, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28arm_binary%2C+sequential%29&name_2=Tests)
 
* ARM Coverage
  * [Stateless tests (arm_coverage, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28arm_coverage%2C+parallel%29&name_2=Tests)
  * [Stateless tests (arm_coverage, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28arm_coverage%2C+sequential%29&name_2=Tests)

* AMD Binary
  * [Stateless tests (amd_binary, ParallelReplicas, s3 storage, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_binary%2C+ParallelReplicas%2C+s3+storage%2C+parallel%29&name_2=Tests)
  * [Stateless tests (amd_binary, ParallelReplicas, s3 storage, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_binary%2C+ParallelReplicas%2C+s3+storage%2C+sequential%29&name_2=Tests)
  * [Stateless tests (amd_binary, old analyzer, s3 storage, DatabaseReplicated, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_binary%2C+old+analyzer%2C+s3+storage%2C+DatabaseReplicated%2C+parallel%29&name_2=Tests)
  * [Stateless tests (amd_binary, old analyzer, s3 storage, DatabaseReplicated, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_binary%2C+old+analyzer%2C+s3+storage%2C+DatabaseReplicated%2C+sequential%29&name_2=Tests)
 
* AMD Debug
  * [Stateless tests (amd_debug, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_debug%2C+parallel%29&name_2=Tests)
  * [Stateless tests (amd_debug, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_debug%2C+sequential%29&name_2=Tests)
  * [Stateless tests (amd_debug, AsyncInsert, s3 storage, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_debug%2C+AsyncInsert%2C+s3+storage%2C+parallel%29&name_2=Tests)
  * [Stateless tests (amd_debug, AsyncInsert, s3 storage, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_debug%2C+AsyncInsert%2C+s3+storage%2C+sequential%29&name_2=Tests)
  * [Stateless tests (amd_debug, distributed plan, s3 storage, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_debug%2C+distributed+plan%2C+s3+storage%2C+parallel%29&name_2=Tests)
  * [Stateless tests (amd_debug, distributed plan, s3 storage, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_debug%2C+distributed+plan%2C+s3+storage%2C+sequential%29&name_2=Tests)

* AMD UBSan
  * [Stateless tests (amd_ubsan, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_ubsan%2C+parallel%29&name_2=Tests)
  * [Stateless tests (amd_ubsan, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_ubsan%2C+sequential%29&name_2=Tests)

* AMD ASan
  * [Stateless tests (amd_asan, distributed plan, parallel, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_asan%2C+distributed+plan%2C+parallel%2C+1%2F2%29&name_2=Tests)
  * [Stateless tests (amd_asan, distributed plan, parallel, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_asan%2C+distributed+plan%2C+parallel%2C+2%2F2%29&name_2=Tests)
  * [Stateless tests (amd_asan, distributed plan, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_asan%2C+distributed+plan%2C+sequential%29&name_2=Tests)

* AMD MSan
  * [Stateless tests (amd_msan, parallel, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_msan%2C+parallel%2C+1%2F2%29&name_2=Tests)
  * [Stateless tests (amd_msan, parallel, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_msan%2C+parallel%2C+2%2F2%29&name_2=Tests)
  * [Stateless tests (amd_msan, sequential, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_msan%2C+sequential%2C+1%2F2%29&name_2=Tests)
  * [Stateless tests (amd_msan, sequential, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_msan%2C+sequential%2C+2%2F2%29&name_2=Tests)

* AMD TSan
  * [Stateless tests (amd_tsan, parallel, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_tsan%2C+parallel%2C+1%2F2%29&name_2=Tests)
  * [Stateless tests (amd_tsan, parallel, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_tsan%2C+parallel%2C+2%2F2%29&name_2=Tests)
  * [Stateless tests (amd_tsan, sequential, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_tsan%2C+sequential%2C+1%2F2%29&name_2=Tests)
  * [Stateless tests (amd_tsan, sequential, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_tsan%2C+sequential%2C+2%2F2%29&name_2=Tests)
  * [Stateless tests (amd_tsan, s3 storage, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_tsan%2C+s3+storage%2C+parallel%29&name_2=Tests)
  * [Stateless tests (amd_tsan, s3 storage, sequential, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_tsan%2C+s3+storage%2C+sequential%2C+1%2F2%29&name_2=Tests)
  * [Stateless tests (amd_tsan, s3 storage, sequential, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stateless+tests+%28amd_tsan%2C+s3+storage%2C+sequential%2C+2%2F2%29&name_2=Tests)
 


The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.

#### Stress

Results:

* [Stress test (amd_debug)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stress+test+%28amd_debug%29)
* [Stress test (amd_msan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stress+test+%28amd_msan%29)
* [Stress test (amd_tsan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stress+test+%28amd_tsan%29)
* [Stress test (amd_ubsan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Stress+test+%28amd_ubsan%29)

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

* ARM Binary
  * [Integration tests (arm_binary, distributed plan, 1/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28arm_binary%2C+distributed+plan%2C+1%2F4%29&name_2=Tests)
  * [Integration tests (arm_binary, distributed plan, 2/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28arm_binary%2C+distributed+plan%2C+2%2F4%29&name_2=Tests)
  * [Integration tests (arm_binary, distributed plan, 3/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28arm_binary%2C+distributed+plan%2C+3%2F4%29&name_2=Tests)
  * [Integration tests (arm_binary, distributed plan, 4/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28arm_binary%2C+distributed+plan%2C+4%2F4%29&name_2=Tests)

* AMD Binary
  * [Integration tests (amd_binary, 1/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_binary%2C+1%2F5%29&name_2=Tests)
  * [Integration tests (amd_binary, 2/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_binary%2C+2%2F5%29&name_2=Tests)
  * [Integration tests (amd_binary, 3/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_binary%2C+3%2F5%29&name_2=Tests)
  * [Integration tests (amd_binary, 4/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_binary%2C+4%2F5%29&name_2=Tests)
  * [Integration tests (amd_binary, 5/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_binary%2C+5%2F5%29&name_2=Tests)

* AMD ASan
  * [Integration tests (amd_asan, old analyzer, 1/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_asan%2C+old+analyzer%2C+1%2F6%29&name_2=Tests)
  * [Integration tests (amd_asan, old analyzer, 2/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_asan%2C+old+analyzer%2C+2%2F6%29&name_2=Tests)
  * [Integration tests (amd_asan, old analyzer, 3/6)](https://github.com/Altinity/ClickHouse/actions/runs/21752809609/job/63286184873) - CI ERROR OOM
  * [Integration tests (amd_asan, old analyzer, 4/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_asan%2C+old+analyzer%2C+4%2F6%29&name_2=Tests)
  * [Integration tests (amd_asan, old analyzer, 5/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_asan%2C+old+analyzer%2C+5%2F6%29&name_2=Tests)
  * [Integration tests (amd_asan, old analyzer, 6/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_asan%2C+old+analyzer%2C+6%2F6%29&name_2=Tests)

* AMD TSan
  * [Integration tests (amd_tsan, 1/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_tsan%2C+1%2F6%29&name_2=Tests)
  * [Integration tests (amd_tsan, 2/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_tsan%2C+2%2F6%29&name_2=Tests)
  * [Integration tests (amd_tsan, 3/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_tsan%2C+3%2F6%29&name_2=Tests)
  * [Integration tests (amd_tsan, 4/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_tsan%2C+4%2F6%29&name_2=Tests)
  * [Integration tests (amd_tsan, 5/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_tsan%2C+5%2F6%29&name_2=Tests)
  * [Integration tests (amd_tsan, 6/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=releases%2F25.8.16&sha=dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272&name_0=MasterCI&name_1=Integration+tests+%28amd_tsan%2C+6%2F6%29&name_2=Tests)


The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### AES Encryption

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html

Altinity AES Encryption tests.

##### Aggregate Functions

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions3/report.html
  
Altinity Aggregate Functions integration tests.

##### Alter

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter1/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter2/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter/move_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter/replace_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter1/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter2/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter/move_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter/replace_partition/report.html

Altinity Alter tests.

##### Atomic Insert

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html

Altinity Atomic Insert integration tests.

##### Attach

Results:

* https://github.com/Altinity/clickhouse-regression/actions/runs/21930308353/job/63345293900
* https://github.com/Altinity/clickhouse-regression/actions/runs/21930289188/job/63332529761

Altinity Attach tests.

##### Base58

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html

Altinity Base58 encode and decode functions integration tests.

##### Ontime Benchmark

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/minio/report.html

Altinity OnTime Benchmark tests.

##### ClickHouse Keeper

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/ssl/report.html

Altinity ClickHouse Keeper integration tests.

##### ClickHouse Keeper Failover

Results:

* https://github.com/Altinity/clickhouse-regression/actions/runs/21930308353/job/63345293709
* https://github.com/Altinity/clickhouse-regression/actions/runs/21930289188/job/63332529783

Altinity ClickHouse Keeper Failover integration tests.

##### Data Types

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html

Altinity data types integration tests.

##### DateTime64 Extended Range

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html

Altinity DateTime64 extended range integration tests.

##### Disk Level Encryption

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html

Altinity Disk Level Encryption integration tests.

##### DNS

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html

Altinity DNS integration tests.

##### Engines

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html

Altinity Engines tests.

##### Example

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/example/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/example/report.html

Altinity Example tests.

##### Extended Precision Data Types

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html

Altinity Extended Precision Data Types integration tests.

##### Functions

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/functions/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/functions/report.html

Altinity Functions tests.

##### Iceberg

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg2/report.html

Altinity Iceberg tests.


##### JWT Authentication

Results:

* https://github.com/Altinity/clickhouse-regression/actions/runs/21930308353/job/63345302185
* https://github.com/Altinity/clickhouse-regression/actions/runs/21930289188/job/63332529810

Altinity JWT Authentication tests.

##### Kafka

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html

Altinity Kafka integration tests.

##### Kerberos

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html

Altinity Kerberos integration tests.

##### Key Value

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html

Altinity Key Value function tests.

##### LDAP

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/authentication/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/external_user_directory/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/role_mapping/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/authentication/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/external_user_directory/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/role_mapping/report.html

Altinity LDAP integration tests.

##### Lightweight Delete

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html

Altinity Lightweight Delete integration tests.

##### Memory

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/memory/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/memory/report.html

Altinity Memory tests.

##### Parquet

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html

Altinity Parquet format integration tests.

##### Part Moves Between Shards

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html

Altinity Part Moves Between Shards integration tests.

##### RBAC

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac3/report.html

Altinity RBAC integration tests.

##### S3

AWS Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/aws_s3/report.html

Azure Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/azure/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/azure/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/azure/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/azure/report.html

GCS Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/gcs/report.html

MinIO Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s33/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s33/minio/report.html

Export Parts Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s3part/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s3part/minio/report.html

Export Partition Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s3partition/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s3partition/minio/report.html


Altinity S3 integration tests.

##### Selects

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html

Altinity Selects tests.

##### Session Timezone

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html

Altinity Session Timezone tests.

##### Settings

Results:

* https://github.com/Altinity/clickhouse-regression/actions/runs/21930308353/job/63403280149
* https://github.com/Altinity/clickhouse-regression/actions/runs/21930289188/job/63403233526

Altinity Settings tests.

##### SSL Server

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server3/report.html

Altinity basic SSL server integration tests.

##### Swarms

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/swarms/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/swarms/report.html

Altinity Swarms tests.

##### Tiered Storage

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/local/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3amazon/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/local/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3amazon/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3gcs/report.html

Altinity Tiered-Storage tests.

##### Version

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/version/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/version/report.html

Altinity Version tests.

##### Window Functions

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html

Altinity Window Functions integration tests.

### Regression Tests with Sanitizers

#### ASAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21893377525

Known issues:
* [TBD]

#### MSAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21893427037

Known issues:
* [TBD]

#### UBSAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21893452122

Known issues:
* [TBD]

#### TSAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21893404832

Known issues:
* [TBD]

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

clickhouse-driver version: 
* 0.2.10

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-driver/
  
The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

Compatibility with the [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

#### ODBC `clickhouse-odbc`

clickhouse-odbc version: 
* v1.3.0.20241018

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.

#### SQLAlchemy

clickhouse-sqlalchemy version: 
* 0.2.9

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.

#### Java `clickhouse-jdbc`

clickhouse-jdbc version: 
* 0.9.0

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-jdbc/

Results (DBeaver): 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/DBeaver/

The  [clickhouse-jdbc](https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-backup/

Results (ACM):
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-backup-acm/

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

clickhouse-operator version: 
* 0.25.2

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-operator/


Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).

#### Altinity.Cloud

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/acm-launch-and-upgrade/launch_with_25.8.16.10001.altinitytest/

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: OK

Approved by Mikhail Filimonov. 

### Upgrade and Downgrade

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/acm-launch-and-upgrade/upgrade_downgrade_from_25.3.6.10034.altinitystable_to_25.8.4.20014.altinitytest/
* Failed due to `Code: 79` (`Unknown mark file extension: '4'`) when attaching/loading `system.*_log` tables.
* Downgrade to previous 25.8.x versions works.

The upgrade and downgrade.

#### Upgrade

* from 25.3 to 25.8

#### Downgrade

* From 25.8 to 25.3

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/grafana/

Compatibility with [Grafana].

#### Tableau

Results:
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/tableau/

Compatibility with [Tableau].

**TDVT results:** 849 passed, 24 failed (97% pass rate). All failures are expected and attributable to ClickHouse or connector limitations, not data loading issues.

**Failure breakdown:**

1. **`time0`/`time1` as String (2 failures)** — calcs_data.time tests. ClickHouse returns quoted strings like `"1899-12-30 21:07:32"` but TDVT expects datetime-formatted values like `#21:07:32#`. This is because time0/time1 are Nullable(String); ClickHouse has no TIME type and time0 has pre-1900 timestamps.
2. **`datetime0 - time0` operations (3 failures)** — operator.datetime.minus_time. Cannot subtract a String from a DateTime. Same root cause as above.
3. **DATETIME cast of pre-1900 dates (3 failures)** — cast.str.datetime. Parsing `'1900-01-01 01:00:00'` etc. returns `#1970-01-01#` instead of the correct value. ClickHouse's DateTime type cannot represent pre-1970 timestamps.
4. **`Date32 - Date32` arithmetic (7 failures)** — date.math.date_minus_date and date.B639952. ClickHouse does not support the minus operator between two Date32 values (known ClickHouse limitation).
5. **`DATE(num4)` cast (1 failure)** — date.cast.num_to_date. Off by one day (`#1970-01-01#` vs `#1969-12-31#`), likely an epoch rounding issue.
6. **Filter.datetime_fractional (1 failure)** — ClickHouse DateTime has no sub-second precision, so .123 is lost.
7. **NULL join tests (6 failures)** — join.null.bool/date/datetime/int/real/str. The connector's INNER JOIN does not match NULL keys, so rows with NULL join columns are excluded (connector behavior).
8. **BUGS.B641638 (1 failure)** — `$IN_SET$` with mixed time0 types. Tableau's IN filter combines SUM with time0; time0 is Nullable(String), so the connector errors ("No such function `$IN_SET$` that takes arguments of type (str, datetime, ...)"). Same root cause as 1 and 2 — no native TIME type in ClickHouse.

**TDVT version comparison:** All three builds produced identical results:

| Version                          | Failures |
|----------------------------------|----------|
| Latest LTS (Altinity 25.8)       | 24       |
| Previous LTS (Altinity 25.3)     | 24       |
| Upstream (ClickHouse 25.8.16.34) | 24       |

All 24 failures are the exact same set across all three builds. They are pre-existing ClickHouse/JDBC connector limitations, not version-specific regressions.

#### Superset

Results:
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/superset/

Compatibility with [Superset].

The tests were run against Superset version `4.1.1`. Currently, there is an issue with establishing a connection to ClickHouse in Superset `5.0.0 (latest)`, due to the absence of the `clickhouse-connect` library in the default setup. This default setup follows the same test procedure we used previously with version `4.1.1`.

### Docker Image Vulnerability Scanning

#### Grype

Results:

https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/grype/altinityinfra_clickhouse-keeper_0-25.8.16.10001.altinitytest/results.html
https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/grype/altinityinfra_clickhouse-server_0-25.8.16.10001.altinitytest-alpine/results.html
https://altinity-build-artifacts.s3.amazonaws.com/REFs/releases/25.8.16/dba4ab3dbd1680ab8620fcc4c1f9209c1e2f8272/grype/altinityinfra_clickhouse-server_0-25.8.16.10001.altinitytest/results.html

[Grype](https://github.com/anchore/grype) Docker image vulnerability scanner.


[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub]: https://github.com
