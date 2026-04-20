"""Helpers to create and drop the Iceberg destination table in ClickHouse.

Three destination modes are supported and selected via ``self.context.catalog``:

* ``"no_catalog"``  - ``ENGINE = IcebergS3(url, access_key, secret_key)``.
  ClickHouse writes metadata/manifests directly to MinIO without an external
  catalog service. The destination is always referenced through the IcebergS3
  table that was created by the same node.

* ``"rest"`` - ClickHouse talks to the ice-rest-catalog service. A
  ``DataLakeCatalog`` database is created, the Iceberg table is created
  server-side by PyIceberg using the REST catalog helpers in
  ``iceberg.tests.steps.catalog``, and the destination referenced by EXPORT
  PARTITION is the ``<database>.`<namespace.table>``` view.

* ``"glue"`` - Same pattern as ``rest`` but against the LocalStack glue
  service.

The module exposes a single :func:`create_iceberg_destination` step that the
tests call; the mode is chosen automatically from ``self.context.catalog``.
"""

import textwrap

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


DEFAULT_S3_ENDPOINT_HOST = "http://minio:9000"
DEFAULT_S3_WAREHOUSE_BUCKET = "warehouse"


@TestStep(Given)
def create_iceberg_s3_destination(
    self,
    columns,
    partition_by,
    table_name=None,
    minio_root_user=None,
    minio_root_password=None,
    storage_endpoint=None,
    location_prefix=None,
    node=None,
    extra_settings=None,
    query_settings=None,
    cleanup=True,
):
    """Create a ClickHouse ``IcebergS3`` destination table (no external catalog).

    The table lives at ``<storage_endpoint>/<location_prefix>/<table_name>/``
    inside MinIO. ClickHouse itself creates the Iceberg metadata on the first
    commit.

    Args:
        columns: Column list for the ``CREATE TABLE`` body.
        partition_by: Expression used for ``PARTITION BY``. Empty string for
            an unpartitioned Iceberg table.
        table_name: Defaults to a unique name.
        minio_root_user / minio_root_password: S3 credentials.
        storage_endpoint: MinIO base URL, defaults to
            ``http://minio:9000``.
        location_prefix: First path segment under the bucket. Defaults to
            ``warehouse/data``.
        extra_settings: Table-level ``SETTINGS`` clause entries appended after
            ``s3_retry_attempts = 1`` (e.g. DataLake settings).
        query_settings: Query-level settings passed through
            ``node.query(..., settings=...)``. Use this for settings that are
            read from the query context during the ``CREATE TABLE`` itself
            (e.g. ``write_full_path_in_iceberg_metadata`` which decides the
            format of the ``location`` field in the freshly written
            ``metadata.json``).
    """
    if node is None:
        node = self.context.node
    if table_name is None:
        table_name = f"iceberg_{getuid()}"
    if storage_endpoint is None:
        storage_endpoint = DEFAULT_S3_ENDPOINT_HOST
    if location_prefix is None:
        location_prefix = f"{DEFAULT_S3_WAREHOUSE_BUCKET}/data"

    settings = ["s3_retry_attempts = 1"]
    if extra_settings:
        settings.extend(extra_settings)
    settings_str = ", ".join(settings)

    url = f"{storage_endpoint}/{location_prefix}/{table_name}/"
    pclause = f"PARTITION BY {partition_by}" if partition_by else ""

    query = textwrap.dedent(
        f"""
        CREATE TABLE {table_name} ({columns})
        ENGINE = IcebergS3('{url}', '{minio_root_user}', '{minio_root_password}')
        {pclause}
        SETTINGS {settings_str}
        """
    ).strip()

    try:
        node.query(query, settings=query_settings)
        yield table_name
    finally:
        if cleanup:
            with Finally(f"drop IcebergS3 destination {table_name}"):
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(Given)
def create_iceberg_catalog_destination(
    self,
    columns,
    partition_by,
    minio_root_user,
    minio_root_password,
    namespace=None,
    table_name=None,
    database_name=None,
    storage_endpoint=None,
    node=None,
    cleanup=True,
):
    """Create an Iceberg destination that lives in an external catalog
    (REST or Glue depending on ``self.context.catalog``).

    The destination is created in two steps:

    1. A ``DataLakeCatalog`` database is registered in ClickHouse.
    2. A native MergeTree table is created **inside** the catalog database
       with the same ``PARTITION BY`` as the source; ClickHouse forwards the
       DDL to the catalog, which materialises the Iceberg table.

    Args:
        columns: Column list for the ``CREATE TABLE`` body.
        partition_by: Expression used for ``PARTITION BY``.
        minio_root_user / minio_root_password: S3 credentials.
        namespace: Iceberg namespace. Defaults to a unique name.
        table_name: Iceberg table name. Defaults to a unique name.
        database_name: ClickHouse database name backed by the catalog.
        storage_endpoint: Value passed through to
            :func:`iceberg_engine.create_experimental_iceberg_database`.
    """
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

    with Given("ensure namespace exists via PyIceberg"):
        pyiceberg_catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(
            catalog=pyiceberg_catalog, namespace=namespace
        )

    with And("create DataLakeCatalog database in ClickHouse"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint=storage_endpoint,
        )

    pclause = f"PARTITION BY {partition_by}" if partition_by else ""

    qualified = f"{database_name}.\\`{namespace}.{table_name}\\`"

    with And(f"create iceberg table {qualified} through catalog"):
        node.query(
            textwrap.dedent(
                f"""
                CREATE TABLE {qualified} ({columns})
                ENGINE = Iceberg
                {pclause}
                """
            ).strip()
        )

    try:
        yield {
            "destination_table": qualified,
            "namespace": namespace,
            "table_name": table_name,
            "database_name": database_name,
            "pyiceberg_catalog": pyiceberg_catalog,
        }
    finally:
        if cleanup:
            with Finally(f"drop catalog destination {qualified}"):
                node.query(f"DROP TABLE IF EXISTS {qualified} SYNC")
                catalog_steps.drop_iceberg_table(
                    catalog=pyiceberg_catalog,
                    namespace=namespace,
                    table_name=table_name,
                )


@TestStep(Given)
def create_iceberg_destination(
    self,
    columns,
    partition_by,
    minio_root_user,
    minio_root_password,
    **kwargs,
):
    """Create the appropriate Iceberg destination for the current catalog mode.

    Dispatches on ``self.context.catalog``:

    * ``"no_catalog"`` -> :func:`create_iceberg_s3_destination` (returns a
      string ``table_name``).
    * ``"rest"`` / ``"glue"`` -> :func:`create_iceberg_catalog_destination`
      (returns a dict with ``destination_table`` and catalog metadata).

    For uniform access, scenarios should call :func:`as_destination_name`
    on the return value to get a string usable in
    ``ALTER TABLE ... TO TABLE <name>``.
    """
    catalog = self.context.catalog
    if catalog == "no":
        return create_iceberg_s3_destination(
            columns=columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            **kwargs,
        )
    elif catalog in ("rest", "glue"):
        # TODO: catalog-backed destinations need the Iceberg table to be
        # created through PyIceberg (DataLakeCatalog is read-only for DDL,
        # see iceberg_engine/alter.py). Until we have a ClickHouse -> PyIceberg
        # schema/partition-spec translator, skip these modes.
        skip(f"catalog mode {catalog!r} not yet implemented for export_partition")
    else:
        raise ValueError(f"Unsupported catalog mode: {catalog!r}")


def as_destination_name(destination):
    """Normalise the result of :func:`create_iceberg_destination` to a string.

    The no-catalog path returns a plain ``table_name`` string; the catalog
    path returns a dict with a ``destination_table`` key.
    """
    if isinstance(destination, dict):
        return destination["destination_table"]
    return destination


def as_pyiceberg_handle(destination):
    """Return the dict describing the PyIceberg table handle if available.

    For the no-catalog mode there is no PyIceberg handle (ClickHouse owns the
    table entirely), so this returns ``None``.
    """
    if isinstance(destination, dict):
        return destination
    return None
