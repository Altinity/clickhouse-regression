# QA-STP006 ClickHouse 23.8 Long-Term Support Release
# Software Test Plan

(c) 2023 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** Nov 1, 2023

## Execution Summary

**Completed:**

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/23.8-lts/

**Summary:**

Started to execute test plan on Nov 1, 2023.

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Timeline](#timeline)
* 4 [Human Resources And Assignments](#human-resources-and-assignments)
* 5 [End User Recommendations](#end-user-recommendations)
    * 5.1 [Notable Differences in Behavior](#notable-differences-in-behavior)
    * 5.2 [Summary of Main Regressions](#summary-of-main-regressions)
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
* Davit Mnatobishvili (parquet, LDAP, benchmarks, alter)
* Alsu Giliazova (aggregate functions, selects, lightweight_delete)
* Stuart Gibb (clickhouse-keeper)
* Andrey Antipov (clickhouse-operator, disk level encryption, Python clickhouse-driver, JDBC driver, ODBC driver, clickhouse-sqlalchemy)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup)
* Dima Borovstov (Tableau)
* Eugene Klimov (Grafana, Superset)
* Tatiana Saltykova (production cluster, upgrade and downgrade)

## End User Recommendations

### Notable Differences in Behavior

* Insert from s3 requieres more memory, so max_insert_thread in tests was lowered.
* Sparkbar aggregate function overflow was fixed after 23.8.
* Different result of topKWeightedMerge aggregate function in versions 23.3.2.37 and 23.8.4.69
  https://github.com/ClickHouse/ClickHouse/issues/55997
* Column name and table name conflict when allow_experimental_analyzer=1
  https://github.com/ClickHouse/ClickHouse/issues/56371

### Summary of Main Regressions

Regressions:

* TBD

## Known Issues

### Reported By Altinity

* Different result of topKWeightedMerge aggregate function in versions 23.3.2.37 and 23.8.4.69  
  https://github.com/ClickHouse/ClickHouse/issues/55997
  
* Column name and table name conflict when allow_experimental_analyzer=1  
  https://github.com/ClickHouse/ClickHouse/issues/56371

* TBD

### Open Issues

[GitHub is:issue is:open label:v23.8-affected](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+is%3Aopen+label%3Av23.8-affected+) as of Nov 13, 2023

* allow_nullable_key + Final = incorrect result  
  https://github.com/ClickHouse/ClickHouse/issues/56417

* List of CTEs in IN clause not recognized when used in subquery  
  https://github.com/ClickHouse/ClickHouse/issues/55981

* TBD

## New Features

### Altinity Stable Backports

### Changelog

### Summary

| Test Suite  | Result | Comments |
| --- | --- | --- |
| Stateless | [](#stateless) |   |
| Stateful | [](#stateful)  |   |
| Stress | []  |   |
| Integration | [](#integration)  |   |
| Key Value | [](#key-value)  |   |
| Engines  | [](#engines)  |   |
| Parquet | [](#parquet)  |   |
| Tiered Storage (Local) | [](#tiered-storage)  |   |
| Tiered Storage (MinIO) | [](#tiered-storage)  |   |
| Tiered Storage (AWS) | [](#tiered-storage)  |   |
| Tiered Storage (GCS) | [](#tiered-storage)  |   |
| S3 (AWS) | [](#s3)  |  |
| S3 (MinIO) | [](#s3)  |   |
| S3 (GCS) | [](#s3) |   |
| Selects | [](#selects) |   |
| AES Encryption | [](#aes-encryption)  |   |
| Atomic Insert | [](#atomic-insert) |   |
| Base58 | []](#base58) |   |
| DNS | [](#dns) |   |
| Kafka | [](#kafka) |   |
| Kerberos | [](#kerberos)  |   |
| DateTime64 Extended Range | [](#datetime64-extended-range)  |   |
| Extended Precision Data Types | [](#extended-precision-data-types) |   |
| LDAP | [](#ldap)  |   |
| RBAC | [](#rbac) |   |
| Window Functions | [](#window-functions)  |   |
| SSL Server | [](#ssl-server)  |   |
| Disk Level Encryption | [](#disk-level-encryption)  |   |
| ClickHouse Keeper | [](#clickhouse-keeper)  |   |
| Map Type | [](#map-type) |   |
| Ontime Bechmark | [](#ontime-benchmark)
| Part Moves Between Shards | [](#part-moves-between-shards) |   |
| Lightweight Delete | [](#lightweight-delete) |    |
| Aggregate Functions | [](#aggregate-functions) |  |
| Python `clickhouse_driver` | [](#python-clickhouse_driver)  |   |
| ODBC `clickhouse-odbc` | [](#odbc-clickhouse-odbc)  |  |
| SQLAlchemy | [](#sqlalchemy) |    |
| Java `clickhouse-jdbc` | [](#java-clickhouse-jdbc)  |   |
| Java `clickhouse-jdbc` (DBeaver) | [](#java-clickhouse-jdbc)  |   |
| Backup `clickhouse-backup` | [](#backup-clickhouse-backup)  |   |
| Kubernetes `clickhouse-operator` | [](#kubernetes-clickhouse-operator) |   |
| Altinity.Cloud | [](#altinitycloud)  |   |
| Production Cluster Operation | [](#production-cluster-operation) |   |
| Upgrade And Downgrade | [](#upgrade-and-downgrade) |   |
| Grafana | [](#grafana) |   |
| Tableau | [](#tableau)  |   |
| Superset | [](#superset)  |   |
| Trivy | [](#trivy) |   |
| Scout | [](#scout) |   |

## Scope

The scope of testing ClickHouse 23.8 LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.


#### Stateful

Results:

The standard `stateful` suite that consists of running SQL scripts executed against a predefined database schema.

#### Stress

Results:

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### Key Value

Results:

Altinity Key Value function tests.


##### Engines

Results:

Altinity Engines tests.

##### Selects

Results:

Altinity Selects tests.

##### AES Encryption

Results:

Altinity AES Encryption tests.

##### Tiered-storage

Results: (Local)

Results: (MinIO)

Results: (AWS)

Results (GCS)

Altinity Tiered-Storage tests.

##### S3

Results: (AWS S3)

Results: (MinIO)

Results: (GCS)

Altinity S3 integration tests.

##### Kafka

Results:

Altinity Kafka integration tests.

##### Kerberos

Results:

Altinity Kerberos integration tests.

##### DateTime64 Extended Range

Results:

Altinity DateTime64 extended range integration tests.

##### Extended Precision Data Types

Results:

Altinity Extended Precision Data Types integration tests.

##### LDAP

Results:

Altinity LDAP integration tests.

##### RBAC

Results:

Altinity RBAC integration tests.

##### Window Functions

Results:

Altinity Window Functions integration tests.

##### SSL Server

Results:

Altinity basic SSL server integration tests.

##### Disk Level Encryption

Results:

Altinity Disk Level Encryption integration tests.

##### ClickHouse Keeper

Results:

Altinity ClickHouse Keeper integration tests.

##### Map Type

Results:

Altinity Map data type integration tests.

##### Part Moves Between Shards

Results:

Altinity Part Moves Between Shards integration tests.

##### Lightweight Delete

Results:

Altinity Lightweight Delete integration tests.

##### Base58

Results:

Altinity Base58 encode and decode functions integration tests.

##### Parquet

Results:
Results (AWS S3):
Results (MinIO S3):


Altinity Parquet format integration tests.


##### Atomic Insert

Results:

Altinity Atomic Insert integration tests.

##### Aggregate Functions

Results:

Altinity Aggregate Functions integration tests.

##### DNS

Results:

Altinity DNS integration tests.

#### Ontime Benchmark

Results:
Results AWS S3:
Altinity OnTime Benchmark tests.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

Results:

The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.


#### ODBC `clickhouse-odbc`

Results:

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.


#### SQLAlchemy

Results: /

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.


#### Java `clickhouse-jdbc`

Results: 6/

Results (DBeaver):

The (https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results:
Results (ACM):

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results:

Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).


#### Altinity.Cloud

Results:

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results:

Operation on a production clusters.

### Upgrade and Downgrade

Results:

The upgrade and downgrade.

#### Upgrade

* from 22.3 to 23.8

#### Downgrade

* from 23.8 to 23.3

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results:

Compatibility with [Grafana].

#### Tableau

Results:

Compatibility with [Tableau].

#### Superset

Results:

Compatibility with [Superset].

### Docker Image Vulnerability Scanning

#### Trivy

Results:

Trivy Docker image vulnerability scanner.


#### Scout

Results:

Scout Docker image vulnerability scanner.

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/docs/qa_stp006_clickhouse-23.8_longterm_support_release.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/docs/qa_stp006_clickhouse_23.8_longterm_support_release.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
