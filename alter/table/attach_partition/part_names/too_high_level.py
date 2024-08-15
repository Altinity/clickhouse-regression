from testflows.combinatorics import product

from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid


@TestScenario
def check_too_high_level_attach_partition(self, engine, partition_key):
    """Check that is not possible to attach a partition with a level greater than the LEGACY_MAX_LEVEL."""
    with Given("I have a table with data"):
        table_name = "source_" + getuid()
        create_MergeTree_table_with_data(
            table_name=table_name,
            order_by="id",
            engine=engine,
            partition_by=partition_key,
            number_of_rows=100,
        )

    with When("I get part name"):
        part_name, partition = (
            self.context.node.query(
                f"SELECT name, partition FROM system.parts WHERE table = '{table_name}' AND active FORMAT TabSeparated"
            )
            .output.split("\n")[0]
            .split("\t")
        )

    with And("I save table state to compare later"):
        table_before = self.context.node.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*) FORMAT TabSeparated"
        ).output
        parts_before = self.context.node.query(
            f"SELECT name FROM system.parts WHERE table = '{table_name}' ORDER BY name FORMAT TabSeparated"
        ).output

    with Then("I detach and rename the part"):
        detach_part(
            table_name=table_name,
            part_name=part_name,
        )
        high_level = str(2 ** 32 + 1)
        new_part_name = "_".join(part_name.split("_")[:-1] + [high_level])
        rename_detached_part(
            table_name=table_name,
            part_name=part_name,
            new_part_name=new_part_name,
        )

    with And("I attach the partition"):
        attach_partition(
            table_name=table_name,
            partition=partition,
        )

    with And("I check that part was not attached by checking the table state"):
        table_after = self.context.node.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*) FORMAT TabSeparated"
        ).output
        assert table_before != table_after, error()

    with And("I check that part was not attached by checking the parts state"):
        parts_after = self.context.node.query(
            f"SELECT name FROM system.parts WHERE table = '{table_name}' ORDER BY name FORMAT TabSeparated"
        ).output
        assert parts_before != parts_after, error()


@TestScenario
def check_too_high_level_attach_part(self, engine, partition_key):
    """Check that is not possible to attach a partition with a level greater than the LEGACY_MAX_LEVEL."""
    with Given("I have a table with data"):
        table_name = "source_" + getuid()
        create_MergeTree_table_with_data(
            table_name=table_name,
            order_by="id",
            engine=engine,
            partition_by=partition_key,
            number_of_rows=100,
        )

    with When("I get part name"):
        part_name, partition = (
            self.context.node.query(
                f"SELECT name, partition FROM system.parts WHERE table = '{table_name}' AND active FORMAT TabSeparated"
            )
            .output.split("\n")[0]
            .split("\t")
        )

    with Then("I detach and rename the part"):
        detach_part(
            table_name=table_name,
            part_name=part_name,
        )
        high_level = str(2 ** 32 + 1)
        new_part_name = "_".join(part_name.split("_")[:-1] + [high_level])
        rename_detached_part(
            table_name=table_name,
            part_name=part_name,
            new_part_name=new_part_name,
        )

    with And("I attach the partition"):
        self.context.node.query(
            f"ALTER TABLE {table_name} ATTACH PART '{new_part_name}'",
            exitcode=233,
            message="DB::Exception: Unexpected part name:",
        )


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartNames_GreaterThanLegacyMaxLevel(
        "1.0"
    )
)
def too_high_level(self):
    """Run test to check that is not possible to attach a partition with a level greater than the LEGACY_MAX_LEVEL."""

    engines = [
        "MergeTree",
        "AggregatingMergeTree",
        "ReplacingMergeTree",
        "CollapsingMergeTree",
        "VersionedCollapsingMergeTree",
        "GraphiteMergeTree",
        "SummingMergeTree",
    ]
    partition_keys = [
        "id",
        "id%2",
        "(id, a)",
        "intDiv(id, 2)",
        "(intDiv(id, 2), intDiv(a, 4))",
        "(a, id)",
        "a%3",
    ]
    for engine, partition_key in product(engines, partition_keys):
        Scenario(
            f"{engine} attach partition",
            test=check_too_high_level_attach_partition,
        )(engine=engine, partition_key=partition_key)

    for engine, partition_key in product(engines, partition_keys):
        Scenario(
            f"{engine} attach part",
            test=check_too_high_level_attach_part,
        )(engine=engine, partition_key=partition_key)


@TestScenario
def check_reset_when_equal_to_legacy_max_level(self, engine, partition_key):
    """Check that part level is reseted to MAX_LEVEL when it is equal to the LEGACY_MAX_LEVEL."""
    with Given("I have a table with data"):
        table_name = "source_" + getuid()
        create_MergeTree_table_with_data(
            table_name=table_name,
            order_by="id",
            engine=engine,
            partition_by=partition_key,
            number_of_rows=100,
        )

    with When("I get part name"):
        part_name, partition = (
            self.context.node.query(
                f"SELECT name, partition FROM system.parts WHERE table = '{table_name}' AND active ORDER BY name FORMAT TabSeparated"
            )
            .output.split("\n")[0]
            .split("\t")
        )

    with And("I save table state to compare later"):
        table_before = self.context.node.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

    with Then("I detach and rename the part"):
        detach_part(
            table_name=table_name,
            part_name=part_name,
        )
        high_level = str(2 ** 32 - 1)
        new_part_name = "_".join(part_name.split("_")[:-1] + [high_level])
        rename_detached_part(
            table_name=table_name,
            part_name=part_name,
            new_part_name=new_part_name,
        )

    with And("I attach the part"):
        attach_partition(
            table_name=table_name,
            partition=partition,
        )

    with And("I save parts state to compare later and optimize table"):
        parts_before = self.context.node.query(
            f"SELECT name FROM system.parts WHERE table = '{table_name}' AND active ORDER BY name FORMAT TabSeparated"
        ).output
        optimize_table(table_name=table_name)

    with And("I check that part was attached"):
        table_after = self.context.node.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*) FORMAT TabSeparated"
        ).output
        assert table_before == table_after, error()

    with And("I check that part level was reseted"):
        parts_after = self.context.node.query(
            f"SELECT name FROM system.parts WHERE table = '{table_name}' AND active ORDER BY name FORMAT TabSeparated"
        ).output
        assert parts_before != parts_after, error()

        new_part_name = parts_before.split("\n")[0]
        expected_part_name = "_".join(new_part_name.split("_")[:-1] + ["1"])
        if check_clickhouse_version("<24.3")(self):
            expected_part_name = "_".join(
                new_part_name.split("_")[:-1] + ["1000000000"]
            )
        assert expected_part_name in parts_after, error()


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartNames_EqualToLegacyMaxLevel(
        "1.0"
    )
)
def reset_when_equal_to_legacy_max_level(self):
    """Run test to check that part level is reseted to MAX_LEVEL when it is equal to the LEGACY_MAX_LEVEL."""

    engines = [
        "MergeTree",
        "AggregatingMergeTree",
        "ReplacingMergeTree",
        "CollapsingMergeTree",
        "VersionedCollapsingMergeTree",
        "GraphiteMergeTree",
        "SummingMergeTree",
    ]

    partition_keys = [
        "id",
        "id%2",
        "(id, a)",
        "intDiv(id, 2)",
        "(intDiv(id, 2), intDiv(a, 4))",
        "(a, id)",
        "a%3",
    ]

    for engine, partition_key in product(engines, partition_keys):
        Scenario(
            f"{engine}",
            test=check_reset_when_equal_to_legacy_max_level,
        )(engine=engine, partition_key=partition_key)
