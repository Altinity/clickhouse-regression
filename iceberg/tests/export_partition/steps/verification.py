"""Verification helpers for EXPORT PARTITION tests.

These wrap the existing iceberg suite readers so assertions look the same no
matter which catalog mode the scenario is parametrised with.
"""

from testflows.core import *
from testflows.asserts import error

import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.icebergS3 as icebergS3_steps

from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    as_pyiceberg_handle,
    DEFAULT_S3_ENDPOINT_HOST,
    DEFAULT_S3_WAREHOUSE_BUCKET,
)


@TestStep(When)
def select_from_destination(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    columns="*",
    where_clause=None,
    order_by=None,
    node=None,
    format="TabSeparated",
):
    """Read from the Iceberg destination, independent of the catalog mode.

    * ``no_catalog`` -> ``SELECT ... FROM <ch_table>`` against the
      ``IcebergS3`` table that owns the destination.
    * ``rest`` / ``glue`` -> ``SELECT ... FROM <db>.`<namespace.table>``` using
      the DataLakeCatalog database.

    Returns the raw query result object.
    """
    if node is None:
        node = self.context.node

    handle = as_pyiceberg_handle(destination)

    if handle is None:
        name = as_destination_name(destination)
        query = f"SELECT {columns} FROM {name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if format:
            query += f" FORMAT {format}"
        return node.query(query)

    return iceberg_engine.read_data_from_clickhouse_iceberg_table(
        database_name=handle["database_name"],
        namespace=handle["namespace"],
        table_name=handle["table_name"],
        columns=columns,
        where_clause=where_clause,
        order_by=order_by,
        format=format,
        node=node,
    )


@TestStep(When)
def count_rows_in_destination(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    where_clause=None,
    node=None,
):
    """Return the row count at the destination as an integer."""
    result = select_from_destination(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="count()",
        where_clause=where_clause,
        order_by=None,
        node=node,
        format="TabSeparated",
    )
    try:
        return int(result.output.strip())
    except (ValueError, AttributeError):
        return 0


@TestStep(When)
def wait_for_destination_row_count(
    self,
    destination,
    expected,
    minio_root_user,
    minio_root_password,
    where_clause=None,
    timeout=120,
    delay=2,
    node=None,
):
    """Poll until the destination has ``expected`` rows matching ``where_clause``.

    Used after ``EXPORT PART``, which does not populate
    ``system.replicated_partition_exports``.
    """
    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            actual = count_rows_in_destination(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                where_clause=where_clause,
                node=node,
            )
            assert actual == expected, error(
                f"destination has {actual} rows, expected {expected} "
                f"(still waiting for EXPORT PART)"
            )


@TestStep(Then)
def assert_destination_row_count(
    self,
    destination,
    expected,
    minio_root_user,
    minio_root_password,
    where_clause=None,
    node=None,
):
    """Assert that the destination row count matches ``expected``."""
    actual = count_rows_in_destination(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        where_clause=where_clause,
        node=node,
    )
    assert actual == expected, error(
        f"Expected {expected} rows at destination "
        f"{as_destination_name(destination)}"
        + (f" WHERE {where_clause}" if where_clause else "")
        + f", got {actual}"
    )


@TestStep(Then)
def assert_source_and_destination_match(
    self,
    source_table,
    destination,
    minio_root_user,
    minio_root_password,
    partition_where=None,
    order_by="tuple()",
    columns="*",
    node=None,
):
    """Assert that the source and destination return byte-identical rows.

    ``partition_where`` is applied to both the source and the destination so
    that partial exports can be compared without pulling the whole table
    across.
    """
    if node is None:
        node = self.context.node

    source_query = f"SELECT {columns} FROM {source_table}"
    if partition_where:
        source_query += f" WHERE {partition_where}"
    source_query += f" ORDER BY {order_by} FORMAT TabSeparated"
    source_output = node.query(source_query).output

    destination_output = select_from_destination(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns=columns,
        where_clause=partition_where,
        order_by=order_by,
        node=node,
        format="TabSeparated",
    ).output

    assert source_output == destination_output, error(
        f"Source and destination rows differ.\n"
        f"Source:\n{source_output}\n"
        f"Destination:\n{destination_output}"
    )


@TestStep(Then)
def read_via_icebergS3_table_function(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    columns="*",
    where_clause=None,
    order_by=None,
    node=None,
):
    """Independent validation path: use the ``icebergS3`` table function to
    read the destination directly from MinIO, bypassing any catalog cache.

    For catalog-backed destinations this uses the warehouse path that MinIO
    manages; for no-catalog destinations it reuses the same URL the IcebergS3
    engine was created with.
    """
    if node is None:
        node = self.context.node

    handle = as_pyiceberg_handle(destination)
    if handle is None:
        # no-catalog: the CH table name matches the last path segment the
        # IcebergS3 storage was created with.
        name = as_destination_name(destination)
        storage_endpoint = (
            f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}/data/{name}/"
        )
    else:
        # catalog-backed: locate the table through the warehouse prefix that
        # PyIceberg uses when creating the table (``s3://warehouse/data``).
        storage_endpoint = (
            f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}/data/"
        )

    return icebergS3_steps.read_data_with_icebergS3_table_function(
        storage_endpoint=storage_endpoint,
        s3_access_key_id=minio_root_user,
        s3_secret_access_key=minio_root_password,
        columns=columns,
        where_clause=where_clause,
        order_by=order_by,
        node=node,
    )
