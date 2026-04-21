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
def create_pyiceberg_catalog_destination(
    self,
    schema,
    partition_spec,
    minio_root_user,
    minio_root_password,
    namespace=None,
    table_name=None,
    database_name=None,
    storage_endpoint=None,
    warehouse_bucket=None,
    pyiceberg_s3_endpoint="http://localhost:9002",
    table_properties=None,
    node=None,
    cleanup=True,
):
    """Create a catalog-backed Iceberg destination for ``EXPORT PARTITION``.

    Unlike :func:`create_iceberg_s3_destination`, the Iceberg table is
    materialised through PyIceberg's ``catalog.create_table(...)`` rather than
    through ClickHouse DDL. This mirrors the upstream pattern in
    ``test_export_partition_iceberg_catalog.py`` and is required because
    ``DataLakeCatalog`` databases are read-only for DDL on the ClickHouse side:
    ``CREATE TABLE ... ENGINE = Iceberg`` inside a ``DataLakeCatalog`` database
    is rejected by the server, so the catalog-registered table has to exist
    *before* the ClickHouse database is wired up to it.

    The returned dict carries both the ClickHouse qualified name (for
    ``ALTER TABLE ... EXPORT PARTITION ... TO TABLE <name>``) and the live
    PyIceberg ``Catalog`` handle, so scenarios can assert on the catalog
    directly after each commit (``current_snapshot()``, ``table.scan()``, etc.).

    Args:
        schema: A ``pyiceberg.schema.Schema``. Field types, ids and
            ``required`` flags must line up with the RMT source columns that
            ``EXPORT PARTITION`` will write. CH ``Int64`` -> ``LongType``,
            CH non-nullable primitive -> ``required=True``.
        partition_spec: A ``pyiceberg.partitioning.PartitionSpec``. Only
            identity transforms are tested end-to-end; other transforms live
            in :mod:`iceberg.tests.export_partition.partition_spec_evolution`.
        minio_root_user / minio_root_password: MinIO credentials used by both
            PyIceberg FileIO (via ``pyiceberg_s3_endpoint``) and the CH-side
            ``DataLakeCatalog`` database (via ``storage_endpoint``).
        namespace / table_name / database_name: Optional overrides, default
            to uniquely-generated names.
        storage_endpoint: S3 endpoint that ClickHouse uses to resolve the
            table's ``location``. Must be reachable from inside the CH
            containers and the bucket segment must match ``warehouse_bucket``
            (i.e. ``http://minio:9000/warehouse`` when ``warehouse_bucket=warehouse``).
        warehouse_bucket: S3 bucket that hosts the table data; inserted into
            the ``s3://<bucket>/data/<table>`` ``location`` passed to
            ``catalog.create_table``.
        pyiceberg_s3_endpoint: S3 endpoint used by PyIceberg on the test
            host (defaults to the MinIO port-forward on ``localhost:9002``).
        table_properties: Extra Iceberg ``properties`` for ``create_table``.
            ``format-version = 2`` is always set so snapshot management uses
            the current spec revision.
        cleanup: When true (default), drop the CH database and the PyIceberg
            table in the finaliser.
    """
    if node is None:
        node = self.context.node
    if namespace is None:
        namespace = f"export_ns_{getuid()}"
    if table_name is None:
        table_name = f"iceberg_{getuid()}"
    if database_name is None:
        database_name = f"datalake_{getuid()}"
    if warehouse_bucket is None:
        warehouse_bucket = DEFAULT_S3_WAREHOUSE_BUCKET
    if storage_endpoint is None:
        storage_endpoint = f"{DEFAULT_S3_ENDPOINT_HOST}/{warehouse_bucket}"

    properties = dict(table_properties or {})
    properties.setdefault("format-version", "2")

    with Given("connect to the external Iceberg catalog via PyIceberg"):
        pyiceberg_catalog = catalog_steps.create_catalog(
            s3_endpoint=pyiceberg_s3_endpoint,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            clean_up_minio_bucket=False,
        )

    with And(f"ensure namespace {namespace!r} exists"):
        catalog_steps.create_namespace(
            catalog=pyiceberg_catalog, namespace=namespace
        )

    with And(f"materialise iceberg table {namespace}.{table_name} through the catalog"):
        pyiceberg_catalog.create_table(
            identifier=f"{namespace}.{table_name}",
            schema=schema,
            location=f"s3://{warehouse_bucket}/data/{table_name}",
            partition_spec=partition_spec,
            properties=properties,
        )

    with And(f"create DataLakeCatalog database {database_name!r} in ClickHouse"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint=storage_endpoint,
        )

    # Backticks need to survive the bash pipeline that `node.query` uses to
    # feed the statement to ``clickhouse client``; otherwise bash interprets
    # them as command substitution and the SQL arrives as fragments. The rest
    # of the iceberg suite escapes them the same way.
    qualified = f"{database_name}.\\`{namespace}.{table_name}\\`"

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
            with Finally(f"drop catalog-backed table {namespace}.{table_name}"):
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

    * ``"no"``           -> :func:`create_iceberg_s3_destination` (returns a
      string ``table_name``).
    * ``"rest"`` / ``"glue"`` -> skipped: see note below.

    Catalog-backed scenarios cannot use this dispatcher because the Iceberg
    table has to be materialised through PyIceberg (see
    :func:`create_pyiceberg_catalog_destination`), which needs an explicit
    ``pyiceberg.schema.Schema`` and ``PartitionSpec`` — neither of which can
    be derived from the CH-style ``columns`` / ``partition_by`` strings used
    by the generic modules. :mod:`iceberg.tests.export_partition.catalogs`
    therefore calls :func:`create_pyiceberg_catalog_destination` directly.

    For uniform access downstream, scenarios should always funnel the return
    value through :func:`as_destination_name` to obtain a ``ALTER TABLE ...
    TO TABLE <name>``-compatible string.
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
        # Generic module-level scenarios (sanity, datatypes, …) express the
        # destination as CH DDL-style strings. We don't have a CH → PyIceberg
        # schema/partition-spec translator in this suite, so those scenarios
        # stay skipped under catalog modes. Tests that actually want to drive
        # the catalog commit path live in `catalogs.py` and reach for
        # `create_pyiceberg_catalog_destination` directly with a hand-written
        # schema + PartitionSpec.
        skip(
            f"catalog mode {catalog!r} requires an explicit PyIceberg "
            f"Schema/PartitionSpec; see create_pyiceberg_catalog_destination"
        )
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
