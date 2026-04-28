"""Catalog-specific scenarios for EXPORT PARTITION.

The outer feature in :mod:`iceberg.tests.export_partition.feature` loops over
``no``, ``rest`` and ``glue``; this module focuses on behaviour that only
becomes interesting once the destination is viewed *through* a specific
catalog integration.

no_catalog (``ENGINE = IcebergS3``):
    * :func:`no_catalog_read_via_icebergS3_table_function` - a committed
      export is readable via the ``icebergS3`` table function (i.e. without
      the destination CH table), confirming the metadata layout on disk.
    * :func:`no_catalog_drop_destination_keeps_metadata` - dropping the CH
      destination table does *not* erase the Iceberg metadata in MinIO;
      recreating the IcebergS3 table against the same URL exposes the same
      rows.

rest / glue (``DataLakeCatalog`` + PyIceberg-materialised tables):
    * :func:`catalog_export_appends_snapshot_visible_via_catalog` - driving
      the ``IcebergMetadata::commitExportPartitionTransaction ->
      catalog->updateMetadata`` path: ClickHouse sees the rows through the
      ``DataLakeCatalog`` database *and* a fresh PyIceberg catalog handle
      reports the new snapshot with the expected row count in its summary.
    * :func:`catalog_external_reader_round_trips_exported_data` - PyIceberg
      ``table.scan().to_arrow()`` against the catalog-backed table reads back
      the committed rows through its own S3 FileIO, mirroring what Spark /
      Trino / duckdb would do. This is the catalog-mode analogue of the
      no-catalog external-reader scenario in
      :mod:`iceberg.tests.export_partition.manifest_integrity`.

Catalog-backed destinations can't reuse
:func:`iceberg_destination.create_iceberg_destination` because
``DataLakeCatalog`` databases in ClickHouse are read-only for DDL — the
Iceberg table has to pre-exist in the catalog. We materialise it via
PyIceberg's ``catalog.create_table`` through
:func:`iceberg_destination.create_pyiceberg_catalog_destination`, matching
the pattern used in the upstream
``test_export_partition_iceberg_catalog.py`` integration test.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_CatalogIntegration

from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import Schema
from pyiceberg.transforms import IdentityTransform
from pyiceberg.types import IntegerType, LongType, NestedField

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    wait_for_export_status,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_ENDPOINT_HOST,
    DEFAULT_S3_WAREHOUSE_BUCKET,
    as_destination_name,
    as_pyiceberg_handle,
    create_iceberg_destination,
    create_iceberg_s3_destination,
    create_pyiceberg_catalog_destination,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    read_via_icebergS3_table_function,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

FULL_PATHS_SETTING = [("write_full_path_in_iceberg_metadata", 1)]


# PyIceberg description of the same shape as ``SIMPLE_COLUMNS`` / ``SIMPLE_PARTITION_BY``.
# ``required=True`` matches CH's non-nullable primitives; the ``field_id``s are
# what will appear in manifest entries and must be stable across exports.
CATALOG_SCHEMA = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=True),
    NestedField(field_id=2, name="year", field_type=IntegerType(), required=True),
)
CATALOG_PARTITION_SPEC = PartitionSpec(
    PartitionField(
        source_id=2,
        field_id=1000,
        transform=IdentityTransform(),
        name="year",
    ),
)


def _require_mode(expected):
    actual = current().context.catalog
    if actual != expected:
        skip(
            f"scenario is only meaningful for catalog={expected!r}, "
            f"current mode is {actual!r}"
        )


def _require_external_catalog():
    """Skip the scenario in ``no_catalog`` mode.

    REST and Glue both exercise the ``catalog->updateMetadata`` commit path,
    so scenarios that target that path run under either mode; only ``no`` is
    meaningfully different (no external catalog to talk to).
    """
    actual = current().context.catalog
    if actual not in ("rest", "glue"):
        skip(
            f"scenario targets catalog-backed destinations; current mode is "
            f"{actual!r} (no external catalog)"
        )


def _seed_source():
    source_table = f"mt_{getuid()}"
    with Given("create the source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert three rows into partition 2020"):
        insert_data(
            table_name=source_table, values="(1, 2020), (2, 2020), (3, 2020)"
        )
    return source_table


@TestScenario
@Name("no_catalog: icebergS3 table function reads the committed export")
def no_catalog_read_via_icebergS3_table_function(
    self, minio_root_user, minio_root_password
):
    """After an export the destination is readable through the ``icebergS3``
    table function (i.e. bypassing the CH destination table).

    This confirms two things that a catalog would otherwise hide:

    1. ``metadata.json`` at the committed path parses without help from
       ClickHouse's own storage entry.
    2. The manifest layout resolves data files correctly when only the
       storage URL is known.
    """
    _require_mode("no")
    source_table = _seed_source()

    with Given("create the IcebergS3 destination with absolute paths"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )
    dest_name = as_destination_name(destination)

    with When("run the export"):
        export_partition(
            source_table=source_table,
            destination_table=dest_name,
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("icebergS3 table function returns the three rows ordered by id"):
        result = read_via_icebergS3_table_function(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year",
            order_by="id",
        )
        rows = [line for line in result.output.strip().splitlines() if line]
        assert rows == ["1\t2020", "2\t2020", "3\t2020"], error(
            f"icebergS3 table function returned unexpected rows:\n{result.output!r}"
        )


@TestScenario
@Name("no_catalog: dropping the destination table keeps the committed data")
def no_catalog_drop_destination_keeps_metadata(
    self, minio_root_user, minio_root_password
):
    """In ``no_catalog`` mode the Iceberg metadata lives entirely in MinIO.

    Dropping the ClickHouse ``IcebergS3`` table must not remove data files or
    metadata; a fresh ``IcebergS3`` storage attached to the same URL via
    ``CREATE TABLE IF NOT EXISTS`` must therefore see the previously
    committed rows without the server having to rewrite any metadata.

    The ``IF NOT EXISTS`` form is the documented way to re-open an existing
    Iceberg location: a plain ``CREATE TABLE`` is deliberately rejected with
    ``TABLE_ALREADY_EXISTS`` by ``IcebergMetadata::createIcebergTable``
    whenever the prefix already contains ``metadata/*.metadata.json`` — the
    safety check that prevents a fresh CREATE from silently overwriting an
    unrelated table at the same URL.
    """
    _require_mode("no")
    node = self.context.node
    source_table = _seed_source()

    table_name = f"iceberg_{getuid()}"
    url = (
        f"{DEFAULT_S3_ENDPOINT_HOST}/"
        f"{DEFAULT_S3_WAREHOUSE_BUCKET}/data/{table_name}/"
    )

    with Given("create the destination with cleanup disabled"):
        destination = create_iceberg_s3_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
            cleanup=False,
        )
    dest_name = as_destination_name(destination)
    assert dest_name == table_name, error(
        f"destination name mismatch: {dest_name!r} vs {table_name!r}"
    )

    try:
        with When("export the single partition"):
            export_partition(
                source_table=source_table,
                destination_table=dest_name,
                partition_id="2020",
                extra_settings=FULL_PATHS_SETTING,
            )

        with And("sanity-check the destination has 3 rows"):
            assert_destination_row_count(
                destination=destination,
                expected=3,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )

        with And("drop the ClickHouse IcebergS3 destination table"):
            node.query(f"DROP TABLE {dest_name} SYNC")

        with Then("attach a fresh IcebergS3 table to the existing metadata"):
            # ``IF NOT EXISTS`` is the documented idiom for re-opening an
            # existing Iceberg location: IcebergMetadata.cpp lists the
            # configured prefix for ``metadata/*.metadata.json`` and refuses
            # a plain ``CREATE TABLE`` with ``TABLE_ALREADY_EXISTS`` when any
            # is found (that's the safety check that prevents silently
            # clobbering someone else's Iceberg table). With ``IF NOT EXISTS``
            # the server skips writing a new ``metadata.json`` and just
            # registers a CH storage pointing at what's already there —
            # exactly the "attach to an existing table" flow this scenario
            # wants to verify.
            node.query(
                f"CREATE TABLE IF NOT EXISTS {dest_name} ({SIMPLE_COLUMNS}) "
                f"ENGINE = IcebergS3('{url}', '{minio_root_user}', "
                f"'{minio_root_password}') "
                f"PARTITION BY {SIMPLE_PARTITION_BY} "
                f"SETTINGS s3_retry_attempts = 1"
            )

        with And("the recreated table sees the committed rows"):
            assert_destination_row_count(
                destination=dest_name,
                expected=3,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    finally:
        with Finally(f"drop destination {dest_name} if it still exists"):
            node.query(f"DROP TABLE IF EXISTS {dest_name} SYNC")


@TestScenario
@Name("catalog: export appends a snapshot visible through the external catalog")
def catalog_export_appends_snapshot_visible_via_catalog(
    self, minio_root_user, minio_root_password
):
    """``EXPORT PARTITION`` against a catalog-backed table drives the
    ``catalog->updateMetadata`` commit path end-to-end.

    Steps:
        1. Materialise an empty Iceberg table through PyIceberg's
           ``catalog.create_table`` (REST or Glue, selected by the outer
           feature loop). This mirrors how users would bootstrap a
           catalog-managed destination.
        2. Wire ClickHouse to the same catalog via a ``DataLakeCatalog``
           database so ``ALTER TABLE ... EXPORT PARTITION ... TO TABLE
           <db>.`<ns.tbl>``` resolves the destination.
        3. Seed a ``ReplicatedMergeTree`` source and export one partition.

    Assertions (complementary sources, both must be satisfied):
        * ClickHouse's own read path through the ``DataLakeCatalog`` DB
          returns the 3 exported rows. This fails if the commit didn't land
          in the catalog or if the catalog returned stale metadata.
        * A **fresh** PyIceberg catalog handle (reloaded, not the one used
          for creation) reports ``current_snapshot()`` with
          ``summary['total-records'] == '3'``. This fails if the commit
          went through CH's in-memory cache but the external catalog never
          saw the update — the exact regression class that makes
          catalog-managed setups undetectable from CH alone.

    Scenario is skipped in ``no_catalog`` mode (there is no external
    catalog to commit to).
    """
    _require_external_catalog()
    source_table = _seed_source()

    with Given("materialise a catalog-backed Iceberg destination via PyIceberg"):
        destination = create_pyiceberg_catalog_destination(
            schema=CATALOG_SCHEMA,
            partition_spec=CATALOG_PARTITION_SPEC,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the single partition through the catalog"):
        # Pass the destination dict so wait_for_export_status can split the
        # catalog-backed qualified name into (destination_database,
        # destination_table) for its filter against
        # ``system.replicated_partition_exports``. See
        # ``_destination_where_pieces`` in ``steps/export_status.py``.
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("ClickHouse reads the committed rows through DataLakeCatalog"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("the external catalog reports the new snapshot independently"):
        handle = as_pyiceberg_handle(destination)
        assert handle is not None, error(
            "Expected catalog-backed destination to expose a PyIceberg handle"
        )
        # Reload the table through the catalog so we see exactly what an
        # external reader would see, not what PyIceberg cached locally at
        # creation time.
        external_view = handle["pyiceberg_catalog"].load_table(
            f"{handle['namespace']}.{handle['table_name']}"
        )
        snapshot = external_view.current_snapshot()
        assert snapshot is not None, error(
            "No current snapshot in catalog after EXPORT PARTITION — the "
            "commit never reached the external catalog"
        )
        summary = snapshot.summary
        total_records = None
        if summary is not None:
            total_records = (summary.additional_properties or {}).get(
                "total-records"
            )
        assert total_records == "3", error(
            f"Catalog snapshot summary reported total-records={total_records!r}, "
            f"expected '3'. Summary: {summary!r}"
        )


@TestScenario
@Name("catalog: external reader round-trips exported data")
def catalog_external_reader_round_trips_exported_data(
    self, minio_root_user, minio_root_password
):
    """A non-ClickHouse Iceberg reader can follow the catalog's metadata
    pointer and read the rows back byte-exact.

    Mirrors
    :func:`iceberg.tests.export_partition.manifest_integrity.external_reader_round_trips_exported_data`
    but for catalog-managed tables: here the metadata pointer comes from
    the catalog (REST / Glue) rather than from scanning an S3 warehouse
    prefix. Catching a regression in which ``EXPORT PARTITION`` mutates the
    catalog pointer but leaves the data files unreadable would surface
    here — if it fires in the wild, users of Spark / Trino / duckdb / dbt
    with an Iceberg catalog would hit the same failure.

    Scenario is skipped in ``no_catalog`` mode.
    """
    _require_external_catalog()
    source_table = _seed_source()

    with Given("materialise a catalog-backed Iceberg destination via PyIceberg"):
        destination = create_pyiceberg_catalog_destination(
            schema=CATALOG_SCHEMA,
            partition_spec=CATALOG_PARTITION_SPEC,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the single partition"):
        # ``destination=`` dispatches the catalog-aware split of
        # (destination_database, destination_table) when waiting for the
        # status to flip to ``COMPLETED``; see Phase 2 notes in
        # ``steps/export_status.py``.
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("PyIceberg (external reader) can materialise the exported rows"):
        handle = as_pyiceberg_handle(destination)
        assert handle is not None, error(
            "Expected catalog-backed destination to expose a PyIceberg handle"
        )
        external_view = handle["pyiceberg_catalog"].load_table(
            f"{handle['namespace']}.{handle['table_name']}"
        )
        try:
            arrow_table = external_view.scan().to_arrow()
        except (FileNotFoundError, OSError) as exc:
            # Same diagnostic shape as the no-catalog sibling: name the
            # offending ``data_file.file_path`` so the failure points
            # straight at the spec violation rather than a PyArrow trace.
            offending = []
            current_snapshot = external_view.current_snapshot()
            if current_snapshot is not None:
                for manifest in current_snapshot.manifests(external_view.io):
                    for entry in manifest.fetch_manifest_entry(external_view.io):
                        offending.append(entry.data_file.file_path)
            assert False, error(
                f"External reader (PyIceberg) could not open a data file "
                f"committed through the catalog. FileIO dispatch fell back "
                f"to the local filesystem, which is the symptom of "
                f"data_file.file_path lacking a URI scheme. Underlying "
                f"error: {type(exc).__name__}: {exc}. "
                f"data_file.file_path values: {offending!r}"
            )

    with And("scanned rows match the exported rows exactly"):
        rows = arrow_table.sort_by("id").to_pylist()
        observed = [(row["id"], row["year"]) for row in rows]
        expected_values = [(1, 2020), (2, 2020), (3, 2020)]
        assert observed == expected_values, error(
            f"PyIceberg scan through the catalog returned the wrong rows. "
            f"Expected {expected_values!r}, got {observed!r}"
        )


SCENARIOS = (
    no_catalog_read_via_icebergS3_table_function,
    no_catalog_drop_destination_keeps_metadata,
    catalog_export_appends_snapshot_visible_via_catalog,
    catalog_external_reader_round_trips_exported_data,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_CatalogIntegration("1.0"))
@Name("catalogs")
def feature(self, minio_root_user, minio_root_password):
    """Catalog-specific export paths (no_catalog today, REST/Glue pending)."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
