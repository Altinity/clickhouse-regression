from functools import partial

from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.replica.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


@TestScenario
def add_remove_replicas(self, source_table_name, active_replicas):
    """Perform either create new replica or remove old replica."""
    operations = [
        partial(
            create_replica_on_first_node,
            table_name=source_table_name,
            active_replicas=active_replicas,
        ),
        partial(
            create_replica_on_second_node,
            table_name=source_table_name,
            active_replicas=active_replicas,
        ),
        partial(
            create_replica_on_third_node,
            table_name=source_table_name,
            active_replicas=active_replicas,
        ),
        partial(
            delete_replica_on_first_node,
            table_name=source_table_name,
            active_replicas=active_replicas,
            keep_one_replica=True,
        ),
        partial(
            delete_replica_on_second_node,
            table_name=source_table_name,
            active_replicas=active_replicas,
            keep_one_replica=True,
        ),
        partial(
            delete_replica_on_third_node,
            table_name=source_table_name,
            active_replicas=active_replicas,
            keep_one_replica=True,
        ),
    ]

    num_iterations = 200
    for _ in range(num_iterations):
        operation = random.choice(operations)
        operation()


@TestScenario
def attach_partition(self, source_table_name, destination_table_name):
    """Try to attach partition on all nodes. For sure there is at least one active node."""
    nodes = self.context.nodes

    for _ in range(10):
        with Pool(3) as executor:
            Step(test=attach_partition_from_on_node, parallel=True, executor=executor)(
                source_table_name=source_table_name,
                destination_table_name=destination_table_name,
                node=nodes[0],
            )
            Step(test=attach_partition_from_on_node, parallel=True, executor=executor)(
                source_table_name=source_table_name,
                destination_table_name=destination_table_name,
                node=nodes[1],
            )
            Step(test=attach_partition_from_on_node, parallel=True, executor=executor)(
                source_table_name=source_table_name,
                destination_table_name=destination_table_name,
                node=nodes[2],
            )
            join()


@TestScenario
@Flags(TE)
def replica(self):
    """
    Operations:
    Add source table replica
    Remove source table replica
    Attach partition from source table to destination table on active replica

    At least one replica is always active.
    """

    self.context.active_replicas = []
    self.context.num_inserted_rows = 0
    self.context.total_attached_rows = 0

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()
    source_table_engines = ["ReplicatedMergeTree"]
    destination_table_engines = ["ReplicatedMergeTree"]

    with Given("I create table to which partitions will be attached"):
        for node in self.context.nodes:
            create_one_replica(table_name=destination_table_name, node=node)

    with Given("I create source table on the first node and insert data"):
        create_one_replica(table_name=source_table_name, node=self.context.node_1)
        insert_random(table_name=source_table_name, node=self.context.node_1)
        self.context.active_replicas.append(0)

    with Pool(2) as executor:
        Scenario(test=attach_partition, parallel=True, executor=executor,)(
            source_table_name=source_table_name,
            destination_table_name=destination_table_name,
        )
        Scenario(test=add_remove_replicas, parallel=True, executor=executor,)(
            source_table_name=source_table_name,
            active_replicas=self.context.active_replicas,
        )
        join()

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

        note(self.context.total_attached_rows)


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas("1.0"))
@Name("replica")
def feature(self):
    """Test that attach partition from can be performed correctly while adding and
    removing replicas of source table."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.node_1,
        self.context.node_2,
        self.context.node_3,
    ]

    Scenario(run=replica)
