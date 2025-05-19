#!/usr/bin/env python3
import os
import sys

from testflows.core import *
from testflows.core.name import clean

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser as argparser_base, CaptureClusterArgs
from helpers.common import *

from ssl_server.requirements import SRS017_ClickHouse_SSL


def argparser(parser):
    """Default argument for regressions."""
    argparser_base(parser)

    parser.add_argument(
        "--force-fips",
        action="store_true",
        help="specify whether the provided ClickHouse binary is in FIPS mode even if fips is not in the version",
        default=False,
    )


xfails = {
    ":/ssl context/enable ssl with server key passphrase": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/35950")
    ],
    ":/ssl context/enable ssl no server key passphrase dynamically": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/35950")
    ],
    "ssl context/enable ssl with server key passphrase dynamically": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/35950")
    ],
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
    ":/fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES256-GCM-SHA384 :": [
        (Fail, "not supported by SSL library")
    ],
    ":/fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES128-GCM-SHA256 :": [
        (Fail, "not supported by SSL library")
    ],
    ":/check certificate/system certificates": [(Fail, "unstable test")],
    # zookeeper ssl
    ":/zookeepe:/fips/ECDHE-ECDSA-AES128-GCM-SHA256/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*(SSLV3_ALERT_HANDSHAKE_FAILURE|tls alert handshake failure).*",
        )
    ],
    ":/zookeepe:/fips/ECDHE-ECDSA-AES256-GCM-SHA384/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*(SSLV3_ALERT_HANDSHAKE_FAILURE|tls alert handshake failure).*",
        )
    ],
    ":/zookeepe:/fips/AES128-GCM-SHA256/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*(SSLV3_ALERT_HANDSHAKE_FAILURE|tls alert handshake failure).*",
        )
    ],
    ":/zookeepe:/fips/AES256-GCM-SHA384/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*(SSLV3_ALERT_HANDSHAKE_FAILURE|tls alert handshake failure).*",
        )
    ],
    ":/:/https server:checks/:onnection:should:": [
        (
            Error,
            "Takes too long on 24.3+ https://github.com/ClickHouse/ClickHouse/issues/62887",
            check_clickhouse_version(">=24.3"),
            r"ExpectTimeoutError.+https_server[\w]+connection.+node.query\($",
        )
    ],
    ":/fips/clickhouse server acting as a client/:/:onnection:should:": [
        (
            Error,
            "Takes too long on 24.3+ https://github.com/ClickHouse/ClickHouse/issues/62887",
            check_clickhouse_version(">=24.3"),
            r"ExpectTimeoutError.+test_https_connection_with.+node.query\($",
        )
    ],
    ":/fips/server/all protocols disabled/tcp connection/clickhouse-client/:/:": [
        (
            Fail,
            "needs workaround https://github.com/ClickHouse/ClickHouse/issues/65187",
            check_clickhouse_version(">=24.4"),
        )
    ],
    ":/ca chain/:/:/missing :": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/67984",
            check_clickhouse_version(">=24.4"),
        )
    ],
    ":/ca chain/:/:/:/missing :": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/67984",
            check_clickhouse_version(">=24.4"),
        )
    ],
}

xflags = {}

ffails = {
    ":/fips": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/79876",
        check_clickhouse_version(">=25.5"),
    ),
    "/ssl server/:/verification modes":(
        Skip,
        "native protocol supported on >=23.3",
        check_clickhouse_version("<23.3"),
    ),
    "/ssl server/:/ca chain": (
        Skip,
        "native protocol supported on >=23.3",
        check_clickhouse_version("<23.3"),
    ),
    ":/check certificate/system certificates": (
        Skip,
        "supported on >=22.8",
        check_clickhouse_version("<22.8"),
    ),
    ":/check certificate/show certificate": (
        Skip,
        "supported on >=22.8",
        check_clickhouse_version("<22.8"),
    ),
    ":/ssl context/enable ssl no server key passphrase dynamically": (
        Skip,
        "supported on >=22.3",
        check_clickhouse_version("<22.3"),
    ),
    ":/ssl context/enable ssl with server key passphrase dynamically": (
        Skip,
        "supported on >=22.3",
        check_clickhouse_version("<22.3"),
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
    # skip zookeeper fips on ARM
    ":/zookeeper fips": (Skip, "not supported on ARM", check_current_cpu("aarch64")),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("ssl server")
@Specifications(SRS017_ClickHouse_SSL)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    force_fips,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse security SSL server regression."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "zookeeper": ("zookeeper", "zookeeper-fips"),
    }

    if current_cpu() == "aarch64":
        nodes["zookeeper"] = (("zookeeper"),)

    if cluster_args.get("zookeeper_version"):
        skip("ssl_server suite does not support specifying zookeeper version")

    self.context.clickhouse_version = clickhouse_version
    self.context.fips_mode = False

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with Given("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with Given("I check if the binary is FIPS compatible"):
        if "fips" in current().context.clickhouse_version or force_fips:
            self.context.fips_mode = True

    with Feature("part 1"):
        Feature(run=load("ssl_server.tests.check_certificate", "feature"))
        Feature(run=load("ssl_server.tests.sanity", "feature"))
        Feature(run=load("ssl_server.tests.ssl_context", "feature"))
        Feature(run=load("ssl_server.tests.certificate_authentication", "feature"))
        Feature(run=load("ssl_server.tests.verification_mode", "feature"))
        Feature(run=load("ssl_server.tests.url_table_function", "feature"))
    
    with Feature("part 2"):
        Feature(run=load("ssl_server.tests.dictionary", "feature"))
        Feature(run=load("ssl_server.tests.fips", "feature"))
    
    with Feature("part 3"):
        Feature(run=load("ssl_server.tests.zookeeper.feature", "feature"))
        Feature(run=load("ssl_server.tests.zookeeper_fips.feature", "feature"))
        Feature(run=load("ssl_server.tests.ca_chain.feature", "feature"))


if main():
    regression()
