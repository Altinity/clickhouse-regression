#!/usr/bin/env python3
import os
import sys
import warnings
from testflows.core import *

append_path(sys.path, "..")

from iceberg.requirements.requirements import *
from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import (
    check_clickhouse_version,
    check_if_not_antalya_build,
    check_is_altinity_build,
    experimental_analyzer,
    check_if_antalya_build,
    check_with_any_sanitizer,
    check_if_antalya_post_26_3_10_20001,
)


xfails = {
    # Server crashes with "Metadata is not initialized" during schema evolution with sanitizers
    "/iceberg/iceberg engine/*/schema evolution/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/86024 - Iceberg metadata initialization bug with sanitizers",
            check_with_any_sanitizer,
        )
    ],
    # Logical error 'prewhere_info' on Iceberg row policies without PREWHERE (sanitizer-only chassert).
    # Fixed upstream in CH#100361; not backported to stable-26.3.
    "/iceberg/iceberg table engine/feature/row policies/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/100361 - not backported to stable-26.3",
            check_with_any_sanitizer,
        ),
        (
            Error,
            "https://github.com/ClickHouse/ClickHouse/pull/100361 - not backported to stable-26.3",
            check_with_any_sanitizer,
        ),
    ],
    "/iceberg/export partition/*/manifest integrity/value_counts across data files sum to source row count": [
        (
            Fail,
            "ClickHouse EXPORT PARTITION never populates `value_counts` in "
            "manifest entries (IcebergWrites.cpp / IcebergDataFileEntry.h "
            "only track column_sizes / null_value_counts / lower_bounds / "
            "upper_bounds). The Avro field is left null.",
        )
    ],
    "/iceberg/export partition/*/manifest integrity/data file paths live under the table prefix": [
        (
            Fail,
            "ClickHouse EXPORT PARTITION writes `path_in_storage` (bucket-"
            "relative path) to manifest entry `file_path`, ignoring "
            "`write_full_path_in_iceberg_metadata`. Per Iceberg spec the "
            "field is a 'Location URI with FS scheme' and should be "
            "`path_in_metadata` (e.g. s3://<bucket>/...). See "
            "MultipleFileWriter::startNewFile in MultipleFileWriter.cpp.",
        )
    ],
    "/iceberg/export partition/*/manifest integrity/external iceberg reader round-trips exported data": [
        (
            Fail,
            "PyIceberg cannot scan EXPORT PARTITION data files: Parquet "
            "written by ClickHouse lacks Iceberg field-ids and IcebergS3 "
            "tables have no schema.name-mapping.default, so strict readers "
            "raise ValueError during schema resolution. On builds that "
            "still write bucket-relative data_file.file_path, the scenario "
            "may instead fail with FileNotFoundError (local FileIO fallback).",
        )
    ],
    "/iceberg/export partition/*/catalogs/catalog: external reader round-trips exported data": [
        (
            Fail,
            "Same Parquet field-id / name-mapping gap as the no_catalog "
            "external-reader scenario: catalog-backed tables get a proper "
            "Iceberg schema from PyIceberg at CREATE time, but EXPORT "
            "PARTITION still writes Parquet without embedded field-ids. "
            "Older builds may instead hit FileNotFoundError when "
            "data_file.file_path lacks a URI scheme.",
        )
    ],
    "/iceberg/export partition/ice catalog/truncate/export after truncate repopulates destination": [
        (
            Fail,
            "ClickHouse bug: TRUNCATE and EXPORT disagree on the Iceberg "
            "metadata path format under Ice (ice-rest-catalog / Iceberg REST "
            "Catalog Spec). EXPORT commits manifest / manifest-list entries "
            "as bucket-relative paths "
            "(`/data/<table>/metadata/snap-...avro`). "
            "`IcebergMetadata::truncate` instead serialises those same "
            "entries as full `s3://bucket/...` URIs. When the next "
            "EXPORT runs after a TRUNCATE, IcebergWrites.cpp refuses "
            "to commit with `Paths in Iceberg must use a consistent "
            "format — either /your/path or s3://your/path. Use the "
            "write_full_path_in_iceberg_metadata setting to control "
            "this behavior`, and the background scheduler retries "
            "forever (task stuck in PENDING). Glue does not trip this "
            "because `apply_glue_metadata_path_workaround` already "
            "forces `write_full_path_in_iceberg_metadata=1` on both "
            "EXPORT and TRUNCATE there, so both sides write full "
            "URIs. Fix is upstream: either `IcebergMetadata::truncate` "
            "must honour the same path-format default as EXPORT, or "
            "the consistency check in IcebergWrites needs to look at "
            "new writes only instead of the inherited snapshot chain.",
        )
    ],
    "/iceberg/export partition/*/datatypes/*/accepted/accepted*UInt64*": [
        (
            Fail,
            "ClickHouse maps UInt64 to Iceberg long (signed). Values above "
            "INT64_MAX (e.g. 18446744073709551615) round-trip as -1 on "
            "IcebergS3 read-back; byte-compare fails until export/read uses "
            "a type that preserves the full unsigned range or rejects "
            "out-of-range values at export time.",
        )
    ],
    "/iceberg/export partition/*/settings/output_format_parquet_compression_method flows to data files": [
        (
            Fail,
            "ClickHouse EXPORT PARTITION does not propagate format-level "
            "settings from the `ALTER ... EXPORT PARTITION ... SETTINGS` "
            "clause to the background export task. "
            "ExportReplicatedMergeTreePartitionManifest has no generic "
            "settings blob and "
            "ExportPartitionUtils::getContextCopyWithTaskSettings uses a "
            "hardcoded allowlist that omits format settings, so "
            "`output_format_parquet_compression_method` is dropped before "
            "ExportPartTask::executeStep calls getFormatSettings and the "
            "Parquet writer always falls back to the server-profile "
            "default codec. Intentional for now per dev; remove this "
            "entry once the manifest carries format settings end-to-end.",
        )
    ],
    "/iceberg/icebergS3 table function/recreate table/scan and display data with pyiceberg, expect empty table": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table and insert new data multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table and insert new data multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/*": [
        (Fail, "Need to investigate", check_clickhouse_version("<=24")),
    ],
    "/iceberg/iceberg engine/* catalog/swarm/*": [
        (Fail, "Only works with antalya build", check_if_not_antalya_build),
    ],
    "/iceberg/iceberg cache/rest catalog/iceberg table engine/*": [
        (Fail, "Need to investigate"),
    ],
    "/iceberg/iceberg cache/glue catalog/iceberg table engine/*": [
        (Fail, "Need to investigate"),
    ],
    "/iceberg/iceberg engine/* catalog/predicate push down/issue with decimal column": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/80200")
    ],
    "/iceberg/iceberg engine/* catalog/predicate push down/issue with float column": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/80200")
    ],
    "/iceberg/iceberg engine/* catalog/feature/multiple tables": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/75187",
            check_clickhouse_version("<25.3"),
        ),
    ],
    "/iceberg/iceberg engine/glue catalog/schema evolution/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/81272",
            check_clickhouse_version("<25.7"),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/nested datatypes/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/81301",
            check_clickhouse_version("<25.5"),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/feature/sanity/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/82601",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_clickhouse_version("<25.4")(test),
        )
    ],
    "/iceberg/iceberg engine/: catalog/feature/alter:/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/86024",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg table engine/feature/alter:/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/86024",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg table engine/feature/alter comment columns": [
        (
            Fail,
            "Need to investigate",
            check_clickhouse_version(">=25.6"),
        )
    ],
    "/iceberg/iceberg engine/rest catalog/feature/show databases queries/*": [
        (
            Fail,
            "https://github.com/Altinity/clickhouse-regression/issues/86",
            lambda test: check_clickhouse_version(">=25.8")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg table engine/write min max pruning/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/91363",
            lambda test: (
                check_if_not_antalya_build(test)
                and check_clickhouse_version("<26.1")(test)
            )
            or (
                check_if_antalya_build(test)
                and check_clickhouse_version("<=25.8.9")(test)
            ),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/feature/show data lake catalogs in system tables/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/91363",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg cache/rest catalog/iceberg database engine/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg cache/rest catalog/icebergS3 table function/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg cache/glue catalog/iceberg database engine/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg cache/glue catalog/icebergS3 table function/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/check iceberg partition pruning with integer type": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/check partition pruning with complex where clause": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/partition pruning with date type": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/predicate push down/check input format parquet filter push down/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/97172",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/feature/select from system databases/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/103542",
            lambda test: check_clickhouse_version("<26.4")(test)
            and check_if_not_antalya_build(),
        )
    ],
}

ffails = {
    "/iceberg/iceberg engine/*": (
        Skip,
        "Iceberg tests unstable with sanitizer builds (server startup issues)",
        check_with_any_sanitizer,
    ),
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
    "/iceberg/iceberg cache/*": (
        Skip,
        "Metadata caching was introduced in antalya build from 24.12",
        check_if_not_antalya_build,
    ),
    "/iceberg/iceberg engine/: catalog/feature/show data lake catalogs in system tables": (
        Skip,
        "show_data_lake_catalogs_in_system_tables setting is not supported before 25.3 and on 25.4",
        lambda test: check_clickhouse_version("<25.3")(test)
        or check_clickhouse_version("==25.4")(test),
    ),
    "/iceberg/icebergS3 table function/: catalog/several iceberg tables in one dir": (
        Skip,
        "setting used for test introduced in 25.8",
        check_clickhouse_version("<25.8"),
    ),
    "/iceberg/iceberg engine/: catalog/iceberg iterator race condition/iceberg iterator race condition": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/92120",
        lambda test: check_clickhouse_version("<=25.8.12")(test)
        or check_if_not_antalya_build(test),
    ),
    "/iceberg/iceberg engine/: catalog/namespace filtering": (
        Skip,
        "namespace filtering is supported only in antalya build from >= 25.8",
        lambda test: check_clickhouse_version("<=25.8.15")(test)
        or check_if_not_antalya_build(test),
    ),
    "/iceberg/iceberg engine/: catalog/sort key timezone/*": (
        Skip,
        "iceberg_partition_timezone sort key support introduced in antalya-26.1",
        lambda test: check_if_not_antalya_build(test)
        or check_clickhouse_version("<26.1")(test),
    ),
    "/iceberg/iceberg engine/: catalog/dot separated column names/*": (
        Skip,
        "dot-separated column names broken before 25.7 and in 25.11-26.1 (https://github.com/ClickHouse/ClickHouse/issues/94196)",
        lambda test: check_clickhouse_version("<25.7")(test)
        or (
            check_clickhouse_version(">=25.11")(test)
            and check_clickhouse_version("<26.2")(test)
        ),
    ),
    "/iceberg/iceberg engine/: catalog/show_data_lake_catalogs hint/*": (
        Skip,
        "Pending https://github.com/ClickHouse/ClickHouse/pull/100452 — Antalya 26.1+ for now; revise when merged",
        lambda test: check_clickhouse_version("<26.1")(test)
        or check_if_not_antalya_build(test),
    ),
    "/iceberg/export partition": (
        Skip,
        "EXPORT PARTITION TO Apache Iceberg is only supported on Antalya builds > 26.1",
        lambda test: check_if_not_antalya_build(test)
        or check_clickhouse_version("<26.1")(test),
    ),
    "/iceberg/export partition/*/schema evolution/rename column between exports": (
        Skip,
        "RENAME COLUMN on IcebergS3 destination is NOT_IMPLEMENTED before 26.3",
        check_clickhouse_version("<26.3"),
    ),
    "/iceberg/export partition/*/casting": (
        Skip,
        "Altinity/ClickHouse#1779 export auto-cast requires antalya > 26.3.10.20001",
        lambda test: not check_if_antalya_post_26_3_10_20001(test),
    ),
    "/iceberg/export partition/*/catalogs/drop with purge allows recreating same table": (
        Skip,
        "Altinity/ClickHouse#1909 iceberg_delete_data_on_drop purge requires "
        "antalya > 26.3.10.20001",
        lambda test: not check_if_antalya_post_26_3_10_20001(test),
    ),
    "/iceberg/export partition/glue catalog/casting": (
        Skip,
        "PR 1779 casting uses CH-native Iceberg DDL destinations (no_catalog and "
        "ice-rest-catalog); Glue/LocalStack DataLakeCatalog is out of scope.",
        lambda test: True,
    ),
    # "/iceberg/iceberg engine/: catalog/feature/alter:/*": (
    #     Skip,
    #     "https://github.com/clickhouse/clickhouse/issues/86024",
    #     check_clickhouse_version(">=25.8"),
    # ),
    # "/iceberg/iceberg table engine/feature/alter:/*": (
    #     Skip,
    #     "https://github.com/clickhouse/clickhouse/issues/86024",
    #     check_clickhouse_version(">=25.8"),
    # ),
}


_RUNTIME_USERS_D_FILES = (
    "allow_experimental_insert_into_iceberg.xml",
)


def _sweep_runtime_users_d_overlays():
    """Remove leftover runtime-pushed users.d files from a previous run."""
    users_d_dir = os.path.join(current_dir(), "configs", "clickhouse", "users.d")
    for name in _RUNTIME_USERS_D_FILES:
        path = os.path.join(users_d_dir, name)
        if os.path.exists(path):
            os.remove(path)


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
    warnings.filterwarnings(
        "ignore", message="Delete operation did not match any records"
    )

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

    with Given("sweep stale runtime users.d overlays"):
        _sweep_runtime_users_d_overlays()

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
    self.context.nodes = [self.context.node, self.context.node2, self.context.node3]

    with And("enable or disable experimental analyzer if needed"):
        for node in self.context.nodes:
            experimental_analyzer(node=node, with_analyzer=with_analyzer)

    Feature(
        test=load("iceberg.tests.iceberg_engine.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.iceberg_table_engine.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.s3_table_function.s3_table_function", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.icebergS3_table_function.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.cache.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.export_partition.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    # Feature(
    #     test=load("iceberg.tests.catalogs.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)


if main():
    regression()
