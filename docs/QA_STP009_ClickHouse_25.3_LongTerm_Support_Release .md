# QA-STP008 ClickHouse 25.3Long-Term Support Release
# Software Test Plan

(c) 2025 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** **TBD**

## Execution Summary

**Completed:** **TBD**

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/

**Build Report:**

**TBD**

**Summary:**

**TBD**

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

This test plan covers testing of ClickHouse 25.3 LTS (long-term support) Altinity Stable release.

## Timeline

The testing of 24.8.8.17 binaries SHALL be started on December 16, 2024 and be completed
by January 13, 2025.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

**TBD**

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

* https://docs.altinity.com/releasenotes/altinity-stable-release-notes/25.3/

## Known Issues



### Open Issues

[GitHub is:issue is:open label:v25.3-affected](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+is%3Aopen+label%3Av25.3-affected) 

* https://github.com/ClickHouse/ClickHouse/issues/81045 (SerializationString Crash after DROP/ADD the same column)
* https://github.com/ClickHouse/ClickHouse/issues/80794 (INCOMPATIBLE_TYPE_OF_JOIN with filter pushdown to Engine Join and analyzer enabled)
* https://github.com/ClickHouse/ClickHouse/issues/79966 (MULTIPLE_EXPRESSIONS_FOR_ALIAS alias clash between column name alias and table name alias)

### Summary
Build report: **TBD**

> [!NOTE]
> **Pass\*** - tests passed with known fails

| Test Suite  | Result                                        | Comments |
| --- |-----------------------------------------------| --- |
| Stateless | [*Pass](#stateless)                     |   |
| Stateful | [Pass](#stateful)                      |   |
| Stress | [Pass](#stress)                        |  Not executed  |
| Integration | [*Pass](#integration)                   |   |
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
| Engines  | [Pass](#engines)                       | Not executed  |
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
| Grype | [Pass](#grype)                         |   |

## Scope

The scope of testing ClickHouse 25.3 Altinity Stable LTS release SHALL be defined as follows.

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

Results:

**TBD**

The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

**TBD**

The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### AES Encryption

Results:

**TBD**

Altinity AES Encryption tests.

##### Aggregate Functions

Results:

**TBD**
  
Altinity Aggregate Functions integration tests.

##### Alter

Results:

**TBD**

Altinity Alter tests.

##### Atomic Insert

Results:

**TBD**

Altinity Atomic Insert integration tests.

##### Attach

Results:

**TBD**

Altinity Attach tests.

##### Base58

Results:

**TBD**

Altinity Base58 encode and decode functions integration tests.

##### Ontime Benchmark

Results:

**TBD**

Altinity OnTime Benchmark tests.

##### ClickHouse Keeper

Results:

**TBD**

Altinity ClickHouse Keeper integration tests.

##### ClickHouse Keeper Failover

Results:

**TBD**

Altinity ClickHouse Keeper Failover integration tests.

##### Data Types

Results:

**TBD**

Altinity data types integration tests.

##### DateTime64 Extended Range

Results:

**TBD**

Altinity DateTime64 extended range integration tests.

##### Disk Level Encryption

Results:

**TBD**

Altinity Disk Level Encryption integration tests.

##### DNS

Results:

**TBD**

Altinity DNS integration tests.

##### Engines

**TBD**

Altinity Engines tests.

##### Example

Results:

**TBD**

Altinity Example tests.

##### Extended Precision Data Types

Results:

**TBD**

Altinity Extended Precision Data Types integration tests.

##### Functions

Results:

**TBD**

Altinity Functions tests.

##### Hive Partitioning

Results:

**TBD**

Altinity Hive Partitioning tests.

##### Iceberg

Results:

**TBD**

Altinity Iceberg tests.


##### JWT Authentication

Results:

**TBD**

Altinity JWT Authentication tests.

##### Kafka

Results:

**TBD**

Altinity Kafka integration tests.

##### Kerberos

Results:

**TBD**

Altinity Kerberos integration tests.

##### Key Value

Results:

**TBD**

Altinity Key Value function tests.

##### LDAP

Results:

**TBD**

Altinity LDAP integration tests.

##### Lightweight Delete

Results:

**TBD**

Altinity Lightweight Delete integration tests.

##### Memory

Results:

**TBD**

Altinity Memory tests.

##### Parquet

Results:

**TBD**

Altinity Parquet format integration tests.

##### Part Moves Between Shards

Results:

**TBD**

Altinity Part Moves Between Shards integration tests.

##### RBAC

Results:

**TBD**

Altinity RBAC integration tests.

##### S3

Results:

**TBD**

Altinity S3 integration tests.

##### Selects

Results:

**TBD**

Altinity Selects tests.

##### Session Timezone

Results:

**TBD**

Altinity Session Timezone tests.

##### Settings

Results:

**TBD**

Altinity Settings tests.

##### SSL Server

Results:

**TBD**

Altinity basic SSL server integration tests.

##### Swarms

Results:

**TBD**

Altinity Swarms tests.

##### Tiered Storage

Results:

**TBD**

Altinity Tiered-Storage tests.

##### Version

Results:

**TBD**

Altinity Version tests.

##### Window Functions

Results:

**TBD**

Altinity Window Functions integration tests.



### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

clickhouse-driver version: 
* 0.2.9

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/clickhouse-driver/
  
The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

Compatibility with the [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

#### ODBC `clickhouse-odbc`

clickhouse-odbc version: 
* v1.3.0.20241018

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.

#### SQLAlchemy

clickhouse-sqlalchemy version: 
* 0.3.2

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.

#### Java `clickhouse-jdbc`

clickhouse-jdbc version: 0.9.0

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/clickhouse-jdbc/

Results (DBeaver): 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/clickhouse-jdbc/DBeaver/

The  [clickhouse-jdbc](https://github.com/ClickHouse/clickhouse-jdbc) driver.


### Backup `clickhouse-backup`

Results: **TBD**
Results (ACM): **TBD**

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/clickhouse-operator/

clickhouse-operator version: 0.25.2

Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).

#### Altinity.Cloud

Results: **TBD**

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: 

Operation on a production clusters.

### Upgrade and Downgrade

Results: **TBD**

The upgrade and downgrade.

#### Upgrade

* from 24.8 to 25.3

#### Downgrade

* from 25.3 to 24.3

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.3.6-lts/grafana/

Compatibility with [Grafana].

#### Tableau

Results:

**TBD**

Compatibility with [Tableau].

#### Superset

Results:

**TBD**

Compatibility with [Superset].

### Docker Image Vulnerability Scanning

#### Grype

Results:

**TBD**

[Grype](https://github.com/anchore/grype) Docker image vulnerability scanner.


[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub]: https://github.com
