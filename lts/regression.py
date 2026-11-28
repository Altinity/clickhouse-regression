#!/usr/bin/env python3
"""LTS regression: top-level orchestrator for all LTS sub-suites."""
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.argparser import argparser, CaptureClusterArgs
from helpers.cluster import PackageDownloader
from helpers.common import check_clickhouse_version
from lts.steps.docker import build_clickhouse_image, pull_image
from lts.steps.image import check_supported_image, clickhouse_version_from_image

# Server image that a binary or package given with --clickhouse is put into,
# unless --base-os names another one.
default_base_image = "altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest"


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
        "--grafana-version",
        type=str,
        dest="grafana_version",
        help="Grafana version, default: 13.2.2",
        default="13.2.2",
    )
    parser.add_argument(
        "--grafana-plugin-version",
        type=str,
        dest="grafana_plugin_version",
        help="Altinity clickhouse-grafana plugin version, default: 3.4.9",
        default="3.4.9",
    )
    parser.add_argument(
        "--clickhouse-driver-release",
        type=str,
        dest="clickhouse_driver_release",
        help="clickhouse-driver (Python) git tag to test, default: 0.2.10",
        default="0.2.10",
    )
    parser.add_argument(
        "--sqlalchemy-release",
        type=str,
        dest="sqlalchemy_release",
        help="clickhouse-sqlalchemy git tag to test, default: 0.3.2",
        default="0.3.2",
    )
    parser.add_argument(
        "--jdbc-release",
        type=str,
        dest="jdbc_release",
        help="clickhouse-java git tag whose clickhouse-jdbc module is tested, default: v0.9.9",
        default="v0.9.9",
    )
    parser.add_argument(
        "--jdbc-maven-args",
        type=str,
        dest="jdbc_maven_args",
        help=(
            "extra options for the clickhouse-jdbc 'mvn verify', for example "
            "'-Dtest=ClickHouseConnectionTest -Dit.test=ClickHouseConnectionTest'"
        ),
        default="",
    )
    parser.add_argument(
        "--dbeaver-version",
        type=str,
        dest="dbeaver_version",
        help=(
            "DBeaver CE release tag: its bundled ClickHouse JDBC driver is used "
            "by the DBeaver smoke checks, and the release itself is run by the "
            "DBeaver UI checks, default: 26.2.1"
        ),
        default="26.2.1",
    )


# ClickHouse#108038: INSERT of string datetime literals ignores
# use_client_time_zone when async_insert is on, the default since 26.3. These
# tests pass with async_insert=0. The xfails apply only from 26.3 and only to
# that failure, so any other failure at these paths is still reported.
issue_108038 = "https://github.com/ClickHouse/ClickHouse/issues/108038"
wrong_client_timezone = r"AssertionError: '\d+\\n\d+\\n' != '\d+\\n\d+\\n'"
naive_column_not_converted = r"AssertionError: np\.False_ is not true"

xfails = {
    "/lts/clickhouse-driver/tests/columns/test_datetime/*TimezonesTestCase/test_use_client_timezone": [
        (Fail, issue_108038, check_clickhouse_version(">=26.3"), wrong_client_timezone)
    ],
    "/lts/clickhouse-driver/tests/numpy/columns/test_datetime/*TimezonesTestCase/test_use_client_timezone": [
        (Fail, issue_108038, check_clickhouse_version(">=26.3"), wrong_client_timezone)
    ],
    "/lts/clickhouse-driver/tests/numpy/columns/test_datetime/*TimezonesTestCase/test_read_tz_naive_column_with_client_timezone": [
        (
            Fail,
            issue_108038,
            check_clickhouse_version(">=26.3"),
            naive_column_not_converted,
        )
    ],
}
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
    grafana_version="13.2.2",
    grafana_plugin_version="3.4.9",
    clickhouse_driver_release="0.2.10",
    sqlalchemy_release="0.3.2",
    jdbc_release="v0.9.9",
    jdbc_maven_args="",
    dbeaver_version="26.2.1",
    stress=None,
    with_analyzer=False,
):
    """Run LTS regression suites against a ClickHouse image, or against a
    ClickHouse binary or package put into a server image."""
    clickhouse_path = str(cluster_args.get("clickhouse_path") or "")
    if clickhouse_path.startswith("docker://"):
        self.context.clickhouse_image = clickhouse_path.removeprefix("docker://")
    else:
        base_image = str(
            cluster_args.get("base_os") or default_base_image
        ).removeprefix("docker://")
        unsupported = check_supported_image(base_image)
        if unsupported:
            fail(unsupported)
        with Given(
            "the ClickHouse binary is put into a server image",
            description=f"{clickhouse_path} into {base_image}",
        ):
            package = PackageDownloader(clickhouse_path)
            if not package.binary_path:
                fail(f"could not get a clickhouse binary from {clickhouse_path}")
            if not package.package_version:
                fail(f"could not read the version of {package.binary_path}")
            pull_image(image=base_image)
            self.context.clickhouse_image = (
                f"lts-clickhouse-server:0-{package.package_version}"
            )
            build_clickhouse_image(
                binary_path=os.path.abspath(package.binary_path),
                base_image=base_image,
                tag=self.context.clickhouse_image,
            )

    unsupported = check_supported_image(self.context.clickhouse_image)
    if unsupported:
        fail(unsupported)

    # The version gates version-specific xfails. Without --clickhouse-version it
    # comes from the image tag; a moving tag such as latest gives None, and then
    # version-specific xfails do not apply.
    self.context.clickhouse_version = (
        clickhouse_version
        or clickhouse_version_from_image(self.context.clickhouse_image)
    )
    note(f"ClickHouse version: {self.context.clickhouse_version}")

    Feature(test=load("lts.clickhouse_odbc.feature", "feature"))(
        release=odbc_release,
    )
    Feature(test=load("lts.superset.feature", "feature"))(
        superset_version=superset_version,
        clickhouse_driver=clickhouse_driver,
    )
    Feature(test=load("lts.grafana.feature", "feature"))(
        grafana_version=grafana_version,
        grafana_plugin_version=grafana_plugin_version,
    )
    Feature(test=load("lts.clickhouse_driver.feature", "feature"))(
        release=clickhouse_driver_release,
    )
    Feature(test=load("lts.clickhouse_sqlalchemy.feature", "feature"))(
        release=sqlalchemy_release,
    )
    Feature(test=load("lts.clickhouse_jdbc.feature", "feature"))(
        release=jdbc_release,
        maven_args=jdbc_maven_args,
    )
    Feature(test=load("lts.dbeaver.feature", "feature"))(
        dbeaver_version=dbeaver_version,
    )
    Feature(test=load("lts.dbeaver_ui.feature", "feature"))(
        dbeaver_version=dbeaver_version,
    )


if main():
    regression()
