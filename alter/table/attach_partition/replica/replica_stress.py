from functools import partial

from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.replica.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


@TestCheck
def execute_operation(self, operation, source_table_name, destination_table_name):
    with Given(f"I execute a step: {operation.func.__name__}"):
        operation()


@TestScenario
@Flags(TE)
def dynamically_add_remove_replica(self):
    """
    Operations:
    Add replica
    Remove replica
    Insert data to random replica
    Attach partition from on random replica
    """
    self.context.num_inserted_rows = 0
    self.context.total_attached_rows = 0
    self.context.active_replicas = []

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()

    table_engines = ["ReplicatedMergeTree"]
    operations = [
        partial(
            create_replica_on_first_node,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
        ),
        partial(
            create_replica_on_second_node,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
        ),
        partial(
            create_replica_on_third_node,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
        ),
        partial(
            delete_replica_on_first_node,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
        ),
        partial(
            delete_replica_on_second_node,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
        ),
        partial(
            delete_replica_on_third_node,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
        ),
        partial(
            insert_to_random_replica,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
            nodes=self.context.nodes,
        ),
        partial(
            insert_to_random_replica,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
            nodes=self.context.nodes,
        ),
        partial(
            insert_to_random_replica,
            table_name=source_table_name,
            active_replicas=self.context.active_replicas,
            nodes=self.context.nodes,
        ),
        partial(
            attach_partition_from,
            source_table_name=source_table_name,
            destination_table_name=destination_table_name,
        ),
    ]

    with Given("I create table to which partitions will be attached"):
        for node in self.context.nodes:
            create_one_replica(table_name=destination_table_name, node=node)

    with And("I perform differen operations"):
        with Pool(1) as executor:
            for num in range(1000):
                operation = random.choice(operations)
                Check(
                    name=f"#{num}",
                    test=execute_operation,
                    parallel=True,
                    executor=executor,
                )(
                    operation=operation,
                    source_table_name=source_table_name,
                    destination_table_name=destination_table_name,
                )
            join()

    with Then("I check that all active nodes have same data"):
        source_data = None
        for i in self.context.active_replicas:
            node = self.context.nodes[i]
            if source_data is None:
                source_data = node.query(
                    f"SELECT * FROM {source_table_name} ORDER BY a,b,c,extra"
                )
            else:
                current_data = node.query(
                    f"SELECT * FROM {source_table_name} ORDER BY a,b,c,extra"
                )
                for attempt in retries(timeout=30, delay=2):
                    with attempt:
                        assert source_data.output == current_data.output, error()

    with Then("I check that all data was inserted"):
        if len(self.context.active_replicas) > 0:
            node_num = random.choice(self.context.active_replicas)
            node = self.context.nodes[node_num]
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert_row_count(
                        table_name=source_table_name,
                        rows=self.context.num_inserted_rows,
                        node=node,
                    )

    with Then("I check that partitions were attached to the destination table"):
        destination_data = None
        for node in self.context.nodes:
            if destination_data is None:
                destination_data = node.query(
                    f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra"
                )
            else:
                current_data = node.query(
                    f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra"
                )
                for attempt in retries(timeout=30, delay=2):
                    with attempt:
                        assert current_data.output == destination_data.output

    with Finally("clean up"):
        for node in self.context.nodes:
            node.query(f"DROP TABLE IF EXISTS {source_table_name} SYNC")
            node.query(f"DROP TABLE IF EXISTS {destination_table_name} SYNC")


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas("1.0"))
@Name("replica stress")
def feature(self):
    """Test that replicas can be added and removed without errors or duplicate data."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.node_1,
        self.context.node_2,
        self.context.node_3,
    ]

    Scenario(test=dynamically_add_remove_replica)()
