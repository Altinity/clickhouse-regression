# SRS-102 Altinity Grafana ClickHouse Plugin LTS Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [Requirements](#requirements)
    * 3.1 [Environment Setup](#environment-setup)
        * 3.1.1 [RQ.SRS-102.Grafana.Environment](#rqsrs-102grafanaenvironment)
        * 3.1.2 [RQ.SRS-102.Grafana.Environment.SeleniumGrid](#rqsrs-102grafanaenvironmentseleniumgrid)
    * 3.2 [Login](#login)
        * 3.2.1 [RQ.SRS-102.Grafana.Login](#rqsrs-102grafanalogin)
    * 3.3 [Datasource Query](#datasource-query)
        * 3.3.1 [RQ.SRS-102.Grafana.DatasourceQuery](#rqsrs-102grafanadatasourcequery)
    * 3.4 [Panel Visualization](#panel-visualization)
        * 3.4.1 [RQ.SRS-102.Grafana.PanelVisualization](#rqsrs-102grafanapanelvisualization)
        * 3.4.2 [RQ.SRS-102.Grafana.Macros.TimeSeries](#rqsrs-102grafanamacrostimeseries)
    * 3.5 [Compatibility](#compatibility)
        * 3.5.1 [RQ.SRS-102.Grafana.Compatibility.LTS](#rqsrs-102grafanacompatibilitylts)

## Introduction

This SRS covers the testing requirements for the Altinity ClickHouse Grafana
datasource plugin when running against Altinity ClickHouse LTS builds. The tests
verify that Grafana starts with the plugin configured against a specific
ClickHouse version, that users can log in, run queries in Explore and see a
dashboard panel drawn from ClickHouse data, using Selenium-based browser
automation. Query results are checked for exact values, not just for the
presence of page content.

## Terminology

- **Grafana** — An open-source analytics and monitoring platform.
- **clickhouse-grafana** — Altinity's Grafana datasource plugin for ClickHouse
  (vertamedia-clickhouse-datasource).
- **Selenium Grid** — A distributed testing infrastructure that allows running
  browser-based tests across multiple machines.
- **LTS** — Long-Term Support ClickHouse release.

## Requirements

### Environment Setup

#### RQ.SRS-102.Grafana.Environment
version: 1.0

The test environment SHALL deploy Grafana with the Altinity ClickHouse
datasource plugin and a ClickHouse server using Docker Compose, along with
a Selenium Grid node for browser-based testing.

#### RQ.SRS-102.Grafana.Environment.SeleniumGrid
version: 1.0

The test environment SHALL include a Selenium Grid hub with Chrome browser
support for automated UI testing of the Grafana web interface.

### Login

#### RQ.SRS-102.Grafana.Login
version: 1.0

Grafana SHALL allow logging in with default admin credentials (admin/admin)
and SHALL display the home page after successful authentication.

### Datasource Query

#### RQ.SRS-102.Grafana.DatasourceQuery
version: 1.0

Grafana SHALL be able to execute SQL queries against ClickHouse through the
Altinity clickhouse-grafana datasource plugin and SHALL display the exact
query results in the Explore view with Table format, for example the server
version for `SELECT version()` and `100` for the row count of the seeded
`default.test_grafana` table.

### Panel Visualization

#### RQ.SRS-102.Grafana.PanelVisualization
version: 1.0

Grafana SHALL render a time-series dashboard panel from data queried from
ClickHouse through the Altinity clickhouse-grafana datasource plugin. The
panel SHALL show no error and SHALL draw the queried series, and the panel's
query SHALL return the seeded data.

#### RQ.SRS-102.Grafana.Macros.TimeSeries
version: 1.0

The plugin SHALL expand the `$timeSeriesMs` and `$timeFilterMs` macros for a
`DateTime` timestamp column, so that a panel query using them returns the
seeded rows grouped into time buckets within the dashboard time range.

### Compatibility

#### RQ.SRS-102.Grafana.Compatibility.LTS
version: 1.0

All Grafana plugin features SHALL be verified to work against the current
Altinity ClickHouse LTS build.
