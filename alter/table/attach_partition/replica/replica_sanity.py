from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.replica.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


@TestScenario
def parallel_add_remove_sanity(self):
    """
    Test that no data is lost when replicas are added and removed
    during inserts on other replicas.
    """

    table_name = "table_" + getuid()
    nodes = self.context.nodes
    rows_per_insert = 100

    try:
        with Given("I have a replicated table on one node"):
            create_one_replica(node=nodes[0], table_name=table_name)

        When(
            "I start parallel inserts on the first node",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[0],
            table_name=table_name,
            rows=rows_per_insert,
        )
        insert_sets = 1
        nodes[0].query(f"SELECT count() from {table_name}")

        And(
            "I replicate the table on the second node in parallel",
            test=create_one_replica,
            parallel=True,
        )(node=nodes[1], table_name=table_name)

        join()

        with Then("I wait for the second node to sync by watching the row count"):
            retry(assert_row_count, timeout=120, delay=1)(
                node=nodes[1], table_name=table_name, rows=rows_per_insert
            )

        And(
            "I start parallel inserts on the second node",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[1],
            table_name=table_name,
            rows=rows_per_insert,
        )
        insert_sets += 1
        nodes[1].query(f"SELECT count() from {table_name}")

        And(
            "I delete the replica on the first node",
            test=delete_one_replica,
            parallel=True,
        )(node=nodes[0], table_name=table_name)

        And(
            "I replicate the table on the third node in parallel",
            test=create_one_replica,
            parallel=True,
        )(node=nodes[2], table_name=table_name)

        And(
            "I continue with parallel inserts on the second node",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[1],
            table_name=table_name,
            rows=rows_per_insert,
        )
        insert_sets += 1
        nodes[1].query(f"SELECT count() from {table_name}")

        join()

        with And("I wait for the third node to sync by watching the row count"):
            retry(assert_row_count, timeout=120, delay=1)(
                node=nodes[2], table_name=table_name, rows=rows_per_insert * insert_sets
            )

        with Then("I also check the row count on the second node"):
            assert_row_count(
                node=nodes[1], table_name=table_name, rows=rows_per_insert * insert_sets
            )

        Given(
            "I start parallel inserts on the second node in parallel",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[1],
            table_name=table_name,
            rows=rows_per_insert,
        )
        insert_sets += 1
        nodes[1].query(f"SELECT count() from {table_name}")

        And(
            "I start parallel inserts on the third node in parallel",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[2],
            table_name=table_name,
            rows=rows_per_insert,
        )
        insert_sets += 1
        nodes[2].query(f"SELECT count() from {table_name}")

        And(
            "I replicate the table on the first node again in parallel",
            test=create_one_replica,
            parallel=True,
        )(node=nodes[0], table_name=table_name)

        join()

        with Then("I wait for the first node to sync by watching the row count"):
            retry(assert_row_count, timeout=120, delay=1)(
                node=nodes[0], table_name=table_name, rows=rows_per_insert * insert_sets
            )

        with And("I check the row count on the other nodes"):
            assert_row_count(
                node=nodes[1], table_name=table_name, rows=rows_per_insert * insert_sets
            )
            assert_row_count(
                node=nodes[2], table_name=table_name, rows=rows_per_insert * insert_sets
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas("1.0"))
@Name("replica sanity")
def feature(self):
    """Test that replicas can be added and removed without errors or duplicate data."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    Scenario(run=parallel_add_remove_sanity)
