# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_105_ClickHouseJDBC_TestSuite = Requirement(
    name="RQ.SRS-105.ClickHouseJDBC.TestSuite",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `clickhouse-jdbc` module tests, at the tested clickhouse-java release tag,\n"
        "SHALL pass against a ClickHouse server started from the LTS image, except for\n"
        "failures listed as known issues.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_105_ClickHouseJDBC_Compatibility_LTS = Requirement(
    name="RQ.SRS-105.ClickHouseJDBC.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "clickhouse-jdbc SHALL be verified to work against the current Altinity\n"
        "ClickHouse LTS build.\n"
        "\n"
        "[clickhouse-java]: https://github.com/ClickHouse/clickhouse-java\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

SRS_105_ClickHouse_JDBC_Driver_clickhouse_jdbc_LTS_Testing = Specification(
    name="SRS-105 ClickHouse JDBC Driver (clickhouse-jdbc) LTS Testing",
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Terminology", level=1, num="2"),
        Heading(name="Requirements", level=1, num="3"),
        Heading(name="Test Suite", level=2, num="3.1"),
        Heading(name="RQ.SRS-105.ClickHouseJDBC.TestSuite", level=3, num="3.1.1"),
        Heading(name="Compatibility", level=2, num="3.2"),
        Heading(
            name="RQ.SRS-105.ClickHouseJDBC.Compatibility.LTS", level=3, num="3.2.1"
        ),
    ),
    requirements=(
        RQ_SRS_105_ClickHouseJDBC_TestSuite,
        RQ_SRS_105_ClickHouseJDBC_Compatibility_LTS,
    ),
    content=r"""
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
""",
)
