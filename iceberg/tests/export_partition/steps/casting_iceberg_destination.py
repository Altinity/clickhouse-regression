"""ClickHouse-native Iceberg destination helpers for the casting module.

Production datalake tables are created with ClickHouse DDL::

    CREATE DATABASE datalake ENGINE = DataLakeCatalog(...);
    CREATE TABLE datalake.`namespace.table` (...)
        ENGINE = IcebergS3('http://minio:9000/warehouse/data/<table>/', ...)
        PARTITION BY ...

The generic :mod:`iceberg.tests.export_partition.steps.iceberg_destination`
module still uses PyIceberg ``catalog.create_table`` for other export_partition
scenarios; only casting goes through this path.
"""

import textwrap

from testflows.core import *

from helpers.common import getuid

import iceberg.tests.steps.iceberg_engine as iceberg_engine

from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_ENDPOINT_HOST,
    DEFAULT_S3_WAREHOUSE_BUCKET,
    create_iceberg_s3_destination,
)


_CATALOG_CREATE_SETTINGS = [
    ("allow_experimental_database_iceberg", 1),
    ("write_full_path_in_iceberg_metadata", 1),
]

_TABLE_SETTINGS = [
    "s3_retry_attempts = 1",
    "iceberg_format_version = 2",
]


def _qualified_catalog_table(database_name, namespace, table_name):
    """Qualified name for ``ALTER``/``INSERT`` via ``node.query`` (bash-escaped)."""
    return f"{database_name}.\\`{namespace}.{table_name}\\`"


def _qualified_catalog_table_sql(database_name, namespace, table_name):
    """Qualified name with real SQL backticks for ``node.query(..., use_file=True)``."""
    return f"{database_name}.`{namespace}.{table_name}`"


def _metadata_prefix(location_prefix, table_name):
    """S3 object key prefix inside the warehouse bucket (no bucket segment)."""
    prefix = location_prefix
    bucket_segment = f"{DEFAULT_S3_WAREHOUSE_BUCKET}/"
    if prefix.startswith(bucket_segment):
        prefix = prefix[len(bucket_segment) :]
    return f"{prefix}/{table_name}"


@TestStep(Given)
def create_casting_catalog_iceberg_destination(
    self,
    columns,
    partition_by,
    minio_root_user,
    minio_root_password,
    table_name=None,
    namespace=None,
    database_name=None,
    storage_endpoint=None,
    location_prefix=None,
    node=None,
    cluster_name=None,
    cleanup=True,
    extra_table_settings=None,
    query_settings=None,
):
    """Create a catalog-backed casting destination via ClickHouse DDL."""
    if node is None:
        node = self.context.node

    if namespace is None:
        namespace = f"export_ns_{getuid()}"
    if table_name is None:
        table_name = f"iceberg_{getuid()}"
    if database_name is None:
        database_name = f"datalake_{getuid()}"
    if storage_endpoint is None:
        storage_endpoint = f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}"
    if location_prefix is None:
        location_prefix = f"{DEFAULT_S3_WAREHOUSE_BUCKET}/data"

    s3_url = f"{DEFAULT_S3_ENDPOINT_HOST}/{location_prefix}/{table_name}/"
    pclause = f"PARTITION BY {partition_by}" if partition_by else ""

    settings = list(_TABLE_SETTINGS)
    if extra_table_settings:
        settings.extend(extra_table_settings)
    settings_str = ", ".join(settings)

    create_settings = list(_CATALOG_CREATE_SETTINGS)
    if query_settings:
        create_settings.extend(query_settings)

    qualified = _qualified_catalog_table(database_name, namespace, table_name)
    qualified_sql = _qualified_catalog_table_sql(database_name, namespace, table_name)

    with Given(f"DataLakeCatalog database {database_name!r}"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint=storage_endpoint,
            node=node,
            cluster_name=cluster_name,
            namespaces=namespace,
        )

    with And(
        f"CH CREATE TABLE {namespace}.{table_name} with Iceberg-compatible schema"
    ):
        create_sql = textwrap.dedent(
            f"""
            CREATE TABLE {qualified_sql} ({columns})
            ENGINE = IcebergS3('{s3_url}', '{minio_root_user}', '{minio_root_password}')
            {pclause}
            SETTINGS {settings_str}
            """
        ).strip()
        node.query(create_sql, settings=create_settings, use_file=True)

    destination = {
        "destination_table": qualified,
        "namespace": namespace,
        "table_name": table_name,
        "database_name": database_name,
        "metadata_prefix": _metadata_prefix(location_prefix, table_name),
    }

    try:
        yield destination
    finally:
        if cleanup:
            with Finally(f"drop CH catalog destination {namespace}.{table_name}"):
                node.query(f"DROP TABLE IF EXISTS {qualified_sql} SYNC", use_file=True)
                node.query(f"DROP DATABASE IF EXISTS {database_name}")


@TestStep(Given)
def create_casting_iceberg_destination(
    self,
    columns,
    partition_by,
    minio_root_user,
    minio_root_password,
    table_name=None,
    namespace=None,
    database_name=None,
    storage_endpoint=None,
    location_prefix=None,
    node=None,
    cluster_name=None,
    cleanup=True,
    extra_table_settings=None,
    query_settings=None,
):
    """Create an Iceberg export destination using ClickHouse DDL.

    Dispatches like :func:`create_iceberg_destination`: return a nested
    ``@TestStep`` generator so ``with Given: dest = ...`` receives the
    yielded table name / destination dict — never ``yield from`` a resolved
    string (that would iterate characters and break ``INSERT INTO``).

    * ``no`` catalog — ``ENGINE = IcebergS3`` in the current database
      (:func:`create_iceberg_s3_destination`).
    * ``ice`` — ``DataLakeCatalog`` (ice-rest-catalog) plus
      ``CREATE TABLE datalake.\\`namespace.table\\``` with ``ENGINE = IcebergS3``.
    """
    catalog = self.context.catalog
    if catalog == "no":
        return create_iceberg_s3_destination(
            columns=columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            table_name=table_name,
            storage_endpoint=storage_endpoint,
            location_prefix=location_prefix,
            node=node,
            query_settings=query_settings,
            cleanup=cleanup,
        )

    if catalog != "ice":
        raise ValueError(
            f"Unsupported catalog mode for casting destinations: {catalog!r}"
        )

    return create_casting_catalog_iceberg_destination(
        columns=columns,
        partition_by=partition_by,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        table_name=table_name,
        namespace=namespace,
        database_name=database_name,
        storage_endpoint=storage_endpoint,
        location_prefix=location_prefix,
        node=node,
        cluster_name=cluster_name,
        cleanup=cleanup,
        extra_table_settings=extra_table_settings,
        query_settings=query_settings,
    )
