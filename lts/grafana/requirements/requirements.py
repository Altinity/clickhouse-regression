# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_102_Grafana_Environment = Requirement(
    name="RQ.SRS-102.Grafana.Environment",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The test environment SHALL deploy Grafana with the Altinity ClickHouse\n"
        "datasource plugin and a ClickHouse server using Docker Compose, along with\n"
        "a Selenium Grid node for browser-based testing.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_102_Grafana_Environment_SeleniumGrid = Requirement(
    name="RQ.SRS-102.Grafana.Environment.SeleniumGrid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The test environment SHALL include a Selenium Grid hub with Chrome browser\n"
        "support for automated UI testing of the Grafana web interface.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.2",
)

RQ_SRS_102_Grafana_Login = Requirement(
    name="RQ.SRS-102.Grafana.Login",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Grafana SHALL allow logging in with default admin credentials (admin/admin)\n"
        "and SHALL display the home page after successful authentication.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

RQ_SRS_102_Grafana_Compatibility_LTS = Requirement(
    name="RQ.SRS-102.Grafana.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "All Grafana plugin features SHALL be verified to work against the current\n"
        "Altinity ClickHouse LTS build.\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

SRS_102_Altinity_Grafana_ClickHouse_Plugin_LTS_Testing = Specification(
    name="SRS-102 Altinity Grafana ClickHouse Plugin LTS Testing",
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
        Heading(name="RQ.SRS-102.Grafana.Environment", level=3, num="3.1.1"),
        Heading(
            name="RQ.SRS-102.Grafana.Environment.SeleniumGrid",
            level=3,
            num="3.1.2",
        ),
        Heading(name="Login", level=2, num="3.2"),
        Heading(name="RQ.SRS-102.Grafana.Login", level=3, num="3.2.1"),
        Heading(name="Compatibility", level=2, num="3.3"),
        Heading(name="RQ.SRS-102.Grafana.Compatibility.LTS", level=3, num="3.3.1"),
    ),
    requirements=(
        RQ_SRS_102_Grafana_Environment,
        RQ_SRS_102_Grafana_Environment_SeleniumGrid,
        RQ_SRS_102_Grafana_Login,
        RQ_SRS_102_Grafana_Compatibility_LTS,
    ),
    content=r"""
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
    * 3.3 [Compatibility](#compatibility)
        * 3.3.1 [RQ.SRS-102.Grafana.Compatibility.LTS](#rqsrs-102grafanacompatibilitylts)

## Introduction

This SRS covers the testing requirements for the Altinity ClickHouse Grafana
datasource plugin when running against Altinity ClickHouse LTS builds. The tests
verify that Grafana starts successfully with the plugin configured against
a specific ClickHouse version, and that basic UI operations (login) work
correctly via Selenium-based browser automation.

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

### Compatibility

#### RQ.SRS-102.Grafana.Compatibility.LTS
version: 1.0

All Grafana plugin features SHALL be verified to work against the current
Altinity ClickHouse LTS build.
""",
)
