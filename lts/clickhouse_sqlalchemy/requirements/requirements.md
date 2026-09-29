# SRS-104 ClickHouse SQLAlchemy Dialect (clickhouse-sqlalchemy) LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Test Suite](#test-suite)
        * 3.1.1 [RQ.SRS-104.ClickHouseSQLAlchemy.TestSuite](#rqsrs-104clickhousesqlalchemytestsuite)
    * 3.2 [Compatibility](#compatibility)
        * 3.2.1 [RQ.SRS-104.ClickHouseSQLAlchemy.Compatibility.LTS](#rqsrs-104clickhousesqlalchemycompatibilitylts)

## Introduction

This SRS covers testing the [clickhouse-sqlalchemy] SQLAlchemy dialect, with its
native, HTTP and asynch drivers, against ClickHouse LTS builds. The dialect's own
test suite is run against a server started from the LTS image.

## Terminology

- **LTS** — Long-Term Support ClickHouse release.
- **Test suite** — the tests in the clickhouse-sqlalchemy repository.

## Requirements

### Test Suite

#### RQ.SRS-104.ClickHouseSQLAlchemy.TestSuite
version: 1.0

The clickhouse-sqlalchemy test suite, at the tested release tag and with the
patches in `lts/clickhouse_sqlalchemy/configs/patches`, SHALL pass against a
ClickHouse server started from the LTS image, except for failures listed as
known issues.

### Compatibility

#### RQ.SRS-104.ClickHouseSQLAlchemy.Compatibility.LTS
version: 1.0

clickhouse-sqlalchemy SHALL be verified to work against the current Altinity
ClickHouse LTS build.

[clickhouse-sqlalchemy]: https://github.com/xzkostyan/clickhouse-sqlalchemy
