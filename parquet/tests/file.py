from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def insert_into_engine(self):
    """Check that when data is inserted into a table with File(Parquet) engine, it is written into the source file correctly."""

    table_name = "table_" + getuid()

    with Given("I have a table with a Parquet type file engine"):
        table(name=table_name, engine='File(Parquet)')

    with When("I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls"):
        insert_test_data(name=table_name)

    with Then("I check that the data inserted into the table was correctly written to the file"):
        check_source_file(path=f'/var/lib/clickhouse/data/default/{table_name}/data.Parquet')

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def select_from_engine(self):
    """Check that when a table with File(Parquet) engine is attached on top of a parquet file, it reads the data correctly."""

    table_name = "table_" + getuid()

    with Given("I attach a table with a File(Parquet) engine on top of a Parquet file"):
        table(name=table_name, engine='File(Parquet)', create="ATTACH")

    with Then("I check that the table reads the data correctly"):
        check_query_output(query=f"SELECT * FROM {table_name}")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def engine_to_file_to_engine(self):
    """Check that when data is inserted into a table with File(Parquet) engine, 
    the data can be read back correctly from the source file using a different table with File(Parquet) engine."""

    node = self.context.node

    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()

    with Given("I have a table"):
        table(name=table0_name, engine='File(Parquet)')

    with When("I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls"):
        insert_test_data(name=table0_name)

    with Then("I check that the data inserted into the table was correctly written to the file"):
        check_source_file(path=f'/var/lib/clickhouse/data/default/{table0_name}/data.Parquet')

    with When("I copy of the Paruqet source file to a new directory"):
        node.command(f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/data/default/{table1_name}/data.Parquet")

    with And("I attach a new table on top of the Parquet source file created by the previous table"):
        table(name=table1_name, engine='File(Parquet)', create="ATTACH")

    with Then("I check that the new table is able to read the data from the file correctly"):
        check_query_output(query=f"SELECT * FROM {table1_name}")

@TestSuite
def engine(self):
    """Check that File table engine correctly reads and writes Parquet format.
    """
    Scenario(run=insert_into_engine)
    Scenario(run=select_from_engine)
    Scenario(run=engine_to_file_to_engine)

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File("1.0"))
def insert_into_function(self):
    """Check that when data is inserted into a table with file(Parquet) table function, it is written into the source file correctly.
    """
    node = self.context.node

    table_name = "table_" + getuid()
    file_name = "file_" + getuid()

    with When("I insert test data into file function in Parquet format"):
        insert_test_data(name=f"FUNCTION file('{file_name}.Parquet', 'Parquet', {all_test_data_types}")

    with Then("I check the file specified by the file function has correct data"):
        check_source_file(path=f'/var/lib/clickhouse/user_files/{file_name}.Parquet')

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File("1.0"))
def select_from_function_manual(self):
    """Check that when data is inserted into a table with file(Parquet) table function, it is written into the source file correctly.
    """

    node = self.context.node

    table_name = "table_" + getuid()
    file_name = "file_" + getuid()

    with Given("I have a table"):
        table(name=table_name, engine='File(Parquet)')

    with When("I insert some data"):
        insert_test_data(name=f"FUNCTION file('{file_name}.Parquet', 'Parquet', {all_test_data_types}")

    with Then("I check the file in the table function"):
        check_source_file(path=f'/var/lib/clickhouse/user_files/{file_name}.Parquet')

@TestSuite
def function(self, node=None):
    """Check that File table function correctly reads and writes Parquet format.
    """

    Scenario(run=insert_into_function)
    Scenario(run=select_from_function_manual)

@TestFeature
@Name("file")
def feature(self, node="clickhouse1"):
    """Run checks for File table engine and table function when used with Parquet format."""

    self.context.node = self.context.cluster.node(node)

    Suite(run=engine)
    Suite(run=function)
