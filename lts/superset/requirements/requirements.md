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
        * 3.3.2 [RQ.SRS-101.Superset.SQLLab.SchemaExplorer](#rqsrs-101supersetsqllabschemaexplorer)
    * 3.4 [Charts](#charts)
        * 3.4.1 [RQ.SRS-101.Superset.Charts.Create](#rqsrs-101supersetchartscreate)
        * 3.4.2 [RQ.SRS-101.Superset.Charts.DataTypes](#rqsrs-101supersetchartsdatatypes)
    * 3.5 [Dashboards](#dashboards)
        * 3.5.1 [RQ.SRS-101.Superset.Dashboards.Create](#rqsrs-101supersetdashboardscreate)
        * 3.5.2 [RQ.SRS-101.Superset.Dashboards.Refresh](#rqsrs-101supersetdashboardsrefresh)
    * 3.6 [Compatibility](#compatibility)
        * 3.6.1 [RQ.SRS-101.Superset.Compatibility.LTS](#rqsrs-101supersetcompatibilitylts)

## Introduction

This SRS covers the testing requirements for Apache Superset integration with
ClickHouse when running against Altinity ClickHouse LTS builds. The tests verify
connectivity (via both `clickhouse-connect` and `clickhouse-sqlalchemy` drivers),
SQL Lab functionality, chart/dashboard creation, and secure (TLS) connections.

## Terminology

- **Superset** — Apache Superset, an open-source data exploration and visualization
  platform.
- **clickhouse-connect** — ClickHouse Python driver using the HTTP interface.
- **clickhouse-sqlalchemy** — SQLAlchemy dialect for ClickHouse.
- **LTS** — Long-Term Support ClickHouse release.

## Requirements

### Environment Setup

#### RQ.SRS-101.Superset.Environment
version: 1.0

The test environment SHALL deploy Apache Superset and ClickHouse using
Docker Compose with all required services (superset, superset-init,
superset-worker, clickhouse).

#### RQ.SRS-101.Superset.Environment.ClickHouseConnect
version: 1.0

The environment SHALL support configuring Superset with the `clickhouse-connect`
Python driver as the database backend.

#### RQ.SRS-101.Superset.Environment.ClickHouseSQLAlchemy
version: 1.0

The environment SHALL support configuring Superset with the `clickhouse-sqlalchemy`
Python driver as the database backend.

### Database Connection

#### RQ.SRS-101.Superset.DatabaseConnection
version: 1.0

Superset SHALL successfully add a ClickHouse database connection and verify
it via the "Test Connection" button.

#### RQ.SRS-101.Superset.DatabaseConnection.HTTP
version: 1.0

Superset SHALL connect to ClickHouse over the HTTP interface (port 8123).

#### RQ.SRS-101.Superset.DatabaseConnection.HTTPS
version: 1.0

Superset SHALL connect to ClickHouse over HTTPS (port 8443) using the
provided TLS certificates.

#### RQ.SRS-101.Superset.DatabaseConnection.NativeProtocol
version: 1.0

Superset SHALL connect to ClickHouse over the native protocol (port 9000/9440)
when using a driver that supports it.

### SQL Lab

#### RQ.SRS-101.Superset.SQLLab.QueryExecution
version: 1.0

Superset SQL Lab SHALL execute queries against ClickHouse and display results
correctly.

#### RQ.SRS-101.Superset.SQLLab.SchemaExplorer
version: 1.0

Superset SQL Lab schema explorer SHALL list ClickHouse databases, tables,
and columns.

### Charts

#### RQ.SRS-101.Superset.Charts.Create
version: 1.0

Superset SHALL allow creating charts from ClickHouse datasets.

#### RQ.SRS-101.Superset.Charts.DataTypes
version: 1.0

Superset charts SHALL correctly render data from ClickHouse columns of
various types (numeric, string, date/time, etc.).

### Dashboards

#### RQ.SRS-101.Superset.Dashboards.Create
version: 1.0

Superset SHALL allow creating dashboards that include charts backed by
ClickHouse data.

#### RQ.SRS-101.Superset.Dashboards.Refresh
version: 1.0

Superset dashboards SHALL support manual and auto-refresh of ClickHouse-backed
charts.

### Compatibility

#### RQ.SRS-101.Superset.Compatibility.LTS
version: 1.0

All Superset features SHALL be verified to work against the current Altinity
ClickHouse LTS build.
