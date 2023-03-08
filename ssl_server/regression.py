#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as argparser_base
from helpers.common import check_clickhouse_version

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
}

xflags = {}

ffails = {
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
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}
    self.context.clickhouse_version = clickhouse_version
    self.context.fips_mode = False

    if stress is not None:
        self.context.stress = stress

    from platform import processor as current_cpu

    folder_name = os.path.basename(current_dir())
    if current_cpu() == "aarch64":
        env = f"{folder_name}_env_arm64"
    else:
        env = f"{folder_name}_env"

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
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


if main():
    regression()
