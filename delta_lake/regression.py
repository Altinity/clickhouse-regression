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
from helpers.common import experimental_analyzer


@TestModule
@Name("delta lake")
@ArgumentParser(argparser_minio)
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
    """Delta Lake reads from MinIO and from the local Unity Catalog."""
    nodes = {
        "clickhouse": ("clickhouse1",),
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
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    with And("enable or disable experimental analyzer if needed"):
        experimental_analyzer(node=self.context.node, with_analyzer=with_analyzer)

    # use_unity_catalog_v2 is checked in the scenario that sets it.
    # deltaLake() and ENGINE = DeltaLake run on older servers.
    Feature(test=load("delta_lake.tests.sanity", "feature"))()
    Feature(test=load("delta_lake.tests.access", "feature"))()


if main():
    regression()
