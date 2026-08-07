"""Shared helpers for Hybrid storage-matrix tests (catalogs, icebergCluster, S3)."""

from testflows.core import *

from helpers.common import getuid
from helpers.tables import create_table

from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_ENDPOINT_HOST,
    as_destination_name,
    create_iceberg_destination,
    create_iceberg_s3_destination,
)
from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    COLUMNS_SQL,
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    cluster_all_tf,
    create_mergetree_segment,
    settings_clause,
    values_sql,
)

# Dedicated MinIO prefix so Hybrid storage tests do not clash with other suites.
HYBRID_P2_LOCATION_PREFIX = "warehouse/data_hybrid_p2"

JOIN_LOCAL = {"object_storage_cluster_join_mode": "'local'"}


def settings_clause_join_local(*rows, extra=None):
    """SETTINGS clause with object_storage_cluster_join_mode=local for icebergCluster paths."""
    merged_extra = dict(JOIN_LOCAL)
    if extra:
        merged_extra.update(extra)
    return settings_clause(*rows, extra=merged_extra)


def iceberg_s3_url(table_name, location_prefix=HYBRID_P2_LOCATION_PREFIX):
    return f"{DEFAULT_S3_ENDPOINT_HOST}/{location_prefix}/{table_name}/"


def iceberg_cluster_tf(url, minio_root_user, minio_root_password, cluster="replicated_cluster"):
    return (
        f"icebergCluster('{cluster}', '{url}', "
        f"'{minio_root_user}', '{minio_root_password}')"
    )


def s3_parquet_tf(url, minio_root_user, minio_root_password):
    return f"s3('{url}', '{minio_root_user}', '{minio_root_password}', 'Parquet')"


def s3_cluster_parquet_tf(
    url, minio_root_user, minio_root_password, cluster="replicated_cluster"
):
    return (
        f"s3Cluster('{cluster}', '{url}', "
        f"'{minio_root_user}', '{minio_root_password}', 'Parquet')"
    )


@TestStep(Given)
def create_cluster_mt_iceberg_catalog_hybrid(
    self,
    minio_root_user,
    minio_root_password,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
):
    """cluster('all', MT) + catalog-aware Iceberg destination as cold segment."""
    with By("create MergeTree on all shards via ON CLUSTER"):
        left = create_mergetree_segment(
            cluster="all",
            seed_all_nodes=False,
            rows=ALL_ROWS,
        )

    with By("create Iceberg destination for current catalog mode and seed rows"):
        destination = create_iceberg_destination(
            columns=COLUMNS_SQL,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(
            destination=destination,
            values=values_sql(ALL_ROWS),
        )

    right = as_destination_name(destination)
    hybrid = f"hybrid_{getuid()}"
    left_tf = cluster_all_tf(left)

    with By("create Hybrid cluster(MT) + Iceberg destination"):
        create_table(
            name=hybrid,
            engine=f"Hybrid({left_tf}, {left_pred}, {right}, {right_pred})",
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    return {
        "hybrid": hybrid,
        "left": left,
        "right": right,
        "destination": destination,
        "left_from": left_tf,
        "right_from": right,
        "left_pred": left_pred,
        "right_pred": right_pred,
    }


@TestStep(Given)
def create_cluster_mt_iceberg_cluster_hybrid(
    self,
    minio_root_user,
    minio_root_password,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
):
    """cluster('all', MT) + icebergCluster cold segment over a seeded IcebergS3 table."""
    with By("create MergeTree on all shards via ON CLUSTER"):
        left = create_mergetree_segment(
            cluster="all",
            seed_all_nodes=False,
            rows=ALL_ROWS,
        )

    iceberg_name = f"iceberg_{getuid()}"
    url = iceberg_s3_url(iceberg_name)

    with By("create IcebergS3 under hybrid_p2 prefix and seed rows"):
        iceberg = create_iceberg_s3_destination(
            columns=COLUMNS_SQL,
            partition_by="",
            table_name=iceberg_name,
            location_prefix=HYBRID_P2_LOCATION_PREFIX,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(
            destination=iceberg,
            values=values_sql(ALL_ROWS),
        )

    hybrid = f"hybrid_{getuid()}"
    left_tf = cluster_all_tf(left)
    right_tf = iceberg_cluster_tf(url, minio_root_user, minio_root_password)

    with By("create Hybrid cluster(MT) + icebergCluster"):
        create_table(
            name=hybrid,
            engine=f"Hybrid({left_tf}, {left_pred}, {right_tf}, {right_pred})",
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    return {
        "hybrid": hybrid,
        "left": left,
        "right": iceberg,
        "right_tf": right_tf,
        "url": url,
        "left_from": left_tf,
        # Reference reads the IcebergS3 table (same data icebergCluster scans).
        "right_from": iceberg,
        "left_pred": left_pred,
        "right_pred": right_pred,
    }


@TestStep(Given)
def write_s3_parquet_rows(
    self,
    minio_root_user,
    minio_root_password,
    rows=ALL_ROWS,
    path_suffix=None,
    node=None,
):
    """Write controlled rows as a single Parquet object under hybrid_p2 prefix."""
    if node is None:
        node = self.context.node
    if path_suffix is None:
        path_suffix = f"parquet_{getuid()}.parquet"

    url = f"{DEFAULT_S3_ENDPOINT_HOST}/{HYBRID_P2_LOCATION_PREFIX}/{path_suffix}"
    # Structure must match Hybrid / reference column list.
    node.query(
        f"INSERT INTO FUNCTION s3("
        f"'{url}', '{minio_root_user}', '{minio_root_password}', 'Parquet', "
        f"'{COLUMNS_SQL}'"
        f") VALUES {values_sql(rows)}",
        exitcode=0,
    )
    return url
