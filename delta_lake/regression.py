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
from helpers.common import check_clickhouse_version, experimental_analyzer
from helpers.feature_support import setting_supported

xfails = {
    "/delta lake/feature/delta schema/nulls": [
        (
            Fail,
            "deltaLake() cannot read a column added in a later commit: "
            "Reading from files with different schema is not possible",
            check_clickhouse_version("<25.8"),
        )
    ],
    "/delta lake/feature/delta schema/nested": [
        (
            Fail,
            "deltaLake() fails on a struct column with LOGICAL_ERROR: "
            "Not found column in schema: person.id",
            lambda test: check_clickhouse_version(">=25.8")(test)
            and check_clickhouse_version("<26.3")(test),
        )
    ],
    "/delta lake/feature/delta column mapping/mode id by field id": [
        (
            Fail,
            "columnMapping.mode id resolves columns by physical name, not by the "
            "Parquet field id: every column is NULL when the names differ",
        )
    ],
    "/delta lake/feature/delta protocol/non parquet provider": [
        (
            Fail,
            "format.provider is not checked: a csv provider is read as Parquet",
        )
    ],
    "/delta lake/feature/delta create table/create in unity": [
        (
            Fail,
            "ClickHouse sends type_json as a bare type string (\"long\"), and OSS "
            "Unity Catalog v0.7.0 rejects it with INVALID_ARGUMENT",
        )
    ],
}

ffails = {
    "/delta lake/feature/delta schema/varchar": (
        Skip,
        "OSS Unity Catalog v0.7.0 rejects varchar(n) in a column type_json "
        "(Unsupported Delta primitive type), so the catalog cannot return it "
        "the way Databricks Unity does.",
    ),
    "/delta lake/feature/delta writes/accurate write cast": (
        Skip,
        "delta_lake_accurate_write_cast exists from 26.9",
        check_clickhouse_version("<26.9"),
    ),
    "/delta lake/feature/delta create table": (
        Skip,
        "Creating a new Delta table needs allow_delta_lake_create_table. Without "
        "it, CREATE TABLE with a column list succeeds and writes no _delta_log",
        lambda test: not setting_supported("allow_delta_lake_create_table")(test),
    ),
}


@TestModule
@Name("delta lake")
@FFails(ffails)
@XFails(xfails)
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
    """Delta Lake reads from RustFS and from the local Unity Catalog."""
    nodes = {
        "clickhouse": ("clickhouse1",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    rustfs_access_key = minio_args["minio_root_user"].value
    rustfs_secret_key = minio_args["minio_root_password"].value

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            environ={
                "RUSTFS_ACCESS_KEY": rustfs_access_key,
                "RUSTFS_SECRET_KEY": rustfs_secret_key,
            },
        )
        self.context.cluster = cluster

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.rustfs_access_key = rustfs_access_key
    self.context.rustfs_secret_key = rustfs_secret_key

    with And("enable or disable experimental analyzer if needed"):
        experimental_analyzer(node=self.context.node, with_analyzer=with_analyzer)

    # use_unity_catalog_v2 is checked in the scenario that sets it.
    # deltaLake() and ENGINE = DeltaLake run on older servers.
    Feature(test=load("delta_lake.tests.feature", "feature"))()


if main():
    regression()
