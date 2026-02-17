#!/usr/bin/env python3
"""Apache Superset ClickHouse integration LTS regression suite."""
import os
import sys

from testflows.core import *

append_path(sys.path, "../..")

from helpers.argparser import argparser, CaptureClusterArgs


def superset_argparser(parser):
    """Extended argument parser for the Superset LTS suite."""
    argparser(parser)
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
@Name("superset")
@ArgumentParser(superset_argparser)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    superset_version="4.1.1",
    clickhouse_driver="clickhouse-connect",
    stress=None,
    with_analyzer=False,
):
    """Run Superset integration tests against a ClickHouse LTS image."""
    from tests.connection import feature as connection_feature
    from tests.sql_lab import feature as sql_lab_feature
    from tests.charts import feature as charts_feature
    from tests.dashboards import feature as dashboards_feature

    suite_dir = os.path.dirname(os.path.abspath(__file__))
    configs_dir = os.path.join(suite_dir, "configs")

    clickhouse_path = cluster_args.get("clickhouse_path", "/usr/bin/clickhouse")
    if clickhouse_path and str(clickhouse_path).startswith("docker://"):
        clickhouse_image = str(clickhouse_path).removeprefix("docker://")
    else:
        clickhouse_image = (
            "altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest"
        )

    note(f"ClickHouse image: {clickhouse_image}")
    note(f"Superset version: {superset_version}")
    note(f"ClickHouse driver: {clickhouse_driver}")

    Feature(run=connection_feature)
    Feature(run=sql_lab_feature)
    Feature(run=charts_feature)
    Feature(run=dashboards_feature)


if main():
    regression()
