#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import CaptureClusterArgs
from helpers.common import check_clickhouse_version
from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.performance_files.argparsers import argparser
from clickhouse_keeper.tests.performance_files.reports import *


append_path(sys.path, "..")

xfails = {}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("performance")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_package_list,
    repeats,
    inserts,
    results_file_name,
    one_node,
    three_node,
    clickhouse_version,
    ssl=None,
    stress=None,
    with_analyzer=False,
):
    """Check ClickHouse performance when using ClickHouse Keeper."""
    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3", "zookeeper"),
        "bash_tools": ("bash_tools"),
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
            "clickhouse4",
            "clickhouse5",
            "clickhouse6",
            "clickhouse7",
            "clickhouse8",
            "clickhouse9",
            "clickhouse10",
            "clickhouse11",
            "clickhouse12",
            "clickhouse13",
        ),
    }

    if len(clickhouse_package_list) == 0:
        clickhouse_package_list.append(
            os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH", "/usr/bin/clickhouse")
        )

    # if clickhouse_path is not the default value, tell user to use --clickhouse-package-list
    assert (
        cluster_args["clickhouse_path"] == "/usr/bin/clickhouse"
    ), "specify version with --clickhouse-package-list"
    del cluster_args["clickhouse_path"]

    self.context.configurations_insert_time_values = {}

    self.context.repeats = repeats
    self.context.inserts = inserts
    self.context.results_file_name = results_file_name
    self.context.one_node = one_node
    self.context.three_node = three_node

    for clickhouse_path in clickhouse_package_list:
        self.context.clickhouse_version = clickhouse_version

        if stress is not None:
            self.context.stress = stress

        from platform import processor as current_cpu

        folder_name = os.path.basename(current_dir())
        if current_cpu() == "aarch64":
            env = f"{folder_name}_env_arm64"
        else:
            env = f"{folder_name}_performance_env"

        for ssl in ["false", "true"]:
            self.context.ssl = ssl

            if ssl == "true":
                self.context.tcp_port_secure = True
                self.context.secure = 1
                self.context.port = "9281"
            else:
                self.context.tcp_port_secure = False
                self.context.secure = 0
                self.context.port = "2181"

            test_features = ["keeper", "zookeeper"]

            for test_feature in test_features:
                with Cluster(
                    clickhouse_path=clickhouse_path,
                    nodes=nodes,
                    **cluster_args,
                ) as cluster:
                    self.context.cluster = cluster

                    if check_clickhouse_version("<21.4")(self):
                        skip(reason="only supported on ClickHouse version >= 21.4")

                    if ssl == "true":
                        create_3_3_cluster_config_ssl()
                    else:
                        create_3_3_cluster_config()

                    Feature(
                        run=load(
                            f"clickhouse_keeper.tests.performance_files.{test_feature}",
                            "feature",
                        )
                    )

    comparison_setups = ["all setups", "ssl", "Zookeeper", "altinitystable"]

    create_csv_file(
        test_results_file_name=self.context.results_file_name,
        repeats=self.context.repeats,
        inserts=self.context.inserts,
        configurations_insert_time_values=self.context.configurations_insert_time_values,
        setups=comparison_setups,
    )

    create_markdown_and_html_reports(
        test_results_file_name=self.context.results_file_name,
        configurations_insert_time_values=self.context.configurations_insert_time_values,
    )


if main():
    regression()
