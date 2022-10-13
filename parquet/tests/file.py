from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def insert_into_engine(self):
    """Check that Parquet format is correctly writen into `File` table engine."""

    if node is None:
        node = self.context.node

    table_name = "table_" + getuid()

    with Given("I have a table"):
        table(name=table_name, engine='File(Parquet)')

    with When("I insert data into the table", desciption="Inserted data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls"):
        insert_test_data(name=table_name)

    with Then("I check that the data inserted into the table was correctly written to the file"):
        check_source_file(path=f'/var/lib/clickhouse/data/default/{table_name}/data.Parquet')

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def select_from_engine(self):
    """Check that Parquet format is correctly read from a `File` table engine."""

    if node is None:
        node = self.context.node

    table_name = "table_" + getuid()

    with Given("I attach a table on top of a Parquet file"):
        table(name=table_name, engine='File(Parquet)', create="ATTACH")

    with Then("I check that the data from the table is read correctly"):
        check_query_output(query=f"SELECT * FROM {table_name}")

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def engine_to_file_to_engine(self):
    """Check that Parquet format is correctly read from a `File` table engine."""

    if node is None:
        node = self.context.node

    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()

    with Given("I have a table"):
        table(name=table0_name, engine='File(Parquet)')

    with When("I insert data into the table", desciption="Inserted data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls"):
        insert_test_data(name=table0_name)

    with Then("I check that the data inserted into the table was correctly written to the file"):
        check_source_file(path=f'/var/lib/clickhouse/data/default/{table0_name}/data.Parquet')

    with When("I copy of the source file to a new directory"):
        node.command(f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/data/default/{table1_name}/data.Parquet")

    with And("I attach a new table on top of the file created by the previous table"):
        table(name=table1_name, engine='File(Parquet)', create="ATTACH")

    with Then("I check that the new file has correct data"):
        check_query_output(query=f"SELECT * FROM {table1_name}")

@TestSuite
def engine(self):
    """Check that File table engine correctly reads and writes in Parquet format."""

    Scenario(run=insert_into_engine)
    Scenario(run=select_from_engine)
    Scenario(run=engine_to_file_to_engine)

@TestSuite
@Requirements()
def function(self, node=None):
    """Check that ClickHouse reads Parquet format correctly using the File table function."""

    if node is None:
        node = self.context.node

    table_name = "table_" + getuid()
    file_name = "file_" + getuid()

    with Scenario("Write Parquet into File function"):

        with Given("I have a table"):
            table(name=table_name, engine='File(Parquet)')

        with When("I insert some data"):
            insert_test_data(name=f"FUNCTION file('{file_name}.Parquet', 'Parquet', {all_test_data_types}")

        with Then("I check the file in the table function"):
            check_source_file(path=f'/var/lib/clickhouse/user_files/{file_name}.Parquet')

    with Scenario("Read Parquet from table function, default type cast"):

        with Then("I check the data from the table function"):
            check_query_output(query=f"SELECT *, toTypeName(*) FROM file('{file_name}.Parquet', 'Parquet')")

    with Scenario("Read Parquet from table function, manual type cast"):

        with Then("I check the data from the table function"):
            check_query_output(query=f"SELECT * FROM file('{file_name}.Parquet', 'Parquet', {all_test_data_types})")

@TestFeature
@Name("file")
def feature(self, node="clickhouse1"):
    """Run checks for File table engine and table function using Parquet format."""

    self.context.node = self.context.cluster.node(node)

    Suite(run=engine)
    Suite(run=function)
