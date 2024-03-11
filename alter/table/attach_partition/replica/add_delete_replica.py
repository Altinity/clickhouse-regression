from functools import partial
import time
import threading


from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.replica.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


@TestScenario
def add_remove_replicas(self, source_table_name, active_replicas, num_iterations=100):
    """Perform create replica and remove replica on three nodes in parallel."""
    operations = [
        add_remove_replica_on_first_node,
        add_remove_replica_on_second_node,
        add_remove_replica_on_third_node,
    ]
    with Pool(5) as executor:
        for _ in range(num_iterations):
            operation = random.choice(operations)
            Step(test=operation, parallel=True, executor=executor)(
                table_name=source_table_name, active_replicas=active_replicas
            )
        join()


@TestStep
def attach_partition(
    self,
    source_table_name,
    destination_table_name,
    source_data,
    num_iterations=100,
):
    """Try to attach partition on random node."""
    for _ in range(num_iterations):
        with Given("I choose random node to perform attach"):
            node = random.choice(self.context.nodes)

        with And("I attach partition on chosen node"):
            attached = attach_partition_from_on_node(
                source_table_name=source_table_name,
                destination_table_name=destination_table_name,
                node=node,
            )

        with Then("I check that partitions were attached to the destination table"):
            if attached:
                check_partition_was_attached(
                    table_name=destination_table_name, expected=source_data
                )

        with And("I detach partition from the table"):
            detach_partition_on_node(
                table_name=destination_table_name,
                node=node,
            )


@TestScenario
@Flags(TE)
def replica(self):
    """
    Performed operations:
    1. Add source table replica
    2. Remove source table replica
    3. Attach partition from source table to destination table on active replica

    At least one replica is always active.
    """

    self.context.active_replicas = []

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()
    source_table_engines = ["ReplicatedMergeTree"]
    destination_table_engines = ["ReplicatedMergeTree"]

    with Given("I create table to which partitions will be attached"):
        for node in self.context.nodes:
            create_one_replica(table_name=destination_table_name, node=node)

    with And("I create source table on the first node and insert data"):
        create_one_replica(table_name=source_table_name, node=self.context.node_1)
        insert_random(table_name=source_table_name, node=self.context.node_1)
        self.context.active_replicas.append(0)

    with And(
        "I save the state of source table to later compare it with the destination table"
    ):
        source_data = self.context.node_1.query(
            f"SELECT * FROM {source_table_name} ORDER BY a,b,c,extra"
        ).output

    with And("I start parallel add/remove replica and attach partition"):
        with Pool(2) as executor:
            Scenario(test=attach_partition, parallel=True, executor=executor,)(
                source_table_name=source_table_name,
                destination_table_name=destination_table_name,
                source_data=source_data,
                num_iterations=300,
            )
            Scenario(test=add_remove_replicas, parallel=True, executor=executor,)(
                source_table_name=source_table_name,
                active_replicas=self.context.active_replicas,
                num_iterations=300,
            )
            join()


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas("1.0"))
@Name("add_remove_replica")
def feature(self):
    """Test that `attach partition from` can be performed correctly while adding and
    removing replicas of source table."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.node_1,
        self.context.node_2,
        self.context.node_3,
    ]
    self.context.replica_operation_lock = threading.Lock()

    Scenario(run=replica)
