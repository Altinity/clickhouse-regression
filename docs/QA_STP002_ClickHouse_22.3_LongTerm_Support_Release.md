# QA-STP002 ClickHouse 22.3 Long-Term Support Release
# Software Test Plan

(c) 2022 Altinity Inc. All Rights Reserved.

**Document status:** Public

**Author:** vzakaznikov

**Date:** March 25, 2022

## Execution Summary

**Completed:** -

**Test Results:** -

**Test Coverage:** - 

**Summary:** 

Started to execute test plan on March 28, 2022.

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Timeline](#timeline)
* 4 [Human Resources And Assignments](#human-resources-and-assignments)
* 5 [Known Issues](#known-issues)
  * 5.1 [Compatibility](#compatibility)
  * 5.2 [Server](#server)
* 6 [Test Results](#test-results)
  * 6.1 [Summary](#summary)
* 7 [Scope](#scope)
  * 7.1 [Automated Regression Tests](#automated-regression-tests)
    * 7.1.1 [Stateless](#stateless)
    * 7.1.2 [Stateful](#stateful)
    * 7.1.3 [Stress](#stress)
    * 7.1.4 [Integration](#integration)
    * 7.1.5 [Altinity Integration](#altinity-integration)
      * 7.1.5.1 [Tiered-storage](#tiered-storage)
      * 7.1.5.2 [S3](#s3)
      * 7.1.5.3 [Kafka](#kafka)
      * 7.1.5.4 [Kerberos](#kerberos)
      * 7.1.5.5 [DateTime64 Extended Range](#datetime64-extended-range)
      * 7.1.5.6 [Extended Precision Data Types](#extended-precision-data-types)
      * 7.1.5.7 [LDAP](#ldap)
      * 7.1.5.8 [RBAC](#rbac)
      * 7.1.5.9 [Window Functions](#window-functions)
      * 7.1.5.10 [SSL Server](#ssl-server)
      * 7.1.5.11 [Disk Level Encryption](#disk-level-encryption)
      * 7.1.5.12 [ClickHouse Keeper](#clickhouse-keeper)
      * 7.1.5.13 [Map Type](#map-type)
      * 7.1.5.14 [Part Moves Between Shards](#part-moves-between-shards)
      * 7.1.5.15 [Delete](#delete)
  * 7.2 [Compatibility with Client Drivers](#compatibility-with-client-drivers)
    * 7.2.1 [Python `clickhouse_driver`](#python-clickhouse_driver)
    * 7.2.2 [ODBC `clickhouse-odbc`](#odbc-clickhouse-odbc)
    * 7.2.3 [SQLAlchemy](#sqlalchemy)
    * 7.2.4 [Java `clickhouse-jdbc`](#java-clickhouse-jdbc)
  * 7.3 [Backup `clickhouse-backup`](#backup-clickhouse-backup)
  * 7.4 [Compatibility With Operation on Kubernetes](#compatibility-with-operation-on-kubernetes)
    * 7.4.1 [Kubernetes `clickhouse-operator`](#kubernetes-clickhouse-operator)
    * 7.4.2 [Altinity.Cloud](#altinitycloud)
  * 7.5 [Production Cluster Operation](#production-cluster-operation)
  * 7.6 [Upgrade and Downgrade](#upgrade-and-downgrade)
    * 7.6.1 [Upgrade](#upgrade)
    * 7.6.2 [Downgrade](#downgrade)
  * 7.7 [Compatibility With BI Tools](#compatibility-with-bi-tools)
    * 7.7.1 [Grafana](#grafana)
    * 7.7.2 [Tableau](#tableau)
    * 7.7.3 [Superset](#superset)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitLab Repository].
All the updates are tracked using the [Revision History].

## Introduction

This test plan covers testing of ClickHouse 22.3 LTS (long-term support) release.

## Timeline

The testing of pre-stable binaries SHALL be started on March 28, 2022 and be completed
by May 27, 2022.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager, regression)
* Myroslav Tkachenko (S3, tiered-storage, regression)
* Andrey Zvonov (build, pipeline)
* Roshanth (clickhouse-operator)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup)
* Ivan Sidorov (clickhouse-keeper, part-moves-between-shards)
* Andrey Antipov (disk level encryption, Python clickhouse-driver, JDBC driver, ODBC driver, clickhouse-sqlalchemy)
* Dima Borovstov (Tableau)
* Eugene Klimov (Grafana, Superset)
* Tatiana Saltykova (production cluster, upgrade and downgrade)

## Known Issues

### Compatibility

* JDBC `clickhouse-jdbc` driver tests fail to run (0.3.1-patch, 0.3.2-patch8)
* ODBC `clickhouse-odbc` `v1.1.10.20210822` tests related to time zones fails (https://github.com/ClickHouse/clickhouse-odbc/issues/394)
* Superset requires `sqlalchemy < 1.4` so with this conflict modern types like Map and Decimal fixes are not available

### Server

* https://github.com/ClickHouse/ClickHouse/issues/37812  
  Missing columns after the upgrade to 22.3
* https://github.com/ClickHouse/ClickHouse/issues/36043  
  Not found column in block exception
* https://github.com/ClickHouse/ClickHouse/issues/37190  
  PREWHERE breaks CTE clause with arrayJoin(arrayEnumerate())
* https://github.com/ClickHouse/ClickHouse/issues/36891 **fixed, not backported**  
  unexpected errors with a clash of constant strings in aggregate function and prewhere and join
* https://github.com/ClickHouse/ClickHouse/issues/36300 **fixed, not backported**  
  Exception: Cannot convert column xxx because it is non constant in source stream but must be constant in result
* https://github.com/ClickHouse/ClickHouse/issues/36279 **fixed, not backported**  
  Argument at index 1 for function ilike must be constant: while executing. (ILLEGAL_COLUMN)
* https://github.com/ClickHouse/ClickHouse/issues/35336 **backport https://github.com/ClickHouse/ClickHouse/pull/36818**  
  Result of a column using if and a subquery changing when using WHERE 1=1 as a filter
* https://github.com/ClickHouse/ClickHouse/issues/37673  
  ORDER BY gives unsorted results when there are duplicate rows in table and projection is used
* https://github.com/ClickHouse/ClickHouse/issues/37032  
  Not found column in distributed query with aggregation and alias
* https://github.com/ClickHouse/ClickHouse/issues/37900  
  max_insert_threads and materialized views performance degradation

## New Features

22.3 as compared to 21.8

https://gist.github.com/filimonov/1659843e64127549a8ba7eecd3a48f6b
2022 - https://github.com/ClickHouse/ClickHouse/blob/master/CHANGELOG.md#223
2021 - https://clickhouse.com/docs/en/whats-new/changelog/2021/

### Tiered Storage

### Auditing

* New `system.session_log` table

### RBAC

* Fix race condition which could happen in RBAC under a heavy load. This PR fixes #24090, #24134,. #24176 (Vitaly Baranov).
* Allow RBAC row policy via postgresql protocol. Closes #22658. PostgreSQL protocol is enabled in configuration by default. #22755 (Kseniia Sumarokova).

### LDAP

### Storage

* Partitioned export to S3
* Integration with Azure Blob Storage similar to S3 (ping Mindaugaz)
* Local Cache For Remote Filesystem
* S3 cache - preview stage, configuration is going to be changed

### ClickHouse Keeper

* Four letter commands added

### Backward Incompatible Changes

### Upgrade and Downgrade

### Hardware Architecture

* ClickHouse on ARM (AArch64)

## Test Results

Test results SHALL be accessible at https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/.

### Summary

| Test Suite  | Result | Comments |
| --- | --- | --- |
| Stateless | [No final results yet ](#stateless) | GitHub Actions |
| Stateful | [No final results yet](#stateful) | GitHub Actions |
| Stress | [No final results yet](#stress) | GitHub Actions |
| Integration | [No final results yet](#integration) | GitHub Actions |
| Tiered Storage (Local) | [Pass](#tiered-storage) |   |
| Tiered Storage (MinIO) | [Pass](#tiered-storage) |   |
| Tiered Storage (AWS) | [Pass](#tiered-storage) |   |
| S3 (AWS) | [Pass](#s3) |  |
| S3 (MinIO) | [Pass](#s3) |   |
| S3 (GCS) | [Pass](#s3) |   |
| Kafka | [Pass](#kafka) |   |
| Kerberos | [Pass](#kerberos) |   |
| DateTime64 Extended Range | [Pass](#datetime64-extended-range) |   |
| Extended Precision Data Types | [Pass](#extended-precision-data-types) |   |
| LDAP | [Pass](#ldap) |   |
| RBAC | [Pass](#rbac) |   |
| Window Functions | [Pass](#window-functions) |   |
| SSL Server | [Pass](#ssl-server) |   |
| Disk Level Encryption | [Pass](#disk-level-encryption) |   |
| ClickHouse Keeper | [Pass](#clickhouse-keeper) |   |
| Map Type | [Pass](#map-type) |   |
| Part Moves Between Shards | [Pass](#part-moves-between-shards) |   |
| Delete | [NA](#delete) | Lightweight deletes are not yet supported |   |
| Python `clickhouse_driver` | [Pass](#python-clickhouse_driver) |   |
| ODBC `clickhouse-odbc` | [Pass*](#odbc-clickhouse-odbc) | In `v1.1.10.20210822` tests related to time zones fail |
| SQLAlchemy | [Pass](#sqlalchemy) |    |
| Java `clickhouse-jdbc` | [Fail](#java-clickhouse-jdbc) | Tests fail to run |
| Java `clickhouse-jdbc` (DBeaver) | [Pass](#java-clickhouse-jdbc) |   |
| Backup `clickhouse-backup` | [Pass](#backup-clickhouse-backup) |   |
| Kubernetes `clickhouse-operator` | [Pass](#kubernetes-clickhouse-operator) |   |
| Altinity.Cloud | [Pass](#altinitycloud) |   |
| Production Cluster Operation | [No results yet](#production-cluster-operation) |   |
| Upgrade And Downgrade | [No results yet](#upgrade-and-downgrade) |   |
| Grafana | [Pass](#grafana) | Tested manually |
| Tableau | [Pass](#tableau) | Tested manually |
| Superset | [Pass](#superset) | Tested manually |

## Scope

The scope of testing ClickHouse 22.3 LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

The `stateless` suite consists of running SQL, python and bash scripts that check various features of the server.
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/master/tests/queries/0_stateless

#### Stateful

Results:

The `stateful` suite consists of running SQL scripts executed against a predefined database schema.
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/master/tests/queries/1_stateful

#### Stress

Results:

The `stress` suite consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

The `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/master/tests/integration

#### Altinity Integration

##### Tiered-storage

Results: (Local) https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/tiered_storage/normal/

Results: (MinIO) https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/tiered_storage/minio/

Results: (AWS) https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/tiered_storage/aws/

The `tiered-storage` suite must be integrated to TestFlows check.

##### S3

Results: (AWS S3) https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/s3/aws/

Results: (MinIO) https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/s3/minio/

Results: (GCS) https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/s3/gcs/

The `s3` suite must be integrated to TestFlows check. The following S3 backends SHALL be verified:

* MinIO
* AWS S3
* GCS

In addition to the following functionality SHALL be verified:

* Zero-copy replication
* Backup/Restore of S3 tables

##### Kafka

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/kafka/

Altinity Kafka integration tests that use docker-compose environment in addition to integration tests
in ClickHouse repo.

##### Kerberos

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/kerberos/

Altinity Kerberos integration tests.

##### DateTime64 Extended Range

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/datetime64_extended_range/

Altinity DateTime64 extended range integration tests.

##### Extended Precision Data Types

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/extended_precision_data_types/

Altinity Extended Precision Data Types integration tests.

##### LDAP

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/ldap/

Altinity LDAP integration tests.

##### RBAC

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/rbac/

Altinity RBAC integration tests.

##### Window Functions

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/window_functions/

Altinity Window Functions integration tests.

##### SSL Server

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/ssl_server/

Altinity basic SSL server integration tests.

##### Disk Level Encryption

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/disk_level_encryption/

Altinity Disk Level Encryption integration tests.

##### ClickHouse Keeper

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/clickhouse_keeper/

Altinity ClickHouse Keeper integration tests.

##### Map Type

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/map_type/

Altinity Map data type integration tests.

##### Part Moves Between Shards

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/testflows/part_moves_between_shards/

Altinity Part Moves Between Shards integration tests.

##### Delete

Results: https://altinity-test-reports.s3.amazonaws.com/reports/22.3-lts/testflows/lightweight_delete/report.html

Altinity Delete (`ALTER DELETE`) integration tests.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-driver/

The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) SHALL be verified to work correctly by
executing automated tests in https://github.com/mymarilyn/clickhouse-driver/tree/master/tests

The following versions SHALL be verified:

* 0.2.1
* 0.2.2
* 0.2.3

#### ODBC `clickhouse-odbc`

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-odbc/,
         `clickhouse-odbc` `v1.1.10.20210822` tests related to time zones fails
         (https://github.com/ClickHouse/clickhouse-odbc/issues/394)

The operation of `clickhouse-odbc` driver SHALL be verified by executing automated tests in
https://github.com/ClickHouse/clickhouse-odbc/tree/master/test

The following versions SHALL be verified:

* https://github.com/ClickHouse/clickhouse-odbc/releases/tag/v1.1.9.20201226
* https://github.com/ClickHouse/clickhouse-odbc/releases/tag/v1.1.10.20210822

#### SQLAlchemy

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-sqlalchemy/

The https://github.com/xzkostyan/clickhouse-sqlalchemy ClickHouse dialect for SQLAlchemy SHALL be verified to work correctly
by executing automated tests in https://github.com/xzkostyan/clickhouse-sqlalchemy/tree/master/tests

The following versions SHALL be verified:

* https://github.com/xzkostyan/clickhouse-sqlalchemy/releases/tag/0.1.6
* https://github.com/xzkostyan/clickhouse-sqlalchemy/releases/tag/0.1.7
* https://github.com/xzkostyan/clickhouse-sqlalchemy/releases/tag/0.1.8
* https://github.com/xzkostyan/clickhouse-sqlalchemy/releases/tag/0.2.0

#### Java `clickhouse-jdbc`

Results (0.3.1-patch): https://altinity-test-reports.s3.amazonaws.com/reports/22.3-lts/clickhouse-jdbc/0.3.1-patch,
                       **tests fail to run**

Results (0.3.2-patch8): https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-jdbc/0.3.2-patch8/, **tests fail to run**

Results (DBeaver): https://altinity-test-reports.s3.amazonaws.com/reports/22.3-lts/clickhouse-jdbc/DBeaver/

Basic functionality of https://github.com/ClickHouse/clickhouse-jdbc SHALL be verified.

The following versions SHALL be verfieid:

* https://github.com/ClickHouse/clickhouse-jdbc/releases/tag/v0.3.1-patch
* https://github.com/ClickHouse/clickhouse-jdbc/releases/tag/v0.3.2-patch8

### Backup `clickhouse-backup`

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-backup/
Results (ACM): https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-backup-acm/

The compatibility with [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility SHALL be verified.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-operator/

Compatibility with `clickhouse-operator` in Kubernetes environment SHALL be verified.

#### Altinity.Cloud

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/clickhouse-backup-acm/

Compatibility with Altinity.Cloud SHALL be verified.

### Production Cluster Operation

Results: _manual testing to be performed by support team_

Operation on a production cluster SHALL be verified.

### Upgrade and Downgrade

Results: _manual testing to be performed by support team_

The upgrade and downgrade path SHALL be verified on the following combinations using ACM
and reference production like cluster

#### Upgrade

* from 22.3 to 21.8

#### Downgrade

* from 22.3 to 21.8

### Compatibility With BI Tools

Compatibility with the following BI tools SHALL be verified.

#### Grafana

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/grafana/

Compatibility with [Grafana] SHALL be verified using
https://grafana.com/grafana/plugins/vertamedia-clickhouse-datasource/ data source for the following versions:

* 2.4.3
* Grafana 8.4

#### Tableau

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/tableau/

Compatibility with [Tableau] SHALL be verified using the current version of
https://github.com/Altinity/clickhouse-tableau-connector-odbc connector.

#### Superset

Results: https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.3-lts/superset/

Compatibility with [Superset] SHALL be verified using the following pre-requisites:

* clickhouse-sqlalchemy==0.1.8
* latest clickhouse-sqlalchemy 0.2.0
* sqlalchemy >= 1.4, < 1.5

> Note: Superset requires sqlalchemy < 1.4 so with this conflict modern types like Map and Decimal fixes not available.

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[GitLab Repository]: https://gitlab.com/altinity-qa/documents/qa-stp002-clickhouse-22.3-long-term-support-release/
[Revision History]: https://gitlab.com/altinity-qa/documents/qa-stp002-clickhouse-22.3-long-term-support-release/-/commits/main/
[Git]: https://git-scm.com/
[GitLab]: https://gitlab.com
