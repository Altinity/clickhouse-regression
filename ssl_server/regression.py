#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as argparser_base
from helpers.common import check_clickhouse_version, check_current_cpu, current_cpu

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
    "ssl context/enable ssl with server key passphrase": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/35950")
    ],
    "ssl context/enable ssl no server key passphrase dynamically": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/35950")
    ],
    "ssl context/enable ssl with server key passphrase dynamically": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/35950")
    ],
    # fips
    ":/:/:/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:/:/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    ":/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    "fips/server/tcp connection/:/:/just disabling TLSv1.1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    "fips/server/:/tcp connection/:/:/just disabling TLSv1.1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    "fips/:/:/:/just disabling TLSv1.1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    ":/:/just disabling TLSv1.1 suite connection should work": [
        (Fail, "needs to be reviewed")
    ],
    "fips/clickhouse client/:/:/: should be rejected": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/45445")
    ],
    "fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES256-GCM-SHA384 :": [
        (Fail, "not supported by SSL library")
    ],
    "fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES128-GCM-SHA256 :": [
        (Fail, "not supported by SSL library")
    ],
    "check certificate/system certificates": [(Fail, "unstable test")],
    # zookeeper ssl
    "zookeepe:/fips/ECDHE-ECDSA-AES128-GCM-SHA256/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*SSLV3_ALERT_HANDSHAKE_FAILURE.*",
        )
    ],
    "zookeepe:/fips/ECDHE-ECDSA-AES256-GCM-SHA384/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*SSLV3_ALERT_HANDSHAKE_FAILURE.*",
        )
    ],
    "zookeepe:/fips/AES128-GCM-SHA256/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*SSLV3_ALERT_HANDSHAKE_FAILURE.*",
        )
    ],
    "zookeepe:/fips/AES256-GCM-SHA384/:": [
        (
            Fail,
            "SSLV3_ALERT_HANDSHAKE_FAILURE",
            None,
            r".*SSLV3_ALERT_HANDSHAKE_FAILURE.*",
        )
    ],
}

xflags = {}

ffails = {
    "check certificate/system certificates": (
        Skip,
        "supported on >=22.8",
        check_clickhouse_version("<22.8"),
    ),
    "check certificate/show certificate": (
        Skip,
        "supported on >=22.8",
        check_clickhouse_version("<22.8"),
    ),
    "ssl context/enable ssl no server key passphrase dynamically": (
        Skip,
        "supported on >=22.3",
        check_clickhouse_version("<22.3"),
    ),
    "ssl context/enable ssl with server key passphrase dynamically": (
        Skip,
        "supported on >=22.3",
        check_clickhouse_version("<22.3"),
    ),
    "fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES256-GCM-SHA384:": (
        XFail,
        "not supported by SSL library",
    ),
    "fips/:/:/connection with at least one FIPS compatible cipher should work, ciphers: ECDHE-ECDSA-AES128-GCM-SHA256:": (
        XFail,
        "not supported by SSL library",
    ),
    "fips/:/:/connection using FIPS compatible cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": (
        XFail,
        "not supported by SSL library",
    ),
    "fips/:/:/connection using FIPS compatible cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": (
        XFail,
        "not supported by SSL library",
    ),
    "fips/:/:/connection using non-FIPS compatible cipher TLS_*": (
        XFail,
        "not supported by TLSv1.2",
    ),
    # skip zookeeper fips on ARM
    "zookeeper fips": (Skip, "not supported on ARM", check_current_cpu("aarch64")),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("ssl server")
@Specifications(SRS017_ClickHouse_SSL)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    force_fips,
    stress=None,
):
    """ClickHouse security SSL server regression."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "zookeeper": ("zookeeper", "zookeeper-fips"),
    }

    if current_cpu() == "aarch64":
        nodes["zookeeper"] = (("zookeeper"),)

    self.context.clickhouse_version = clickhouse_version
    self.context.fips_mode = False

    if stress is not None:
        self.context.stress = stress

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
        use_zookeeper_nodes=True,
    ) as cluster:
        self.context.cluster = cluster

        with Given("I check if the binary is FIPS compatible"):
            if "fips" in current().context.clickhouse_version or force_fips:
                self.context.fips_mode = True

        Feature(run=load("ssl_server.tests.check_certificate", "feature"))
        Feature(run=load("ssl_server.tests.sanity", "feature"))
        Feature(run=load("ssl_server.tests.ssl_context", "feature"))
        Feature(run=load("ssl_server.tests.certificate_authentication", "feature"))
        Feature(run=load("ssl_server.tests.verification_mode", "feature"))
        Feature(run=load("ssl_server.tests.url_table_function", "feature"))
        Feature(run=load("ssl_server.tests.dictionary", "feature"))
        Feature(run=load("ssl_server.tests.fips", "feature"))
        Feature(run=load("ssl_server.tests.zookeeper.feature", "feature"))
        Feature(run=load("ssl_server.tests.zookeeper_fips.feature", "feature"))
        Feature(run=load("ssl_server.tests.ca_chain.feature", "feature"))


if main():
    regression()
