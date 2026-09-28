# SRS-104 ClickHouse SQLAlchemy Dialect (clickhouse-sqlalchemy) LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Upstream Tests](#upstream-tests)
        * 3.1.1 [RQ.SRS-104.ClickHouseSQLAlchemy.UpstreamTests](#rqsrs-104clickhousesqlalchemyupstreamtests)
    * 3.2 [Compatibility](#compatibility)
        * 3.2.1 [RQ.SRS-104.ClickHouseSQLAlchemy.Compatibility.LTS](#rqsrs-104clickhousesqlalchemycompatibilitylts)

## Introduction

This SRS covers testing the [clickhouse-sqlalchemy] SQLAlchemy dialect, with its
native, HTTP and asynch drivers, against ClickHouse LTS builds. The dialect's own
test suite is run against a server started from the LTS image.

## Terminology

- **LTS** — Long-Term Support ClickHouse release.
- **Upstream tests** — the test suite in the clickhouse-sqlalchemy repository.

## Requirements

### Upstream Tests

#### RQ.SRS-104.ClickHouseSQLAlchemy.UpstreamTests
version: 1.0

The clickhouse-sqlalchemy upstream test suite, at the tested release tag and with the
patches in `lts/clickhouse_sqlalchemy/configs/patches`, SHALL pass against a
ClickHouse server started from the LTS image, except for failures listed as
known issues.

### Compatibility

#### RQ.SRS-104.ClickHouseSQLAlchemy.Compatibility.LTS
version: 1.0

clickhouse-sqlalchemy SHALL be verified to work against the current Altinity
ClickHouse LTS build.

[clickhouse-sqlalchemy]: https://github.com/xzkostyan/clickhouse-sqlalchemy
