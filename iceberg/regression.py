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

from iceberg.requirements.requirements import *


xfails = {
    "/iceberg/iceberg integration/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/iceberg integration/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #100": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
}
ffails = {}


@TestModule
@Name("iceberg")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser_minio)
@Specifications(Apache_Iceberg_Table)
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
    """Run tests for Iceberg tables."""
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

    root_user = minio_args["minio_root_user"].value
    root_password = minio_args["minio_root_password"].value

    note(root_user)
    note(root_password)

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_USER": root_user,
                "MINIO_ROOT_PASSWORD": root_password,
            },
        )
        self.context.cluster = cluster

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")

    Feature(run=load("iceberg.tests.feature", "feature"))


if main():
    regression()
