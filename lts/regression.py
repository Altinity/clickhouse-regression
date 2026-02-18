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
    stress=None,
    with_analyzer=False,
):
    """Run LTS regression suites against a ClickHouse image."""
    clickhouse_path = cluster_args.get("clickhouse_path", "/usr/bin/clickhouse")
    if clickhouse_path and str(clickhouse_path).startswith("docker://"):
        self.context.clickhouse_image = str(clickhouse_path).removeprefix("docker://")
    else:
        self.context.clickhouse_image = (
            "altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest"
        )

    self.context.clickhouse_version = clickhouse_version

    Feature(test=load("lts.clickhouse_odbc.feature", "feature"))(
        odbc_release=odbc_release,
    )
    Feature(test=load("lts.superset.feature", "feature"))(
        superset_version=superset_version,
        clickhouse_driver=clickhouse_driver,
    )


if main():
    regression()
