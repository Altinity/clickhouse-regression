"""Distributed reads: *Cluster table functions return identical results,
old-protocol workers fail closed, and split data files apply vectors to the
correct absolute positions."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_ClusterFunctions("1.0"))
def read_variant(self, name, kwargs):
    """icebergS3Cluster returns exactly the single-node result for one
    representative deletion-vector read."""
    table = self.context.table

    with When("the read runs on a single node and on the cluster"):
        single = common.read_result(table=table, **kwargs)
        clustered = common.read_result(table=table, cluster=True, **kwargs)

    with Then("both results are identical"):
        assert single.output == clustered.output, error(
            f"cluster read of '{name}' differs from single-node read"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_ClusterFunctions("1.0"))
def cluster_functions(self):
    """icebergS3Cluster returns exactly the single-node result for
    representative deletion-vector reads."""
    with Given(
        "a table with two data files, one fully deleted, one with a partial vector"
    ):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[
                common.insert_range_statement(100),
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id + 100, "
                "concat('row-', CAST(id + 100 AS STRING)) FROM range(50)",
                "DELETE FROM {table} WHERE id < 100 AND id % 10 = 0",
                "DELETE FROM {table} WHERE id >= 140",
            ],
        )
        self.context.table = table
        snapshots = s3_objects.get_snapshots(table.namespace, table.table_name)

    read_variants = {
        "full read": dict(columns="id, data", order_by="id"),
        "filtered read": dict(columns="id", where_clause="id % 3 = 0", order_by="id"),
        "count": dict(columns="count()"),
        "aggregate": dict(columns="sum(id), uniqExact(data)"),
        "time travel to the first snapshot": dict(
            columns="id",
            order_by="id",
            settings=[("iceberg_snapshot_id", str(snapshots[0]["snapshot-id"]))],
        ),
    }

    for name, kwargs in read_variants.items():
        Scenario(test=read_variant, name=name)(name=name, kwargs=kwargs)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_ProtocolFailClosed("1.0"))
def protocol_fail_closed(self):
    """A worker whose protocol version cannot carry the deletion state must
    fail with UNKNOWN_PROTOCOL rather than silently return deleted rows."""
    skip(
        "requires a cluster worker running an older ClickHouse whose "
        "protocol lacks excluded_rows / iceberg_info / file_bucket_info "
        "support; all nodes in this environment run the same build"
    )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_SplitDataFile("1.0"))
def single_node_threads(self, threads):
    """A single split Parquet file applies the vector at correct absolute
    positions for one max_threads value."""
    ctx = self.context
    with Then("the visible row set matches"):
        ids = common.select_ids(table=ctx.table, settings=[("max_threads", threads)])
        assert ids == ctx.expected, error(
            f"max_threads={threads} returned {len(ids)} rows"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_SplitDataFile("1.0"))
def cluster_read(self):
    """A single split Parquet file applies the vector at correct absolute
    positions when read through the cluster function."""
    ctx = self.context
    with Then("the visible row set matches"):
        ids = common.select_ids(table=ctx.table, cluster=True)
        assert ids == ctx.expected, error(f"cluster read returned {len(ids)} rows")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_SplitDataFile("1.0"))
def counts_agree(self):
    """Single-node and cluster counts agree over a split data file."""
    ctx = self.context
    with Then("single-node and cluster counts match"):
        assert common.count_rows(table=ctx.table) == len(ctx.expected), error()
        assert common.count_rows(table=ctx.table, cluster=True) == len(
            ctx.expected
        ), error()


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_Distributed_SplitDataFile("1.0"))
def split_data_file(self):
    """A single Parquet file split by row group across threads or nodes
    applies the vector at correct absolute positions for any max_threads
    value."""
    rows = 10000
    deleted = {i for i in range(rows) if i % 500 < 3}  # deletions in every region

    with Given(
        "a single-file table with many row groups and deletions in every row group"
    ):
        table = common.table_with_deletion_vectors(
            rows=rows,
            delete_condition="id % 500 < 3",
            extra_properties={
                "write.parquet.row-group-size-bytes": "4096",
                "write.parquet.page-size-bytes": "1024",
            },
        )

    with And("the writer really produced one file with many row groups"):
        common.assert_data_file_count(table=table, count=1)
        common.assert_min_row_groups(table=table, min_row_groups=2)

    self.context.table = table
    self.context.expected = [i for i in range(rows) if i not in deleted]

    for threads in ("1", "4", "16"):
        Scenario(test=single_node_threads, name=f"max_threads={threads}")(
            threads=threads
        )
    Scenario(run=cluster_read)
    Scenario(run=counts_agree)


@TestFeature
@Name("distributed")
def feature(self, minio_root_user, minio_root_password):
    """Distributed deletion-vector reads."""
    Suite(run=cluster_functions)
    Scenario(run=protocol_fail_closed)
    Suite(run=split_data_file)
