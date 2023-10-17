from testflows.core import *
from testflows.asserts import *
from alter.table.requirements.replace_partition import *
from helpers.common import getuid
from helpers.tables import create_table, create_temporary_table, Column
from helpers.datatypes import *


@TestOutline
def create_merge_tree_tables(self, node, table1, table2):
    """An outline to create two tables with the same structure and insert values needed for test scenarios."""
    with By("Creating a MergeTree table partitioned by column p"):
        create_table(
            name=table1,
            engine="MergeTree",
            partition_by="p",
            order_by="tuple()",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
        )
    with And("Creating a new table with the same structure as the table_1"):
        node.query(f"CREATE TABLE {table2} AS {table1}")

    with When("I insert the data into table_1"):
        node.query(f"INSERT INTO {table1} VALUES (1, 1), (2, 2)")

    with And(
        "I insert the same data into table_2 but with the different value for column i"
    ):
        node.query(f"INSERT INTO {table2} VALUES (1, 1) (2, 3)")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition("1.0"))
def between_two_tables(self):
    """Creating two tables and checking that the `REPLACE PARTITION` works when both tables have the same structure,
    partition key, and order by."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "table_" + getuid()

    with Given("I have two tables with the same structure"):
        create_merge_tree_tables(node=node, table1=table_1, table2=table_2)

    with Then("I replace partition for table_1 from table_2"):
        node.query(f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2}")

    with Check(
        "I check that the values on the partition of table_1 are changed and are the same as on table_2"
    ):
        replaced_value = node.query(f"SELECT i FROM {table_1} WHERE p = 2")
        assert replaced_value.output.strip() == "3", error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition("1.0"))
def keep_data_after_replacing(self):
    """Creating two tables and checking that the `REPLACE PARTITION` does not delete the data from the table the partition was replaced from."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "table_" + getuid()

    with Given("I have two tables with the same structure"):
        create_merge_tree_tables(node=node, table1=table_1, table2=table_2)

    with Then("I replace partition for table_1 from table_2"):
        node.query(f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2}")

    with Check(
        "I check that the values on the partition of table_1 are changed and are the same as on table_2"
    ):
        replaced_value = node.query(f"SELECT i FROM {table_2} WHERE p = 2")
        assert replaced_value.output.strip() == "3", error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromTemporaryTable("1.0")
)
def between_temporary_and_regular_tables(self):
    """Replacing partition from temporary MergeTree table into a regular MergeTree table."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "temporary_" + getuid()

    with Then("I replace partition for table_1 from table_2"):
        node.query(f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2}")

    with Check(
        "I check that the values on the partition of table_1 are changed and are the same as on table_2"
    ):
        replaced_value = node.query(f"SELECT i FROM {table_1} WHERE p = 2")
        assert replaced_value.output.strip() == "3", error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTables("1.0"))
def between_temporary_tables(self):
    """Replacing partition from temporary MergeTree table to another temporary table."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "temporary_" + getuid()

    with Given("I have a temporary MergeTree table partitioned by column p"):
        create_temporary_table(
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
        create_temporary_table(
            name=table_2,
            engine="MergeTree",
            partition_by="p",
            order_by="tuple()",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
        )

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
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_IntoOutfile("1.0"))
def into_outfile(self):
    """Checking that the usage of INTO OUTFILE does output any errors and does not crash the ClickHouse."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "table_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_merge_tree_tables(node=node, table1=table_1, table2=table_2)

    with Check("I check tha the INTO OUTFILE clause does not output any errors"):
        node.query(
            f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2} INTO OUTFILE 'test.file'",
            exitcode=0,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Format("1.0"))
def format(self):
    """Checking that the usage of FORMAT does output any errors and does not crash the ClickHouse."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "table_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_merge_tree_tables(node=node, table1=table_1, table2=table_2)

    with Check("I check tha the FORMAT clause does not output any errors"):
        node.query(
            f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2} FORMAT CSV",
            exitcode=0,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Settings("1.0"))
def settings(self):
    """Checking that the usage of SETTINGS does not output any errors and does not crash the ClickHouse."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "table_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_merge_tree_tables(node=node, table1=table_1, table2=table_2)

    with Check("I check tha the SETTINGS clause does not output any errors"):
        node.query(
            f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2} SETTINGS async_insert = 1",
            exitcode=0,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_TableFunctions("1.0")
)
def table_functions(self):
    """Checking that the usage of table functions outputs an expected error and does not crash the ClickHouse."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "table_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_merge_tree_tables(node=node, table1=table_1, table2=table_2)

    with Check("I check tha the usage of table functions outputs an expected errors"):
        node.query(
            f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2} file('file.parquet')",
            exitcode=62,
            message="DB::Exception: Syntax error",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_TableFunctions("1.0")
)
def join(self):
    """Checking that the usage of JOIN does output an expected error and does not crash the ClickHouse."""
    node = self.context.node
    table_1 = "table_" + getuid()
    table_2 = "table_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_merge_tree_tables(node=node, table1=table_1, table2=table_2)

    with Check("I check tha the SETTINGS clause does not output any errors"):
        node.query(
            f"ALTER TABLE {table_1} REPLACE PARTITION 2 FROM {table_2} JOIN table_2 ON table_1.p",
            exitcode=62,
            message="DB::Exception: Syntax error",
        )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition("1.0"))
@Name("replace partition")
def feature(self, node="clickhouse1"):
    """Check that replace partition functionality works as expected."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
