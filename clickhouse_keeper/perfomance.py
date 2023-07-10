#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl import *
import csv



def argparser(parser):
    """Custom argperser that add --ssl option."""
    base_argparser(parser)

    parser.add_argument(
        "--ssl",
        action="store_true",
        help="enable ssl connection for clickhouse keepers and clickhouse",
        default=False,
    )

    parser.add_argument(
        "--clickhouse-binary-list",
        action="append",
        dest="clickhouse_binary_list",
        help="path to ClickHouse binary, default: /usr/bin/clickhouse",
        metavar="path",
        default=[],
    )

    parser.add_argument(
        "--number-of-repeats",
        type=int,
        dest="number_of_repeats",
        help="number of insert time check for 'mean value calculation",
        default=2,
    )

    parser.add_argument(
        "--number-of-inserts",
        type=int,
        dest="number_of_inserts",
        help="number of inserts into table on one repeat",
        default=100,
    )


xfails = {}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("benchmark clickhouse keeper")
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_binary_list,
    number_of_repeats,
    number_of_inserts,
    clickhouse_version,
    collect_service_logs,
    ssl=None,
    stress=None,
):
    """ClickHouse benchmark when using clickhouse-keeper."""
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

    if len(clickhouse_binary_list) == 0:
        clickhouse_binary_list.append(os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH", "/usr/bin/clickhouse"))

    self.context.uid = getuid()

    self.context.dict = {}

    self.context.number_of_repeats = number_of_repeats
    self.context.number_of_inserts = number_of_inserts

    for clickhouse_binary_path in clickhouse_binary_list:
        self.context.clickhouse_version = clickhouse_version

        if stress is not None:
            self.context.stress = stress

        from platform import processor as current_cpu

        folder_name = os.path.basename(current_dir())
        if current_cpu() == "aarch64":
            env = f"{folder_name}_env_arm64"
        else:
            env = f"{folder_name}_env"

        for ssl in ["true", "false"]:

            self.context.ssl = ssl

            if ssl == "true":
                self.context.tcp_port_secure = True
                self.context.secure = 1
                self.context.port = "9281"
            else:
                self.context.tcp_port_secure = False
                self.context.secure = 0
                self.context.port = "2181"

            with Cluster(
                local,
                clickhouse_binary_path=clickhouse_binary_path,
                collect_service_logs=collect_service_logs,
                nodes=nodes,
                docker_compose_project_dir=os.path.join(current_dir(), env),
            ) as cluster:
                self.context.cluster = cluster

                if check_clickhouse_version("<21.4")(self):
                    skip(reason="only supported on ClickHouse version >= 21.4")

                if ssl == "true":
                    create_3_3_cluster_config_ssl()
                else:
                    create_3_3_cluster_config()

                Feature(
                    run=load("clickhouse_keeper.tests.bench", "feature")
                )

    file_name = (
        f"bench_{self.context.uid}.csv"
    )

    with open(file_name, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)

        buffer_list = ['config name:']
        for name1 in list(self.context.dict):
            buffer_list.append(name1)
        writer.writerow(buffer_list)

        for name1 in list(self.context.dict):
            buffer_list = [name1]
            for name2 in list(self.context.dict):
                buffer_list.append(float(self.context.dict[name2]/float(self.context.dict[name1])))
            writer.writerow(buffer_list)


if main():
    regression()
