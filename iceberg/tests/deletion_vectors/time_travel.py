"""Snapshots and time travel: deletion vectors belong to the snapshot that
committed them — earlier snapshots, newer commits, sequence numbers and
compaction all resolve vectors per snapshot."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.manifest as manifest


def snapshot_settings(snapshot):
    return [("iceberg_snapshot_id", str(snapshot["snapshot-id"]))]


def timestamp_settings(timestamp_ms):
    return [("iceberg_timestamp_ms", str(timestamp_ms))]


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_TimeTravel("1.0"))
def time_travel(self):
    """A vector introduced in snapshot B is invisible when reading snapshot
    A, via both iceberg_snapshot_id and iceberg_timestamp_ms."""
    rows = 100
    deleted = [0, 20, 40, 60, 80]

    with Given("snapshot A inserts 100 rows, snapshot B deletes 5 via a vector"):
        table = common.table_with_deletion_vectors(
            rows=rows,
            delete_condition="id IN (0, 20, 40, 60, 80)",
        )
        snapshots = s3_objects.get_snapshots(table.namespace, table.table_name)
        assert len(snapshots) == 2, error(f"expected 2 snapshots, got {len(snapshots)}")
        snapshot_a, snapshot_b = snapshots

    expected_after = common.expected_ids(rows, deleted)

    with Then("the current read returns 95 rows as exact row sets"):
        common.assert_visible_ids(table=table, ids=expected_after)

    with And("snapshot A returns the original 100 rows"):
        common.assert_visible_ids(
            table=table, ids=list(range(rows)), settings=snapshot_settings(snapshot_a)
        )

    with And("snapshot B read explicitly returns 95 rows"):
        common.assert_visible_ids(
            table=table, ids=expected_after, settings=snapshot_settings(snapshot_b)
        )

    with And("a timestamp before the delete returns the original 100 rows"):
        common.assert_visible_ids(
            table=table,
            ids=list(range(rows)),
            settings=timestamp_settings(snapshot_a["timestamp-ms"]),
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_TimeTravel_MultipleGenerations("1.0"))
def multiple_generations(self):
    """Each snapshot exposes its own deletion-vector state regardless of
    query order and caching."""
    rows = 20

    with Given("snapshots A (no vector), B (deletes 1,5), C (deletes 9 too)"):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[
                common.insert_range_statement(rows),
                "DELETE FROM {table} WHERE id IN (1, 5)",
                "DELETE FROM {table} WHERE id = 9",
            ],
        )
        snapshots = s3_objects.get_snapshots(table.namespace, table.table_name)
        assert len(snapshots) == 3, error(f"expected 3 snapshots, got {len(snapshots)}")
        snapshot_a, snapshot_b, snapshot_c = snapshots

    generations = {
        "A": (snapshot_a, list(range(rows))),
        "B": (snapshot_b, [i for i in range(rows) if i not in (1, 5)]),
        "C": (snapshot_c, [i for i in range(rows) if i not in (1, 5, 9)]),
    }

    for order in (("C", "A", "B"), ("B", "C", "A"), ("A", "B", "C")):
        with Check(f"query order {'-'.join(order)}"):
            for generation in order:
                snapshot, expected = generations[generation]
                common.assert_visible_ids(
                    table=table, ids=expected, settings=snapshot_settings(snapshot)
                )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_SnapshotRefresh("1.0"))
def snapshot_refresh(self):
    """The next query after an external DELETE observes the new snapshot
    with all caches at default settings — no restart, no cache drops."""
    rows = 50

    with Given("a table without deletes and an Iceberg engine table over it"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition=None, verify_puffin=False
        )
        engine_table = common.engine_table(table=table)

    with And("both access forms are read once to warm every cache"):
        common.assert_visible_ids(table=table, ids=list(range(rows)))
        self.context.node.query(f"SELECT count() FROM {engine_table}")

    with When("an external DELETE commits a deletion vector"):
        spark.delete_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            condition="id < 10",
        )
        s3_objects.assert_puffin_exists(
            namespace=table.namespace, table_name=table.table_name
        )

    expected = list(range(10, rows))

    with Then("the very next table-function query observes the delete"):
        common.assert_visible_ids(table=table, ids=expected)

    with And("the very next table-engine query observes the delete"):
        result = self.context.node.query(
            f"SELECT id FROM {engine_table} ORDER BY id FORMAT TabSeparated"
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected, error(f"engine table returned {len(ids)} rows")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_SequenceNumbers("1.0"))
def sequence_numbers(self):
    """A vector does not affect data files added after it, and a vector
    whose data file left the snapshot is ignored rather than an error."""
    with Check("vector does not apply to newer files with equal values"):
        with Given("a table where ids 5 and 6 were deleted via a vector"):
            table = common.table_with_deletion_vectors(
                rows=0,
                setup_statements=[
                    common.insert_range_statement(100),
                    "DELETE FROM {table} WHERE id IN (5, 6)",
                    # same values, committed after the vector
                    "INSERT INTO {table} VALUES (5, 'row-5'), (6, 'row-6')",
                ],
            )

        with Then("the re-inserted rows are visible exactly once"):
            common.assert_visible_ids(table=table, ids=list(range(100)))

    with Check("vector referencing a data file not in the snapshot is ignored"):
        with Given("a table with files A (with vector) and B (without)"):
            table = common.table_with_deletion_vectors(
                rows=0,
                setup_statements=[
                    common.insert_range_statement(100),
                    "INSERT INTO {table} SELECT id + 100, "
                    "concat('row-', CAST(id + 100 AS STRING)) FROM range(50)",
                    "DELETE FROM {table} WHERE id < 100 AND id % 10 = 0",
                ],
            )

        with When("file A's entry is removed from the data manifests"):
            dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
            assert len(dv_entries) == 1, error()
            target = dv_entries[0]["entry"]["data_file"]["referenced_data_file"]

            def drop_target(entry):
                if entry["data_file"]["file_path"] == target:
                    return None
                return entry

            manifest.mutate_manifest_entries(
                namespace=table.namespace,
                table_name=table.table_name,
                mutator=drop_target,
                content=manifest.MANIFEST_LIST_DATA,
            )
            common.drop_iceberg_metadata_cache()

        with Then("the read succeeds with only file B's rows"):
            common.assert_visible_ids(
                table=table,
                ids=list(range(100, 150)),
                settings=[("use_iceberg_metadata_files_cache", "0")],
            )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Compaction("1.0"))
def compaction(self):
    """After external rewrite_data_files, old vectors do not apply to the
    rewritten files and the logical result is unchanged."""
    rows = 100
    deleted = list(range(0, rows, 10))
    expected = common.expected_ids(rows, deleted)

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    with And("its pre-compaction result is verified"):
        common.assert_visible_ids(table=table, ids=expected)

    with When("Spark compacts the data files"):
        spark.rewrite_data_files(
            namespace=table.namespace,
            table_name=table.table_name,
            options="'delete-file-threshold', '1'",
        )

    with Then("the logical result is identical after the compaction"):
        common.assert_visible_ids(table=table, ids=expected)

    with And("count() agrees"):
        assert common.count_rows(table=table) == len(expected), error()


@TestFeature
@Name("time travel")
def feature(self, minio_root_user, minio_root_password):
    """Snapshots and time travel with deletion vectors."""
    Scenario(test=time_travel, flags=TE)()
    Scenario(test=multiple_generations, flags=TE)()
    Scenario(test=snapshot_refresh, flags=TE)()
    Scenario(test=sequence_numbers, flags=TE)()
    Scenario(test=compaction, flags=TE)()
