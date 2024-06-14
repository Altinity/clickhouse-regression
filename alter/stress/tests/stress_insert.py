#!/usr/bin/env python3
from testflows.core import *

from alter.stress.tests.actions import *
from alter.stress.tests.steps import *


@TestOutline(Scenario)
@Examples(
    "n_cols max_inserts",
    [
        (1, 2_000_000_000),
        (1, 2_000_000_000),
        (40, 50_000_000),
        (40, 50_000_000),
        (1000, 1_250_000),
        (1000, 1_250_000),
    ],
)
def stress_inserts(self, n_cols=40, max_inserts=50e6):
    """
    Check that performing tens of millions of individual inserts does not cause data to be lost.
    """
    nodes = self.context.ch_nodes[:2]
    max_inserts = int(max_inserts)

    columns = ", ".join([f"d{i} UInt8" for i in range(n_cols)])

    insert_settings = ", ".join(
        [
            "max_insert_block_size=1",  # Stress (zoo)keeper by inflating transaction counts
            "max_insert_threads=16",
            "max_memory_usage=0",  # Ignore per-query memory limits
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

    with Given(f"I create a replicated table with {n_cols} cols on each node"):
        _, table_name = replicated_table_cluster(columns=columns)

    total_rows = 0
    for n_inserts in insert_sequence():
        with When(f"I perform {n_inserts:,} individual inserts"):
            insert_random(
                node=nodes[0],
                table_name=table_name,
                columns=columns,
                rows=n_inserts,
                settings=insert_settings,
                timeout=600,
            )
            total_rows += n_inserts

        with Then(f"there should be {total_rows} rows"):
            assert_row_count(node=nodes[0], table_name=table_name, rows=total_rows)

    with When("I perform optimize on each node"):
        for node in nodes:
            optimize(node=node, table_name=table_name)

    with Then(f"there should still be {total_rows} rows"):
        assert_row_count(node=nodes[0], table_name=table_name, rows=total_rows)
        retry(assert_row_count, timeout=120, delay=1)(
            node=nodes[1], table_name=table_name, rows=total_rows
        )


@TestFeature
@Name("insert")
def feature(self):
    """Stress test with many inserts."""
    with Given("I have S3 disks configured"):
        disk_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
