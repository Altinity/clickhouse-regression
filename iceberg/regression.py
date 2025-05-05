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
from helpers.common import check_clickhouse_version, check_if_antalya_build

from iceberg.requirements.requirements import *


xfails = {
    "/iceberg/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/recreate table and insert new data multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/iceberg engine/feature/recreate table/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/iceberg engine/feature/recreate table multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/*": [
        (Fail, "Need to investigate", check_clickhouse_version("<=24")),
    ],
    "/iceberg/iceberg engine/swarm/*": [
        (Fail, "Only works with antalya build", check_if_antalya_build),
    ],
    "/iceberg/iceberg cache/iceberg table engine/*": [
        (Fail, "Need to investigate"),
    ],
}
ffails = {
    "/iceberg/iceberg engine": (
        Skip,
        "Iceberg engine was introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/iceberg/iceberg cache": (
        Skip,
        "Iceberg engine was introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/iceberg/icebergS3 table function": (
        Skip,
        "Iceberg engine was introduced in 23.2",
        check_clickhouse_version("<=23.2"),
    ),
    "/iceberg/s3 table function": (
        Skip,
        "Support for codec 'zstd' not built",
        check_clickhouse_version("<23.8"),
    ),
    "/iceberg/iceberg table engine": (
        Skip,
        "Iceberg table engine was introduced in 23.2",
        check_clickhouse_version("<24.2"),
    ),
}


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

    # Feature(
    #     test=load("iceberg.tests.iceberg_engine.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    #
    # Feature(
    #     test=load("iceberg.tests.iceberg_table_engine.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    #
    # Feature(
    #     test=load("iceberg.tests.s3_table_function.s3_table_function", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    # Feature(
    #     test=load(
    #         "iceberg.tests.icebergS3_table_function.icebergS3_table_function",
    #         "icebergS3_table_function",
    #     ),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.cache.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    # Feature(
    #     test=load("iceberg.tests.catalogs.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)


if main():
    regression()
