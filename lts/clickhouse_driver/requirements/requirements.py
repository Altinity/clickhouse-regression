# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_103_ClickHouseDriver_UpstreamTests = Requirement(
    name="RQ.SRS-103.ClickHouseDriver.UpstreamTests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The clickhouse-driver upstream test suite, at the tested release tag and with the\n"
        "patches in `lts/clickhouse_driver/configs/patches`, SHALL pass against a\n"
        "ClickHouse server started from the LTS image, except for failures listed as\n"
        "known issues.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_103_ClickHouseDriver_Compatibility_LTS = Requirement(
    name="RQ.SRS-103.ClickHouseDriver.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "clickhouse-driver SHALL be verified to work against the current Altinity\n"
        "ClickHouse LTS build.\n"
        "\n"
        "[clickhouse-driver]: https://github.com/mymarilyn/clickhouse-driver\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

SRS_103_ClickHouse_Python_Driver_clickhouse_driver_LTS_Testing = Specification(
    name="SRS-103 ClickHouse Python Driver (clickhouse-driver) LTS Testing",
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
        Heading(name="Upstream Tests", level=2, num="3.1"),
        Heading(name="RQ.SRS-103.ClickHouseDriver.UpstreamTests", level=3, num="3.1.1"),
        Heading(name="Compatibility", level=2, num="3.2"),
        Heading(
            name="RQ.SRS-103.ClickHouseDriver.Compatibility.LTS", level=3, num="3.2.1"
        ),
    ),
    requirements=(
        RQ_SRS_103_ClickHouseDriver_UpstreamTests,
        RQ_SRS_103_ClickHouseDriver_Compatibility_LTS,
    ),
    content=r"""
# SRS-103 ClickHouse Python Driver (clickhouse-driver) LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Upstream Tests](#upstream-tests)
        * 3.1.1 [RQ.SRS-103.ClickHouseDriver.UpstreamTests](#rqsrs-103clickhousedriverupstreamtests)
    * 3.2 [Compatibility](#compatibility)
        * 3.2.1 [RQ.SRS-103.ClickHouseDriver.Compatibility.LTS](#rqsrs-103clickhousedrivercompatibilitylts)

## Introduction

This SRS covers testing the [clickhouse-driver] Python package, which talks to
ClickHouse over the native protocol, against ClickHouse LTS builds. The driver's
own test suite is run against a server started from the LTS image.

## Terminology

- **LTS** — Long-Term Support ClickHouse release.
- **Upstream tests** — the test suite in the clickhouse-driver repository.

## Requirements

### Upstream Tests

#### RQ.SRS-103.ClickHouseDriver.UpstreamTests
version: 1.0

The clickhouse-driver upstream test suite, at the tested release tag and with the
patches in `lts/clickhouse_driver/configs/patches`, SHALL pass against a
ClickHouse server started from the LTS image, except for failures listed as
known issues.

### Compatibility

#### RQ.SRS-103.ClickHouseDriver.Compatibility.LTS
version: 1.0

clickhouse-driver SHALL be verified to work against the current Altinity
ClickHouse LTS build.

[clickhouse-driver]: https://github.com/mymarilyn/clickhouse-driver
""",
)
