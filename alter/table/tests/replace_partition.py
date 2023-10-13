from testflows.core import *
from testflows.asserts import *
from alter.table.requirements.replace_partition import *
from helpers.common import getuid
from helpers.tables import create_table, Column
from helpers.datatypes import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition("1.0"))
def between_two_tables(self):
    """Creating two tables and checking that the `REPLACE PARTITION` works when both tables have the same structure,
    partition key, and order by."""
    node = self.context.node
    table_1 = "table" + getuid()
    table_2 = "table" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_table(
            name=table_1,
            engine="MergeTree",
            partition_by="p",
            order_by="tuple()",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
        )

        node.query(f"CREATE TABLE {table_2} AS {table_1}")

    with When("I insert the data into table_1"):
        node.query(f"INSERT INTO {table_1} VALUES (1, 1), (2, 2)")

    with And(
        "I insert the same data into table_2 but with the different value for column i"
    ):
        node.query(f"INSERT INTO {table_2} VALUES (1, 1) (2, 3)")

    with Then("I replace partition for table_1 from table_2"):
        node.query(f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2}")

    with Check(
        "I check that the values on the partition of table_1 are changed and are the same as on table_2"
    ):
        replaced_value = node.query(f"SELECT i FROM {table_1} WHERE p = 2")
        assert replaced_value.output.strip() == "3", error()


@TestScenario
def between_temporary_and_regular_tables(self):
    """Replacing partition from temporary MergeTree table into a regular MergeTree table."""
    node = self.context.node
    table_1 = "table" + getuid()
    table_2 = "temporary" + getuid()

    with Given("I have a MergeTree table partitioned by column p"):
        create_table(
            name=table_1,
            engine="MergeTree",
            partition_by="p",
            order_by="tuple()",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
        )
    with And("I create a new temporary table with the same structure as the table_1"):
        node.query(f"CREATE TEMPORARY TABLE {table_2} AS {table_1}")

    with When("I insert the data into table_1"):
        node.query(f"INSERT INTO {table_1} VALUES (1, 1), (2, 2)")

    with And(
        "I insert the same data into table_2 but with the different value for column i"
    ):
        node.query(f"INSERT INTO {table_2} VALUES (1, 1) (2, 3)")

    with Then("I replace partition for table_1 from table_2"):
        node.query(f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2}")

    with Check(
        "I check that the values on the partition of table_1 are changed and are the same as on table_2"
    ):
        replaced_value = node.query(f"SELECT i FROM {table_1} WHERE p = 2")
        assert replaced_value.output.strip() == "3", error()


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition("1.0"))
@Name("replace partition")
def feature(self, node="clickhouse1"):
    """Check that replace partition functionality works as expected."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
