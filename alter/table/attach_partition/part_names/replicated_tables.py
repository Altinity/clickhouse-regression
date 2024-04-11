import random

from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid


max_range = 10_000_000


@TestStep
def insert_random_number_of_rows(self, destination_table, node=None, **kwargs):
    """Insert a random number of rows into a table on a random node."""
    node = random.choice(self.context.nodes) if node is None else node
    number_of_rows = random.randint(1, max_range)
    node.query(
        f"INSERT INTO {destination_table} (id, a) SELECT number, number FROM numbers({number_of_rows})"
    )


@TestStep
def attach_random_partition(self, source_table, destination_table, node=None):
    """Attach a random partition from a source table to a destination table on a random node."""
    node = random.choice(self.context.nodes) if node is None else node
    partition = random.choice(range(20))
    node.query(
        f"ALTER TABLE {destination_table} ATTACH PARTITION {partition} FROM {source_table}"
    )


@TestStep
def update_table_on_random_node(
    self, destination_table, update_column="a", node=None, **kwargs
):
    """Update a table on a random node."""
    node = random.choice(self.context.nodes) if node is None else node
    update_table(table_name=destination_table, update_column=update_column, node=node)


@TestStep
def optimize_table_on_random_node(self, destination_table, node=None, **kwargs):
    """Optimize a table on a random node."""
    node = random.choice(self.context.nodes) if node is None else node
    optimize_table(table_name=destination_table, node=node)


@TestStep
def attach_detach_partition(self, destination_table, node=None, **kwargs):
    """Attach and detach a random partition on a random node."""
    node = random.choice(self.context.nodes) if node is None else node
    partition = random.choice(range(20))
    detach_partition(table_name=destination_table, partition=partition, node=node)
    attach_partition(table_name=destination_table, partition=partition, node=node)


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartNames_Replication("1.0")
)
def replicated_tables(self):
    """Check that parts in different replicas are the same when replication queue is empty."""
    node = self.context.node

    source_table = "source_" + getuid()
    destination_table = "destination_" + getuid()

    with Given("I create a source table on cluster with data"):
        create_table_on_cluster_with_data(
            table_name=source_table,
            cluster="replicated_cluster_secure",
            order_by="id",
            partition_by="id%20",
            number_of_rows=10_000_000,
        )

    with And("I create an empty destination table on cluster"):
        create_table_on_cluster_with_data(
            table_name=destination_table,
            cluster="replicated_cluster_secure",
            order_by="id",
            partition_by="id%20",
            number_of_rows=0,
        )

    with And("I perform various operations on the destination table"):
        operations = [
            insert_random_number_of_rows,
            attach_random_partition,
            update_table_on_random_node,
            optimize_table_on_random_node,
            attach_detach_partition,
        ]
        with Pool(1) as executor:
            for _ in range(100):
                operation = random.choice(operations)
                Step(test=operation, parallel=True, executor=executor)(
                    source_table=source_table, destination_table=destination_table
                )
            join()

    with And("I check that all mutations are done and replication queue is empty"):
        for node in self.context.nodes:
            optimize_table(table_name=destination_table, node=node)

        for attempt in retries(timeout=60 * 15, delay=10):
            with attempt:
                for node in self.context.nodes:
                    assert is_all_mutations_applied(
                        node=node, table_name=destination_table
                    ), error()
                    assert is_replication_queue_empty(
                        node=node, table_name=destination_table
                    ), error()

    with Then("I check that part names are the same on all replicas"):
        for attempt in retries(timeout=60, delay=2):
            with attempt:
                assert (
                    select_active_parts(
                        node=self.context.node_1, table_name=destination_table
                    )
                    == select_active_parts(
                        node=self.context.node_2, table_name=destination_table
                    )
                    == select_active_parts(
                        node=self.context.node_3, table_name=destination_table
                    )
                ), error()
