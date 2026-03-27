#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from ssl_keeper.helpers.cluster import Cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer


xfails = {
    "ssl keeper/FIPS SSL/openssl check/port:%%%%/connection using FIPS compatible cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    "/ssl keeper/FIPS SSL/openssl check/port:%%%%/connection using FIPS compatible cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
    # "/ssl keeper/fips 140-3/openssl check/port﹕9444/connection using non-FIPS compatible TLSv1․2 cipher : should be rejected": [
    #     (Fail, "Keeper Raft port (NuRaft) does not enforce cipherList restrictions from openSSL config")
    # ],
    "/ssl keeper/fips 140-3/tcp connection check/port﹕9440/just disabling TLSv1․1 suite connection should work": [
        (Fail, "BoringSSL/AWS-LC requires contiguous TLS version range; disabling only TLSv1.1 creates a gap")
    ],
    "/ssl keeper/fips 140-3/tcp connection check/port﹕9440/just disabling TLSv1․2 suite connection should work": [
        (Fail, "BoringSSL/AWS-LC requires contiguous TLS version range; disabling only TLSv1.2 creates a gap")
    ],
}
xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("ssl keeper")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse ssl ClickHouse Keeper regression."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "bash_tools": ("bash_tools"),
    }

    self.context.clickhouse_version = clickhouse_version

    self.context.transaction_atomic_insert = True

    if stress is not None:
        self.context.stress = stress

    with Cluster(
        local=cluster_args.get("local", False),
        clickhouse_binary_path=cluster_args.get("clickhouse_path"),
        collect_service_logs=cluster_args.get("collect_service_logs", False),
        thread_fuzzer=cluster_args.get("thread_fuzzer", False),
        docker_compose_project_dir=os.path.join(
            current_dir(), "ssl_keeper_env"
        ),
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster

        if check_clickhouse_version("<22.4")(self):
            skip(reason="only supported on ClickHouse version >= 22.4")

        with Given("I enable or disable experimental analyzer if needed"):
            for node in nodes["clickhouse"]:
                experimental_analyzer(
                    node=cluster.node(node), with_analyzer=with_analyzer
                )

        Feature(run=load("ssl_keeper.tests.sanity", "feature"))
        # Feature(run=load("ssl_keeper.tests.fips_ssl", "feature"))
        Feature(run=load("ssl_keeper.tests.fips_ssl_140_3", "feature"))


if main():
    regression()
