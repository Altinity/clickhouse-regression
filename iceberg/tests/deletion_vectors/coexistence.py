"""Coexistence of deletion vectors with Parquet position deletes and
equality deletes, including the v3 supersession rule and format-version
upgrades."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.manifest as manifest
import iceberg.tests.deletion_vectors.steps.delete_files as delete_files

MOR_V2_PROPERTIES = {
    "format-version": "2",
    "write.delete.mode": "merge-on-read",
    "write.update.mode": "merge-on-read",
    "write.merge.mode": "merge-on-read",
}


@TestStep(Given)
def v2_table_with_position_deletes(
    self, rows=100, delete_condition="id < 20 AND id % 2 = 0"
):
    """A format-version 2 merge-on-read table where Spark's DELETE produced
    a Parquet position-delete file (not a deletion vector)."""
    table = common.table_with_deletion_vectors(
        rows=rows,
        delete_condition=delete_condition,
        extra_properties=MOR_V2_PROPERTIES,
        verify_puffin=False,
    )

    with And("the v2 delete produced no Puffin file"):
        puffin_keys = s3_objects.find_puffin_keys(
            namespace=table.namespace, table_name=table.table_name
        )
        assert not puffin_keys, error(
            f"v2 table unexpectedly has Puffin files: {puffin_keys}"
        )

    return table


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Coexistence_AcrossDataFiles("1.0"))
def across_data_files(self):
    """Different data files of one snapshot independently carry a position
    delete (pre-upgrade), a deletion vector, an equality delete, or nothing —
    each file's result comes from its own delete metadata only."""
    with Given("a v2 table with file A (ids 0..99) and a position delete on it"):
        table = v2_table_with_position_deletes(
            rows=100, delete_condition="id < 20 AND id % 2 = 0"
        )

    with When("the table is upgraded to format version 3"):
        spark.set_table_properties(
            namespace=table.namespace,
            table_name=table.table_name,
            properties={"format-version": "3"},
        )

    with And("file B (ids 100..199) is added and gets a deletion vector"):
        spark.execute(
            namespace=table.namespace,
            table_name=table.table_name,
            statements=[
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id + 100, "
                "concat('row-', CAST(id + 100 AS STRING)) FROM range(100)",
                "DELETE FROM {table} WHERE id >= 100 AND id % 10 = 0",
            ],
        )
        s3_objects.assert_puffin_exists(
            namespace=table.namespace, table_name=table.table_name
        )

    with And("file C (ids 200..249) is added with no delete at all"):
        spark.execute(
            namespace=table.namespace,
            table_name=table.table_name,
            statements=[
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id + 200, "
                "concat('row-', CAST(id + 200 AS STRING)) FROM range(50)",
            ],
        )

    with And("an equality delete targeting ids of file A is added"):
        # ids 1 and 3 survive the position delete (odd) — the equality
        # delete removes them independently of the other delete formats
        delete_files.add_equality_delete(
            namespace=table.namespace,
            table_name=table.table_name,
            ids=[1, 3],
        )
        common.drop_iceberg_metadata_cache()

    with Then("each data file reflects exactly its own delete metadata"):
        absent = (
            {i for i in range(20) if i % 2 == 0}  # position delete on A
            | {1, 3}  # equality delete
            | {i for i in range(100, 200) if i % 10 == 0}  # vector on B
        )
        expected = [i for i in range(250) if i not in absent]
        common.assert_visible_ids(
            table=table,
            ids=expected,
            settings=common.FRESH_READ_SETTINGS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Coexistence_SupersedesPositionDeletes("1.0"))
def supersedes_position_deletes(self):
    """A position-delete file for a data file that also has a deletion
    vector is ignored: overlapping rows are removed exactly once and rows
    only in the superseded file remain visible."""
    rows = 100
    dv_deleted = set(range(0, rows, 10))

    with Given("a table whose single data file has a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )
        common.assert_data_file_count(table=table, count=1)
        # positions are derived from the file's physical row order, so the
        # scenario holds even if the writer stores rows out of insertion
        # order
        position_of = {
            value: position
            for position, value in enumerate(common.parquet_column_values(table=table))
        }

    with When(
        "a position-delete file for the same data file marks the position "
        "of id 0 (also in the vector) and of id 5 (not in the vector)"
    ):
        delete_files.add_position_delete(
            namespace=table.namespace,
            table_name=table.table_name,
            data_file_path=delete_files.first_data_file_path(
                table.namespace, table.table_name
            ),
            positions=[position_of[0], position_of[5]],
        )
        common.drop_iceberg_metadata_cache()

    with Then(
        "vector rows are absent exactly once and row 5 stays visible "
        "because the position-delete file is superseded"
    ):
        expected = [i for i in range(rows) if i not in dv_deleted]
        assert 5 in expected, error("test invariant broken")
        common.assert_visible_ids(
            table=table,
            ids=expected,
            settings=common.FRESH_READ_SETTINGS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Coexistence_EqualityDeletes("1.0"))
def equality_deletes(self):
    """An equality delete applies in addition to the deletion vector on the
    same data file: vector first (by position), then the equality predicate
    on survivors."""
    rows = 100
    dv_deleted = set(range(0, rows, 10))

    with Given("a table whose single data file has a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    with When(
        "an equality delete removes id 20 (already in the vector) and "
        "id 5 (a vector survivor)"
    ):
        delete_files.add_equality_delete(
            namespace=table.namespace,
            table_name=table.table_name,
            ids=[5, 20],
        )
        common.drop_iceberg_metadata_cache()

    with Then("both delete formats apply, overlapping rows removed once"):
        absent = dv_deleted | {5}
        expected = [i for i in range(rows) if i not in absent]
        common.assert_visible_ids(
            table=table,
            ids=expected,
            settings=common.FRESH_READ_SETTINGS,
        )
        assert common.count_rows(
            table=table,
            settings=common.FRESH_READ_SETTINGS,
        ) == len(expected), error()


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Coexistence_MultipleVectorsError("1.0"))
def multiple_vectors_error(self):
    """Two live deletion-vector entries referencing the same data file fail
    the query — no picking one, no union."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with When("the deletion-vector manifest entry is duplicated"):
        manifest.duplicate_dv_entry(
            namespace=table.namespace, table_name=table.table_name
        )

    with Then("the read fails with ICEBERG_SPECIFICATION_VIOLATION"):
        common.assert_table_read_fails(
            table=table,
            error_name="ICEBERG_SPECIFICATION_VIOLATION",
            message_fragment="Multiple deletion vectors match data file",
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Coexistence_FormatVersionUpgrade("1.0"))
def format_version_upgrade(self):
    """A v2 table with position deletes reads identically right after the
    upgrade to v3, and the first v3 delete removes new rows while
    pre-upgrade deletes stay absent."""
    rows = 100
    v2_deleted = {i for i in range(20) if i % 2 == 0}
    expected_before = [i for i in range(rows) if i not in v2_deleted]

    with Given("a v2 table with a Parquet position delete"):
        table = v2_table_with_position_deletes(
            rows=rows, delete_condition="id < 20 AND id % 2 = 0"
        )

    with And("its pre-upgrade result is verified"):
        common.assert_visible_ids(table=table, ids=expected_before)

    with When("the table is upgraded to format version 3"):
        spark.set_table_properties(
            namespace=table.namespace,
            table_name=table.table_name,
            properties={"format-version": "3"},
        )

    with Then("the result is identical immediately after the upgrade"):
        common.assert_visible_ids(table=table, ids=expected_before)

    with When("the first v3 delete produces a deletion vector"):
        spark.delete_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            condition="id IN (50, 51)",
        )
        s3_objects.assert_puffin_exists(
            namespace=table.namespace, table_name=table.table_name
        )

    with Then("pre-upgrade deletes stay absent and newly deleted rows disappear"):
        expected_after = [i for i in expected_before if i not in (50, 51)]
        common.assert_visible_ids(table=table, ids=expected_after)


@TestFeature
@Name("coexistence")
def feature(self, minio_root_user, minio_root_password):
    """Coexistence with other delete formats."""
    Scenario(run=across_data_files)
    Scenario(run=supersedes_position_deletes)
    Scenario(run=equality_deletes)
    Scenario(run=multiple_vectors_error)
    Scenario(run=format_version_upgrade)
