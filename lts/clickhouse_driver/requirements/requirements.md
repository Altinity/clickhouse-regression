# SRS-103 ClickHouse Python Driver (clickhouse-driver) LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Test Suite](#test-suite)
        * 3.1.1 [RQ.SRS-103.ClickHouseDriver.TestSuite](#rqsrs-103clickhousedrivertestsuite)
    * 3.2 [Compatibility](#compatibility)
        * 3.2.1 [RQ.SRS-103.ClickHouseDriver.Compatibility.LTS](#rqsrs-103clickhousedrivercompatibilitylts)

## Introduction

This SRS covers testing the [clickhouse-driver] Python package, which talks to
ClickHouse over the native protocol, against ClickHouse LTS builds. The driver's
own test suite is run against a server started from the LTS image.

## Terminology

- **LTS** — Long-Term Support ClickHouse release.
- **Test suite** — the tests in the clickhouse-driver repository.

## Requirements

### Test Suite

#### RQ.SRS-103.ClickHouseDriver.TestSuite
version: 1.0

The clickhouse-driver test suite, at the tested release tag and with the
patches in `lts/clickhouse_driver/configs/patches`, SHALL pass against a
ClickHouse server started from the LTS image, except for failures listed as
known issues.

### Compatibility

#### RQ.SRS-103.ClickHouseDriver.Compatibility.LTS
version: 1.0

clickhouse-driver SHALL be verified to work against the current Altinity
ClickHouse LTS build.

[clickhouse-driver]: https://github.com/mymarilyn/clickhouse-driver
