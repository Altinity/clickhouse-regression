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

from iceberg.tests.export_partition.steps.pyiceberg_schema import (
    UnsupportedCHPartitionExprError,
    UnsupportedCHTypeError,
    ch_columns_to_pyiceberg_schema,
    ch_partition_by_to_pyiceberg_spec,
)


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
    cluster_name=None,
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
            node=node,
            cluster_name=cluster_name,
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


# Kwargs that only make sense for ``create_iceberg_s3_destination``. Under
# catalog mode PyIceberg owns the Iceberg layout so none of these have an
# analogue; scenarios that rely on them must stay no_catalog-only (e.g.
# :mod:`iceberg.tests.export_partition.storage_paths`).
_ICEBERG_S3_ONLY_KWARGS = (
    "storage_endpoint",
    "location_prefix",
    "extra_settings",
    "query_settings",
)


# Individual ``query_settings`` / ``extra_settings`` entries that exist only
# as workarounds for PyIceberg's ``StaticTable`` code path used under
# ``no_catalog`` mode. REST / Glue read table layout through the catalog
# instead of re-parsing ``metadata.json``, so these entries are irrelevant
# under catalog mode and can be dropped silently:
#
# * ``write_full_path_in_iceberg_metadata`` — forces CH to write absolute
#   ``s3://`` URIs for ``metadata.json`` ``location`` and every
#   ``manifest-list`` entry. ``StaticTable`` treats bucket-relative paths
#   as local-FS paths and blows up; the catalog path gets the table
#   location directly from the REST service. Dropping this setting does
#   not change what the catalog-mode scenario is asserting.
#
# Any other setting keeps its IcebergS3-only classification and forces a
# skip with a reason naming the offending setting.
_NO_CATALOG_STATICTABLE_WORKAROUND_SETTING_KEYS = frozenset(
    {"write_full_path_in_iceberg_metadata"}
)


def _strip_no_catalog_workarounds(settings):
    """Return a new settings list with known no_catalog-only workaround
    entries removed.

    ``settings`` is the list-of-2-tuples form used throughout the suite
    (e.g. ``[("write_full_path_in_iceberg_metadata", 1)]``). ``None`` is
    returned unchanged so callers don't need to probe for empty lists.
    """
    if not settings:
        return settings
    return [
        (key, value)
        for key, value in settings
        if key not in _NO_CATALOG_STATICTABLE_WORKAROUND_SETTING_KEYS
    ]


def _require_no_catalog(reason):
    """Skip the current scenario unless ``self.context.catalog == "no"``.

    Intended for scenarios and modules that are fundamentally about
    ``IcebergS3(...)`` semantics (CREATE-time settings that only live in
    the table engine, bucket layout assertions, ALTER DDL on the CH-side
    destination, …). ``reason`` is appended to the standard skip message
    so the test tree explains why the scenario is no_catalog-only.
    """
    catalog = current().context.catalog
    if catalog != "no":
        skip(
            f"scenario is no_catalog-only: {reason} "
            f"(current catalog mode: {catalog!r})"
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
      ``table_name`` string).
    * ``"rest"`` / ``"glue"`` -> :func:`create_pyiceberg_catalog_destination`
      after translating ``columns`` / ``partition_by`` into an explicit
      PyIceberg ``Schema`` + ``PartitionSpec`` via
      :mod:`iceberg.tests.export_partition.steps.pyiceberg_schema`.

    Under catalog modes, the destination dict returned by
    :func:`create_pyiceberg_catalog_destination` carries both the CH-side
    qualified name (for ``ALTER TABLE ... TO TABLE <name>``) and a live
    PyIceberg catalog handle — :func:`as_destination_name` /
    :func:`as_pyiceberg_handle` normalise access across both branches.

    Catalog mode cannot emulate a few ``IcebergS3(...)``-only kwargs
    (``storage_endpoint``, ``location_prefix``, ``query_settings``,
    ``extra_settings``). Passing any of them with a non-no_catalog mode
    skips the scenario with a reason that names the kwarg, rather than
    silently dropping settings the test depends on. If the underlying
    translator can't express the CH type / partition expression under
    test, the scenario is likewise skipped with the translator's own
    error message so the reason is specific to the untranslatable
    fragment.
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

    if catalog not in ("rest", "glue"):
        raise ValueError(f"Unsupported catalog mode: {catalog!r}")

    # ``query_settings`` / ``extra_settings`` that only hold the PyIceberg
    # StaticTable workaround keys (see
    # :data:`_NO_CATALOG_STATICTABLE_WORKAROUND_SETTING_KEYS`) get dropped
    # here so that catalog-mode scenarios can keep passing the same
    # no_catalog-friendly defaults without paying a false skip. Any
    # *other* entry keeps its IcebergS3-only status and triggers the
    # skip below with the offending key named in the reason.
    for key in ("query_settings", "extra_settings"):
        remaining = _strip_no_catalog_workarounds(kwargs.get(key))
        if remaining is None:
            continue
        if remaining:
            kwargs[key] = remaining
        else:
            kwargs.pop(key)

    s3_only_used = [key for key in _ICEBERG_S3_ONLY_KWARGS if key in kwargs]
    if s3_only_used:
        skip(
            f"catalog mode {catalog!r} cannot honour IcebergS3-only "
            f"kwargs: {s3_only_used!r}; scenario stays no_catalog-only"
        )

    try:
        schema, column_id_map = ch_columns_to_pyiceberg_schema(columns)
    except UnsupportedCHTypeError as e:
        skip(f"catalog mode {catalog!r}: {e}")

    try:
        partition_spec = ch_partition_by_to_pyiceberg_spec(
            partition_by, column_id_map
        )
    except UnsupportedCHPartitionExprError as e:
        skip(f"catalog mode {catalog!r}: {e}")

    forwarded = {
        key: value
        for key, value in kwargs.items()
        if key in ("table_name", "cleanup", "node", "cluster_name")
    }
    unknown = set(kwargs) - set(forwarded) - set(_ICEBERG_S3_ONLY_KWARGS)
    if unknown:
        # Surface unexpected kwargs loudly rather than silently dropping them —
        # every supported kwarg should be listed in one of the allow-lists
        # above. If a new kwarg is added to ``create_iceberg_s3_destination``,
        # this branch reminds us to classify it for the catalog path too.
        raise ValueError(
            f"create_iceberg_destination received unknown kwargs under "
            f"catalog mode {catalog!r}: {sorted(unknown)!r}"
        )

    return create_pyiceberg_catalog_destination(
        schema=schema,
        partition_spec=partition_spec,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        **forwarded,
    )


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


def as_system_destination_table(destination):
    """Return the value ClickHouse stores in
    ``system.replicated_partition_exports.destination_table`` for this
    destination.

    CH splits the destination identifier through ``StorageID`` when the
    manifest is written, so the ``destination_table`` column always holds
    the *unqualified* table name — even when the CH-side identifier is a
    backtick-escaped compound like ``datalake_xxx.\\`ns.tbl\\``` (see
    ``StorageSystemReplicatedPartitionExports.cpp`` and the
    ``destination_storage_id.table_name`` assignments in
    ``MergeTreeData.cpp`` / ``ExportList.cpp``).

    In ``no_catalog`` mode that's the same string as ``as_destination_name``
    (a bare identifier like ``iceberg_xxx``). Under ``rest`` / ``glue`` the
    identifier is qualified via ``<database>.\\`<namespace>.<table>\\```
    and CH stores ``"<namespace>.<table>"`` here.
    """
    if isinstance(destination, dict):
        return f"{destination['namespace']}.{destination['table_name']}"
    return destination


def as_system_destination_database(destination):
    """Return the value ClickHouse stores in
    ``system.replicated_partition_exports.destination_database`` for this
    destination.

    ``no_catalog`` mode returns ``None`` because the destination is a bare
    table name in the *current* database (CH's own default), which varies
    per test run — callers should not assert on it. ``rest`` / ``glue``
    return the PyIceberg-backed ``DataLakeCatalog`` database wired up in
    :func:`create_pyiceberg_catalog_destination`.
    """
    if isinstance(destination, dict):
        return destination["database_name"]
    return None
