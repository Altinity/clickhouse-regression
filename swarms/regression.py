#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import (
    check_if_not_antalya_build,
)

from swarms.requirements.requirements import *


xfails = {}
ffails = {
    "/swarms/feature": (
        Skip,
        "swarms work only with antalya",
        check_if_not_antalya_build,
    ),
}


@TestModule
@Name("swarms")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser_minio)
@Specifications(SRS_044_Swarm_Cluster_Query_Execution)
@CaptureClusterArgs
@CaptureMinioArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    minio_args=None,
):
    """Run tests for Swarm clusters."""
    nodes = {
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
        ),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    minio_root_user = minio_args["minio_root_user"].value
    minio_root_password = minio_args["minio_root_password"].value

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_USER": minio_root_user,
                "MINIO_ROOT_PASSWORD": minio_root_password,
            },
        )
        self.context.cluster = cluster

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.node,
        self.context.node2,
        self.context.node3,
    ]

    Feature(test=load("swarms.tests.feature", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


if main():
    regression()
