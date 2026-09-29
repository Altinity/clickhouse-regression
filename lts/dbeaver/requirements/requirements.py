# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_106_DBeaver_Driver = Requirement(
    name="RQ.SRS-106.DBeaver.Driver",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The smoke checks SHALL use the ClickHouse JDBC driver and httpclient5 versions\n"
        "that the DBeaver ClickHouse plugin (`org.jkiss.dbeaver.ext.clickhouse/plugin.xml`)\n"
        "declares at the tested DBeaver release tag.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_106_DBeaver_SmokeChecks = Requirement(
    name="RQ.SRS-106.DBeaver.SmokeChecks",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The following SHALL work against a ClickHouse server started from the LTS image:\n"
        "\n"
        "* connecting over HTTP and reading the server version with `SELECT VERSION()`\n"
        "* creating a dataset (database, MergeTree table and 100 rows) from the SQL editor\n"
        "* listing databases, table engines, tables and columns in the navigator\n"
        "* reading database and table statistics from `system.parts`\n"
        "* showing a table's DDL with `SHOW CREATE TABLE`\n"
        "* querying the dataset with `count()`, aggregates, `WHERE`, `GROUP BY`,\n"
        "  `ORDER BY ... LIMIT` and `ARRAY JOIN`, with exact expected results\n"
        "* reading rows of common types in the data editor\n"
        "* inserting rows with a batched prepared statement\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

RQ_SRS_106_DBeaver_Compatibility_LTS = Requirement(
    name="RQ.SRS-106.DBeaver.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The JDBC driver bundled with DBeaver and the SQL DBeaver sends SHALL be\n"
        "verified to work against the current Altinity ClickHouse LTS build.\n"
        "\n"
        "[DBeaver]: https://github.com/dbeaver/dbeaver\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

SRS_106_DBeaver_JDBC_Compatibility_Smoke_Testing = Specification(
    name="SRS-106 DBeaver JDBC Compatibility Smoke Testing",
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
        Heading(name="Driver", level=2, num="3.1"),
        Heading(name="RQ.SRS-106.DBeaver.Driver", level=3, num="3.1.1"),
        Heading(name="Smoke Checks", level=2, num="3.2"),
        Heading(name="RQ.SRS-106.DBeaver.SmokeChecks", level=3, num="3.2.1"),
        Heading(name="Compatibility", level=2, num="3.3"),
        Heading(name="RQ.SRS-106.DBeaver.Compatibility.LTS", level=3, num="3.3.1"),
    ),
    requirements=(
        RQ_SRS_106_DBeaver_Driver,
        RQ_SRS_106_DBeaver_SmokeChecks,
        RQ_SRS_106_DBeaver_Compatibility_LTS,
    ),
    content=r"""
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
""",
)
