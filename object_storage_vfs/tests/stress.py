#!/usr/bin/env python3
from testflows.core import *

from helpers.create import create_replicated_merge_tree_table
from s3.tests.common import s3_storage, enable_vfs

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Performance("1.0"))
def stress_inserts(self):
    """
    Check that performing tens of millions of individual inserts does not cause data to be lost
    """
    cluster = self.context.cluster

    max_inserts = 50_000_000
    n_cols = 40

    columns = ", ".join([f"d{i} UInt8" for i in range(n_cols)])

    def insert_sequence():
        """
        Produce a sequence of increasing numbers.
        It is desireable to know how close ClickHouse gets to max_inserts before failing.
        """
        n = 10000
        while n < max_inserts:
            n = min(n * 10, max_inserts)
            yield n // 4
            yield n // 2
            yield n

    with Given("I get some cluster nodes"):
        nodes = cluster.nodes["clickhouse"]

    with And(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    with And(f"I create a replicated table with {n_cols} cols on each node"):
        replicated_table(
            table_name="vfs_stress_test",
            columns=columns,
            allow_vfs=True,
        )

    total_rows = 0
    for n_inserts in insert_sequence():
        with When(f"I perform {n_inserts:,} individual inserts"):
            nodes[0].query(
                f"""
                INSERT INTO vfs_stress_test SELECT * FROM generateRandom('{columns}') 
                LIMIT {n_inserts} SETTINGS max_insert_block_size=1, max_insert_threads=32
                """,
                exitcode=0,
                timeout=600,
            )
            total_rows += n_inserts

        with Then(f"there should be {total_rows} rows"):
            assert_row_count(
                node=nodes[0], table_name="vfs_stress_test", rows=total_rows
            )

    with When("I perform optimize on each node"):
        for node in nodes:
            node.query("OPTIMIZE TABLE vfs_stress_test")

    with Then(f"there should still be {total_rows} rows"):
        assert_row_count(node=nodes[0], table_name="vfs_stress_test", rows=total_rows)
        assert_row_count(node=nodes[1], table_name="vfs_stress_test", rows=total_rows)


@TestFeature
@Name("stress")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def feature(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
