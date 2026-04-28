"""Schema evolution between EXPORT PARTITION calls.

These scenarios exercise the Antalya-specific
``IcebergMetadata::alter`` path (``Mutations.cpp``) to evolve the Iceberg
destination's schema in lock-step with the MergeTree source, then verify
that subsequent ``EXPORT PARTITION`` calls pick up the new schema:

* ``add_column_between_exports`` - ``ADD COLUMN`` on both sides, export a
  second partition whose rows use the new column.
* ``drop_column_between_exports`` - ``DROP COLUMN`` on both sides, export
  the "narrower" partition.
* ``modify_column_widen`` - ``MODIFY COLUMN Int32 -> Int64`` on both sides,
  export new data that needs the widened range.
* ``rejected_rename_column`` - ``RENAME COLUMN`` on the Iceberg destination
  is rejected by ``IcebergMetadata::checkAlterIsPossible``.
* ``source_change_only_is_rejected`` - altering *only* the source while
  the destination keeps its older schema must fail at EXPORT time, not
  silently truncate/extend rows.
* ``iceberg_schema_history_advances`` - ``table.schemas()`` grows by at
  least one entry after an ADD COLUMN.

Every ALTER on the Iceberg destination is issued with
``allow_experimental_insert_into_iceberg = 1`` (required by
``IcebergMetadata::alter``). The ``EXPORT PARTITION`` statement itself is
enabled server-side via ``configs/clickhouse/config.d/export_partition.xml``.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_SchemaEvolution

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    _require_no_catalog,
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    select_from_destination,
)


BAD_ARGUMENTS = 36
NOT_IMPLEMENTED = 48
INCOMPATIBLE_COLUMNS = 122


ICEBERG_WRITE_SETTINGS = [("allow_experimental_insert_into_iceberg", 1)]


@TestStep(When)
def alter_source(self, source_table, alter_clause, node=None):
    """Run ``ALTER TABLE <source> <clause>`` on the MergeTree source."""
    if node is None:
        node = self.context.node
    node.query(f"ALTER TABLE {source_table} {alter_clause}")


@TestStep(When)
def alter_iceberg_destination(
    self,
    destination,
    alter_clause,
    exitcode=0,
    message=None,
    node=None,
):
    """Run ``ALTER TABLE <iceberg_dest> <clause>``.

    Iceberg writes require ``allow_experimental_insert_into_iceberg = 1``
    (``IcebergMetadata::alter`` rejects the ALTER otherwise with
    ``SUPPORT_IS_DISABLED``).
    """
    if node is None:
        node = self.context.node
    name = as_destination_name(destination)
    expect_failure = exitcode != 0 or message is not None
    return node.query(
        f"ALTER TABLE {name} {alter_clause}",
        settings=ICEBERG_WRITE_SETTINGS,
        exitcode=exitcode,
        message=message,
        ignore_exception=expect_failure,
    )


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


@TestScenario
@Name("add column between exports")
def add_column_between_exports(self, minio_root_user, minio_root_password):
    """Two sequential exports with an ``ADD COLUMN`` in between.

    Both sides grow a nullable ``score`` column before the second export;
    the destination must end up with both partitions, the Iceberg schema
    must contain the new field, and the pre-ADD rows must read back with
    ``score = NULL``.
    """
    source_table = f"mt_{getuid()}"
    initial_columns = "id Int64, year Int32"
    partition_by = "year"

    with Given("create source ReplicatedMergeTree with the initial schema"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=initial_columns,
            partition_by=partition_by,
        )

    with And("insert the first partition"):
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020)")

    with And("create the Iceberg destination with the initial schema"):
        destination = create_iceberg_destination(
            columns=initial_columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the 2020 partition"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
        )

    with And("ADD COLUMN score Nullable(Int32) on both source and destination"):
        alter_source(
            source_table=source_table,
            alter_clause="ADD COLUMN score Nullable(Int32)",
        )
        alter_iceberg_destination(
            destination=destination,
            alter_clause="ADD COLUMN score Nullable(Int32)",
        )

    with And("insert the second partition with a score"):
        insert_data(
            table_name=source_table, values="(3, 2021, 42), (4, 2021, NULL)"
        )

    with And("export the 2021 partition"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2021",
        )

    with Then("destination contains both partitions (4 rows total)"):
        assert_destination_row_count(
            destination=destination,
            expected=4,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("the 2020 rows read back with score = NULL"):
        result = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year, score",
            where_clause="year = 2020",
            order_by="id",
            format="TabSeparated",
        )
        expected = "1\t2020\t\\N\n2\t2020\t\\N"
        actual = result.output.strip()
        assert actual == expected, error(
            f"Pre-ADD-COLUMN rows should read back with score = NULL, got:\n{actual}"
        )

    with And("the 2021 rows carry their explicit scores"):
        result = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year, score",
            where_clause="year = 2021",
            order_by="id",
            format="TabSeparated",
        )
        expected = "3\t2021\t42\n4\t2021\t\\N"
        actual = result.output.strip()
        assert actual == expected, error(
            f"Post-ADD-COLUMN rows should carry their scores, got:\n{actual}"
        )


@TestScenario
@Name("drop column between exports")
def drop_column_between_exports(self, minio_root_user, minio_root_password):
    """Two sequential exports with a ``DROP COLUMN`` in between.

    Before the drop the destination has a ``note`` column; after the drop
    new rows are written without it, but the older snapshot's ``note``
    values should still be readable when selecting the remaining columns.
    """
    source_table = f"mt_{getuid()}"
    initial_columns = "id Int64, year Int32, note String"
    partition_by = "year"

    with Given("create source ReplicatedMergeTree with an extra column"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=initial_columns,
            partition_by=partition_by,
        )

    with And("insert the first partition"):
        insert_data(
            table_name=source_table, values="(1, 2020, 'a'), (2, 2020, 'b')"
        )

    with And("create the Iceberg destination with the extra column"):
        destination = create_iceberg_destination(
            columns=initial_columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the 2020 partition"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
        )

    with And("DROP COLUMN note on both sides"):
        alter_source(
            source_table=source_table, alter_clause="DROP COLUMN note"
        )
        alter_iceberg_destination(
            destination=destination, alter_clause="DROP COLUMN note"
        )

    with And("insert and export the 2021 partition without the column"):
        insert_data(table_name=source_table, values="(3, 2021), (4, 2021)")
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2021",
        )

    with Then("destination has both partitions"):
        assert_destination_row_count(
            destination=destination,
            expected=4,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("remaining columns read back byte-identically for both partitions"):
        result = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year",
            order_by="id",
            format="TabSeparated",
        )
        expected = "1\t2020\n2\t2020\n3\t2021\n4\t2021"
        actual = result.output.strip()
        assert actual == expected, error(
            f"Rows after DROP COLUMN differ from expected:\n{actual}"
        )


@TestScenario
@Name("modify column widen Int32 -> Int64")
def modify_column_widen(self, minio_root_user, minio_root_password):
    """``MODIFY COLUMN val Int64`` on both sides and export values that
    require the wider range.

    Iceberg allows the ``int -> long`` widening without rewriting data;
    we verify that after the MODIFY a ``Int64``-sized value round-trips
    unchanged.
    """
    source_table = f"mt_{getuid()}"
    initial_columns = "id Int64, year Int32, val Int32"
    widened_columns = "id Int64, year Int32, val Int64"
    partition_by = "year"

    with Given("create source and destination with val Int32"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=initial_columns,
            partition_by=partition_by,
        )
        insert_data(table_name=source_table, values="(1, 2020, 100)")
        destination = create_iceberg_destination(
            columns=initial_columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the 2020 partition (narrow values)"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
        )

    with And("widen val to Int64 on both sides"):
        alter_source(
            source_table=source_table,
            alter_clause="MODIFY COLUMN val Int64",
        )
        alter_iceberg_destination(
            destination=destination,
            alter_clause="MODIFY COLUMN val Int64",
        )

    with And("insert a wider value and export the 2021 partition"):
        insert_data(
            table_name=source_table,
            values="(2, 2021, 9223372036854775807)",
        )
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2021",
        )

    with Then("destination has both partitions"):
        assert_destination_row_count(
            destination=destination,
            expected=2,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("the wide value read back intact from the destination"):
        result = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year, val",
            order_by="id",
            format="TabSeparated",
        )
        expected = "1\t2020\t100\n2\t2021\t9223372036854775807"
        actual = result.output.strip()
        assert actual == expected, error(
            f"Widened values differ from expected:\n{actual}"
        )


@TestScenario
@Name("rejected: RENAME COLUMN on iceberg destination")
def rejected_rename_column(self, minio_root_user, minio_root_password):
    """``RENAME COLUMN`` is not accepted by ``IcebergMetadata::checkAlterIsPossible``.

    Iceberg preserves field identity through ids, so a rename would be a
    metadata-only operation; the C++ side still rejects it today. We
    assert the rejection with ``NOT_IMPLEMENTED`` (exit code 48).
    """
    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns="id Int64, year Int32, note String",
            partition_by="year",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("RENAME COLUMN is rejected"):
        alter_iceberg_destination(
            destination=destination,
            alter_clause="RENAME COLUMN note TO comment",
            exitcode=NOT_IMPLEMENTED,
            message="not supported",
        )


@TestScenario
@Name("source-only schema drift is rejected at EXPORT")
def source_only_schema_drift_rejected(
    self, minio_root_user, minio_root_password
):
    """Alter the source but leave the destination schema alone.

    The EXPORT PARTITION planner compares schemas and must reject the
    mismatch rather than write truncated / extended rows.
    """
    source_table = f"mt_{getuid()}"
    initial_columns = "id Int64, year Int32"

    with Given("create source and destination with the same schema"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=initial_columns,
            partition_by="year",
        )
        destination = create_iceberg_destination(
            columns=initial_columns,
            partition_by="year",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("add a column on the source only"):
        alter_source(
            source_table=source_table,
            alter_clause="ADD COLUMN score Nullable(Int32)",
        )
        insert_data(table_name=source_table, values="(1, 2020, 10)")

    with Then("EXPORT PARTITION is rejected for schema mismatch"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
            exitcode=INCOMPATIBLE_COLUMNS,
            message="INCOMPATIBLE_COLUMNS",
            wait_for_completion=False,
        )


@TestScenario
@Name("iceberg schema history grows after ADD COLUMN")
def iceberg_schema_history_advances(
    self, minio_root_user, minio_root_password
):
    """``table.schemas()`` gains at least one new entry after an ADD COLUMN.

    PyIceberg tracks every schema version the table has ever held; this
    scenario asserts that an ADD COLUMN on the Iceberg destination
    produces a new entry, so downstream readers can resolve rows written
    under each schema version.
    """
    initial_columns = "id Int64, year Int32"

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=initial_columns,
            partition_by="year",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("note the number of schemas recorded initially"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        schemas_before = len(table.schemas())

    with When("ADD COLUMN on the Iceberg destination"):
        alter_iceberg_destination(
            destination=destination,
            alter_clause="ADD COLUMN score Nullable(Int32)",
        )

    with Then("table.schemas() has at least one more entry"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        schemas_after = len(table.schemas())
        assert schemas_after > schemas_before, error(
            f"Expected Iceberg schema history to grow after ADD COLUMN, "
            f"but went from {schemas_before} to {schemas_after} entries"
        )

    with And("the latest schema carries the new field"):
        field_names = {field.name for field in table.schema().fields}
        assert "score" in field_names, error(
            f"New column 'score' is missing from the latest Iceberg schema. "
            f"Fields: {field_names}"
        )


SCENARIOS = (
    add_column_between_exports,
    drop_column_between_exports,
    modify_column_widen,
    rejected_rename_column,
    source_only_schema_drift_rejected,
    iceberg_schema_history_advances,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_SchemaEvolution("1.0"))
@Name("schema evolution")
def feature(self, minio_root_user, minio_root_password):
    """Schema evolution between EXPORT PARTITION calls.

    All scenarios drive ``ALTER TABLE <iceberg-destination> ...`` on the CH
    side, which is only accepted when the destination is a locally-managed
    ``IcebergS3(...)`` storage. ``DataLakeCatalog`` databases are read-only
    for DDL, so evolving a catalog-backed Iceberg table from ClickHouse is
    not currently possible — an equivalent catalog-mode module would have
    to drive ``table.update_schema()`` through PyIceberg instead. Gate the
    whole feature on ``no_catalog`` so the test tree is explicit about
    what isn't covered.
    """
    _require_no_catalog(
        "schema evolution drives `ALTER TABLE <iceberg-destination>` on "
        "the CH side; DataLakeCatalog databases are read-only for DDL so "
        "these scenarios only run against IcebergS3 destinations."
    )
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
