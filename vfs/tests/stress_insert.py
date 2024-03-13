#!/usr/bin/env python3
from testflows.core import *

from helpers.create import create_replicated_merge_tree_table

from vfs.tests.steps import *
from vfs.requirements import *


@TestOutline(Scenario)
@Tags("long", "combinatoric")
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Performance("1.0"))
@Examples(
    "n_cols max_inserts allow_vfs",
    [
        (1, 2_000_000_000, False),
        (1, 2_000_000_000, True),
        (40, 50_000_000, False),
        (40, 50_000_000, True),
        (1000, 1_250_000, False),
        (1000, 1_250_000, True),
    ],
)
def stress_inserts(self, n_cols=40, max_inserts=50e6, allow_vfs=True):
    """
    Check that performing tens of millions of individual inserts does not cause data to be lost.
    """
    nodes = self.context.ch_nodes[:2]
    max_inserts = int(max_inserts)
    fault_probability = 0.001

    columns = ", ".join([f"d{i} UInt8" for i in range(n_cols)])

    insert_settings = ", ".join(
        [
            "max_insert_block_size=1",  # Stress (zoo)keeper by inflating transaction counts
            "max_insert_threads=16",
            "max_memory_usage=0",  # Ignore per-query memory limits
            f"insert_keeper_fault_injection_probability={fault_probability}",  # Stress (zoo)keeper by injecting faults during inserts
        ]
    )

    def insert_sequence():
        """
        Produce a sequence of increasing numbers.
        It is desireable to know how close ClickHouse gets to max_inserts before failing.
        """
        n = 100_000
        while n < max_inserts:
            n = min(n * 10, max_inserts)
            yield n // 4
            yield n // 2
            yield n

    if allow_vfs:
        with Given("vfs is enabled"):
            enable_vfs()

    with Given(f"I create a replicated table with {n_cols} cols on each node"):
        _, table_name = replicated_table_cluster(columns=columns)

    total_rows = 0
    for n_inserts in insert_sequence():
        with When(f"I perform {n_inserts:,} individual inserts"):
            nodes[0].query(
                f"""
                INSERT INTO {table_name} SELECT * FROM generateRandom('{columns}') 
                LIMIT {n_inserts} SETTINGS {insert_settings}
                """,
                exitcode=0,
                timeout=600,
            )
            total_rows += n_inserts

        with Then(f"there should be {total_rows} rows"):
            assert_row_count(node=nodes[0], table_name=table_name, rows=total_rows)

    with When("I perform optimize on each node"):
        for node in nodes:
            node.query(f"OPTIMIZE TABLE {table_name}")

    with Then(f"there should still be {total_rows} rows"):
        assert_row_count(node=nodes[0], table_name=table_name, rows=total_rows)
        retry(assert_row_count, timeout=120, delay=1)(
            node=nodes[1], table_name=table_name, rows=total_rows
        )


@TestFeature
@Name("stress insert")
def feature(self):
    """Stress test with many inserts."""
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
