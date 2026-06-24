"""Catalog-specific scenarios for EXPORT PARTITION.

Behaviour that only becomes interesting through a specific catalog
integration: ``no_catalog`` (icebergS3 table function, drop-and-reattach)
and ``rest`` / ``glue`` (``DataLakeCatalog`` commit path, external-reader
round-trip via PyIceberg).
"""

import textwrap

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_CatalogIntegration_NoCatalog,
    RQ_Iceberg_ExportPartition_CatalogIntegration_RestGlue,
)

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
from iceberg.tests.export_partition.steps.casting_iceberg_destination import (
    create_casting_catalog_iceberg_destination,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    read_via_icebergS3_table_function,
)

SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

FULL_PATHS_SETTING = [("write_full_path_in_iceberg_metadata", 1)]

DROP_PURGE_SETTINGS = [("iceberg_delete_data_on_drop", 1)]
INSERT_INTO_ICEBERG_SETTINGS = [("allow_experimental_insert_into_iceberg", 1)]
_CATALOG_CREATE_SETTINGS = [
    ("allow_experimental_database_iceberg", 1),
    ("write_full_path_in_iceberg_metadata", 1),
]


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


NO_CATALOG_MODES = ("no",)
EXTERNAL_CATALOG_MODES = ("ice", "glue")
ICE_CATALOG_MODES = ("ice",)


def _seed_source():
    source_table = f"mt_{getuid()}"
    with Given("create the source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert three rows into partition 2020"):
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020), (3, 2020)")
    return source_table


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_CatalogIntegration_NoCatalog("1.0"))
@Name("no_catalog: icebergS3 table function reads the committed export")
def no_catalog_read_via_icebergS3_table_function(
    self, minio_root_user, minio_root_password
):
    """A committed export is readable via the ``icebergS3`` table
    function (without the CH destination table), confirming the
    on-disk metadata is self-contained.
    """
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
@Requirements(RQ_Iceberg_ExportPartition_CatalogIntegration_NoCatalog("1.0"))
@Name("no_catalog: dropping the destination table keeps the committed data")
def no_catalog_drop_destination_keeps_metadata(
    self, minio_root_user, minio_root_password
):
    """Dropping the ClickHouse ``IcebergS3`` destination keeps the
    Iceberg metadata in MinIO; reattaching with ``CREATE TABLE IF NOT
    EXISTS`` on the same URL exposes the previously committed rows.
    """
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
@Requirements(RQ_Iceberg_ExportPartition_CatalogIntegration_RestGlue("1.0"))
@Name("catalog: export appends a snapshot visible through the external catalog")
def catalog_export_appends_snapshot_visible_via_catalog(
    self, minio_root_user, minio_root_password
):
    """``EXPORT PARTITION`` against a catalog-backed table drives the
    ``catalog->updateMetadata`` path end-to-end. Both ClickHouse (via
    ``DataLakeCatalog``) and a freshly reloaded PyIceberg handle must
    see the new snapshot with ``total-records = 3``. Skipped under
    ``no_catalog``.
    """
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
            total_records = (summary.additional_properties or {}).get("total-records")
        assert total_records == "3", error(
            f"Catalog snapshot summary reported total-records={total_records!r}, "
            f"expected '3'. Summary: {summary!r}"
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_CatalogIntegration_RestGlue("1.0"))
@Name("catalog: external reader round-trips exported data")
def catalog_external_reader_round_trips_exported_data(
    self, minio_root_user, minio_root_password
):
    """PyIceberg, following the catalog's metadata pointer, reads back
    the exported rows byte-exact. Catalog-mode analogue of the
    ``manifest_integrity`` external-reader scenario; skipped under
    ``no_catalog``.
    """
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
        except ValueError as exc:
            msg = str(exc)
            if "field-ids" not in msg and "name-mapping.default" not in msg:
                raise
            assert False, error(
                "External reader (PyIceberg) could not map exported Parquet "
                "columns to the Iceberg table schema. EXPORT PARTITION writes "
                "Parquet without Iceberg field-ids even when the catalog "
                "table was created with a proper schema. Underlying error: "
                f"{type(exc).__name__}: {exc}"
            )
        except (FileNotFoundError, OSError) as exc:
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


def _no_catalog_iceberg_s3_create_sql(
    table_name, columns, partition_by, url, minio_root_user, minio_root_password
):
    return textwrap.dedent(
        f"""
        CREATE TABLE {table_name} ({columns})
        ENGINE = IcebergS3('{url}', '{minio_root_user}', '{minio_root_password}')
        PARTITION BY {partition_by}
        SETTINGS s3_retry_attempts = 1
        """
    ).strip()


def _catalog_iceberg_create_sql(
    destination, columns, partition_by, minio_root_user, minio_root_password
):
    s3_url = (
        f"{DEFAULT_S3_ENDPOINT_HOST}/"
        f"{DEFAULT_S3_WAREHOUSE_BUCKET}/data/{destination['table_name']}/"
    )
    qualified_sql = (
        f"{destination['database_name']}."
        f"`{destination['namespace']}.{destination['table_name']}`"
    )
    pclause = f"PARTITION BY {partition_by}" if partition_by else ""
    return (
        qualified_sql,
        textwrap.dedent(
            f"""
            CREATE TABLE {qualified_sql} ({columns})
            ENGINE = IcebergS3('{s3_url}', '{minio_root_user}', '{minio_root_password}')
            {pclause}
            SETTINGS s3_retry_attempts = 1, iceberg_format_version = 2
            """
        ).strip(),
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_CatalogIntegration_NoCatalog("1.0"))
@Name("drop with purge allows recreating same table")
def no_catalog_drop_with_purge_recreates_same_table(
    self, minio_root_user, minio_root_password
):
    """With ``iceberg_delete_data_on_drop = 1``, ``DROP TABLE`` removes the
    on-disk Iceberg metadata so the same ``IcebergS3`` table name and URL
    can be created again without error (Altinity/ClickHouse#1909).
    """
    node = self.context.node
    table_name = f"iceberg_{getuid()}"
    url = (
        f"{DEFAULT_S3_ENDPOINT_HOST}/"
        f"{DEFAULT_S3_WAREHOUSE_BUCKET}/data/{table_name}/"
    )
    create_sql = _no_catalog_iceberg_s3_create_sql(
        table_name=table_name,
        columns=SIMPLE_COLUMNS,
        partition_by=SIMPLE_PARTITION_BY,
        url=url,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    with Given("create an IcebergS3 table"):
        node.query(create_sql, settings=FULL_PATHS_SETTING)

    with When("drop the table with iceberg_delete_data_on_drop enabled"):
        node.query(
            f"DROP TABLE {table_name} SYNC",
            settings=DROP_PURGE_SETTINGS,
        )

    with Then("recreate the same table name at the same location succeeds"):
        node.query(create_sql, settings=FULL_PATHS_SETTING)

    with And("the fresh table accepts writes"):
        node.query(
            f"INSERT INTO {table_name} VALUES (1, 2020)",
            settings=INSERT_INTO_ICEBERG_SETTINGS,
        )
        assert_destination_row_count(
            destination=table_name,
            expected=1,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Finally(f"drop destination {table_name} if it still exists"):
        node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_CatalogIntegration_RestGlue("1.0"))
@Name("drop with purge allows recreating same table")
def catalog_drop_with_purge_recreates_same_table(
    self, minio_root_user, minio_root_password
):
    """With ``iceberg_delete_data_on_drop = 1``, ``DROP TABLE`` on a
    ``DataLakeCatalog`` Iceberg table removes warehouse metadata so the
    same qualified name can be created again without error
    (Altinity/ClickHouse#1909).
    """
    node = self.context.node

    with Given("create a catalog-backed Iceberg table via ClickHouse DDL"):
        destination = create_casting_catalog_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            cleanup=False,
        )

    qualified_sql, create_sql = _catalog_iceberg_create_sql(
        destination=destination,
        columns=SIMPLE_COLUMNS,
        partition_by=SIMPLE_PARTITION_BY,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    try:
        with When("drop the table with iceberg_delete_data_on_drop enabled"):
            node.query(
                f"DROP TABLE {qualified_sql} SYNC",
                settings=DROP_PURGE_SETTINGS,
                use_file=True,
            )

        with Then("recreate the same catalog table name succeeds"):
            node.query(
                create_sql,
                settings=_CATALOG_CREATE_SETTINGS,
                use_file=True,
            )

        with And("the fresh table accepts writes through DataLakeCatalog"):
            node.query(
                f"INSERT INTO {qualified_sql} VALUES (1, 2020)",
                settings=INSERT_INTO_ICEBERG_SETTINGS,
                use_file=True,
            )
            assert_destination_row_count(
                destination=destination,
                expected=1,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    finally:
        with Finally(f"drop catalog destination {qualified_sql} if it exists"):
            node.query(
                f"DROP TABLE IF EXISTS {qualified_sql} SYNC",
                use_file=True,
            )
            node.query(f"DROP DATABASE IF EXISTS {destination['database_name']}")


SCENARIOS = (
    (no_catalog_read_via_icebergS3_table_function, NO_CATALOG_MODES),
    (no_catalog_drop_destination_keeps_metadata, NO_CATALOG_MODES),
    (no_catalog_drop_with_purge_recreates_same_table, NO_CATALOG_MODES),
    (catalog_export_appends_snapshot_visible_via_catalog, EXTERNAL_CATALOG_MODES),
    (catalog_external_reader_round_trips_exported_data, EXTERNAL_CATALOG_MODES),
    (catalog_drop_with_purge_recreates_same_table, ICE_CATALOG_MODES),
)


@TestFeature
@Name("catalogs")
def feature(self, minio_root_user, minio_root_password):
    """Catalog-specific export paths.

    Per-scenario applicability is filtered at load time so scenarios
    that don't apply to the current catalog mode are never registered;
    this keeps the requirement-satisfaction count from being penalised
    by not-applicable runtime ``skip()`` calls.
    """
    for scenario, applicable_modes in SCENARIOS:
        if self.context.catalog not in applicable_modes:
            continue
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
