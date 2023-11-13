# QA-STP001 ClickHouse 21.8 Long-Term Support Release
# Software Test Plan

(c) 2021 Altinity Inc. All Rights Reserved.

**Document status:** Public

**Author:** vzakaznikov

**Date:** July 16, 2021

## Execution Summary

**Completed:** October 1, 2021

**Test Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/

**Test Coverage:** Approximately 80% 

**Summary:** 

* Tests suites for ClickHouse Keeper and Disk Level Encryption features were not completed and are still in progress.
* S3 backup/restore feature testing was not completed and is still in progress.
* Operation on production cluster and upgrade/downgrade path from 21.3 to 21.8 was only verified manually by support team.
* All compatibility testing with BI tools was performed manually.

**Future Improvements**

* Identify and test backward incompatible changes
  * Extract this from release notes
* Test small rolling cluster upgrade
* Verification and identification of outstanding issues
* Better project timeline planning
* Reduce manual testing and icrease number of modules that we run in our build pipeline

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Timeline](#timeline)
* 4 [Human Resources](#human-resources)
* 5 [Scope](#scope)
  * 5.1 [New Features](#new-features)
    * 5.1.1 [Untested](#untested)
    * 5.1.2 [Tested](#tested)
  * 5.2 [Automated Regression Tests](#automated-regression-tests)
    * 5.2.1 [Stateless](#stateless)
    * 5.2.2 [Stateful](#stateful)
    * 5.2.3 [Stress](#stress)
    * 5.2.4 [Integration](#integration)
    * 5.2.5 [TestFlows](#testflows)
      * 5.2.5.1 [Tiered-storage ](#tiered-storage-)
      * 5.2.5.2 [S3](#s3)
  * 5.3 [Compatibility with Client Drivers](#compatibility-with-client-drivers)
    * 5.3.1 [Python `clickhouse_driver`](#python-clickhouse_driver)
    * 5.3.2 [ODBC `clickhouse-odbc`](#odbc-clickhouse-odbc)
    * 5.3.3 [SQLAlchemy](#sqlalchemy)
    * 5.3.4 [Java (JDBC) Maven](#java-jdbc-maven)
  * 5.4 [Compatibility With `clickhouse-backup`](#compatibility-with-clickhouse-backup)
  * 5.5 [Compatibility With Operation on Kubernetes](#compatibility-with-operation-on-kubernetes)
    * 5.5.1 [`clickhouse-operator`](#clickhouse-operator)
  * 5.6 [Operation on Production Cluster](#operation-on-production-cluster)
  * 5.7 [Upgrade and Downgrade Path](#upgrade-and-downgrade-path)
    * 5.7.1 [Upgrade](#upgrade)
    * 5.7.2 [Downgrade](#downgrade)
  * 5.8 [Compatibility With BI Tools](#compatibility-with-bi-tools)
    * 5.8.1 [Grafana](#grafana)
    * 5.8.2 [Tableau](#tableau)
    * 5.8.3 [Superset](#superset)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitLab Repository].
All the updates are tracked using the [Revision History].

## Introduction

This test plan covers testing of ClickHouse 21.8 LTS (long-term support) release.

## Timeline

The testing of pre-stable binaries SHALL be started on July 26, 2021 and be completed
by October 1, 2021.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager, tiered-storage, ODBC driver)
* Sergio Henandez (builds, execution of automated tests in CI/CD pipeline)
* Myroslav Tkachenko (S3)
* Andrey Zvonov (clickhouse-operator, clickhouse-backup, JDBC driver)
* Ivan Sidorov (clickhouse-keeper)
* Andrey Antipov (disk level encryption)
* Dima Borovstov (Tableau)
* Eugene Klimov (Grafana, Superset)
* Tatiana Saltykova (production cluster, upgrade and downgrade)

## Scope

The scope of testing ClickHouse 21.8 LTS release SHALL be defined as follows.

### New Features

#### Untested

* clickhouse keeper (end of November)
  * https://gitlab.com/altinity-qa/clickhouse/cicd/regression/-/tree/main/clickhouse_keeper (in progress, 10% completed)
* disk level encryption (end of October)
  * https://gitlab.com/altinity-qa/clickhouse/cicd/regression/-/tree/main/disk_level_encryption (in progress, 33% completed)
* backup/restore of S3 tables
  * https://gitlab.com/altinity-qa/clickhouse/cicd/regression/-/blob/main/s3/tests/backup.py (in progress, 90% completed)

#### Tested

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/build/testflows_results.html

* Kerberos auth for HTTP
* DateTime64 extended range
* LDAP support for active directory
* S3 zero copy replication
* Window functions

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/build/stateless_results.html

The `stateless` suite consists of running SQL, python and bash scripts that check various features of the server.
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/master/tests/queries/0_stateless

#### Stateful

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/build/stateful_results.html

The `stateful` suite consists of running SQL scripts executed against a predefined database schema.
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/master/tests/queries/1_stateful

#### Stress

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/build/stress_results.html

The `stress` suite consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/build/integration_results.html

The `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/master/tests/integration

#### TestFlows

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/build/testflows_results.html

The `testflows` suite of tests consists of various modules of automated tests that use [TestFlows Framework](https://testflows.com).
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/master/tests/testflows

##### Tiered-storage 

**Results: (local)** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/tiered-storage/results_local.html

**Results: (minio)** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/tiered-storage/results_minio.html

The `tiered-storage` suite must be integrated to TestFlows check.

##### S3

**Results: (AWS S3)** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/s3/aws/results.html

**Results: (MinIO)** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/s3/minio/results.html

**Results: (GCS)** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/s3/gcs/result.html 

The `s3` suite must be integrated to TestFlows check. The following S3 backends SHALL be verified:

* MinIO
* AWS S3

##### Kafka

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/kafka/results.html

Run out Kafka integration tests that use docker-compose environment in addition to integration tests
in Yandex repo.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/clickhouse-driver/results.html

The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) SHALL be verified to work correctly by
executing automated tests in https://github.com/mymarilyn/clickhouse-driver/tree/master/tests

The following versions SHALL be verified:

* 0.2.1

#### ODBC `clickhouse-odbc`

**Results:** https://gitlab.com/altinity-qa/results/-/tree/master/results/ClickHouse/21.8-LTS/clickhouse-odbc

The operation of `clickhouse-odbc` driver SHALL be verified by executing automated tests in
https://github.com/ClickHouse/clickhouse-odbc/tree/master/test

The following versions SHALL be verified:

* https://github.com/ClickHouse/clickhouse-odbc/releases/tag/v1.1.9.20201226

#### SQLAlchemy

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/clickhouse-sqlalchemy/1.6/

The https://github.com/xzkostyan/clickhouse-sqlalchemy ClickHouse dialect for SQLAlchemy SHALL be verified to work correctly
by executing automated tests in https://github.com/xzkostyan/clickhouse-sqlalchemy/tree/master/tests

The following versions SHALL be verified:

* https://github.com/xzkostyan/clickhouse-sqlalchemy/releases/tag/0.1.6

#### Java (JDBC) Maven

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/clickhouse-jdbc/

* Basic functionality of https://github.com/ClickHouse/clickhouse-jdbc SHALL be verified.

The following versions SHALL be verfieid:

* https://github.com/ClickHouse/clickhouse-jdbc/releases/tag/v0.3.1-patch

### Compatibility With `clickhouse-backup`

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/clickhouse-backup/

The compatibility with [clickhouse-backup](https://github.com/AlexAkulov/clickhouse-backup) utility SHALL be verified

* by executing automated tests in https://github.com/AlexAkulov/clickhouse-backup/tree/master/test/integration
* by executing automated tests in ACM

### Compatibility With Operation on Kubernetes

#### `clickhouse-operator`

**Results:** https://altinity-qa.gitlab.io/results/ClickHouse/21.8-LTS/clickhouse-operator/results.html

Compatibility with `clickhouse-operator` in Kubernetes environment SHALL be verified.

### Operation on Production Cluster

**Results:** _manual testing performed by support team_

Operation on a production cluster SHALL be verified.

### Upgrade and Downgrade Path

**Results:** _manual testing performed by support team_

The upgrade and downgrade path SHALL be verified on the following combinations using ACM
and reference production like cluster

#### Upgrade

* from 21.3 to 21.8 [tsaltykova]

#### Downgrade

* from 21.8 to 21.3 [tsaltykova]

### Compatibility With BI Tools

Compatibility with the following BI tools SHALL be verified.

#### Grafana

**Results:** https://gitlab.com/altinity-qa/results/-/tree/master/results/ClickHouse/21.8-LTS/clickhouse-grafana

Compatibility with [Grafana] SHALL be verified using
https://grafana.com/grafana/plugins/vertamedia-clickhouse-datasource/ data source for the following versions:

* 2.3.1
* Grafana 7.x (latest)

#### Tableau

**Results:** https://gitlab.com/altinity-qa/results/-/tree/master/results/ClickHouse/21.8-LTS/tableau

Compatibility with [Tableau] SHALL be verified using the current version of
https://github.com/Altinity/clickhouse-tableau-connector-odbc connector.

#### Superset

**Results:** https://gitlab.com/altinity-qa/results/-/tree/master/results/ClickHouse/21.8-LTS/superset

Compatibility with [Superset] SHALL be verified using the following pre-requisites:

* clickhouse-driver==0.2.1
* clickhouse-sqlalchemy==0.1.6

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[GitLab Repository]: https://gitlab.com/altinity-qa/documents/qa-stp001-clickhouse-21.8-long-term-support-release/
[Revision History]: https://gitlab.com/altinity-qa/documents/qa-stp001-clickhouse-21.8-long-term-support-release/-/commits/main/
[Git]: https://git-scm.com/
[GitLab]: https://gitlab.com
