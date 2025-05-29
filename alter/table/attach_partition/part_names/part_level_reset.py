import random

from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid


@TestScenario
@Flags(TE)
def check_part_level_reset(self, engine="MergeTree"):
    """Check that when attaching a part or partition to a MergeTree table,
    the chunk level will be reset."""
    node = self.context.node
    source_table = "source_" + getuid()

    with Given("I create a source table with data"):
        create_MergeTree_table_with_data(
            table_name=source_table,
            order_by="id",
            engine=engine,
            number_of_rows=5,
        )

    with And("I optimize the source table to increase chunk level"):
        optimize_table(table_name=source_table)
        optimize_table(table_name=source_table)

    with And("I get part name"):
        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active AND rows>0 FORMAT TabSeparated"
        ).output

    with And("I detach the part"):
        detach_part(
            table_name=source_table,
            part_name=part_name,
        )

    with And("I attach the part"):
        attach_partition(
            table_name=source_table,
            partition="tuple()",
        )

    with And("I get part name and check if it is renamed"):
        if check_clickhouse_version("<24.3")(self):
            expected_part_name = "all_2_2_2"
        else:
            expected_part_name = "all_2_2_0"

        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active AND rows>0 FORMAT TabSeparated"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert part_name.output == expected_part_name, error(
                    f"Unexpected part name: {part_name.output}, expected: {expected_part_name}"
                )


@TestScenario
@Flags(TE)
def check_part_level_reset_replicated(self, engine):
    """Check that when attaching a part or partition to a MergeTree table,
    the chunk level will be reset."""
    source_table = "source_" + getuid()

    with Given("I create a source table"):
        create_table_on_cluster_with_data(
            table_name=source_table,
            cluster="replicated_cluster_secure",
            order_by="id",
            engine=engine,
            number_of_rows=5,
        )

    with And("I optimize the source table to increase chunk level"):
        optimize_table(table_name=source_table)
        optimize_table(table_name=source_table)

    with And("I get part name"):
        node = random.choice(self.context.nodes)
        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active AND rows>0 FORMAT TabSeparated"
        ).output

    with And("I detach the part"):
        node = random.choice(self.context.nodes)
        detach_part(table_name=source_table, part_name=part_name, node=node)

    with And("I attach the part on random node"):
        node = random.choice(self.context.nodes)
        attach_part(table_name=source_table, part_name=part_name, node=node)

    with Then("I get part name and check it is renamed"):
        expected_part_name = "all_1_1_0"

        for node in self.context.nodes:
            part_name = node.query(
                f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active AND rows>0 FORMAT TabSeparated"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert part_name.output == expected_part_name, error(
                        f"Unexpected part name: {part_name.output}, expected: {expected_part_name}"
                    )


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartNames_ChunkLevelReset("1.0")
)
@Flags(TE)
def part_level_reset(self):
    """Check that when attach a part or partition to a MergeTree table, the c
    hunk level will be reseted. Possible combinations: detach part - attach part,
    detach partition - attach partition, detach part - attach partition,
    detach partition - attach part.
    """
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
