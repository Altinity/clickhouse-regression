#!/usr/bin/env python3
"""ClickHouse ODBC driver LTS regression suite."""
import os
import sys

from testflows.core import *

append_path(sys.path, "../..")

from helpers.argparser import argparser, CaptureClusterArgs


def odbc_argparser(parser):
    """Extended argument parser for the ODBC LTS suite."""
    argparser(parser)
    parser.add_argument(
        "--odbc-release",
        type=str,
        dest="odbc_release",
        help="clickhouse-odbc driver version (git tag), default: v1.2.1.20220905",
        default="v1.2.1.20220905",
    )


xfails = {}

ffails = {}


@TestModule
@Name("clickhouse-odbc")
@ArgumentParser(odbc_argparser)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    odbc_release="v1.2.1.20220905",
    stress=None,
    with_analyzer=False,
):
    """Run clickhouse-odbc tests against a ClickHouse LTS image."""
    from tests.build_and_run import feature as build_and_run_feature

    suite_dir = os.path.dirname(os.path.abspath(__file__))
    configs_dir = os.path.join(suite_dir, "configs")
    packages_dir = os.path.join(configs_dir, "PACKAGES")
    os.makedirs(packages_dir, exist_ok=True)

    clickhouse_path = cluster_args.get("clickhouse_path", "/usr/bin/clickhouse")
    if clickhouse_path and str(clickhouse_path).startswith("docker://"):
        clickhouse_image = str(clickhouse_path).removeprefix("docker://")
    else:
        clickhouse_image = (
            "altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest"
        )

    Feature(
        run=build_and_run_feature,
        kwargs=dict(
            configs_dir=configs_dir,
            packages_dir=packages_dir,
            clickhouse_image=clickhouse_image,
            odbc_release=odbc_release,
        ),
    )


if main():
    regression()
