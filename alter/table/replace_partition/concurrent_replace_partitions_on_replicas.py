import random

from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    replace_partition_and_validate_data,
)
from alter.table.replace_partition.requirements.requirements import *
from helpers.alter import *
from helpers.common import getuid, replace_partition
from helpers.tables import create_table_partitioned_by_column


@TestStep(Given)
def create_table_on_cluster(self, table_name, cluster=None):
    """Create table on a cluster"""

    if cluster is None:
        cluster = "sharded_cluster"

    node = self.context.node_1

    with By("creating a MergeTree table on a replicated_different_versions cluster"):
        node.query(
            f"CREATE TABLE {table_name} ON CLUSTER {cluster} (p Int16, i UInt64) "
            f"ENGINE=ReplicatedMergeTree('/clickhouse/tables/{{shard}}/default/{table_name}', '{{replica}}') ORDER BY "
            f"tuple() PARTITION BY p"
        )


@TestStep(Given)
def create_partitions_with_random_parts(self, table_name, number_of_partitions):
    """Create a number of partitions inside the table with random number of parts."""
    node = self.context.node_1

    with By(
        f"Inserting data into a {table_name} table",
        description="each insert creates a new part inside a partiion resulting in a partition with a set numebr of parts",
    ):
        for partition in range(1, number_of_partitions):
            number_of_parts = random.randrange(1, 50)
            with By(
                f"creating {number_of_parts} parts inside the {partition} partition"
            ):
                for parts in range(1, number_of_parts):
                    node.query(
                        f"INSERT INTO {table_name} (p, i) SELECT {partition}, rand64() FROM numbers(10)"
                    )


@TestStep(Given)
def destination_table_with_partitions(
    self, table_name, number_of_partitions, cluster=None
):
    """Create a destination table with set number of partitions and parts."""
    with By(f"creating a {table_name} table with {number_of_partitions} partitions"):
        create_table_on_cluster(table_name=table_name, cluster=cluster)
        create_partitions_with_random_parts(
            table_name=table_name, number_of_partitions=number_of_partitions
        )


@TestStep(Given)
def source_table_with_partitions(self, table_name, number_of_partitions, cluster=None):
    """Create a source table with set number of partitions and parts."""

    with By(f"creating a {table_name} table with {number_of_partitions} partitions"):
        create_table_on_cluster(table_name=table_name, cluster=cluster)
        create_partitions_with_random_parts(
            table_name=table_name, number_of_partitions=number_of_partitions
        )


@TestStep(Given)
def create_two_tables(
    self,
    destination_table=None,
    source_table=None,
    number_of_partitions=None,
    cluster=None,
):
    """Create two tables with the same structure having the specified number of partitions.
    The destination table will be used as the table where replace partition command will be
    replacing the partition and the source table will be used as the table from which partitions will be taken.
    """
    if destination_table is None:
        destination_table = self.context.destination_table

    if source_table is None:
        source_table = self.context.source_table

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    with By("creating destination table"):
        destination_table_with_partitions(
            table_name=destination_table,
            number_of_partitions=number_of_partitions,
            cluster=cluster,
        )

    with And("creating source table"):
        source_table_with_partitions(
            table_name=source_table,
            number_of_partitions=number_of_partitions,
            cluster=cluster,
        )


@TestOutline
def concurrent_replace_on_three_replicas(
    self,
    cluster=None,
    number_of_partitions=None,
    number_of_concurrent_queries=None,
    destination_table=None,
    source_table=None,
    delay_before=None,
    delay_after=None,
):
    """Concurrently run multiple replace partitions on the destination table and
    validate that the data on both destination and source tables is the same."""
    validate = self.context.validate
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    node_1 = self.context.node_1
    node_2 = self.context.node_2
    node_3 = self.context.node_3

    list_of_nodes = [node_1, node_2, node_3]

    if delay_before is None:
        delay_before = self.context.delay_before

    if delay_after is None:
        delay_after = self.context.delay_after

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if number_of_concurrent_queries is None:
        number_of_concurrent_queries = self.context.number_of_concurrent_queries

    if destination_table is None:
        destination_table = self.context.destination_table

    if source_table is None:
        source_table = self.context.source_table

    list_of_partitions_replaced = []

    with Given(
        "I create destination and source tables for the replace partition command"
    ):
        create_two_tables(
            destination_table=destination_table,
            source_table=source_table,
            cluster=cluster,
        )

    for i in range(number_of_concurrent_queries):
        partition_to_replace = random.sample(range(1, number_of_partitions), 3)

        list_of_partitions_replaced.append(partition_to_replace)

        Check(
            name=f"replace partition #{i} partition {partition_to_replace[0]}",
            test=replace_partition,
            parallel=True,
        )(
            node=random.choice(list_of_nodes),
            destination_table=destination_table,
            source_table=source_table,
            partition=partition_to_replace[0],
        )
        Check(
            name=f"replace partition #{i} partition {partition_to_replace[1]}",
            test=replace_partition,
            parallel=True,
        )(
            node=random.choice(list_of_nodes),
            destination_table=destination_table,
            source_table=source_table,
            partition=partition_to_replace[1],
        )
        Check(
            name=f"replace partition #{i} partition {partition_to_replace[2]}",
            test=replace_partition,
            parallel=True,
        )(
            node=random.choice(list_of_nodes),
            destination_table=destination_table,
            source_table=source_table,
            partition=partition_to_replace[2],
        )
    join()
    if not validate:
        with Then("checking that the partition was replaced on the destination table"):
            for i in list_of_partitions_replaced:
                check_partition_was_replaced(
                    destination_table=destination_table,
                    source_table=source_table,
                    partition=i,
                )


@TestScenario
def single_shard_three_replicas(self):
    """Concurrently run replace partition on different replicas of a cluster with a single shard and three replicas."""
    concurrent_replace_on_three_replicas(cluster="replicated_cluster")


@TestScenario
def single_shard_three_replicas_secure(self):
    """Concurrently run replace partition on different replicas of a secured cluster with a single shard and three replicas."""
    concurrent_replace_on_three_replicas(cluster="replicated_cluster_secure")


@TestScenario
def multiple_shards_with_replicas(self):
    """Concurrently run replace partition on a cluster with multiple shards."""
    concurrent_replace_on_three_replicas(cluster="sharded_cluster")


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace(
        "1.0"
    )
)
@Name("concurrent replace partitions on replicas")
def feature(
    self,
    node="clickhouse1",
    number_of_partitions=100,
    number_of_concurrent_queries=100,
    delay_before=None,
    delay_after=None,
    validate=True,
):
    """
    On a cluster we create destination and source tables and populate them with set
    number of partitions. On each replica we concurrently execute replace partition on randomly picked partitions.
    At the end we validate that the data on the destination table partition is the same as the source table.
    """
    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.delay_before = delay_before
    self.context.delay_after = delay_after
    self.context.number_of_partitions = number_of_partitions
    self.context.number_of_concurrent_queries = number_of_concurrent_queries
    self.context.validate = validate

    for scenario in loads(current_module(), Scenario):
        scenario()
