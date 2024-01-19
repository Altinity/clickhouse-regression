from testflows.core import *
from alter.table.attach_partition.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


def get_node(self, table):
    if table == "source":
        if "Replicated" in self.context.source_engine:
            return random.choice(
                [self.context.node_1, self.context.node_2, self.context.node_3]
            )
        else:
            return self.context.node_1
    elif table == "destination":
        if "Replicated" in self.context.destination_engine:
            return random.choice(
                [self.context.node_1, self.context.node_2, self.context.node_3]
            )
        else:
            return self.context.node_1


@TestScenario
@Flags(TE)
def check_attach_partition_from(
    self,
    source_partition_key,
    destination_partition_key,
    source_table_engine="MergeTree",
    destination_table_engine="MergeTree",
):
    self.context.source_engine = source_table_engine
    self.context.destination_engine = destination_table_engine

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()

    with Given(
        "I create two tables with specified engines and partition keys",
    ):

        create_partitioned_table_with_data(
            table_name=source_table_name,
            engine=source_table_engine,
            partition_by=source_partition_key,
            node=get_node(self, "source"),
        )

        if "Replicated" in destination_table_engine:
            create_empty_partitioned_replicated_table(
                table_name=destination_table_name,
                engine=destination_table_engine,
                partition_by=destination_partition_key,
                node=get_node(self, "destination"),
            )
        else:
            create_empty_partitioned_table(
                table_name=destination_table_name,
                engine=destination_table_engine,
                partition_by=destination_partition_key,
                node=get_node(self, "destination"),
            )

    with And("I attach partition from source table to the destination table"):
        partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id"
        partition_ids = sorted(
            list(
                set(get_node(self, "source").query(partition_list_query).output.split())
            )
        )
        note(partition_ids)

        for partition_id in partition_ids:
            get_node(self, "destination").query(
                f"SELECT * FROM '{destination_table_name}' format PrettyCompactMonoBlock"
            )
            get_node(self, "destination").query(
                f"SELECT partition, partition_id, part_type, part_name, table FROM system.parts WHERE table='{destination_table_name}' ORDER BY partition_id format PrettyCompactMonoBlock"
            )
            get_node(self, "source").query(
                f"SELECT partition, partition_id, part_type, part_name, table FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id format PrettyCompactMonoBlock"
            )
            query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
            self.context.node_1.query(query)

    with Then(
        f"I check that partitions were attached when source table partition_id - {source_partition_key}, destination table partition key - {destination_partition_key}, source table engine - {source_table_engine}, destination table engine - {destination_table_engine}:"
    ):

        source_partition_data = (
            get_node(self, "source")
            .query(f"SELECT * FROM {source_table_name} ORDER BY a,b,c")
            .output
        )
        destination_partition_data = (
            get_node(self, "destination")
            .query(f"SELECT * FROM {destination_table_name} ORDER BY a,b,c")
            .output
        )
        assert source_partition_data == destination_partition_data


@TestFeature
@Name("simple test")
def feature(self):
    """Check conditions for partition key."""
    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    pause()

    Scenario("attach partition from without id", test=check_attach_partition_from,)(
        source_table_engine="MergeTree",
        destination_table_engine="ReplicatedMergeTree",
        source_partition_key="a",
        destination_partition_key="tuple()",
    )


"""
create table source (a UInt16, b UInt16, c UInt16) engine=MergeTree partition by a order by tuple()
insert into source (a,b,c) select 1,2,2 from numbers(5)
insert into source (a,b,c) select 2,3,3 from numbers(5)


CREATE TABLE IF NOT EXISTS destination ON CLUSTER replicated_cluster_secure (a UInt16,b UInt16,c UInt16) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/destination', '{replica}') ORDER BY tuple()

alter table destination attach partition 1 from source
"""
