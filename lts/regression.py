#!/usr/bin/env python3
"""LTS regression: top-level orchestrator for all LTS sub-suites."""
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.argparser import argparser, CaptureClusterArgs


def lts_argparser(parser):
    """Extended argument parser for the LTS meta-suite."""
    argparser(parser)
    parser.add_argument(
        "--odbc-release",
        type=str,
        dest="odbc_release",
        help="clickhouse-odbc driver version (git tag), default: v1.2.1.20220905",
        default="v1.2.1.20220905",
    )
    parser.add_argument(
        "--superset-version",
        type=str,
        dest="superset_version",
        help="Apache Superset version, default: 4.1.1",
        default="4.1.1",
    )
    parser.add_argument(
        "--clickhouse-driver",
        type=str,
        dest="clickhouse_driver",
        choices=["clickhouse-connect", "clickhouse-sqlalchemy"],
        help="ClickHouse Python driver for Superset, default: clickhouse-connect",
        default="clickhouse-connect",
    )
    parser.add_argument(
        "--suite",
        type=str,
        dest="suite",
        choices=["all", "clickhouse-odbc", "superset"],
        help="Which sub-suite to run, default: all",
        default="all",
    )


xfails = {}

ffails = {}


@TestModule
@Name("lts")
@ArgumentParser(lts_argparser)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    odbc_release="v1.2.1.20220905",
    superset_version="4.1.1",
    clickhouse_driver="clickhouse-connect",
    suite="all",
    stress=None,
    with_analyzer=False,
):
    """Run LTS regression suites against a ClickHouse image.

    Orchestrates clickhouse-odbc, superset (and future grafana/dbeaver) sub-suites.
    """
    if suite in ("all", "clickhouse-odbc"):
        from clickhouse_odbc.regression import regression as odbc_regression

        Module(run=odbc_regression)

    if suite in ("all", "superset"):
        from superset.regression import regression as superset_regression

        Module(run=superset_regression)


if main():
    regression()
