# SRS-105 ClickHouse JDBC Driver (clickhouse-jdbc) LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Test Suite](#test-suite)
        * 3.1.1 [RQ.SRS-105.ClickHouseJDBC.TestSuite](#rqsrs-105clickhousejdbctestsuite)
    * 3.2 [Compatibility](#compatibility)
        * 3.2.1 [RQ.SRS-105.ClickHouseJDBC.Compatibility.LTS](#rqsrs-105clickhousejdbccompatibilitylts)

## Introduction

This SRS covers testing the `clickhouse-jdbc` module of [clickhouse-java], the
JDBC driver used by Java applications and by tools such as DBeaver, against
ClickHouse LTS builds. The module's own unit and integration tests are run, with
the integration tests starting ClickHouse from the LTS image.

## Terminology

- **LTS** — Long-Term Support ClickHouse release.
- **Test suite** — the surefire and failsafe tests of the `clickhouse-jdbc`
  module in the clickhouse-java repository.

## Requirements

### Test Suite

#### RQ.SRS-105.ClickHouseJDBC.TestSuite
version: 1.0

The `clickhouse-jdbc` module tests, at the tested clickhouse-java release tag,
SHALL pass against a ClickHouse server started from the LTS image, except for
failures listed as known issues.

### Compatibility

#### RQ.SRS-105.ClickHouseJDBC.Compatibility.LTS
version: 1.0

clickhouse-jdbc SHALL be verified to work against the current Altinity
ClickHouse LTS build.

[clickhouse-java]: https://github.com/ClickHouse/clickhouse-java
