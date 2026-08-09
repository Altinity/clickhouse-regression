"""Partitioning: vectors apply on partitioned tables under any transform,
and partition pruning also skips loading the pruned files' vectors."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.metrics as metrics
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.manifest as manifest

# partition transforms exercised against the same logical (id, category)
# data set: category = str(id % 4)
PARTITION_TRANSFORMS = {
    "identity": "category",
    "bucket": "bucket(4, id)",
    "truncate": "truncate(1, category)",
}

CATEGORIES = 4


def deleted_ids(rows):
    """Union of the per-category deletes: id % 10 < 4 across the table."""
    return {i for i in range(rows) if i % 10 < 4}


@TestStep(Given)
def partitioned_table_with_vectors(self, transform, rows=100):
    """Partitioned v3 table with (id, category=str(id % 4)) where deletion
    vectors were produced by one DELETE commit **per category** — under
    identity partitioning each commit therefore writes its own Puffin file
    for its own partition, which the pruning scenario depends on."""
    return common.table_with_deletion_vectors(
        columns="id BIGINT, category STRING",
        partitioned_by=transform,
        rows=0,
        setup_statements=[
            "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id, CAST(id % 4 AS STRING) "
            f"FROM range({rows})"
        ]
        + [
            f"DELETE FROM {{table}} WHERE category = '{k}' AND id % 10 < 4"
            for k in range(CATEGORIES)
        ],
    )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Partitioning("1.0"))
def partition_transform(self, transform, rows=100):
    """Vectors apply correctly under one partition transform, including
    queries touching only a vector-bearing partition."""
    deleted = deleted_ids(rows)
    expected = [i for i in range(rows) if i not in deleted]

    with Given(f"a table partitioned by {transform} with vectors"):
        table = partitioned_table_with_vectors(transform=transform, rows=rows)

    with Then("the full read applies every partition's vector"):
        common.assert_visible_ids(table=table, ids=expected)

    with And("a query touching one vector-bearing partition applies it"):
        result = common.read_result(
            table=table,
            columns="id",
            where_clause="category = '0'",
            order_by="id",
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == [i for i in expected if i % 4 == 0], error(
            f"partition read returned {len(ids)} rows"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_Partitioning("1.0"))
def partitioning(self):
    """Vectors apply correctly under identity, bucket, and truncate
    partitioning."""
    for name, transform in PARTITION_TRANSFORMS.items():
        Scenario(test=partition_transform, name=f"{name} partitioning")(
            transform=transform
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Partitioning_PruningSkipsVectorLoad("1.0"))
def pruning_skips_vector_load(self):
    """Partition pruning skips the pruned files' Puffin reads, and pruning
    never drops a delete file needed by a file being read."""
    rows = 100
    deleted = deleted_ids(rows)

    with Given("an identity-partitioned table with a vector per partition"):
        table = partitioned_table_with_vectors(transform="category", rows=rows)

    with And(
        "each partition's vector really lives in its own Puffin file — "
        "with a single shared file, PuffinFilesRead could not distinguish "
        "pruned vector loads from unpruned ones"
    ):
        dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
        puffin_paths = {
            entry["entry"]["data_file"]["file_path"] for entry in dv_entries
        }
        referenced = {
            entry["entry"]["data_file"]["referenced_data_file"] for entry in dv_entries
        }
        assert len(dv_entries) == CATEGORIES, error(
            f"expected {CATEGORIES} vector entries, found {len(dv_entries)}"
        )
        assert len(puffin_paths) == CATEGORIES, error(
            f"expected {CATEGORIES} distinct Puffin files, found "
            f"{len(puffin_paths)}: {sorted(puffin_paths)}"
        )
        assert len(referenced) == CATEGORIES, error(
            f"expected each vector to reference its own data file, got "
            f"{len(referenced)} distinct references"
        )

    with And("the Puffin cache is cold"):
        common.drop_puffin_cache()

    with When("a query prunes down to a single partition"):
        log_comment = common.unique_log_comment("prune")
        result = common.read_result(
            table=table,
            columns="id",
            where_clause="category = '1'",
            order_by="id",
            log_comment=log_comment,
            use_iceberg_partition_pruning="1",
            settings=[("use_puffin_files_cache", "1")],
        )

    with Then("the surviving partition's vector was applied"):
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == [
            i for i in range(rows) if i % 4 == 1 and i not in deleted
        ], error(f"pruned read returned {len(ids)} rows")

    with And("files of other partitions were pruned"):
        pruned = metrics.get_IcebergPartitionPrunedFiles(log_comment=log_comment)
        assert int(pruned.output.strip() or 0) > 0, error(
            "expected partition pruning to skip files"
        )

    with And("no Puffin read happened for pruned files"):
        reads = metrics.get_profile_event(
            event="PuffinFilesRead", log_comment=log_comment
        )
        assert reads == 1, error(
            f"expected exactly the surviving partition's vector to be read, "
            f"PuffinFilesRead = {reads}"
        )


@TestFeature
@Name("partitioning")
def feature(self, minio_root_user, minio_root_password):
    """Partitioning and pruning with deletion vectors."""
    Suite(run=partitioning)
    Scenario(run=pruning_skips_vector_load)
