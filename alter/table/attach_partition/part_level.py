import random
from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.common import partitioned_MergeTree
from alter.table.attach_partition.requirements.requirements import *
from helpers.common import getuid, check_clickhouse_version
from helpers.tables import *


@TestStep
def rename_detached_part(
    self, table_name, part_name, new_part_name, database="default", node=None
):
    """Rename a detached part."""
    if node is None:
        node = self.context.node

    node.command(
        f"mv /var/lib/clickhouse/data/{database}/{table_name}/detached/{part_name} /var/lib/clickhouse/data/{database}/{table_name}/detached/{new_part_name}"
    )


@TestStep
def create_table_on_cluster_with_data(
    self,
    table_name,
    cluster,
    engine="ReplicatedMergeTree",
    order_by="()",
    node=None,
    columns=None,
    config="graphite_rollup_example",
    sign="sign",
    version="id",
    number_of_rows=100000000,
):
    """Create a table on a specified cluster with data."""
    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"ReplicatedGraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"ReplicatedVersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"ReplicatedCollapsingMergeTree({sign})"

    create_table(
        name=table_name,
        cluster=cluster,
        order_by=order_by,
        node=node,
        engine=engine,
        columns=columns,
    )

    node.query(
        f"INSERT INTO {table_name} (id, sign) SELECT number, 1 FROM numbers({number_of_rows})"
    )


@TestStep
def create_MergeTree_table(
    self,
    table_name,
    engine="MergeTree",
    order_by="()",
    node=None,
    columns=None,
    config="graphite_rollup_example",
    sign="sign",
    version="id",
):
    """Create a MergeTree table."""
    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if engine == "GraphiteMergeTree":
        engine = f"GraphiteMergeTree('{config}')"
    elif engine == "VersionedCollapsingMergeTree":
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif engine == "CollapsingMergeTree":
        engine = f"CollapsingMergeTree({sign})"

    create_table(
        name=table_name,
        order_by=order_by,
        node=node,
        engine=engine,
        columns=columns,
    )


@TestStep
def optimize_table(self, table_name, node=None):
    """Optimize a table."""
    if node is None:
        node = self.context.node

    node.query(f"OPTIMIZE TABLE {table_name} FINAL")


@TestStep
def attach_partition_from(self, source_table, destination_table, partition, node=None):
    """Attach a partition from a source table to a destination table."""
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {destination_table} ATTACH PARTITION {partition} FROM {source_table}"
    )


@TestStep
def attach_partition(self, table_name, partition, node=None):
    """Attach a partition to a table."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} ATTACH PARTITION {partition}")


@TestStep
def detach_partition(self, table_name, partition, node=None):
    """Detach a partition from a table."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} DETACH PARTITION {partition}")


@TestStep
def attach_part(self, table_name, part_name, node=None):
    """Attach a part to a table from a detached directory."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} ATTACH PART '{part_name}'")


@TestStep
def detach_part(self, table_name, part_name, node=None):
    """Detach a part from a table."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} DETACH PART '{part_name}'")


@TestScenario
def part_levels_user_example(self):
    """Check reset part level upon attach from disk on MergeTree."""
    node = self.context.node

    source_table = "source_" + getuid()
    destination_table = "destination_" + getuid()

    with Given("I create a source table on cluster with data"):
        create_table_on_cluster_with_data(
            table_name=source_table,
            cluster="replicated_cluster_secure",
            order_by="id",
            number_of_rows=100000000,
        )
        optimize_table(table_name=source_table)

    with And("I create a destination table"):
        create_MergeTree_table(
            table_name=destination_table,
            order_by="id",
        )

    with And("I attach a partition from the source table to the destination table"):
        attach_partition_from(
            source_table=source_table,
            destination_table=destination_table,
            partition="tuple()",
        )
        optimize_table(table_name=destination_table)

    with And("I get part name and construct new part name with too high level"):
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table}'"
        ).output.split("\n")
        part_name = random.choice(part_names)
        new_part_name = "_".join(part_name.split("_")[:-1]) + "_4294967295"

    with And("I detach the partition"):
        detach_partition(
            table_name=destination_table,
            partition="tuple()",
        )

    with And("Rename detached part of destination table"):
        rename_detached_part(
            table_name=destination_table,
            part_name=part_name,
            new_part_name=new_part_name,
        )

    with And("I attach detached partition"):
        attach_partition(
            table_name=destination_table,
            partition="tuple()",
        )

    with And("I attach partition from destination table to source table"):
        attach_partition_from(
            source_table=destination_table,
            destination_table=source_table,
            partition="tuple()",
        )
        optimize_table(table_name=source_table)

    with And("I check current part names in source table"):
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active"
        ).output.split("\n")

    with And("I create second destination table"):
        destination_table_2 = "destination_2_" + getuid()
        create_MergeTree_table(
            table_name=destination_table_2,
            order_by="id",
        )

    with And(
        "I attach a partition from the source table to the second destination table"
    ):
        attach_partition_from(
            source_table=source_table,
            destination_table=destination_table_2,
            partition="tuple()",
        )
        optimize_table(table_name=destination_table_2)

    with And("I get part name and construct new part name"):
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table_2}' AND active"
        ).output.split("\n")
        part_name = random.choice(part_names)
        new_part_name = "_".join(part_name.split("_")[:-1]) + "_4294967294"

    with And("I detach the partition"):
        detach_partition(
            table_name=destination_table_2,
            partition="tuple()",
        )

    with And("Rename detached part of second destination table"):
        rename_detached_part(
            table_name=destination_table_2,
            part_name=part_name,
            new_part_name=new_part_name,
        )

    with And("I attach detached partition"):
        attach_partition(
            table_name=destination_table_2,
            partition="tuple()",
        )

    with And("I attach partition from second destination table to source table"):
        attach_partition_from(
            source_table=destination_table_2,
            destination_table=source_table,
            partition="tuple()",
        )
        optimize_table(table_name=source_table)


@TestScenario
@Flags(TE)
def check_part_level_reset(self, engine="MergeTree"):
    """Check that when attach a part to a plain MergeTree table,
    it will be renamed.."""
    node = self.context.node
    source_table = "source_" + getuid()

    with Given("I create a source table"):
        create_MergeTree_table(
            table_name=source_table,
            order_by="id",
            engine=engine,
        )

    with And("I insert data into the source table"):
        node.query(
            f"INSERT INTO {source_table} (id, sign) SELECT number, 1 FROM numbers(5)"
        )

    with And("I optimize the source table"):
        optimize_table(table_name=source_table)

    with And("I get part name"):
        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active"
        ).output

    with And("I detach the part"):
        detach_part(
            table_name=source_table,
            part_name=part_name,
        )

    with And("I attach the part"):
        attach_part(
            table_name=source_table,
            part_name=part_name,
        )

    with And("I get part name and check it is renamed"):
        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active"
        ).output
        assert part_name == "all_2_2_0", f"Unexpected part name: {part_name}"


@TestScenario
@Flags(TE)
def check_part_level_reset_replicated(self, engine):
    """Check that when attach a part to a plain replicated MergeTree table,
    it will be renamed."""
    node = self.context.node
    source_table = "source_" + getuid()

    with Given("I create a source table"):
        create_table_on_cluster_with_data(
            table_name=source_table,
            cluster="replicated_cluster_secure",
            order_by="id",
            engine=engine,
            number_of_rows=5,
        )

    with And("I optimize the source table"):
        optimize_table(table_name=source_table)

    with And("I get part name"):
        node = random.choice(self.context.nodes)
        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active"
        ).output

    with And("I detach the part"):
        node = random.choice(self.context.nodes)
        detach_part(table_name=source_table, part_name=part_name, node=node)

    with And("I attach the part"):
        node = random.choice(self.context.nodes)
        attach_part(table_name=source_table, part_name=part_name, node=node)

    with Then("I get part name and check it is renamed"):
        for node in self.context.nodes:
            part_name = node.query(
                f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active"
            ).output
            assert part_name == "all_1_1_0", f"Unexpected part name: {part_name}"


@TestScenario
@Flags(TE)
def part_level_reset(self):
    engines = [
        "MergeTree",
        "ReplacingMergeTree",
        "SummingMergeTree",
        "CollapsingMergeTree",
        "VersionedCollapsingMergeTree",
        "GraphiteMergeTree",
        "AggregatingMergeTree",
    ]
    replicated_engines = [
        "ReplicatedMergeTree",
        "ReplicatedReplacingMergeTree",
        "ReplicatedSummingMergeTree",
        "ReplicatedCollapsingMergeTree",
        "ReplicatedVersionedCollapsingMergeTree",
        "ReplicatedGraphiteMergeTree",
        "ReplicatedAggregatingMergeTree",
    ]

    for engine in engines:
        Scenario(f"{engine}", test=check_part_level_reset)(engine=engine)

    for engine in replicated_engines:
        Scenario(f"{engine}", test=check_part_level_reset_replicated)(engine=engine)


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom("1.0"))
@Name("part level")
def feature(self):
    """Check that too high part levels are fixed upon attach from disk."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]
    self.context.node = self.context.node_1

    Scenario(run=part_levels_user_example)
    Scenario(run=part_level_reset)
