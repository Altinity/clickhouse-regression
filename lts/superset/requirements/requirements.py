# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_101_Superset_Environment = Requirement(
    name="RQ.SRS-101.Superset.Environment",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The test environment SHALL deploy Apache Superset, ClickHouse and a Selenium\n"
        "Grid node using Docker Compose (services `superset`, `clickhouse` and\n"
        "`selenium`), with ClickHouse serving HTTP, HTTPS and the native protocol.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_101_Superset_Environment_ClickHouseConnect = Requirement(
    name="RQ.SRS-101.Superset.Environment.ClickHouseConnect",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When built with the `clickhouse-connect` driver, Superset SHALL list the\n"
        "ClickHouse Connect database engine as available.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.2",
)

RQ_SRS_101_Superset_Environment_ClickHouseSQLAlchemy = Requirement(
    name="RQ.SRS-101.Superset.Environment.ClickHouseSQLAlchemy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When built with the `clickhouse-sqlalchemy` driver, Superset SHALL list the\n"
        "`clickhouse` database engine as available.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.3",
)

RQ_SRS_101_Superset_DatabaseConnection = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL add a ClickHouse database connection, show it in the Databases\n"
        "list, and report the connection as working through its test-connection API,\n"
        'which is what the "Test Connection" button in the database form calls.\n'
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

RQ_SRS_101_Superset_DatabaseConnection_HTTP = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection.HTTP",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL connect to ClickHouse over the HTTP interface (port 8123).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.2",
)

RQ_SRS_101_Superset_DatabaseConnection_HTTPS = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection.HTTPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL connect to ClickHouse over HTTPS (port 8443) using the\n"
        "provided TLS certificates.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.3",
)

RQ_SRS_101_Superset_DatabaseConnection_NativeProtocol = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection.NativeProtocol",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When using the `clickhouse-sqlalchemy` driver, Superset SHALL connect to\n"
        "ClickHouse over the native protocol (port 9000). `clickhouse-connect` has no\n"
        "native protocol support, so this is not tested with it.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.4",
)

RQ_SRS_101_Superset_SQLLab_QueryExecution = Requirement(
    name="RQ.SRS-101.Superset.SQLLab.QueryExecution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SQL Lab SHALL execute queries against ClickHouse and display the\n"
        "exact results: for the seeded `lts.events` table, one row per country with\n"
        "200 events each and the expected average amount.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

RQ_SRS_101_Superset_Compatibility_LTS = Requirement(
    name="RQ.SRS-101.Superset.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The features above SHALL be verified to work against the current Altinity\n"
        "ClickHouse LTS build.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.4.1",
)

SRS_101_Apache_Superset_ClickHouse_Integration_LTS_Testing = Specification(
    name="SRS-101 Apache Superset ClickHouse Integration LTS Testing",
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
        Heading(name="Environment Setup", level=2, num="3.1"),
        Heading(name="RQ.SRS-101.Superset.Environment", level=3, num="3.1.1"),
        Heading(
            name="RQ.SRS-101.Superset.Environment.ClickHouseConnect",
            level=3,
            num="3.1.2",
        ),
        Heading(
            name="RQ.SRS-101.Superset.Environment.ClickHouseSQLAlchemy",
            level=3,
            num="3.1.3",
        ),
        Heading(name="Database Connection", level=2, num="3.2"),
        Heading(name="RQ.SRS-101.Superset.DatabaseConnection", level=3, num="3.2.1"),
        Heading(
            name="RQ.SRS-101.Superset.DatabaseConnection.HTTP", level=3, num="3.2.2"
        ),
        Heading(
            name="RQ.SRS-101.Superset.DatabaseConnection.HTTPS", level=3, num="3.2.3"
        ),
        Heading(
            name="RQ.SRS-101.Superset.DatabaseConnection.NativeProtocol",
            level=3,
            num="3.2.4",
        ),
        Heading(name="SQL Lab", level=2, num="3.3"),
        Heading(name="RQ.SRS-101.Superset.SQLLab.QueryExecution", level=3, num="3.3.1"),
        Heading(name="Compatibility", level=2, num="3.4"),
        Heading(name="RQ.SRS-101.Superset.Compatibility.LTS", level=3, num="3.4.1"),
        Heading(name="Not Yet Covered", level=1, num="4"),
    ),
    requirements=(
        RQ_SRS_101_Superset_Environment,
        RQ_SRS_101_Superset_Environment_ClickHouseConnect,
        RQ_SRS_101_Superset_Environment_ClickHouseSQLAlchemy,
        RQ_SRS_101_Superset_DatabaseConnection,
        RQ_SRS_101_Superset_DatabaseConnection_HTTP,
        RQ_SRS_101_Superset_DatabaseConnection_HTTPS,
        RQ_SRS_101_Superset_DatabaseConnection_NativeProtocol,
        RQ_SRS_101_Superset_SQLLab_QueryExecution,
        RQ_SRS_101_Superset_Compatibility_LTS,
    ),
    content=r"""
# SRS-101 Apache Superset ClickHouse Integration LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Environment Setup](#environment-setup)
        * 3.1.1 [RQ.SRS-101.Superset.Environment](#rqsrs-101supersetenvironment)
        * 3.1.2 [RQ.SRS-101.Superset.Environment.ClickHouseConnect](#rqsrs-101supersetenvironmentclickhouseconnect)
        * 3.1.3 [RQ.SRS-101.Superset.Environment.ClickHouseSQLAlchemy](#rqsrs-101supersetenvironmentclickhousesqlalchemy)
    * 3.2 [Database Connection](#database-connection)
        * 3.2.1 [RQ.SRS-101.Superset.DatabaseConnection](#rqsrs-101supersetdatabaseconnection)
        * 3.2.2 [RQ.SRS-101.Superset.DatabaseConnection.HTTP](#rqsrs-101supersetdatabaseconnectionhttp)
        * 3.2.3 [RQ.SRS-101.Superset.DatabaseConnection.HTTPS](#rqsrs-101supersetdatabaseconnectionhttps)
        * 3.2.4 [RQ.SRS-101.Superset.DatabaseConnection.NativeProtocol](#rqsrs-101supersetdatabaseconnectionnativeprotocol)
    * 3.3 [SQL Lab](#sql-lab)
        * 3.3.1 [RQ.SRS-101.Superset.SQLLab.QueryExecution](#rqsrs-101supersetsqllabqueryexecution)
    * 3.4 [Compatibility](#compatibility)
        * 3.4.1 [RQ.SRS-101.Superset.Compatibility.LTS](#rqsrs-101supersetcompatibilitylts)
* 4 [Not Yet Covered](#not-yet-covered)

## Introduction

This SRS covers the testing requirements for Apache Superset integration with
ClickHouse when running against Altinity ClickHouse LTS builds. The tests verify
that Superset loads the selected ClickHouse driver, connects to ClickHouse over
HTTP, HTTPS and, with `clickhouse-sqlalchemy`, the native protocol, and runs
queries in SQL Lab with exact expected results.

One run uses one driver, selected with `--clickhouse-driver`. Covering both
drivers takes one run per driver.

## Terminology

- **Superset** — Apache Superset, an open-source data exploration and visualization
  platform.
- **clickhouse-connect** — ClickHouse Python driver using the HTTP interface.
- **clickhouse-sqlalchemy** — SQLAlchemy dialect for ClickHouse, supporting the
  HTTP and native protocols.
- **LTS** — Long-Term Support ClickHouse release.

## Requirements

### Environment Setup

#### RQ.SRS-101.Superset.Environment
version: 1.0

The test environment SHALL deploy Apache Superset, ClickHouse and a Selenium
Grid node using Docker Compose (services `superset`, `clickhouse` and
`selenium`), with ClickHouse serving HTTP, HTTPS and the native protocol.

#### RQ.SRS-101.Superset.Environment.ClickHouseConnect
version: 1.0

When built with the `clickhouse-connect` driver, Superset SHALL list the
ClickHouse Connect database engine as available.

#### RQ.SRS-101.Superset.Environment.ClickHouseSQLAlchemy
version: 1.0

When built with the `clickhouse-sqlalchemy` driver, Superset SHALL list the
`clickhouse` database engine as available.

### Database Connection

#### RQ.SRS-101.Superset.DatabaseConnection
version: 1.0

Superset SHALL add a ClickHouse database connection, show it in the Databases
list, and report the connection as working through its test-connection API,
which is what the "Test Connection" button in the database form calls.

#### RQ.SRS-101.Superset.DatabaseConnection.HTTP
version: 1.0

Superset SHALL connect to ClickHouse over the HTTP interface (port 8123).

#### RQ.SRS-101.Superset.DatabaseConnection.HTTPS
version: 1.0

Superset SHALL connect to ClickHouse over HTTPS (port 8443) using the
provided TLS certificates.

#### RQ.SRS-101.Superset.DatabaseConnection.NativeProtocol
version: 1.0

When using the `clickhouse-sqlalchemy` driver, Superset SHALL connect to
ClickHouse over the native protocol (port 9000). `clickhouse-connect` has no
native protocol support, so this is not tested with it.

### SQL Lab

#### RQ.SRS-101.Superset.SQLLab.QueryExecution
version: 1.0

Superset SQL Lab SHALL execute queries against ClickHouse and display the
exact results: for the seeded `lts.events` table, one row per country with
200 events each and the expected average amount.

### Compatibility

#### RQ.SRS-101.Superset.Compatibility.LTS
version: 1.0

The features above SHALL be verified to work against the current Altinity
ClickHouse LTS build.

## Not Yet Covered

These are part of normal Superset use but have no tests yet, so they are not
listed as requirements:

- the SQL Lab schema explorer listing ClickHouse databases, tables and columns;
- creating charts from ClickHouse datasets, and rendering columns of the
  common types;
- creating dashboards with ClickHouse-backed charts, and refreshing them.
""",
)
