"""Count paths: the metadata count shortcut, the count-only fast path, and
the count-from-files cache must all agree in the presence of deletion
vectors."""

import json

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Count_TrivialCountOptimization("1.0"))
def trivial_count_optimization(self):
    """The metadata count shortcut fails closed with live delete entries,
    and a lying snapshot summary loses to the manifest sum on a table
    without deletes."""
    rows = 100
    expected_count = 90

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    counts = {}
    with When("count() runs with the trivial count shortcut on and off"):
        for optimize in ("1", "0"):
            log_comment = common.unique_log_comment(f"trivial_{optimize}")
            counts[optimize] = common.count_rows(
                table=table,
                log_comment=log_comment,
                settings=[("optimize_trivial_count_query", optimize)],
            )
            if optimize == "1":
                with By("verifying the shortcut was not applied"):
                    applied = metrics.get_IcebergTrivialCountOptimizationApplied(
                        log_comment=log_comment
                    )
                    assert int(applied.output.strip() or 0) == 0, error(
                        "trivial count optimization was applied despite "
                        "live delete entries"
                    )

    with And("count() runs over a full subquery scan"):
        result = self.context.node.query(
            f"SELECT count() FROM (SELECT * FROM {table.sql_expr()})"
        )
        counts["subquery"] = int(result.output.strip())

    with Then("all three counts agree and reflect the vector"):
        assert (
            counts["1"] == counts["0"] == counts["subquery"] == expected_count
        ), error(f"counts disagree: {counts}")

    with Check("manifest sum wins over a lying snapshot summary"):
        with Given("a table without deletes"):
            plain = common.table_with_deletion_vectors(
                rows=50, delete_condition=None, verify_puffin=False
            )

        with When("the snapshot summary's total-records is corrupted"):
            metadata_key = s3_objects.latest_metadata_key(
                plain.namespace, plain.table_name
            )
            metadata = json.loads(s3_objects.get_object_bytes(metadata_key))
            for snapshot in metadata["snapshots"]:
                snapshot["summary"]["total-records"] = "999999"
            s3_objects.put_object_bytes(
                metadata_key, json.dumps(metadata).encode("utf-8")
            )
            common.drop_iceberg_metadata_cache()

        with Then("count() returns the manifest sum, not the summary"):
            count = common.count_rows(
                table=plain,
                settings=[
                    ("optimize_trivial_count_query", "1"),
                    ("use_iceberg_metadata_files_cache", "0"),
                ],
            )
            assert count == 50, error(
                f"count() = {count}, expected the manifest sum 50"
            )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Count_CountOnlyFastPath("1.0"))
def count_only_fast_path(self):
    """Counts are identical with and without PREWHERE, with and without a
    filter, and for data files split across multiple row groups."""
    rows = 10000
    deleted = {i for i in range(rows) if i % 100 == 0}
    expected = rows - len(deleted)

    with Given("a multi-row-group table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows,
            delete_condition="id % 100 = 0",
            extra_properties={
                "write.parquet.row-group-size-bytes": "4096",
                "write.parquet.page-size-bytes": "1024",
            },
        )
        common.assert_min_row_groups(table=table, min_row_groups=2)
        engine_table = common.engine_table(table=table)

    node = self.context.node
    predicate = "id % 2 = 1"
    expected_filtered = len(
        [i for i in range(rows) if i not in deleted and i % 2 == 1]
    )

    count_queries = {
        "plain count": (
            f"SELECT count() FROM {engine_table}",
            expected,
        ),
        "count with filter": (
            f"SELECT count() FROM {engine_table} WHERE {predicate}",
            expected_filtered,
        ),
        "count with prewhere": (
            f"SELECT count() FROM {engine_table} PREWHERE {predicate}",
            expected_filtered,
        ),
    }

    for name, (query, expected_value) in count_queries.items():
        for optimize_count in ("0", "1"):
            with Check(f"{name} with optimize_count_from_files={optimize_count}"):
                result = node.query(
                    query,
                    settings=[("optimize_count_from_files", optimize_count)],
                )
                assert int(result.output.strip()) == expected_value, error(
                    f"{name}: got {result.output.strip()}, "
                    f"expected {expected_value}"
                )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Count_CountFromFilesCache("1.0"))
def count_from_files_cache(self):
    """The count-from-files cache is neither used nor populated for data
    files with delete entries, in both directions of staleness."""
    rows = 100
    cache_setting = [("use_cache_for_count_from_files", "1")]

    with Given("a table without deletes"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition=None, verify_puffin=False
        )

    with When("count() with the count-from-files cache enabled returns N"):
        assert common.count_rows(table=table, settings=cache_setting) == rows, error()

    with And("an external DELETE produces a deletion vector"):
        spark.delete_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            condition="id < 10",
        )
        s3_objects.assert_puffin_exists(
            namespace=table.namespace, table_name=table.table_name
        )

    with Then("the next count() is N - deleted, not the cached N"):
        count = common.count_rows(table=table, settings=cache_setting)
        assert count == rows - 10, error(
            f"count() = {count}: stale count served from the "
            f"count-from-files cache"
        )

    with When(
        "counts are taken while deletes exist and the deletes are then "
        "compacted away"
    ):
        assert common.count_rows(table=table, settings=cache_setting) == rows - 10
        spark.rewrite_data_files(
            namespace=table.namespace,
            table_name=table.table_name,
            options="'delete-file-threshold', '1'",
        )

    with Then("the post-compaction count is not served stale"):
        count = common.count_rows(table=table, settings=cache_setting)
        assert count == rows - 10, error(
            f"count() = {count} after compaction, expected {rows - 10}"
        )

    with And("a subsequent insert is reflected immediately"):
        spark.insert_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            values="(1000, 'late'), (1001, 'late')",
        )
        count = common.count_rows(table=table, settings=cache_setting)
        assert count == rows - 10 + 2, error(f"count() = {count}")


@TestFeature
@Name("count paths")
def feature(self, minio_root_user, minio_root_password):
    """Count paths with deletion vectors."""
    Scenario(run=trivial_count_optimization)
    Scenario(run=count_only_fast_path)
    Scenario(run=count_from_files_cache)
