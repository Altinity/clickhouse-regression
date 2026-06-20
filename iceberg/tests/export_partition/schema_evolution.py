"""Schema evolution between EXPORT PARTITION calls.

Drives the ``IcebergMetadata::alter`` path to evolve the Iceberg
destination's schema in lock-step with the MergeTree source (ADD /
DROP / MODIFY column) and verifies subsequent exports pick up the new
schema. Also covers rejected source-only drift and the Iceberg
schema-history bookkeeping.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_SchemaEvolution_AcceptedAlterations,
    RQ_Iceberg_ExportPartition_SchemaEvolution_RejectedAlterations,
    RQ_Iceberg_ExportPartition_SchemaEvolution_SchemaHistory,
)

from helpers.common import getuid, check_if_antalya_post_26_3_10_20001

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
INCOMPATIBLE_COLUMNS = 122
NUMBER_OF_COLUMNS_DOESNT_MATCH = 20


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
    """Run ``ALTER TABLE <iceberg_dest> <clause>`` with
    ``allow_experimental_insert_into_iceberg = 1`` (required by
    ``IcebergMetadata::alter``).
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
@Requirements(RQ_Iceberg_ExportPartition_SchemaEvolution_AcceptedAlterations("1.0"))
@Name("add column between exports")
def add_column_between_exports(self, minio_root_user, minio_root_password):
    """``ADD COLUMN score Nullable(Int32)`` on both sides between two
    exports; the destination has both partitions and pre-ADD rows read
    back with ``score = NULL``.
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
        insert_data(table_name=source_table, values="(3, 2021, 42), (4, 2021, NULL)")

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
@Requirements(RQ_Iceberg_ExportPartition_SchemaEvolution_AcceptedAlterations("1.0"))
@Name("drop column between exports")
def drop_column_between_exports(self, minio_root_user, minio_root_password):
    """``DROP COLUMN note`` on both sides between two exports; the
    destination has both partitions and remaining columns read back
    byte-identically.
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
        insert_data(table_name=source_table, values="(1, 2020, 'a'), (2, 2020, 'b')")

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
        alter_source(source_table=source_table, alter_clause="DROP COLUMN note")
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
@Requirements(RQ_Iceberg_ExportPartition_SchemaEvolution_AcceptedAlterations("1.0"))
@Name("modify column widen Int32 -> Int64")
def modify_column_widen(self, minio_root_user, minio_root_password):
    """``MODIFY COLUMN val Int64`` on both sides; an Int64-only value
    round-trips through a subsequent export.
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
@Requirements(RQ_Iceberg_ExportPartition_SchemaEvolution_AcceptedAlterations("1.0"))
@Name("rename column between exports")
def rename_column_between_exports(self, minio_root_user, minio_root_password):
    """``RENAME COLUMN note TO comment`` on both sides between two
    exports; previously exported rows remain readable under the new
    column name and subsequent exports use the renamed field.
    """
    source_table = f"mt_{getuid()}"
    initial_columns = "id Int64, year Int32, note String"
    partition_by = "year"

    with Given("create source ReplicatedMergeTree with the initial schema"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=initial_columns,
            partition_by=partition_by,
        )

    with And("insert the first partition"):
        insert_data(table_name=source_table, values="(1, 2020, 'a'), (2, 2020, 'b')")

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

    with And("RENAME COLUMN note TO comment on both sides"):
        alter_source(
            source_table=source_table,
            alter_clause="RENAME COLUMN note TO comment",
        )
        alter_iceberg_destination(
            destination=destination,
            alter_clause="RENAME COLUMN note TO comment",
        )

    with And("insert and export the 2021 partition under the new column name"):
        insert_data(
            table_name=source_table,
            values="(3, 2021, 'c'), (4, 2021, 'd')",
        )
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

    with And("rows read back through the renamed column"):
        result = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year, comment",
            order_by="id",
            format="TabSeparated",
        )
        expected = "1\t2020\ta\n2\t2020\tb\n3\t2021\tc\n4\t2021\td"
        actual = result.output.strip()
        assert actual == expected, error(
            f"Rows after RENAME COLUMN differ from expected:\n{actual}"
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_SchemaEvolution_RejectedAlterations("1.0"))
@Name("source-only schema drift is rejected at EXPORT")
def source_only_schema_drift_rejected(self, minio_root_user, minio_root_password):
    """Altering only the source schema leaves the destination behind;
    the next ``EXPORT PARTITION`` is rejected instead of silently truncating.

    Before Altinity/ClickHouse#1779 (``>26.3.10.20001.altinityantalya``) the
    error is ``INCOMPATIBLE_COLUMNS``; afterward it is
    ``NUMBER_OF_COLUMNS_DOESNT_MATCH`` because column-count mismatch is
    checked before type compatibility.
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
        if check_if_antalya_post_26_3_10_20001(self):
            expected_exitcode = NUMBER_OF_COLUMNS_DOESNT_MATCH
            expected_message = "NUMBER_OF_COLUMNS"
        else:
            expected_exitcode = INCOMPATIBLE_COLUMNS
            expected_message = "INCOMPATIBLE_COLUMNS"
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
            exitcode=expected_exitcode,
            message=expected_message,
            wait_for_completion=False,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_SchemaEvolution_SchemaHistory("1.0"))
@Name("iceberg schema history grows after ADD COLUMN")
def iceberg_schema_history_advances(self, minio_root_user, minio_root_password):
    """``ADD COLUMN`` on the Iceberg destination grows
    ``table.schemas()`` by at least one entry, and the latest schema
    contains the new field.
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
    rename_column_between_exports,
    source_only_schema_drift_rejected,
    iceberg_schema_history_advances,
)


@TestFeature
@Name("schema evolution")
def feature(self, minio_root_user, minio_root_password):
    """Schema evolution between EXPORT PARTITION calls. ``no_catalog``
    only: ``DataLakeCatalog`` databases are read-only for DDL, so
    evolving a catalog-backed Iceberg table from ClickHouse is not
    currently possible.
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
