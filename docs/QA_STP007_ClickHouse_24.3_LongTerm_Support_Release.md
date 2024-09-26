# QA-STP007 ClickHouse 24.3 Long-Term Support Release
# Software Test Plan

(c) 2024 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** July 1, 2024

## Execution Summary

**Completed:** August 31, 2024

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/

**Build Report:**

* https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.3.5.48.altinityfips/2024-08-30T17-37-09.905/report.html

**Summary:**

Started to execute test plan on July 1, 2024 and ended on August 31, 2024.

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
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This test plan covers testing of ClickHouse 24.3 LTS (long-term support) Altinity Stable release.

## Timeline

The testing of pre-stable binaries SHALL be started on July 1, 2024 and be completed
by July 15, 2023.

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

https://docs.altinity.com/releasenotes/altinity-stable-release-notes/24.3/altinity-stable-24.3.4/ **TBD**

### Notable Differences in Behavior

* Analyzer is enabled by default.
* Multiple array joins.
* Final can be passed to particular table in joins.
* Refreshable materialized views.
* S3 queue.
* PASTE JOIN.
* Variant data type.

### Summary of Main Regressions

## Known Issues

### Reported By Altinity

* https://github.com/ClickHouse/ClickHouse/issues/62791 (usability, no answer, 24.3 affected)
* https://github.com/ClickHouse/ClickHouse/issues/63107 (question, no answer, issue appeared in 24.3)
* https://github.com/ClickHouse/ClickHouse/issues/64746 (unexpected behaviour | minor, no answer, 24.3 affected)
* https://github.com/ClickHouse/ClickHouse/issues/65134 (unexpected behaviour, no answer, issue appeared in 24.3, was fixed in 24.3.4)
* https://github.com/ClickHouse/ClickHouse/issues/65146 (unexpected behaviour, no answer, issue appeared in 24.3 since analyzer is on by default)
* https://github.com/ClickHouse/ClickHouse/issues/63960 (bug | analyzer, fixed by upstream, appeared in 24.3)
* https://github.com/ClickHouse/ClickHouse/issues/63818 (potential bug | invalid, issue fixed by analyzer, 24.3 affected) - will not be fixed without analyzer
* https://github.com/ClickHouse/ClickHouse/issues/63539  (analyzer | bug | unexpected behaviour, fixed by upstream,  issue appeared in 24.3)
* https://github.com/ClickHouse/ClickHouse/issues/63118 (comp-aarch64 | invalid | unexpected behaviour, not important, issue appeared in 24.3)
* https://github.com/ClickHouse/ClickHouse/issues/62905 (potential bug, fixed by developer, 24.3 affected | crashing the server)
* https://github.com/ClickHouse/ClickHouse/issues/63701 (bug | analyzer, fixed by upstream, appeared in 24.3)
* https://github.com/ClickHouse/ClickHouse/issues/62042 (backward compatibility | st-fixed, reverted by milovidov, appeared in 24.3)
* https://github.com/ClickHouse/ClickHouse/issues/64965 (feature, not yet implemented, 24.3 affected)
* https://github.com/ClickHouse/ClickHouse/issues/62459 (unexpected behaviour, fixed, 24.3 affected)
* https://github.com/ClickHouse/ClickHouse/issues/62580 (unfinished code, not fixed yet, 24.3 affected)
* https://github.com/ClickHouse/ClickHouse/issues/62887 (performance, no answer, appeared in 24.3)
* https://github.com/ClickHouse/ClickHouse/issues/63545 (potential bug, under discussion, 24.3 affected)
* https://github.com/ClickHouse/ClickHouse/issues/63576 (usability | minor, won't fix, 24.3 affected)

### Open Issues

[GitHub is:issue is:open label:v24.3-affected](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+is%3Aopen+label%3Av24.3-affected+) as of July 3, 2024

* No issues 

### Summary

Build report: https://altinity-test-reports.s3.amazonaws.com/builds/stable/v24.3.4.21.altinitystable/2023-12-26T23-40-44.341/report.html **TBD**

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
| Trivy | [Pass](#trivy)                         |   |
| Scout | [Pass](#scout)                         |   |

## Scope

The scope of testing ClickHouse 24.3 Altinity Stable LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

**TBD**

The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.

#### Stateful

Results:

**TBD**

The standard `stateful` suite that consists of running SQL scripts executed against a predefined database schema.

#### Stress

Results: not executed

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

**TBD**

The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### Key Value

Results:

**TBD**

Altinity Key Value function tests.

##### Engines

Results: not executed

Altinity Engines tests.

##### Selects

Results:

**TBD**

Altinity Selects tests.

##### Session Timezone

Results:

**TBD**

Altinity Session Timezone tests.

##### AES Encryption

Results:

**TBD**

Altinity AES Encryption tests.

##### Tiered-storage

Results:

**TBD**

Altinity Tiered-Storage tests.

##### S3

Results:

**TBD**

Altinity S3 integration tests.

##### Kafka

Results:

**TBD**

Altinity Kafka integration tests.

##### Kerberos

Results:

**TBD**

Altinity Kerberos integration tests.

##### DateTime64 Extended Range

Results:

**TBD**

Altinity DateTime64 extended range integration tests.

##### Extended Precision Data Types

Results:

**TBD**

Altinity Extended Precision Data Types integration tests.

##### LDAP

Results:

**TBD**

Altinity LDAP integration tests.

##### RBAC

Results:

**TBD**

Altinity RBAC integration tests.

##### Window Functions

Results:

**TBD**

Altinity Window Functions integration tests.

##### SSL Server

Results:

**TBD**

Altinity basic SSL server integration tests.

##### Disk Level Encryption

Results:

**TBD**

Altinity Disk Level Encryption integration tests.

##### ClickHouse Keeper

Results:

**TBD**

Altinity ClickHouse Keeper integration tests.

##### Data Types

Results:

**TBD**

Altinity data types integration tests.

##### Part Moves Between Shards

Results:

**TBD**

Altinity Part Moves Between Shards integration tests.

##### Lightweight Delete

Results:

**TBD**

Altinity Lightweight Delete integration tests.

##### Base58

Results:

**TBD**

Altinity Base58 encode and decode functions integration tests.

##### Parquet

Results:

**TBD**

Altinity Parquet format integration tests.


##### Atomic Insert

Results:

**TBD**

Altinity Atomic Insert integration tests.

##### Aggregate Functions

Results:

**TBD**
  
Altinity Aggregate Functions integration tests.

##### DNS

Results:

**TBD**

Altinity DNS integration tests.

#### Benchmark

Results:

***TBD**

Altinity OnTime Benchmark tests.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

clickhouse-driver version: 0.2.8

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-driver/

The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

```
Test: tests/test_connect.py
Reason: connecting to secure port without credentials.
Status: [Fail](https://github.com/mymarilyn/clickhouse-driver/issues/442)
```

Compatibility with the [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

#### ODBC `clickhouse-odbc`

clickhouse-odbc version: v1.2.1.20220905

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.

#### SQLAlchemy

clickhouse-sqlalchemy version: 0.3.2

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.

#### Java `clickhouse-jdbc`

clickhouse-jdbc version: v0.6.2

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-jdbc/

Results (DBeaver): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-jdbc/DBeaver/

The (https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-backup/
Results (ACM): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-backup-acm/

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/clickhouse-operator/

clickhouse-operator version: 0.24.0

Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).

#### Altinity.Cloud

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/acm-launch-and-upgrade/launch_with_24.3.4.148.altinitytest/

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/acm-launch-and-upgrade/launch_with_24.3.4.148.altinitytest/

Operation on a production clusters.

### Upgrade and Downgrade

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/acm-launch-and-upgrade/upgrade_downgrade_from_23.8.11.29.altinitystable_to_24.3.4.148.altinitytest/

The upgrade and downgrade.

#### Upgrade

* from 23.8 to 24.3

#### Downgrade

* from 24.3 to 23.8

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/grafana/

Compatibility with [Grafana].

#### Tableau

Results:


* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/tableau/results.png

Compatibility with [Tableau].

#### Superset

Results:

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/24.3-lts/superset/

Compatibility with [Superset].

### Docker Image Vulnerability Scanning

#### Trivy

Results:

**TBD**

Trivy Docker image vulnerability scanner.

#### Scout

Results:

**TBD**

Scout Docker image vulnerability scanner.

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/docs/qa_stp006_clickhouse-23.8_longterm_support_release.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/docs/qa_stp006_clickhouse_23.8_longterm_support_release.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
