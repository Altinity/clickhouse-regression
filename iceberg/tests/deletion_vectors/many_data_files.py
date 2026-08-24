"""Many Parquet data files in one snapshot.

The rest of the suite forces ``COALESCE(1)`` so position-based fixtures
stay on a single data file. These scenarios drop that constraint: one
writer ``INSERT`` shards into many files, then a ``DELETE`` produces a
deletion vector per affected file — the layout a real Iceberg table has.

Adaptive query execution is disabled for the writer session so Spark
cannot coalesce the requested partitions back into one file.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.manifest as manifest

FILE_COUNT = 16
ROWS_PER_FILE = 100
ROWS = FILE_COUNT * ROWS_PER_FILE
DELETE_STEP = 10

MIX_FILE_COUNT = 8
MIX_ROWS = MIX_FILE_COUNT * ROWS_PER_FILE

# Iceberg must keep incoming Spark partitions; AQE would otherwise
# collapse a small REPARTITION back to one task / one file
SHARDING_PROPERTIES = {"write.distribution-mode": "none"}
DISABLE_AQE = (
    "SET spark.sql.adaptive.enabled = false",
    "SET spark.sql.adaptive.coalescePartitions.enabled = false",
)


def sharded_insert(rows, file_count, id_offset=0):
    """One INSERT that asks Spark for *file_count* output files.

    Only ``{table}`` is left for ``table_with_deletion_vectors`` to fill.
    """
    return (
        f"INSERT INTO {{table}} SELECT /*+ REPARTITION({file_count}) */ "
        f"id + {id_offset}, "
        f"concat('row-', CAST(id + {id_offset} AS STRING)) "
        f"FROM range({rows})"
    )


def deleted_ids(rows, step=DELETE_STEP, start=0):
    """Ids in ``start..start+rows-1`` that the writer DELETE removes."""
    return [i for i in range(start, start + rows) if i % step == 0]


@TestStep(Then)
def assert_many_file_layout(self, table, file_count, vector_count):
    """The current snapshot has exactly *file_count* live data files and
    *vector_count* deletion vectors, each vector referencing a distinct
    live data file."""
    files = manifest.live_data_files(table.namespace, table.table_name)
    dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
    live_paths = {data_file["file_path"] for data_file in files}
    referenced = {
        entry["entry"]["data_file"]["referenced_data_file"] for entry in dv_entries
    }

    assert len(files) == file_count, error(
        f"expected {file_count} live data files, found {len(files)}: "
        f"{sorted(live_paths)}"
    )
    assert len(dv_entries) == vector_count, error(
        f"expected {vector_count} deletion-vector entries, found "
        f"{len(dv_entries)}; referenced={sorted(referenced)}"
    )
    assert len(referenced) == vector_count, error(
        f"vectors do not each reference a distinct data file: " f"{sorted(referenced)}"
    )
    assert referenced <= live_paths, error(
        f"vectors reference files that are not live: "
        f"{sorted(referenced - live_paths)}"
    )
    return files, dv_entries


@TestStep(Given)
def sharded_table_with_vectors(self, file_count=FILE_COUNT, rows=ROWS):
    """One INSERT shards into *file_count* Parquet files; one DELETE then
    writes a deletion vector for every file."""
    table = common.table_with_deletion_vectors(
        rows=0,
        extra_properties=SHARDING_PROPERTIES,
        setup_statements=[
            *DISABLE_AQE,
            sharded_insert(rows=rows, file_count=file_count),
            f"DELETE FROM {{table}} WHERE id % {DELETE_STEP} = 0",
        ],
    )
    with And(f"the snapshot holds {file_count} data files, each with a vector"):
        assert_many_file_layout(
            table=table, file_count=file_count, vector_count=file_count
        )
    return table


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Read("1.0"))
def visible_rows(self):
    """Every file's vector is applied: the visible row set matches the
    writer, including a predicate that only some files can satisfy."""
    table = self.context.table
    expected = self.context.expected_ids

    with Then("ClickHouse rows equal the writer engine's own rows"):
        spark_rows = spark.select_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            columns="id",
            order_by="id",
        )
        spark_ids = [int(row[0]) for row in spark_rows]
        common.assert_visible_ids(table=table, ids=expected)
        assert spark_ids == expected, error(
            f"Spark returned {len(spark_ids)} rows, expected {len(expected)}"
        )

    with And("a filtered read still applies each touched file's vector"):
        cutoff = ROWS // 2
        result = common.read_result(
            table=table,
            columns="id",
            where_clause=f"id >= {cutoff}",
            order_by="id",
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == [i for i in expected if i >= cutoff], error(
            f"filtered read returned {len(ids)} rows"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_ClusterFunctions("1.0"))
def cluster_matches_single_node(self):
    """icebergS3Cluster returns the same rows and count as a single-node
    read of the many-file table."""
    table = self.context.table
    expected = self.context.expected_ids

    with Then("the full cluster read matches the single-node row set"):
        single = common.select_ids(table=table)
        clustered = common.select_ids(table=table, cluster=True)
        assert single == clustered == expected, error(
            f"single={len(single)} cluster={len(clustered)} "
            f"expected={len(expected)}"
        )

    with And("cluster count() agrees"):
        assert common.count_rows(table=table, cluster=True) == len(expected), error()


@TestScenario
@Requirements(
    RQ_Iceberg_DeletionVectors_Count_TrivialCountOptimization("1.0"),
    RQ_Iceberg_DeletionVectors_Count_CountOnlyFastPath("1.0"),
    RQ_Iceberg_DeletionVectors_Count_CountFromFilesCache("1.0"),
)
def count_paths_agree(self):
    """All count paths agree on the many-file table and the metadata
    shortcut stays fail-closed."""
    table = self.context.table
    expected = self.context.expected_count
    expr = table.sql_expr()
    counts = {}

    with When("count() runs with the trivial-count shortcut on and off"):
        for optimize in ("1", "0"):
            log_comment = common.unique_log_comment(f"many_trivial_{optimize}")
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
                        "live delete entries on many files"
                    )

    with And("count() runs over a full subquery scan"):
        result = self.context.node.query(f"SELECT count() FROM (SELECT * FROM {expr})")
        counts["subquery"] = int(result.output.strip())

    with And("count() runs with the count-from-files cache enabled"):
        counts["files_cache"] = common.count_rows(
            table=table, settings=[("use_cache_for_count_from_files", "1")]
        )

    with Then("every count path returns the post-vector row count"):
        assert all(value == expected for value in counts.values()), error(
            f"counts disagree: {counts}, expected {expected}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Cache_Setting("1.0"))
def warm_cache_hits_all_vectors(self):
    """A warm read of the many-file table is served from cache: every
    vector is a cache hit and no Puffin file is re-fetched."""
    table = self.context.table
    expected = self.context.expected_count
    vector_count = self.context.vector_count

    with When("a cold read populates the cache"):
        common.drop_puffin_cache()
        cold_comment = common.unique_log_comment("many_cold")
        cold = common.count_rows(table=table, log_comment=cold_comment)

    with Then("the cold read fetched Puffin data and is correct"):
        assert cold == expected, error(f"cold count() = {cold}")
        events = common.get_puffin_events(log_comment=cold_comment)
        assert events["PuffinFilesRead"] > 0, error(f"cold read events: {events}")

    with When("the table is read again"):
        warm_comment = common.unique_log_comment("many_warm")
        warm = common.count_rows(table=table, log_comment=warm_comment)

    with Then("the repeated query is served from cache for every vector"):
        assert warm == expected, error(f"warm count() = {warm}")
        events = common.get_puffin_events(log_comment=warm_comment)
        assert events["PuffinFilesCacheHits"] >= vector_count, error(
            f"warm read hits {events['PuffinFilesCacheHits']}, "
            f"expected at least {vector_count}: {events}"
        )
        assert events["PuffinFilesRead"] == 0, error(f"warm read events: {events}")


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_Read("1.0"))
def sharded_write(self):
    """One writer commit shards the table into many Parquet files, each
    carrying its own deletion vector. Row visibility, cluster reads,
    count paths, and the Puffin cache are all checked on that table."""
    with Given(
        f"a {ROWS}-row table written as {FILE_COUNT} Parquet files, "
        f"each with a deletion vector"
    ):
        table = sharded_table_with_vectors()
        self.context.table = table
        self.context.expected_ids = common.expected_ids(ROWS, deleted_ids(ROWS))
        self.context.expected_count = len(self.context.expected_ids)
        self.context.vector_count = FILE_COUNT

    Scenario(run=visible_rows)
    Scenario(run=cluster_matches_single_node)
    Scenario(run=count_paths_agree)
    Scenario(run=warm_cache_hits_all_vectors)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Coexistence_AcrossDataFiles("1.0"))
def mixed_files_with_and_without_vectors(self):
    """In one snapshot, some data files carry a deletion vector and later
    files carry none. Each file's result comes from its own delete
    metadata only — files without a vector contribute every row."""
    first_rows = MIX_ROWS
    second_rows = MIX_ROWS
    total_rows = first_rows + second_rows
    deleted = deleted_ids(first_rows)
    expected = common.expected_ids(total_rows, deleted)

    with Given(
        f"{MIX_FILE_COUNT} files with a vector (ids 0..{first_rows - 1}) "
        f"and {MIX_FILE_COUNT} files with none (ids {first_rows}..{total_rows - 1})"
    ):
        table = common.table_with_deletion_vectors(
            rows=0,
            extra_properties=SHARDING_PROPERTIES,
            setup_statements=[
                *DISABLE_AQE,
                sharded_insert(rows=first_rows, file_count=MIX_FILE_COUNT),
                f"DELETE FROM {{table}} WHERE id < {first_rows} "
                f"AND id % {DELETE_STEP} = 0",
                sharded_insert(
                    rows=second_rows,
                    file_count=MIX_FILE_COUNT,
                    id_offset=first_rows,
                ),
            ],
        )

    with And("the snapshot mixes vector-bearing and vector-free files"):
        assert_many_file_layout(
            table=table,
            file_count=MIX_FILE_COUNT * 2,
            vector_count=MIX_FILE_COUNT,
        )

    with Then("only the first batch's deleted ids are hidden"):
        spark_rows = spark.select_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            columns="id",
            order_by="id",
        )
        spark_ids = [int(row[0]) for row in spark_rows]
        common.assert_visible_ids(table=table, ids=expected)
        assert spark_ids == expected, error(
            f"Spark returned {len(spark_ids)} rows, expected {len(expected)}"
        )

    with And("every row of the vector-free files is visible"):
        later = common.select_ids(table=table, where_clause=f"id >= {first_rows}")
        assert later == list(range(first_rows, total_rows)), error(
            f"vector-free files contributed {len(later)} rows, "
            f"expected {second_rows}"
        )


@TestFeature
@Name("many data files")
def feature(self, minio_root_user, minio_root_password):
    """Deletion vectors on snapshots whose rows live in many Parquet files."""
    Suite(run=sharded_write)
    Scenario(run=mixed_files_with_and_without_vectors)
