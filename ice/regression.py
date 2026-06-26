#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from iceberg.requirements.requirements import *
from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import check_clickhouse_version, check_if_not_antalya_build
from parquet.tests.common import start_minio


xfails = {
    '/ice/feature/hybrid/hybrid_alias/query context/subquery alias/subquery select alias': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
    '/ice/feature/hybrid/hybrid_alias/query context/subquery nested/cte with alias': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
    '/ice/feature/hybrid/hybrid_alias/query context/subquery nested/cte with group by': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
    '/ice/feature/hybrid/hybrid_alias/query context/subquery nested/cte with order by': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
    '/ice/feature/hybrid/hybrid_alias/query context/subquery nested/cte with limit': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
   '/ice/feature/hybrid/hybrid_alias/query context/subquery nested/cte with order by and limit': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
    '/ice/feature/hybrid/hybrid_alias/query context/union alias/union all with alias': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
    '/ice/feature/hybrid/hybrid_alias/query context/set operations alias/intersect except with alias/*': [
        (Fail, 'https://github.com/Altinity/ClickHouse/issues/1424'),
    ],
}

ffails = {}


@TestModule
@Name("ice")
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
    """Run tests for Ice tool."""
    nodes = {
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
        ),
        "ice": ("ice",),
    }

    self.context.clickhouse_version = clickhouse_version

    # Set up parquet module context variables
    self.context.json_files_local = os.path.join(current_dir(), "data", "json_files")
    self.context.json_files = "/json_files"
    self.context.parquet_output_path = "/parquet-files"

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

    self.context.ice_node = self.context.cluster.node("ice")
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node2, self.context.node3]

    with Given("I set up MinIO S3 client"):
        self.context.storage = "minio"
        start_minio(
            access_key=minio_root_user,
            secret_key=minio_root_password,
            uri="localhost:9002",
        )

    Feature(
        test=load("ice.tests.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)


if main():
    regression()
