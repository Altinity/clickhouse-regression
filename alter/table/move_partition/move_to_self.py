import os
from testflows.core import *
from testflows.combinatorics import product, CoveringArray

from alter.table.attach_partition.common import *
from alter.table.move_partition.common import execute_query
from alter.table.move_partition.requirements.requirements import *
from alter.table.attach_partition.partition_key import valid_partition_key_pair

from helpers.common import (
    getuid,
)
from helpers.tables import *


def get_node(self, table):
    """Returns first node for non-replicated tables and returns random node for replicated tables."""
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


def check(
    self,
    partition_ids,
    source_table_name,
    destination_table_name,
    exitcode=None,
    message=None,
):
    """Check `move partition` statement."""
    for partition_id in partition_ids:
        query = f"ALTER TABLE {source_table_name} MOVE PARTITION {partition_id} TO TABLE {destination_table_name}"

        self.context.node_1.query(
            query,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Flags(TE)
def check_move_partition(
    self,
    source_partition_key,
    source_table,
):
    """Check `move partition to table` where source and destination tables are the same."""

    self.context.source_engine = source_table.__name__.split("_")[-1]
    self.context.destination_engine = self.context.source_engine

    source_is_replicated = "Replicated" in self.context.source_engine
    destination_is_replicated = "Replicated" in self.context.destination_engine
    if source_is_replicated != destination_is_replicated:
        skip(
            "Source and destination table engines both must be either replicated or non-replicated"
        )

    source_table_name = "source_" + getuid()
    destination_table_name = source_table_name

    with Given(
        "I create two tables with specified engines and partition keys",
        description=f"""
            partition keys:
            source table partition key: {source_partition_key}
            engines:
            source table engine: {self.context.source_engine}
            """,
    ):
        source_table(
            table_name=source_table_name,
            partition_by=source_partition_key,
            node=self.context.node_1,
        )

    if check_clickhouse_version(
        f">={version_when_attach_partition_with_different_keys_merged}"
    )(self):
        with And(
            "I add setting to allow alter partition with different partition keys"
        ):
            if "Replicated" in self.context.destination_engine:
                for node in self.context.nodes:
                    node.query(
                        f"ALTER TABLE {destination_table_name} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
                    )
            else:
                get_node(self, "destination").query(
                    f"ALTER TABLE {destination_table_name} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
                )

    with And("I get the list of partitions and validate partition keys pair"):
        partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id FORMAT TabSeparated"

        partition_ids = sorted(
            list(
                set(get_node(self, "source").query(partition_list_query).output.split())
            )
        )

    with And("I save the state of source table before moving"):
        source_before = (
            get_node(self, "source")
            .query(
                f"SELECT * FROM {source_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            .output
        )

    with And("I move partition from source table to the destination table"):

        for partition_id in partition_ids:
            query = f"ALTER TABLE {source_table_name} MOVE PARTITION {partition_id} TO TABLE {destination_table_name}"
            self.context.node_1.query(query)
            self.context.node_1.query(
                f"SELECT * FROM {destination_table_name} format PrettyCompactMonoBlock"
            )

    with And(
        "I change engine names to compare replicated results with non-replicated results in snapshots"
    ):
        if "Replicated" in self.context.source_engine:
            source_engine = self.context.source_engine.replace("Replicated", "")
        else:
            source_engine = self.context.source_engine
        if "Replicated" in self.context.destination_engine:
            destination_engine = self.context.destination_engine.replace(
                "Replicated", ""
            )
        else:
            destination_engine = self.context.destination_engine

    with Then(
        f"I check that partitions were moved when source table partition_id - {source_partition_key}, source table engine - {source_engine}, destination table engine - {destination_engine}:"
    ):
        destination_partition_data = get_node(self, "destination").query(
            f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert destination_partition_data.output == source_before, error()

    with And(f"I check that all replicas of destination table have same data:"):
        if "Replicated" in self.context.destination_engine:
            destination_partition_data_1 = self.context.node_1.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            destination_partition_data_2 = self.context.node_2.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            destination_partition_data_3 = self.context.node_3.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert (
                        destination_partition_data_1.output
                        == destination_partition_data_2.output
                        == destination_partition_data_3.output
                    )

    with And(
        "I check that I can use data in the destination table after detach attach"
    ):
        data_before = self.context.node_1.query(
            f"SELECT * FROM {destination_table_name} WHERE a > 1 ORDER BY a,b,c,extra FORMAT TabSeparated"
        ).output
        self.context.node_1.query(f"DETACH TABLE {destination_table_name}")
        self.context.node_1.query(f"ATTACH TABLE {destination_table_name}")
        data_after = self.context.node_1.query(
            f"SELECT * FROM {destination_table_name} WHERE a > 1 ORDER BY a,b,c,extra FORMAT TabSeparated"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert data_after.output == data_before, error()


@TestScenario
@Flags(TE)
def move_partition(self):
    """Run test check what happens when source and destination
    tables are the same"""

    source_partition_keys = {
        "tuple()",
    }

    source_table_types = {
        partitioned_MergeTree,
        partitioned_small_MergeTree,
        partitioned_ReplicatedMergeTree,
        partitioned_small_ReplicatedMergeTree,
        partitioned_ReplacingMergeTree,
        partitioned_ReplicatedReplacingMergeTree,
        partitioned_AggregatingMergeTree,
        partitioned_ReplicatedAggregatingMergeTree,
        partitioned_SummingMergeTree,
        partitioned_ReplicatedSummingMergeTree,
        partitioned_CollapsingMergeTree,
        partitioned_ReplicatedCollapsingMergeTree,
        partitioned_VersionedCollapsingMergeTree,
        partitioned_ReplicatedVersionedCollapsingMergeTree,
        partitioned_GraphiteMergeTree,
        partitioned_ReplicatedGraphiteMergeTree,
    }

    if not self.context.stress:
        source_table_types = {
            partitioned_MergeTree,
            partitioned_small_MergeTree,
            partitioned_ReplicatedMergeTree,
            partitioned_small_ReplicatedMergeTree,
        }
        combinations = product(source_partition_keys, source_table_types)
    else:
        combinations_dict = {
            "source_table": source_table_types,
            "source_key": source_partition_keys,
        }
        covering_array = CoveringArray(combinations_dict, strength=3)
        combinations = [
            (
                item["source_key"],
                item["source_table"],
            )
            for item in covering_array
        ]

    with Pool(10) as executor:
        for partition_key, table in combinations:
            source_partition_key = destination_partition_key = partition_key
            source_table = destination_table = table

            source_partition_key_str = clean_name(source_partition_key)
            destination_partition_key_str = clean_name(destination_partition_key)

            Scenario(
                f"combination partition keys  {source_partition_key_str} {destination_partition_key_str}  tables  {source_table.__name__} {destination_table.__name__}",
                test=check_move_partition,
                parallel=False,
                executor=executor,
            )(
                source_table=source_table,
                source_partition_key=source_partition_key,
            )
        join()


@TestFeature
@Requirements(
    RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Key_PartitionKey("1.0"),
)
@Name("move to self")
def feature(self):
    """Check conditions using `move partition` statement on the same table."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    Scenario(
        "move partition",
        run=move_partition,
    )
