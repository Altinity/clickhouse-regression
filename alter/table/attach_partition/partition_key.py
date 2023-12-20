from testflows.core import *

from alter.table.attach_partition.common import insert_data, insert_date_data
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


@TestScenario
@Flags(TE)
def attach_partition_from_partitioned_to_unpartitioned(
    self, source_table_engine="MergeTree", destination_table_engine="MergeTree"
):
    """Check `attach partition from` from partitioned table to unpartitioned table."""
    node = self.context.node

    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given(
        "I create two tables: partitioned and unpartitioned",
        description=f"""
               engines:
               destination table: {destination_table_engine}
               source table: {source_table_engine}
               """,
    ):
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="i", datatype=UInt64()),
        ]
        create_table(
            name=destination_table_name,
            engine=destination_table_engine,
            order_by="tuple()",
            columns=columns,
            if_not_exists=True,
        )
        create_table_partitioned_by_columns(
            table_name=source_table_name, partition_by="a", engine=source_table_engine
        )

    with And(
        f"I insert data into tables that will create different partitions for tables"
    ):
        insert_data(node=node, table_name=source_table_name, number_of_values=10)
        insert_data(
            node=node, table_name=destination_table_name, number_of_values=10, bias=4
        )

    with And("I attach partition from source table into destination table"):
        partition = "1"
        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition}' FROM {source_table_name}"
        node.query(query)

    with Then("I check that specidied partition was attached"):
        source_partition_data = node.query(
            f"SELECT * from {source_table_name} where a = 1 order by a,b"
        ).output
        destination_partition_data = node.query(
            f"SELECT * from {destination_table_name} where a = 1 order by a,b"
        ).output
        assert source_partition_data == destination_partition_data


@TestScenario
@Flags(TE)
def attach_partition_from_subset(
    self, source_table_engine="MergeTree", destination_table_engine="MergeTree"
):
    """Check `attach partition from` when destination partition expression is a subset of the source partition expressions."""
    node = self.context.node

    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given(
        "I create two tables that have different partition keys",
        description=f"""
               engines:
               destination table: {destination_table_engine}
               source table: {source_table_engine}
               """,
    ):
        create_table_partitioned_by_columns(
            table_name=source_table_name,
            partition_by="(a,b)",
            engine=source_table_engine,
        )
        create_table_partitioned_by_columns(
            table_name=destination_table_name,
            partition_by="a",
            engine=destination_table_engine,
        )

    with And(
        f"I insert data into tables that will create different partitions for tables"
    ):
        insert_data(node=node, table_name=source_table_name, number_of_values=10)
        insert_data(
            node=node, table_name=destination_table_name, number_of_values=10, bias=4
        )

    with And("I attach partition from source table into destination table"):
        partition = "1-1"
        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition}' FROM {source_table_name}"
        node.query(query)

    with Then("I check that specidied partition was attached"):
        source_partition_data = node.query(
            f"SELECT * from {source_table_name} where a = 1 and b = 1 order by a,b"
        ).output
        destination_partition_data = node.query(
            f"SELECT * from {destination_table_name} where a = 1 order by a,b"
        ).output
        assert source_partition_data == destination_partition_data


@TestScenario
@Flags(TE)
def attach_partition_from_monotonical_increase(
    self, source_table_engine="MergeTree", destination_table_engine="MergeTree"
):
    """Check `attach partition from` when destination partition expression monotonically increase in the source partition min max range."""
    node = self.context.node

    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given(
        "I create two tables that have different partition keys",
        description=f"""
               engines:
               destination table: {destination_table_engine}
               source table: {source_table_engine}
               """,
    ):
        source_partition_expression = "toYYYYMMDD(timestamp)"
        destination_partition_expression = "toYYYYMM(timestamp)"

        columns = [
            Column(name="timestamp", datatype=Date()),
        ]
        create_table(
            name=source_table_name,
            engine=destination_table_engine,
            order_by="tuple()",
            partition_by=source_partition_expression,
            columns=columns,
            if_not_exists=True,
        )
        create_table(
            name=destination_table_name,
            engine=destination_table_engine,
            order_by="tuple()",
            partition_by=destination_partition_expression,
            columns=columns,
            if_not_exists=True,
        )

    with And(
        f"I insert data into tables that will create different partitions for tables"
    ):
        insert_date_data(node=node, table_name=source_table_name)
        insert_date_data(node=node, table_name=destination_table_name, bias=32)

    with And("I attach partition from source table into destination table"):
        partition = "20231221"
        node.query(
            f"select partition_id from system.parts where table='{destination_table_name}'"
        )
        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition}' FROM {source_table_name}"
        node.query(query)
        node.query(
            f"select partition_id from system.parts where table='{destination_table_name}'"
        )

    with Then("I check that specidied partition was attached"):
        source_partition_data = node.query(
            f"SELECT * from {source_table_name} where timestamp = '2023-12-21'"
        ).output
        destination_partition_data = node.query(
            f"SELECT * from {destination_table_name} where timestamp = '2023-12-21'"
        ).output
        assert source_partition_data == destination_partition_data


@TestSketch(Scenario)
@Flags(TE)
def engines_permutation(self):
    """Run tests with different engines."""
    values = {
        "MergeTree",
        "ReplacingMergeTree",
        "AggregatingMergeTree",
        # "CollapsingMergeTree",
        # "VersionedCollapsingMergeTree",
        # "GraphiteMergeTree",
        "SummingMergeTree",
    }

    attach_partition_from_subset(
        source_table_engine=either(*values, i="source_table_engine"),
        destination_table_engine=either(*values, i="destination_table_engine"),
    )
    attach_partition_from_partitioned_to_unpartitioned(
        source_table_engine=either(*values, i="source_table_engine"),
        destination_table_engine=either(*values, i="destination_table_engine"),
    )


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey(
        "1.0"
    )
)
@Name("partition key")
def feature(self, node="clickhouse1"):
    """Check condtitions for partition key."""

    self.context.node = self.context.cluster.node(node)

    Scenario(run=engines_permutation)
    Scenario(run=attach_partition_from_monotonical_increase)
