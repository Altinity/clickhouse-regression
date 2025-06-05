#!/usr/bin/env python3
import os
import sys

from testflows.core import *
from testflows.core.name import clean

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser as base_argparser, CaptureClusterArgs
from helpers.common import *
from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *


def argparser(parser):
    """Custom argparser that adds --ssl option."""
    base_argparser(parser)

    parser.add_argument(
        "--ssl",
        action="store_true",
        help="enable ssl connection for clickhouse keepers and clickhouse",
        default=False,
    )


xfails = {
    # fips
    ":/:/:/:/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:/:/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:/:/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/fips/server/tcp connection/:/:/just disabling TLSv1_1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    ":/fips/server/:/tcp connection/:/:/just disabling TLSv1_1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    ":/fips/:/:/:/just disabling TLSv1_1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    ":/:/:/just disabling TLSv1_1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    ":/fips/clickhouse client/:/:/: should be rejected": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/45445")
    ],
    ":/ports ssl fips/:/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/ports ssl fips/:/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/ports ssl fips/openssl all ports/port﹕9444": [
        (
            Fail,
            "Doesn't work as expected on 24.3 altinitystable and 24.9 upstream",
            check_clickhouse_version(">=24.3"),
            r".+Connection reset by peer in connection.+",
        ),
        (
            Error,
            "Doesn't work as expected, timeout",
            check_clickhouse_version(">=24.6"),
            r".+ExpectTimeoutError.+",
        ),
    ],
    ":/ports ssl fips/:/:/just disabling "
    + clean("TLSv1_1 suite connection should work"): [(Fail, "needs to be reviewed")],
    "/clickhouse keeper/:/cli converter/output dir invalid": [
        (Fail, "Improper behaviour <23.8", check_clickhouse_version("<23.8"))
    ],
    "/clickhouse keeper/:/cli converter/snapshot invalid dir": [
        (Fail, "Improper behaviour <23.8", check_clickhouse_version("<23.8"))
    ],
    ":/fips/clickhouse server acting as a client/:/:onnection:should:": [
        (
            Error,
            "Takes too long on 24.3+ https://github.com/ClickHouse/ClickHouse/issues/62887",
            check_clickhouse_version(">=24.3"),
            r"ExpectTimeoutError.+test_https_connection_with.+node.query\($",
        )
    ],
    ":/fips/server/all protocols disabled/:/:/:/:": [
        (
            Fail,
            "needs workaround https://github.com/ClickHouse/ClickHouse/issues/65187",
            check_clickhouse_version(">=24.4"),
        )
    ],
    ":/ports ssl fips/check clickhouse connection to keeper/:": [
        (Fail, "Doesn't work on 22.3", check_clickhouse_version("<22.8"))
    ],
    ":/four letter word commands/wchs command": [
        (
            Fail,
            "not stable, needs investigation",
        ),
    ]
}


xflags = {}

ffails = {
    ":/ports ssl fips": (
    Skip,
    "https://github.com/ClickHouse/ClickHouse/issues/79876",
    check_clickhouse_version(">=25.5"),
    ),
    ":/fips": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/79876",
        check_clickhouse_version(">=25.5"),
    ),
    "/clickhouse keeper/:/migration/migrate from zookeeper to standalone keeper": (
        XFail,
        "test doesn't work from 23.3",
        check_clickhouse_version(">=23.3"),
    ),
    "/clickhouse keeper/:/keeper cluster tests/zookeepers 3": (XFail, "Not stable"),
    "/clickhouse keeper/:/keeper cluster tests/standalone keepers 3": (
        XFail,
        "Not stable",
    ),
    "/clickhouse keeper/:/four letter word commands/wchc command": (
        XFail,
        "test doesn't work from 22.8",
        check_clickhouse_version(">=22.8"),
    ),
    "/clickhouse keeper/:/coordination settings": (
        XFail,
        "test doesn't work from 23.3",
        check_clickhouse_version(">=23.3"),
    ),
    "/clickhouse keeper/:/coordination settings/server id": (
        XFail,
        "doesn't function beyond version 22.3",
        check_clickhouse_version(">=22.3"),
    ),
    "/clickhouse keeper/:/coordination settings/startup timeout": (
        XFail,
        "doesn't function beyond version 22.3",
        check_clickhouse_version(">=22.3"),
    ),
    "/clickhouse keeper/:/*/tcp connection all ports": (XFail, "duplication test"),
    "/clickhouse keeper/:/servers start up": (XFail, "unstable fix check"),
    "/clickhouse keeper/:/servers start up/different shared start up": (
        XFail,
        "test doesn't work from 23.3",
        check_clickhouse_version(">=23.3"),
    ),
    ":/fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES256-GCM-SHA384:": (
        XFail,
        "not supported by SSL library",
    ),
    ":/fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES128-GCM-SHA256:": (
        XFail,
        "not supported by SSL library",
    ),
    ":/fips/:/:/connection using FIPS compatible cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": (
        XFail,
        "not supported by SSL library",
    ),
    ":/fips/:/:/connection using FIPS compatible cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": (
        XFail,
        "not supported by SSL library",
    ),
    ":/fips/:/:/connection using non-FIPS compatible cipher TLS_*": (
        XFail,
        "not supported by TLSv1.2",
    ),
    "/clickhouse keeper/:/alter column distributed/alter comment column": (
        XFail,
        "Fails on 23.10",
        check_clickhouse_version("=23.10"),
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("clickhouse keeper")
@Requirements(RQ_SRS_024_ClickHouse_Keeper("1.0"))
@Specifications(SRS024_ClickHouse_Keeper)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    ssl=None,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse regression when using clickhouse-keeper."""
    nodes = {
        "zookeeper": (
            "zookeeper1",
            "zookeeper2",
            "zookeeper3",
            "zookeeper",
            # "zookeeper-fips",
        ),
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

    self.context.clickhouse_version = clickhouse_version
    self.context.ssl = ssl

    if stress is not None:
        self.context.stress = stress

    if ssl:
        self.context.tcp_port_secure = True
        self.context.secure = 1
        self.context.port = "9281"
        self.context.ssl = "true"
    else:
        self.context.tcp_port_secure = False
        self.context.secure = 0
        self.context.ssl = "false"
        self.context.port = "2181"

    if not current_cpu() == "aarch64":
        nodes["zookeeper"] += ("zookeeper-fips",)

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    if check_clickhouse_version("<21.4")(self):
        skip(reason="only supported on ClickHouse version >= 21.4")

    with Given("I check if the binary is FIPS compatible"):
        if "fips" in current().context.clickhouse_version:
            self.context.fips_mode = True
        else:
            self.context.fips_mode = False

    if ssl:
        create_3_3_cluster_config_ssl()
        with Feature("part 1"):
            Feature(run=load("clickhouse_keeper.tests.sanity", "feature"))
            Feature(run=load("clickhouse_keeper.tests.cli", "feature"))
            Feature(run=load("clickhouse_keeper.tests.synchronization", "feature"))
            Feature(
                run=load("clickhouse_keeper.tests.non_distributed_ddl_queries", "feature")
            )
        with Feature("part 2"):
            Feature(run=load("clickhouse_keeper.tests.keeper_cluster_tests", "feature"))
            Feature(run=load("clickhouse_keeper.tests.alter_column_distributed", "feature"))
            Feature(
                run=load("clickhouse_keeper.tests.alter_partition_distributed", "feature")
            )
            Feature(run=load("clickhouse_keeper.tests.servers_start_up", "feature"))

            Feature(run=load("clickhouse_keeper.tests.ports_ssl_fips", "feature"))
            Feature(run=load("clickhouse_keeper.tests.fips", "feature"))

    else:
        create_3_3_cluster_config()
        with Feature("part 1"):
            Feature(run=load("clickhouse_keeper.tests.sanity", "feature"))
            Feature(run=load("clickhouse_keeper.tests.migration", "feature"))
            Feature(run=load("clickhouse_keeper.tests.synchronization", "feature"))
            Feature(run=load("clickhouse_keeper.tests.cli", "feature"))
            Feature(run=load("clickhouse_keeper.tests.cli_converter", "feature"))
            Feature(
                run=load("clickhouse_keeper.tests.non_distributed_ddl_queries", "feature")
            )
        with Feature("part 2"):
            Feature(run=load("clickhouse_keeper.tests.keeper_cluster_tests", "feature"))
            Feature(run=load("clickhouse_keeper.tests.alter_column_distributed", "feature"))
            Feature(
                run=load("clickhouse_keeper.tests.alter_partition_distributed", "feature")
            )
            Feature(
                run=load("clickhouse_keeper.tests.four_letter_word_commands", "feature")
            )
            Feature(run=load("clickhouse_keeper.tests.servers_start_up", "feature"))
            Feature(run=load("clickhouse_keeper.tests.coordination_settings", "feature"))


if main():
    regression()
