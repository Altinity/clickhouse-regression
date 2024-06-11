#!/usr/bin/env python3
import time

from testflows.core import *

from helpers.alter import *
from alter.stress.tests.actions import *
from alter.stress.tests.steps import *


@TestScenario
def drop_projection_freeze_partition(self):
    """Dropping a projection with a frozen partition."""

    @TestStep(When)
    def freeze(self):
        with When("I freeze a partition"):
            node.query(
                f"ALTER TABLE {table_name} FREEZE PARTITION 1 WITH NAME 'my_backup'"
            )

    @TestStep(When)
    def unfreeze(self):
        with When("I unfreeze the partition"):
            node.query(
                f"ALTER TABLE {table_name} UNFREEZE PARTITION 1 WITH NAME 'my_backup'"
            )

    @TestStep(When)
    def freeze_unfreeze(self):
        delay = 1
        freeze()

        with When(f"I wait {delay}s"):
            time.sleep(delay)

        unfreeze()

    @TestStep(When)
    def drop_projection(self, projection_name):
        with When("I drop the projection"):
            node.query(f"ALTER TABLE {table_name} DROP PROJECTION {projection_name}")

    with Given("I have a ClickHouse node"):
        node = self.context.ch_nodes[0]

    try:
        with Given("I have a table"):
            table_name = "my_table"
            columns = "a UInt16, b UInt16, c UInt16"
            node.query(
                f"""CREATE TABLE {table_name} ({columns}) 
                    ENGINE=MergeTree() 
                    ORDER BY a PARTITION BY (a % 2)"""
            )

        with When("I insert data into the table"):
            insert_random(node=node, table_name=table_name, rows=100, columns=columns)

        # with Then("I add and drop a projection with a frozen partition"):
        #     for attempt in repeats(30, until="fail"):
        #         with attempt:
        with When("I create a projection"):
            projection_name = "proj_" + getuid()[:8]
            node.query(
                f"ALTER TABLE {table_name} ADD PROJECTION {projection_name} (SELECT b, a ORDER BY a)"
            )

        with And("I materialize the projection"):
            node.query(
                f"ALTER TABLE {table_name} MATERIALIZE PROJECTION {projection_name} "
            )

        with Then("I check the projection exists"):
            for attempt in retries(timeout=10, delay=2):
                with attempt:
                    r = node.query(
                        f"SELECT partition, name, parent_name, active FROM system.projection_parts WHERE name='{projection_name}' AND active FORMAT TSV"
                    )
                    assert r.output.count(projection_name) == 2, error()

        with When("I combine freeze partition and drop projection"):
            wait1 = max(0, random.random() * 6 - 0.5)
            wait2 = max(0, random.random() * 6 - 0.5)
            note(f"wait1: {wait1:.3f}, wait2: {wait2:.3f}")
            By(run=freeze, parallel=True)
            time.sleep(wait1)
            By(test=drop_projection, parallel=True)(projection_name=projection_name)
            time.sleep(wait2)
            By(run=unfreeze, parallel=True)
            join()
            # time.sleep(30)

        with Then("I check the projection does not exist"):
            for attempt in retries(timeout=10, delay=2):
                with attempt:
                    r = node.query(
                        f"SELECT partition, name, parent_name, active FROM system.projection_parts WHERE name='{projection_name}' AND active FORMAT TSV"
                    )
                    assert r.output == "", error()

        # with When("I create the projection again"):
        #     node.query(
        #         f"ALTER TABLE {table_name} ADD PROJECTION {projection_name} (SELECT c, a ORDER BY a)"
        #     )

        # with And("I materialize the projection"):
        #     node.query(
        #         f"ALTER TABLE {table_name} MATERIALIZE PROJECTION {projection_name} "
        #     )

        # with Then("I check the projection exists"):
        #     for attempt in retries(timeout=10, delay=2):
        #         with attempt:
        #             r = node.query(
        #                 f"SELECT partition, name, parent_name, active FROM system.projection_parts WHERE name='{projection_name}' FORMAT TSV"
        #             )
        #             assert r.output.count(projection_name) == 2, error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
def add_column_drop_index(self):

    with Given("I have a ClickHouse node"):
        node = self.context.ch_nodes[0]

    try:
        with Given("I have a table"):
            table_name = "my_table"
            columns = "a UInt16, b UInt16, c UInt16"
            node.query(
                f"""CREATE TABLE {table_name} ({columns}) 
                    ENGINE=MergeTree() 
                    ORDER BY a PARTITION BY (a % 2)"""
            )

        with When("I insert data into the table"):
            insert_random(node=node, table_name=table_name, rows=100, columns=columns)

        with When("I add a column"):
            node.query(f"ALTER TABLE {table_name} ADD COLUMN d UInt16")

        with When("I create an index"):
            node.query(
                f"ALTER TABLE {table_name} ADD INDEX index_d d TYPE bloom_filter"
            )

        with When("I add another index"):
            node.query(
                f"ALTER TABLE {table_name} ADD INDEX index_b b TYPE bloom_filter"
            )

        with Then("I drop the new index"):
            node.query(f"ALTER TABLE {table_name} DROP INDEX index_b", exitcode=0)

        with Then("I make sure mutations are done"):
            wait_for_mutations_to_finish(node=node)

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
def rename_column_select(self):

    select_time_period = 3 * 60
    select_delay = 10

    with Given("I have ClickHouse nodes"):
        nodes = self.context.ch_nodes

    with Given("I have a replicated table"):
        table_name = "my_table"
        columns = "a UInt16, b UInt16, c UInt16"
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="external",
            columns=columns,
        )
    with When("I insert data into the table"):
        insert_random(node=nodes[0], table_name=table_name, rows=100, columns=columns)
        insert_random(node=nodes[1], table_name=table_name, rows=100, columns=columns)

    with When("I rename a column"):
        nodes[2].query(f"ALTER TABLE {table_name} RENAME COLUMN b TO d")

    with Then("I select continuously from the table"):
        for attempt in repeats(
            count=select_time_period // select_delay, delay=select_delay, until="fail"
        ):
            with attempt:
                nodes[0].query(
                    f"SELECT count() FROM {table_name}", exitcode=0, timeout=60
                )


@TestScenario
def select_all_missing_column(self):
    """
    SELECT count() can fail after detaching and attaching a partition where a column has been dropped
    """

    @TestStep(When)
    def drop_column(self, table_name):
        nodes[0].query(f"ALTER TABLE {table_name} DROP COLUMN c10")

    @TestStep(When)
    def replace_partition(self, table1_name, table2_name):
        nodes[1].query(
            f"ALTER TABLE {table1_name} REPLACE PARTITION 3 FROM {table2_name}"
        )

    with Given("I have ClickHouse nodes"):
        nodes = self.context.ch_nodes

    with Given("I have a replicated table"):
        table1_name = "table0"
        columns = ", ".join([f"c{i} UInt64" for i in range(50)])
        replicated_table_cluster(
            table_name=table1_name,
            storage_policy="external",
            columns=columns,
            partition_by="c0 % 4",
            settings="min_bytes_for_wide_part=0",
        )

    with Given("I have a another replicated table"):
        table2_name = "table1"
        replicated_table_cluster(
            table_name=table2_name,
            storage_policy="external",
            columns=columns,
            partition_by="c0 % 4",
            settings="min_bytes_for_wide_part=0",
        )

    with When("I insert lots of data into the tables"):
        insert_random(
            node=nodes[0], table_name=table1_name, rows=2_000_000, columns=columns
        )
        insert_random(
            node=nodes[0], table_name=table2_name, rows=2_000_000, columns=columns
        )

    with When("I drop a column and replace a partition"):
        By(test=drop_column, parallel=True)(table_name=table1_name)
        By(test=drop_column, parallel=True)(table_name=table2_name)
        time.sleep(1)
        By(test=replace_partition, parallel=True)(
            table1_name=table1_name, table2_name=table2_name
        )
        By(test=replace_partition, parallel=True)(
            table1_name=table2_name, table2_name=table1_name
        )

        with By("I check system.mutations"):
            for node in nodes:
                node.query(
                    "SELECT * FROM system.mutations FORMAT Vertical",
                    exitcode=0,
                    timeout=60,
                )

        join()

    with When("I detach and attach a different partition"):
        nodes[1].query(f"ALTER TABLE {table1_name} DETACH PARTITION 0")
        nodes[1].query(f"ALTER TABLE {table2_name} DETACH PARTITION 0")

        time.sleep(0.5)
        nodes[1].query(f"ALTER TABLE {table1_name} ATTACH PARTITION 0")
        nodes[1].query(f"ALTER TABLE {table2_name} ATTACH PARTITION 0")

    with Then("I select from the table"):
        for node in nodes:
            node.query(f"SELECT count() FROM {table1_name}", exitcode=0, timeout=60)
            node.query(f"SELECT count() FROM {table2_name}", exitcode=0, timeout=60)


@TestFeature
@Name("simplified")
def feature(self):
    """Run test simplified scenarios."""

    with Given("I have S3 disks configured"):
        disk_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
