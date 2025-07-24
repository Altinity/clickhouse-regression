# QA-STP006 ClickHouse 23.8 Long-Term Support Release
# Software Test Plan

(c) 2023 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** Nov 1, 2023

## Execution Summary

**Completed:** Dec 27, 2023

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/

**Summary:**

Started to execute test plan on Nov 1, 2023 and ended on Dec 27, 2024.

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Timeline](#timeline)
* 4 [Human Resources And Assignments](#human-resources-and-assignments)
* 5 [End User Recommendations](#end-user-recommendations)
    * 5.1 [Release Notes](#release-notes)
    * 5.2 [Notable Differences in Behavior](#notable-differences-in-behavior)
    * 5.3 [Summary of Main Regressions](#summary-of-main-regressions)
* 6 [Known Issues](#known-issues)
    * 6.1 [Reported By Altinity](#reported-by-altinity)
    * 6.2 [Open Issues](#open-issues)
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
            * 8.1.5.17 [Data Types](#Data-types)
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
    * 8.4 [Compatibility With Operation on es](#compatibility-with-operation-on-es)
        * 8.4.1 [es `clickhouse-operator`](#es-clickhouse-operator)
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
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This test plan covers testing of ClickHouse 23.8 LTS (long-term support) release.

## Timeline

The testing of pre-stable binaries SHALL be started on Nov 1, 2023 and be completed
by Nov 30, 2023.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager, regression)
* Davit Mnatobishvili (parquet, LDAP, benchmarks, alter, extended precision data types)
* Alsu Giliazova (aggregate functions, selects, lightweight_delete)
* Stuart Gibb (clickhouse-keeper, RBAC, S3, tiered_storage)
* Andrey Antipov (clickhouse-operator, disk level encryption, Python clickhouse-driver, JDBC driver, ODBC driver, clickhouse-sqlalchemy)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup)
* Dima Borovstov (Tableau)
* Eugene Klimov (Grafana, Superset)
* Tatiana Saltykova (production cluster, upgrade and downgrade)

## End User Recommendations

### Release Notes

https://docs.altinity.com/releasenotes/altinity-stable-release-notes/23.8/

### Notable Differences in Behavior

* Insert from s3 requires more memory, so max_insert_thread in tests was lowered.
* Sparkbar aggregate function overflow was fixed after 23.4.
* Different result of topKWeightedMerge aggregate function in versions 23.3.2.37 and 23.8.4.69  
  https://github.com/ClickHouse/ClickHouse/issues/55997
* Column name and table name conflict when allow_experimental_analyzer=1  
  https://github.com/ClickHouse/ClickHouse/issues/56371
* Using the array of `Int128` inside the following `arrayDifference`, `arrayCumSum` and `arrayCumSumNonNegative` functions no longer results in the exception.
    ```sql
    SELECT arrayDifference(array(toInt128('3'), toInt128('2'), toInt128('1')));
    SELECT arrayCumSum(array(toInt128('3'), toInt128('2'), toInt128('1')));
    SELECT arrayCumSumNonNegative(array(toInt128('3'), toInt128('2'), toInt128('1')));
    ```
* `SELECT bitCount(toInt128('170141183460469231731687303715884105727'));` now shows correct 127 bits instead of 64.
* `SELECT modulo(toDecimal256(1,0), toDecimal256(1,0));` no longer results in a `Exception: Illegal types`.
* When granting roles to a user that is in an active clickhouse-client session, the role change can not be observed by a user until the clickhouse-client instance is restarted.  
  https://github.com/ClickHouse/ClickHouse/issues/56646
* When using clickhouse keeper-converter, the output directory for the snapshots must exist and will not be created automatically
* SYSTEM RELOAD SYMBOLS has been removed
* Access error with skip_access_check=1 now raises on CREATE instead of waiting for INSERT

### Summary of Main Regressions

## Known Issues

### Reported By Altinity

* Different result of topKWeightedMerge aggregate function in versions 23.3.2.37 and 23.8.4.69   
  https://github.com/ClickHouse/ClickHouse/issues/55997
  
* Column name and table name conflict when allow_experimental_analyzer=1  
  https://github.com/ClickHouse/ClickHouse/issues/56371

* Role changes can’t be observed in active clickhouse-client sessions  
  https://github.com/ClickHouse/ClickHouse/issues/56646

* Net Exception: Cannot assign requested address when trying to insert data from the s3 storage  
  https://github.com/ClickHouse/ClickHouse/issues/56678

* Starting 23.8 MemoryTracker messages will be ignored if the amount is too small
  https://github.com/ClickHouse/ClickHouse/issues/57522
  https://github.com/mymarilyn/clickhouse-driver/issues/403

### Open Issues

[GitHub is:issue is:open label:v23.8-affected](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+is%3Aopen+label%3Av23.8-affected+) as of Nov 13, 2023

* allow_nullable_key + Final = incorrect result  
  https://github.com/ClickHouse/ClickHouse/issues/56417
* List of CTEs in IN clause not recognized when used in subquery  
  https://github.com/ClickHouse/ClickHouse/issues/55981
* JSONEachRow format is incorrect when used with select from parameterized view  
  https://github.com/ClickHouse/ClickHouse/issues/55709
* Versions 23.4-23.8: Parquet files importing issue  
  https://github.com/ClickHouse/ClickHouse/issues/55487
* v23.3.13.6-lts Unexpected behaviour : NOT FOUND COLUMN IN BLOCK exception  
  https://github.com/ClickHouse/ClickHouse/issues/55466
* 23.1+ join disables PREWHERE optimization  
  https://github.com/ClickHouse/ClickHouse/issues/55265
* Light Weight Delete does not works well with limit  
  https://github.com/ClickHouse/ClickHouse/issues/54392
* clickhouse starts with readonly table without try to fix it and reports ReplicasMaxAbsoluteDelay / ReadonlyReplica incorrectly  
  https://github.com/ClickHouse/ClickHouse/issues/53479
* Some queries does not respect max_threads and can make server non-responsible by starting too many threads  
  https://github.com/ClickHouse/ClickHouse/issues/53287
* Column is not under aggregate function and not in GROUP BY in mat view in 23.5  
  https://github.com/ClickHouse/ClickHouse/issues/50928
* Regression in nested SELECT (might be related to WINDOW function)  
  https://github.com/ClickHouse/ClickHouse/issues/47217
* Segfault after alter table on target of nullable materialized column  
  https://github.com/ClickHouse/ClickHouse/issues/42918

### Summary

Build report: https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/report.html

> `Pass*` - Pass with known fails

| Test Suite  | Result                                | Comments |
| --- |---------------------------------------| --- |
| Stateless | [Pass*](#stateless)                        |   |
| Stateful | [Pass](#stateful)                         |   |
| Stress | [not executed](#stress)                  |  Not executed  |
| Integration | [Pass*](#integration)                      |   |
| Key Value | [Pass](#key-value)                        |   |
| Engines  | [not executed](#engines)                          | Not executed  |
| Parquet | [Pass](#parquet)                          |   |
| Tiered Storage (Local) | [Pass](#tiered-storage)                   |   |
| Tiered Storage (MinIO) | [Pass](#tiered-storage)                   |   |
| Tiered Storage (AWS) | [Pass](#tiered-storage)                   |   |
| Tiered Storage (GCS) | [Pass*](#tiered-storage)                   |   |
| S3 (AWS) | [Pass*](#s3)                               |  |
| S3 (MinIO) | [Pass](#s3)                               |   |
| S3 (GCS) | [Pass](#s3)                               |   |
| Selects | [Pass](#selects)                          |   |
[ Session Timezone | [Pass](#session-timezone)        |   |
| AES Encryption | [Pass](#aes-encryption)                   |   |
| Atomic Insert | [Pass](#atomic-insert)                    |   |
| Base58 | [Pass](#base58)                          |   |
| DNS | [Pass](#dns)                              |   |
| Kafka | [Pass](#kafka)                            |   |
| Kerberos | [Pass](#kerberos)                         |   |
| DateTime64 Extended Range | [Pass](#datetime64-extended-range)        |   |
| Extended Precision Data Types | [Pass](#extended-precision-data-types)    |   |
| LDAP | [Pass](#ldap)                             |   |
| RBAC | [Pass](#rbac)                             |   |
| Window Functions | [Pass*](#window-functions)                 |   |
| SSL Server | [Pass](#ssl-server)                       |   |
| Disk Level Encryption | [Pass](#disk-level-encryption)            |   |
| ClickHouse Keeper | [Pass](#clickhouse-keeper)                |   |
| Data Types | [Pass](#data-types)                         |   |
| Ontime Bechmark | [Pass](#ontime-benchmark)                 
| Part Moves Between Shards | [Pass](#part-moves-between-shards)        |   |
| Lightweight Delete | [Pass](#lightweight-delete)               |    |
| Aggregate Functions | [Pass](#aggregate-functions)              |   |
| Python `clickhouse_driver` | [Pass*](#python-clickhouse_driver)    |   |
| ODBC `clickhouse-odbc` | [Pass](#odbc-clickhouse-odbc)         |  |
| SQLAlchemy | [Pass](#sqlalchemy)                   |    |
| Java `clickhouse-jdbc` | [Pass](#java-clickhouse-jdbc)         |   |
| Java `clickhouse-jdbc` (DBeaver) | [Pass](#java-clickhouse-jdbc)         |   |
| Backup `clickhouse-backup` | [Pass](#backup-clickhouse-backup)     |   |
| Kubernetes `clickhouse-operator` | [Pass](#kubernetes-clickhouse-operator)   |   |
| Altinity.Cloud | [Pass](#altinitycloud)                |   |
| Production Cluster Operation | [Pass](#production-cluster-operation) |   |
| Upgrade And Downgrade | [Pass](#upgrade-and-downgrade)        |   |
| Grafana | [Pass](#grafana)                          |   |
| Tableau | [Pass](#tableau)                          |   |
| Superset | [Pass](#superset)                         |   |
| Trivy | [Pass](#trivy)                            |   |
| Scout | [Pass](#scout)                            |   |

## Scope

The scope of testing ClickHouse 23.8 LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/stateless/amd64/stateless_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/stateless/aarch64/stateless_results.html

The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.

#### Stateful

Results:

* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/stateful/amd64/stateful_results.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/stateful/aarch64/stateful_results.html

The standard `stateful` suite that consists of running SQL scripts executed against a predefined database schema.

#### Stress

Results: not executed

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/integration/integration_results_1.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/integration/integration_results_2.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/integration/integration_results_3.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/integration/integration_results_4.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/integration/integration_results_5.html
* https://s3.amazonaws.com/altinity-test-reports/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/integration/integration_results_6.html

The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### Key Value

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/key_value/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/key_value/report.html

Altinity Key Value function tests.

##### Engines

Results: not executed

Altinity Engines tests.

##### Selects

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/selects/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/selects/report.html

Altinity Selects tests.

##### Session Timezone

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/session_timezone/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/session_timezone/report.html

Altinity Session Timezone tests.

##### AES Encryption

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/aes_encryption/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/aes_encryption/report.html

Altinity AES Encryption tests.

##### Tiered-storage

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/tiered_storage/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/tiered_storage/s3amazon/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/tiered_storage/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/tiered_storage/s3gcs/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/tiered_storage/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/tiered_storage/s3amazon/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/tiered_storage/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/tiered_storage/s3gcs/report.html

Altinity Tiered-Storage tests.

##### S3

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/s3/aws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/s3/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/s3/gcs/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/s3/aws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/s3/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/s3/gcs/report.html

Altinity S3 integration tests.

##### Kafka

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/kafka/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/kafka/report.html

Altinity Kafka integration tests.

##### Kerberos

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/kerberos/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/kerberos/report.html

Altinity Kerberos integration tests.

##### DateTime64 Extended Range

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/datetime64_extended_range/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/datetime64_extended_range/report.html

Altinity DateTime64 extended range integration tests.

##### Extended Precision Data Types

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/extended_precision_data_types/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/extended_precision_data_types/report.html

Altinity Extended Precision Data Types integration tests.

##### LDAP

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/ldap/authentication/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/ldap/external_user_directory/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/ldap/role_mapping/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/ldap/authentication/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/ldap/external_user_directory/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/ldap/role_mapping/report.html

Altinity LDAP integration tests.

##### RBAC

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/rbac/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/rbac/report.html

Altinity RBAC integration tests.

##### Window Functions

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/window_functions/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/window_functions/report.html

Altinity Window Functions integration tests.

##### SSL Server

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/ssl_server/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/ssl_server/report.html

Altinity basic SSL server integration tests.

##### Disk Level Encryption

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/disk_level_encryption/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/disk_level_encryption/report.html

Altinity Disk Level Encryption integration tests.

##### ClickHouse Keeper

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/clickhouse_keeper/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/clickhouse_keeper/ssl/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/clickhouse_keeper/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/clickhouse_keeper/ssl/report.html

Altinity ClickHouse Keeper integration tests.

##### Data Types

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/data_types/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/data_types/report.html

Altinity data types integration tests.

##### Part Moves Between Shards

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/part_moves_between_shards/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/part_moves_between_shards/report.html

Altinity Part Moves Between Shards integration tests.

##### Lightweight Delete

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/lightweight_delete/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/lightweight_delete/report.html

Altinity Lightweight Delete integration tests.

##### Base58

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/base_58/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/base_58/report.html

Altinity Base58 encode and decode functions integration tests.

##### Parquet

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/parquet/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/parquetaws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/parquetminio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/parquet/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/parquetaws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/parquetminio/report.html

Altinity Parquet format integration tests.


##### Atomic Insert

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/atomic_insert/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/atomic_insert/report.html

Altinity Atomic Insert integration tests.

##### Aggregate Functions

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/aggregate_functions/report.html
* https://github.com/Altinity/clickhouse-regression/actions/runs/7324808186/job/19948716863
  
Altinity Aggregate Functions integration tests.

##### DNS

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/dns/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/dns/report.html

Altinity DNS integration tests.

#### Ontime Benchmark

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/ontime_benchmark/aws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/ontime_benchmark/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/x86_64/ontime_benchmark/gcs/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/ontime_benchmark/aws_s3/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/ontime_benchmark/minio/report.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/regression/aarch64/ontime_benchmark/gcs/report.html

Altinity OnTime Benchmark tests.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

clickhouse-driver version: 0.2.6

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-driver/

The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

```
Test: tests/test_blocks.py
Reason: clickhouse expected message text is changed.
Status: [Fail](https://github.com/mymarilyn/clickhouse-driver/issues/403)
```

#### ODBC `clickhouse-odbc`

clickhouse-odbc version: v1.2.1.20220905

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.


#### SQLAlchemy

clickhouse-sqlalchemy version: 0.3.0

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.


#### Java `clickhouse-jdbc`

clickhouse-jdbc version: v0.5.0

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-jdbc/

DBeaver version: 23.2.5

Results (DBeaver): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-jdbc/DBeaver/

The (https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-backup/
Results (ACM): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-backup-acm/

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/clickhouse-operator/

clickhouse-operator version: 0.23.0

Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).


#### Altinity.Cloud

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/acm-launch-and-upgrade/launch_with_23.8.5.17.altinitytest/

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/acm-launch-and-upgrade/launch_with_23.8.5.17.altinitytest/

Operation on a production clusters.

### Upgrade and Downgrade

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/acm-launch-and-upgrade/upgrade_downgrade_from_23.3.13.7.altinitystable_to_23.8.5.17.altinitytest/

The upgrade and downgrade.

#### Upgrade

* from 22.3 to 23.8

#### Downgrade

* from 23.8 to 23.3

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/grafana/

Compatibility with [Grafana].

#### Tableau

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/tableau/

Compatibility with [Tableau].

#### Superset

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/superset/

Compatibility with [Superset].

### Docker Image Vulnerability Scanning

#### Trivy

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/report.html#trivy-x86_64-results
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/staging-docker-trivy-ubuntu-server-arm64/results.html

Trivy Docker image vulnerability scanner.

#### Scout

Results:

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/staging-docker-scout-ubuntu-server-amd64/results.html
* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v23.8.8.21.altinitystable/2023-12-26T23-40-44.341/staging-docker-scout-ubuntu-server-arm64/results.html

Scout Docker image vulnerability scanner.

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/docs/qa_stp006_clickhouse-23.8_longterm_support_release.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/docs/qa_stp006_clickhouse_23.8_longterm_support_release.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
