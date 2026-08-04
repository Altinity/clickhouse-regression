"""Shared helpers for Hybrid lifecycle tests (EXPORT → watermark, Distributed replace)."""

from testflows.core import *

from helpers.common import getuid
from helpers.tables import create_table

from iceberg.tests.export_partition.steps.common import (
    SOURCE_ENGINE_PLAIN,
    create_export_source_table,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import export_partition
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.verification import assert_destination_row_count

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    COLUMNS_SQL,
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    remote_tf,
    values_sql,
)

# Iceberg-compatible month transform (export_partition accepts this; toYYYYMM does not).
EXPORT_PARTITION_BY = "toMonthNumSinceEpoch(date_col)"

# IcebergS3 exposes Iceberg ``date`` as Date32 while Hybrid hot segments use Date.
# EXPORT requires an explicit opt-in for that cast (same gate as export_partition).
EXPORT_ALLOW_LOSSY_CAST = ("export_merge_tree_part_allow_lossy_cast", 1)

# Required for PyIceberg ``StaticTable`` under no_catalog: without absolute
# ``s3://`` URIs, bucket-relative manifest-list paths are opened as local
# files and fail with FileNotFoundError. Must be set on Iceberg CREATE and
# on EXPORT (same pattern as export_partition/storage_paths.py).
WRITE_FULL_ICEBERG_PATHS = ("write_full_path_in_iceberg_metadata", 1)

# Advanced watermark used after exporting an additional hot-side month.
ADVANCED_WATERMARK = "2025-03-01"
ADVANCED_LEFT = f"date_col >= '{ADVANCED_WATERMARK}'"
ADVANCED_RIGHT = f"date_col < '{ADVANCED_WATERMARK}'"


def hybrid_columns_sql():
    return ", ".join(c.full_definition() for c in COLUMNS)


@TestStep(Given)
def create_exportable_hot_segment(self, rows=ALL_ROWS, table_name=None):
    """Plain MergeTree with block number/offset columns for EXPORT PARTITION."""
    self.context.source_engine = SOURCE_ENGINE_PLAIN
    if table_name is None:
        table_name = f"hot_{getuid()}"

    create_export_source_table(
        table_name=table_name,
        columns=COLUMNS_SQL,
        partition_by=EXPORT_PARTITION_BY,
        order_by="(date_col, id)",
    )
    insert_data(table_name=table_name, values=values_sql(rows))
    return table_name


@TestStep(Given)
def create_iceberg_cold_destination(
    self, minio_root_user, minio_root_password, partition_by=EXPORT_PARTITION_BY
):
    """Empty Iceberg destination with export-compatible partition key."""
    return create_iceberg_destination(
        columns=COLUMNS_SQL,
        partition_by=partition_by,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        query_settings=[WRITE_FULL_ICEBERG_PATHS],
    )


def partition_ids_matching(node, table_name, where):
    """Distinct ``_partition_id`` values for rows matching ``where``."""
    output = node.query(
        f"SELECT DISTINCT _partition_id FROM {table_name} WHERE {where}"
    ).output
    return sorted({line.strip() for line in output.splitlines() if line.strip()})


@TestStep(When)
def export_partitions_matching(
    self,
    source_table,
    destination,
    where,
    minio_root_user,
    minio_root_password,
    node=None,
    expected_rows=None,
):
    """EXPORT each partition that contains rows matching ``where``."""
    if node is None:
        node = self.context.node

    partition_ids = partition_ids_matching(node, source_table, where)
    assert partition_ids, f"no partitions matched WHERE {where}"

    for partition_id in partition_ids:
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
            extra_settings=[EXPORT_ALLOW_LOSSY_CAST, WRITE_FULL_ICEBERG_PATHS],
        )

    if expected_rows is not None:
        assert_destination_row_count(
            destination=destination,
            expected=expected_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    return partition_ids


@TestStep(When)
def create_or_replace_hybrid(
    self,
    hybrid_name,
    left_tf,
    left_pred,
    right_tf,
    right_pred,
    node=None,
):
    """CREATE OR REPLACE Hybrid with new segment predicates."""
    if node is None:
        node = self.context.node
    node.query(
        f"CREATE OR REPLACE TABLE {hybrid_name} ({hybrid_columns_sql()}) "
        f"ENGINE = Hybrid({left_tf}, {left_pred}, {right_tf}, {right_pred})",
        settings=[("allow_experimental_hybrid_table", 1)],
    )


@TestStep(Given)
def create_hybrid_remote_iceberg(
    self,
    hot_table,
    iceberg_destination,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
    hybrid_name=None,
):
    """Hybrid: remote(hot MT) + Iceberg destination with static watermarks."""
    if hybrid_name is None:
        hybrid_name = f"hybrid_{getuid()}"

    left_tf = remote_tf(hot_table)
    right_tf = as_destination_name(iceberg_destination)

    create_table(
        name=hybrid_name,
        engine=f"Hybrid({left_tf}, {left_pred}, {right_tf}, {right_pred})",
        columns=COLUMNS,
        settings=[("allow_experimental_hybrid_table", 1)],
    )

    return {
        "hybrid": hybrid_name,
        "left": hot_table,
        "right": iceberg_destination,
        "left_tf": left_tf,
        "right_tf": right_tf,
        "left_from": hot_table,
        "right_from": right_tf,
        "left_pred": left_pred,
        "right_pred": right_pred,
    }


@TestStep(Given)
def create_local_and_distributed(
    self, rows=ALL_ROWS, cluster="replicated_cluster", local_name=None, distributed_name=None
):
    """MergeTree local table + Distributed head over ``cluster``.

    Defaults to ``replicated_cluster`` (one shard, multiple replicas) so a
    Hybrid head that replaces Distributed can still INSERT without a
    sharding key. Multi-shard ``all`` needs a sharding key that ``cluster()``
    does not carry into Hybrid.
    """
    if local_name is None:
        local_name = f"local_{getuid()}"
    if distributed_name is None:
        distributed_name = f"dist_{getuid()}"

    create_table(
        name=local_name,
        engine="MergeTree",
        columns=COLUMNS,
        order_by="(date_col, id)",
        partition_by="toYYYYMM(date_col)",
        cluster=cluster,
    )
    self.context.node.query(
        f"INSERT INTO {local_name} (id, value, date_col) VALUES {values_sql(rows)}"
    )

    self.context.node.query(
        f"CREATE TABLE {distributed_name} AS {local_name} "
        f"ENGINE = Distributed('{cluster}', currentDatabase(), {local_name}, id)"
    )

    return {"local": local_name, "distributed": distributed_name, "cluster": cluster}


def cluster_tf(table_name, cluster="replicated_cluster"):
    return f"cluster('{cluster}', currentDatabase(), '{table_name}')"
