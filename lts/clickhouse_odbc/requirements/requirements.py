# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_100_ODBC_DriverBuild = Requirement(
    name="RQ.SRS-100.ODBC.DriverBuild",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The clickhouse-odbc driver SHALL be buildable from source against the target\n"
        "ClickHouse version and produce working shared libraries\n"
        "(`libclickhouseodbc.so`, `libclickhouseodbcw.so`).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_100_ODBC_Connection = Requirement(
    name="RQ.SRS-100.ODBC.Connection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL successfully connect to a running ClickHouse server\n"
        "and execute a basic `SELECT 1` query.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

RQ_SRS_100_ODBC_Connection_DSN = Requirement(
    name="RQ.SRS-100.ODBC.Connection.DSN",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL support connection via both ANSI and Unicode DSN\n"
        "configurations.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.2",
)

RQ_SRS_100_ODBC_DataTypes_Int8 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int8` values including boundary\n"
        "values (-128, 0, 127).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

RQ_SRS_100_ODBC_DataTypes_Int16 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int16` values including boundary\n"
        "values (-32768, 0, 32767).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.2",
)

RQ_SRS_100_ODBC_DataTypes_Int32 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int32` values including boundary\n"
        "values (-2147483648, 0, 2147483647).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.3",
)

RQ_SRS_100_ODBC_DataTypes_Int64 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int64` values including boundary\n"
        "values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.4",
)

RQ_SRS_100_ODBC_DataTypes_UInt8 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt8` values (0, 255).\n" "\n"
    ),
    link=None,
    level=3,
    num="3.3.5",
)

RQ_SRS_100_ODBC_DataTypes_UInt16 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt16` values (0, 65535).\n" "\n"
    ),
    link=None,
    level=3,
    num="3.3.6",
)

RQ_SRS_100_ODBC_DataTypes_UInt32 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt32` values (0, 4294967295).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.7",
)

RQ_SRS_100_ODBC_DataTypes_UInt64 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt64` values (0, 18446744073709551615).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.8",
)

RQ_SRS_100_ODBC_DataTypes_Float32 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Float32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Float32` values including special\n"
        "values (inf, -inf, nan).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.9",
)

RQ_SRS_100_ODBC_DataTypes_Float64 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Float64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Float64` values including special\n"
        "values (inf, -inf, nan).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.10",
)

RQ_SRS_100_ODBC_DataTypes_Decimal = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Decimal",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Decimal32`, `Decimal64`, and\n"
        "`Decimal128` values with configurable precision and scale.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.11",
)

RQ_SRS_100_ODBC_DataTypes_String = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.String",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `String` values including UTF-8,\n"
        "ASCII, and special characters.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.12",
)

RQ_SRS_100_ODBC_DataTypes_FixedString = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.FixedString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `FixedString(N)` values with\n"
        "proper null-byte padding.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.13",
)

RQ_SRS_100_ODBC_DataTypes_Date = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Date",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `Date` values.\n" "\n"),
    link=None,
    level=3,
    num="3.3.14",
)

RQ_SRS_100_ODBC_DataTypes_DateTime = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.DateTime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `DateTime` values.\n" "\n"
    ),
    link=None,
    level=3,
    num="3.3.15",
)

RQ_SRS_100_ODBC_DataTypes_Enum = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Enum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Enum` values with both UTF-8\n"
        "and ASCII keys.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.16",
)

RQ_SRS_100_ODBC_DataTypes_UUID = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UUID",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `UUID` values.\n" "\n"),
    link=None,
    level=3,
    num="3.3.17",
)

RQ_SRS_100_ODBC_DataTypes_IPv4 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.IPv4",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `IPv4` values.\n" "\n"),
    link=None,
    level=3,
    num="3.3.18",
)

RQ_SRS_100_ODBC_DataTypes_IPv6 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.IPv6",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `IPv6` values.\n" "\n"),
    link=None,
    level=3,
    num="3.3.19",
)

RQ_SRS_100_ODBC_DataTypes_Nullable = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Nullable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly handle `Nullable` variants of all supported\n"
        "data types, returning `None` for NULL values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.20",
)

RQ_SRS_100_ODBC_ParameterizedQueries = Requirement(
    name="RQ.SRS-100.ODBC.ParameterizedQueries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL support parameterized queries (`?` placeholders) for\n"
        "all supported data types.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.4.1",
)

RQ_SRS_100_ODBC_ParameterizedQueries_Null = Requirement(
    name="RQ.SRS-100.ODBC.ParameterizedQueries.Null",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly handle `NULL` parameter values in\n"
        "parameterized queries including with `isNull()` and `arrayReduce()` functions.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.4.2",
)

RQ_SRS_100_ODBC_Compatibility_LTS = Requirement(
    name="RQ.SRS-100.ODBC.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL be verified to work against the current Altinity\n"
        "ClickHouse LTS build.\n"
    ),
    link=None,
    level=3,
    num="3.5.1",
)

SRS_100_ClickHouse_ODBC_Driver_LTS_Testing = Specification(
    name="SRS-100 ClickHouse ODBC Driver LTS Testing",
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
        Heading(name="Driver Build", level=2, num="3.1"),
        Heading(name="RQ.SRS-100.ODBC.DriverBuild", level=3, num="3.1.1"),
        Heading(name="Connection", level=2, num="3.2"),
        Heading(name="RQ.SRS-100.ODBC.Connection", level=3, num="3.2.1"),
        Heading(name="RQ.SRS-100.ODBC.Connection.DSN", level=3, num="3.2.2"),
        Heading(name="Data Types", level=2, num="3.3"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Int8", level=3, num="3.3.1"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Int16", level=3, num="3.3.2"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Int32", level=3, num="3.3.3"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Int64", level=3, num="3.3.4"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.UInt8", level=3, num="3.3.5"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.UInt16", level=3, num="3.3.6"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.UInt32", level=3, num="3.3.7"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.UInt64", level=3, num="3.3.8"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Float32", level=3, num="3.3.9"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Float64", level=3, num="3.3.10"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Decimal", level=3, num="3.3.11"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.String", level=3, num="3.3.12"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.FixedString", level=3, num="3.3.13"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Date", level=3, num="3.3.14"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.DateTime", level=3, num="3.3.15"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Enum", level=3, num="3.3.16"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.UUID", level=3, num="3.3.17"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.IPv4", level=3, num="3.3.18"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.IPv6", level=3, num="3.3.19"),
        Heading(name="RQ.SRS-100.ODBC.DataTypes.Nullable", level=3, num="3.3.20"),
        Heading(name="Parameterized Queries", level=2, num="3.4"),
        Heading(name="RQ.SRS-100.ODBC.ParameterizedQueries", level=3, num="3.4.1"),
        Heading(name="RQ.SRS-100.ODBC.ParameterizedQueries.Null", level=3, num="3.4.2"),
        Heading(name="Compatibility", level=2, num="3.5"),
        Heading(name="RQ.SRS-100.ODBC.Compatibility.LTS", level=3, num="3.5.1"),
    ),
    requirements=(
        RQ_SRS_100_ODBC_DriverBuild,
        RQ_SRS_100_ODBC_Connection,
        RQ_SRS_100_ODBC_Connection_DSN,
        RQ_SRS_100_ODBC_DataTypes_Int8,
        RQ_SRS_100_ODBC_DataTypes_Int16,
        RQ_SRS_100_ODBC_DataTypes_Int32,
        RQ_SRS_100_ODBC_DataTypes_Int64,
        RQ_SRS_100_ODBC_DataTypes_UInt8,
        RQ_SRS_100_ODBC_DataTypes_UInt16,
        RQ_SRS_100_ODBC_DataTypes_UInt32,
        RQ_SRS_100_ODBC_DataTypes_UInt64,
        RQ_SRS_100_ODBC_DataTypes_Float32,
        RQ_SRS_100_ODBC_DataTypes_Float64,
        RQ_SRS_100_ODBC_DataTypes_Decimal,
        RQ_SRS_100_ODBC_DataTypes_String,
        RQ_SRS_100_ODBC_DataTypes_FixedString,
        RQ_SRS_100_ODBC_DataTypes_Date,
        RQ_SRS_100_ODBC_DataTypes_DateTime,
        RQ_SRS_100_ODBC_DataTypes_Enum,
        RQ_SRS_100_ODBC_DataTypes_UUID,
        RQ_SRS_100_ODBC_DataTypes_IPv4,
        RQ_SRS_100_ODBC_DataTypes_IPv6,
        RQ_SRS_100_ODBC_DataTypes_Nullable,
        RQ_SRS_100_ODBC_ParameterizedQueries,
        RQ_SRS_100_ODBC_ParameterizedQueries_Null,
        RQ_SRS_100_ODBC_Compatibility_LTS,
    ),
    content=r"""
# SRS-100 ClickHouse ODBC Driver LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Driver Build](#driver-build)
        * 3.1.1 [RQ.SRS-100.ODBC.DriverBuild](#rqsrs-100odbcdriverbuild)
    * 3.2 [Connection](#connection)
        * 3.2.1 [RQ.SRS-100.ODBC.Connection](#rqsrs-100odbcconnection)
        * 3.2.2 [RQ.SRS-100.ODBC.Connection.DSN](#rqsrs-100odbcconnectiondsn)
    * 3.3 [Data Types](#data-types)
        * 3.3.1 [RQ.SRS-100.ODBC.DataTypes.Int8](#rqsrs-100odbcdatatypesint8)
        * 3.3.2 [RQ.SRS-100.ODBC.DataTypes.Int16](#rqsrs-100odbcdatatypesint16)
        * 3.3.3 [RQ.SRS-100.ODBC.DataTypes.Int32](#rqsrs-100odbcdatatypesint32)
        * 3.3.4 [RQ.SRS-100.ODBC.DataTypes.Int64](#rqsrs-100odbcdatatypesint64)
        * 3.3.5 [RQ.SRS-100.ODBC.DataTypes.UInt8](#rqsrs-100odbcdatatypesuint8)
        * 3.3.6 [RQ.SRS-100.ODBC.DataTypes.UInt16](#rqsrs-100odbcdatatypesuint16)
        * 3.3.7 [RQ.SRS-100.ODBC.DataTypes.UInt32](#rqsrs-100odbcdatatypesuint32)
        * 3.3.8 [RQ.SRS-100.ODBC.DataTypes.UInt64](#rqsrs-100odbcdatatypesuint64)
        * 3.3.9 [RQ.SRS-100.ODBC.DataTypes.Float32](#rqsrs-100odbcdatatypesfloat32)
        * 3.3.10 [RQ.SRS-100.ODBC.DataTypes.Float64](#rqsrs-100odbcdatatypesfloat64)
        * 3.3.11 [RQ.SRS-100.ODBC.DataTypes.Decimal](#rqsrs-100odbcdatatypesdecimal)
        * 3.3.12 [RQ.SRS-100.ODBC.DataTypes.String](#rqsrs-100odbcdatatypesstring)
        * 3.3.13 [RQ.SRS-100.ODBC.DataTypes.FixedString](#rqsrs-100odbcdatatypesfixedstring)
        * 3.3.14 [RQ.SRS-100.ODBC.DataTypes.Date](#rqsrs-100odbcdatatypesdate)
        * 3.3.15 [RQ.SRS-100.ODBC.DataTypes.DateTime](#rqsrs-100odbcdatatypesdatetime)
        * 3.3.16 [RQ.SRS-100.ODBC.DataTypes.Enum](#rqsrs-100odbcdatatypesenum)
        * 3.3.17 [RQ.SRS-100.ODBC.DataTypes.UUID](#rqsrs-100odbcdatatypesuuid)
        * 3.3.18 [RQ.SRS-100.ODBC.DataTypes.IPv4](#rqsrs-100odbcdatatypesipv4)
        * 3.3.19 [RQ.SRS-100.ODBC.DataTypes.IPv6](#rqsrs-100odbcdatatypesipv6)
        * 3.3.20 [RQ.SRS-100.ODBC.DataTypes.Nullable](#rqsrs-100odbcdatatypesnullable)
    * 3.4 [Parameterized Queries](#parameterized-queries)
        * 3.4.1 [RQ.SRS-100.ODBC.ParameterizedQueries](#rqsrs-100odbcparameterizedqueries)
        * 3.4.2 [RQ.SRS-100.ODBC.ParameterizedQueries.Null](#rqsrs-100odbcparameterizedqueriesnull)
    * 3.5 [Compatibility](#compatibility)
        * 3.5.1 [RQ.SRS-100.ODBC.Compatibility.LTS](#rqsrs-100odbccompatibilitylts)

## Introduction

This SRS covers the testing requirements for the ClickHouse ODBC driver when used
against ClickHouse LTS (Long-Term Support) builds. The goal is to verify that the
ODBC driver correctly handles connectivity, data type round-trips, and parameterized
queries across supported ClickHouse versions.

## Terminology

- **ODBC** — Open Database Connectivity, a standard API for accessing database
  management systems.
- **LTS** — Long-Term Support ClickHouse release.
- **DSN** — Data Source Name, a named ODBC configuration entry.

## Requirements

### Driver Build

#### RQ.SRS-100.ODBC.DriverBuild
version: 1.0

The clickhouse-odbc driver SHALL be buildable from source against the target
ClickHouse version and produce working shared libraries
(`libclickhouseodbc.so`, `libclickhouseodbcw.so`).

### Connection

#### RQ.SRS-100.ODBC.Connection
version: 1.0

The ODBC driver SHALL successfully connect to a running ClickHouse server
and execute a basic `SELECT 1` query.

#### RQ.SRS-100.ODBC.Connection.DSN
version: 1.0

The ODBC driver SHALL support connection via both ANSI and Unicode DSN
configurations.

### Data Types

#### RQ.SRS-100.ODBC.DataTypes.Int8
version: 1.0

The ODBC driver SHALL correctly round-trip `Int8` values including boundary
values (-128, 0, 127).

#### RQ.SRS-100.ODBC.DataTypes.Int16
version: 1.0

The ODBC driver SHALL correctly round-trip `Int16` values including boundary
values (-32768, 0, 32767).

#### RQ.SRS-100.ODBC.DataTypes.Int32
version: 1.0

The ODBC driver SHALL correctly round-trip `Int32` values including boundary
values (-2147483648, 0, 2147483647).

#### RQ.SRS-100.ODBC.DataTypes.Int64
version: 1.0

The ODBC driver SHALL correctly round-trip `Int64` values including boundary
values.

#### RQ.SRS-100.ODBC.DataTypes.UInt8
version: 1.0

The ODBC driver SHALL correctly round-trip `UInt8` values (0, 255).

#### RQ.SRS-100.ODBC.DataTypes.UInt16
version: 1.0

The ODBC driver SHALL correctly round-trip `UInt16` values (0, 65535).

#### RQ.SRS-100.ODBC.DataTypes.UInt32
version: 1.0

The ODBC driver SHALL correctly round-trip `UInt32` values (0, 4294967295).

#### RQ.SRS-100.ODBC.DataTypes.UInt64
version: 1.0

The ODBC driver SHALL correctly round-trip `UInt64` values (0, 18446744073709551615).

#### RQ.SRS-100.ODBC.DataTypes.Float32
version: 1.0

The ODBC driver SHALL correctly round-trip `Float32` values including special
values (inf, -inf, nan).

#### RQ.SRS-100.ODBC.DataTypes.Float64
version: 1.0

The ODBC driver SHALL correctly round-trip `Float64` values including special
values (inf, -inf, nan).

#### RQ.SRS-100.ODBC.DataTypes.Decimal
version: 1.0

The ODBC driver SHALL correctly round-trip `Decimal32`, `Decimal64`, and
`Decimal128` values with configurable precision and scale.

#### RQ.SRS-100.ODBC.DataTypes.String
version: 1.0

The ODBC driver SHALL correctly round-trip `String` values including UTF-8,
ASCII, and special characters.

#### RQ.SRS-100.ODBC.DataTypes.FixedString
version: 1.0

The ODBC driver SHALL correctly round-trip `FixedString(N)` values with
proper null-byte padding.

#### RQ.SRS-100.ODBC.DataTypes.Date
version: 1.0

The ODBC driver SHALL correctly round-trip `Date` values.

#### RQ.SRS-100.ODBC.DataTypes.DateTime
version: 1.0

The ODBC driver SHALL correctly round-trip `DateTime` values.

#### RQ.SRS-100.ODBC.DataTypes.Enum
version: 1.0

The ODBC driver SHALL correctly round-trip `Enum` values with both UTF-8
and ASCII keys.

#### RQ.SRS-100.ODBC.DataTypes.UUID
version: 1.0

The ODBC driver SHALL correctly round-trip `UUID` values.

#### RQ.SRS-100.ODBC.DataTypes.IPv4
version: 1.0

The ODBC driver SHALL correctly round-trip `IPv4` values.

#### RQ.SRS-100.ODBC.DataTypes.IPv6
version: 1.0

The ODBC driver SHALL correctly round-trip `IPv6` values.

#### RQ.SRS-100.ODBC.DataTypes.Nullable
version: 1.0

The ODBC driver SHALL correctly handle `Nullable` variants of all supported
data types, returning `None` for NULL values.

### Parameterized Queries

#### RQ.SRS-100.ODBC.ParameterizedQueries
version: 1.0

The ODBC driver SHALL support parameterized queries (`?` placeholders) for
all supported data types.

#### RQ.SRS-100.ODBC.ParameterizedQueries.Null
version: 1.0

The ODBC driver SHALL correctly handle `NULL` parameter values in
parameterized queries including with `isNull()` and `arrayReduce()` functions.

### Compatibility

#### RQ.SRS-100.ODBC.Compatibility.LTS
version: 1.0

The ODBC driver SHALL be verified to work against the current Altinity
ClickHouse LTS build.
""",
)
