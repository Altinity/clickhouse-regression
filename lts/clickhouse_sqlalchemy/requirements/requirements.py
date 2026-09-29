# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_104_ClickHouseSQLAlchemy_TestSuite = Requirement(
    name="RQ.SRS-104.ClickHouseSQLAlchemy.TestSuite",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The clickhouse-sqlalchemy test suite, at the tested release tag and with the\n"
        "patches in `lts/clickhouse_sqlalchemy/configs/patches`, SHALL pass against a\n"
        "ClickHouse server started from the LTS image, except for failures listed as\n"
        "known issues.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_104_ClickHouseSQLAlchemy_Compatibility_LTS = Requirement(
    name="RQ.SRS-104.ClickHouseSQLAlchemy.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "clickhouse-sqlalchemy SHALL be verified to work against the current Altinity\n"
        "ClickHouse LTS build.\n"
        "\n"
        "[clickhouse-sqlalchemy]: https://github.com/xzkostyan/clickhouse-sqlalchemy\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

SRS_104_ClickHouse_SQLAlchemy_Dialect_clickhouse_sqlalchemy_LTS_Testing = Specification(
    name="SRS-104 ClickHouse SQLAlchemy Dialect (clickhouse-sqlalchemy) LTS Testing",
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
        Heading(name="RQ.SRS-104.ClickHouseSQLAlchemy.TestSuite", level=3, num="3.1.1"),
        Heading(name="Compatibility", level=2, num="3.2"),
        Heading(
            name="RQ.SRS-104.ClickHouseSQLAlchemy.Compatibility.LTS",
            level=3,
            num="3.2.1",
        ),
    ),
    requirements=(
        RQ_SRS_104_ClickHouseSQLAlchemy_TestSuite,
        RQ_SRS_104_ClickHouseSQLAlchemy_Compatibility_LTS,
    ),
    content=r"""
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
""",
)
