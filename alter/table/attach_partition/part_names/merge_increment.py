import random

from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid


@TestScenario
def check_merge_increment(self, engine):
    """Check that when two or more parts are merged into one, the chunk level is
    incremented by one from highest level."""
    first_table = "first_" + getuid()
    node = self.context.node

    with Given("I create an empty source table"):
        create_MergeTree_table_with_data(
            table_name=first_table,
            engine=engine,
            order_by="id",
            number_of_rows=0,
        )

    with And(
        "I insert data to create multiple parts and optimize table so first part will have chunk level 2"
    ):
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(20)"
        )
        optimize_table(table_name=first_table)
        optimize_table(table_name=first_table)
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(2)"
        )
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(10)"
        )
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(5)"
        )

    with And("I create second table"):
        second_table = "second_" + getuid()
        create_MergeTree_table_with_data(
            table_name=second_table,
            engine=engine,
            order_by="id",
            number_of_rows=30,
        )

    with And("I optimize the second table 10 times to increase chunk level to 10"):
        for _ in range(10):
            optimize_table(table_name=second_table)

    with And("I attach partition from the second table to the first table"):
        attach_partition_from(
            source_table=second_table,
            destination_table=first_table,
            partition="tuple()",
        )

    with And("I check part names"):
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{first_table}' AND active"
        ).output.split("\n")

    with And(
        "I merge all parts into one and expect chunk level to be incremented by one from highest level"
    ):
        optimize_table(table_name=first_table)
        expected_part_name = "all_1_5_11"

        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{first_table}' AND active"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert part_name.output == expected_part_name, error(
                    f"Unexpected part name: {part_name.output}"
                )


@TestScenario
def check_merge_increment_replicated(self, engine):
    """Check that when two or more parts are merged into one, the chunk level is
    incremented by one from highest level."""
    first_table = "first_" + getuid()

    with Given("I create an empty source table"):
        create_table_on_cluster_with_data(
            table_name=first_table,
            engine=engine,
            cluster="replicated_cluster_secure",
            order_by="id",
            number_of_rows=0,
        )

    with And(
        "I insert data to create multiple parts and optimize table so first part will have chunk level 2"
    ):
        node = random.choice(self.context.nodes)
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(20)"
        )
        optimize_table(table_name=first_table)
        optimize_table(table_name=first_table)
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(2)"
        )
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(10)"
        )
        node.query(
            f"INSERT INTO {first_table} (id, sign) SELECT number,1 FROM numbers(5)"
        )

    with And("I create second table"):
        second_table = "second_" + getuid()
        create_table_on_cluster_with_data(
            table_name=second_table,
            engine=engine,
            cluster="replicated_cluster_secure",
            order_by="id",
            number_of_rows=30,
        )

    with And("I optimize the second table 10 times to increase chunk level to 10"):
        node = random.choice(self.context.nodes)
        for _ in range(10):
            optimize_table(table_name=second_table, node=node)

    with And("I attach partition from the second table to the first table"):
        attach_partition_from(
            source_table=second_table,
            destination_table=first_table,
            partition="tuple()",
        )

    with And("I check part names"):
        node = random.choice(self.context.nodes)
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{first_table}' AND active"
        ).output

    with And(
        "I merge all parts into one and expect chunk level to be incremented by one from highest level"
    ):
        node = random.choice(self.context.nodes)
        optimize_table(table_name=first_table, node=node)
        expected_part_name = ["all_0_5_11"]
        if engine == "ReplicatedGraphiteMergeTree":
            expected_part_name = ["all_0_2_11", "all_1_5_12"]

        part_name = node.query(
            f"SELECT name FROM system.parts WHERE table = '{first_table}' AND active"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert part_name.output in expected_part_name, error(
                    f"Unexpected part name: {part_name.output}"
                )


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartNames_MergeIncrement("1.0")
)
@Flags(TE)
def merge_increment(self):
    """Check that when two or more parts are merged into one after attaching a partition or part
    from another table, the chunk level is incremented by one from highest level."""
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
        Scenario(
            f"{engine}",
            test=check_merge_increment,
        )(engine=engine)

    for engine in replicated_engines:
        Scenario(
            f"{engine}",
            test=check_merge_increment_replicated,
        )(engine=engine)
