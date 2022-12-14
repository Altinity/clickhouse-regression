#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser
from helpers.common import check_clickhouse_version

from ssl_server.requirements import SRS017_ClickHouse_Security_SSL_Server

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
    "fips/server/:/:/:cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    "fips/server/:/:/:cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    "fips/server/:/:/TLSv1.3 suite connection should be rejected": [
        (Fail, "needs to be reviewed")
    ],
    "fips/server/tcp connection/clickhouse-client/just disabling TLSv1.1 suite connection should work": [
        (Fail, "needs to be reviewed")
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
@Specifications(SRS017_ClickHouse_Security_SSL_Server)
def regression(self, local, clickhouse_binary_path, clickhouse_version, stress=None):
    """ClickHouse security SSL server regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

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
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster

        Feature(run=load("ssl_server.tests.sanity", "feature"))
        Feature(run=load("ssl_server.tests.ssl_context", "feature"))
        Feature(run=load("ssl_server.tests.fips", "feature"))


if main():
    regression()
