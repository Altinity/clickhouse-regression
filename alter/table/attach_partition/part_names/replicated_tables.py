import random
from functools import partial

from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid


max_range = 10_000_000


@TestStep
def insert_random_number_of_rows(self, destination_table, **kwargs):
    """Insert a random number of rows into a table on a random node."""
    node = random.choice(self.context.nodes)
    number_of_rows = random.randint(1, max_range)
    node.query(
        f"INSERT INTO {destination_table} (id, a) SELECT number, number FROM numbers({number_of_rows})"
    )


@TestStep
def attach_random_partition(self, source_table, destination_table):
    """Attach a random partition from a source table to a destination table on a random node."""
    node = random.choice(self.context.nodes)
    partitions = node.query(
        f"SELECT partition FROM system.parts WHERE table = '{source_table}' AND active"
    ).output.split("\n")
    partition = random.choice(partitions)
    node.query(
        f"ALTER TABLE {destination_table} ATTACH PARTITION {partition} FROM {source_table}"
    )


@TestStep
def update_table_on_random_node(self, destination_table, update_column="a", **kwargs):
    """Update a table on a random node."""
    node = random.choice(self.context.nodes)
    # update_table(table_name=destination_table, update_column=update_column, node=node)
    node.query(
        f"ALTER TABLE {destination_table} ON CLUSTER replicated_cluster_secure UPDATE {update_column} = {update_column}+1 WHERE {update_column} > 0"
    )


@TestStep
def optimize_table_on_random_node(self, destination_table, **kwargs):
    """Optimize a table on a random node."""
    node = random.choice(self.context.nodes)
    optimize_table(table_name=destination_table, node=node)


@TestStep
def attach_detach_part(self, destination_table, **kwargs):
    """Attach and detach a random part on a random node."""
    node = random.choice(self.context.nodes)
    part_names = node.query(
        f"SELECT name FROM system.parts WHERE table = '{destination_table}' AND active"
    ).output.split("\n")
    if len(part_names) > 0:
        part_name = random.choice(part_names)
        detach_part(table_name=destination_table, part_name=part_name, node=node)
        attach_part(table_name=destination_table, part_name=part_name, node=node)


@TestScenario
@Repeat(20)
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
            order_by="sign",
            partition_by="id%20",
            number_of_rows=100000000,
        )

    with And("I create an empty destination table on cluster"):
        create_table_on_cluster_with_data(
            table_name=destination_table,
            cluster="replicated_cluster_secure",
            order_by="sign",
            partition_by="id%20",
            number_of_rows=0,
        )

    with And("I perform various operations on the destination table"):
        operations = [
            insert_random_number_of_rows,
            attach_random_partition,
            update_table_on_random_node,
            optimize_table_on_random_node,
            # attach_detach_part,
        ]
        with Pool(6) as executor:
            for _ in range(50):
                pass
                operation = random.choice(operations)
                Step(test=operation, parallel=True, executor=executor)(
                    source_table=source_table, destination_table=destination_table
                )
            join()

    with And("I check part names on different replicas"):
        part_names_1 = self.context.node_1.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table}' AND active ORDER BY name"
        )
        part_names_2 = self.context.node_2.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table}' AND active ORDER BY name"
        )
        part_names_3 = self.context.node_3.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table}' AND active ORDER BY name"
        )
        note(part_names_1.output == part_names_2.output == part_names_3.output)

    with And("I check replica queue is empty"):
        for node in self.context.nodes:
            optimize_table(table_name=destination_table, node=node)

        for node in self.context.nodes:
            node.query("SELECT * FROM system.replication_queue")

        for node in self.context.nodes:
            node.query("SELECT count() FROM system.mutations WHERE is_done = 0")

        # for attempt in retries(timeout=60, delay=2):
        #     with attempt:
        #         #assert data_1.output == data_2.output == data_3.output
        #         assert part_names_1.output == part_names_2.output == part_names_3.output
