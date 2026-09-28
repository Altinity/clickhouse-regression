# SRS-106 DBeaver JDBC Compatibility Smoke Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Driver](#driver)
        * 3.1.1 [RQ.SRS-106.DBeaver.Driver](#rqsrs-106dbeaverdriver)
    * 3.2 [Smoke Checks](#smoke-checks)
        * 3.2.1 [RQ.SRS-106.DBeaver.SmokeChecks](#rqsrs-106dbeaversmokechecks)
    * 3.3 [Compatibility](#compatibility)
        * 3.3.1 [RQ.SRS-106.DBeaver.Compatibility.LTS](#rqsrs-106dbeavercompatibilitylts)

## Introduction

This SRS covers a compatibility smoke test of the ClickHouse JDBC driver that
[DBeaver] Community Edition bundles, against ClickHouse LTS builds. The checks
replay what a user does in DBeaver: connect, create a dataset, query it,
browse the navigator, open a table and edit its data, using the same JDBC
driver and the same SQL as the DBeaver ClickHouse plugin.

DBeaver itself is not run. Its startup, plugin runtime, classloading,
connection dialogs and result grid are not tested, so a passing run shows that
the driver and SQL DBeaver uses work with the LTS build, not that DBeaver as a
whole does.

## Terminology

- **LTS** — Long-Term Support ClickHouse release.
- **Navigator** — the DBeaver tree of databases, tables and columns.

## Requirements

### Driver

#### RQ.SRS-106.DBeaver.Driver
version: 1.0

The smoke checks SHALL use the ClickHouse JDBC driver and httpclient5 versions
that the DBeaver ClickHouse plugin (`org.jkiss.dbeaver.ext.clickhouse/plugin.xml`)
declares at the tested DBeaver release tag.

### Smoke Checks

#### RQ.SRS-106.DBeaver.SmokeChecks
version: 1.0

The following SHALL work against a ClickHouse server started from the LTS image:

* connecting over HTTP and reading the server version with `SELECT VERSION()`
* creating a dataset (database, MergeTree table and 100 rows) from the SQL editor
* listing databases, table engines, tables and columns in the navigator
* reading database and table statistics from `system.parts`
* showing a table's DDL with `SHOW CREATE TABLE`
* querying the dataset with `count()`, aggregates, `WHERE`, `GROUP BY`,
  `ORDER BY ... LIMIT` and `ARRAY JOIN`, with exact expected results
* reading rows of common types in the data editor
* inserting rows with a batched prepared statement

### Compatibility

#### RQ.SRS-106.DBeaver.Compatibility.LTS
version: 1.0

The JDBC driver bundled with DBeaver and the SQL DBeaver sends SHALL be
verified to work against the current Altinity ClickHouse LTS build.

[DBeaver]: https://github.com/dbeaver/dbeaver
