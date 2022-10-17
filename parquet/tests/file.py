from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *


@TestScenario
def insert_into_engine(self):
    """Check that when data is inserted into a table with File(Parquet) engine, it is written into the source file correctly."""

    table_name = "table_" + getuid()

    with Given("I have a table with a Parquet type file engine"):
        table(name=table_name, engine="File(Parquet)")

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table_name)

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file(
            path=f"/var/lib/clickhouse/data/default/{table_name}/data.Parquet"
        )


@TestScenario
def select_from_engine(self):
    """Check that when a table with File(Parquet) engine is attached on top of a parquet file, it reads the data correctly."""

    table_name = "table_" + getuid()

    with Given("I attach a table with a File(Parquet) engine on top of a Parquet file"):
        table(name=table_name, engine="File(Parquet)", create="ATTACH")

    with Then("I check that the table reads the data correctly"):
        check_query_output(query=f"SELECT * FROM {table_name}")


@TestScenario
def engine_to_file_to_engine(self):
    """Check that when data is inserted into a table with File(Parquet) engine,
    the data can be read back correctly from the source file using a different table with File(Parquet) engine."""

    node = self.context.node

    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()

    with Given("I have a table"):
        table(name=table0_name, engine="File(Parquet)")

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table0_name)

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file(
            path=f"/var/lib/clickhouse/data/default/{table0_name}/data.Parquet"
        )

    with When("I copy of the Paruqet source file to a new directory"):
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/data/default/{table1_name}/data.Parquet"
        )

    with And(
        "I attach a new table on top of the Parquet source file created by the previous table"
    ):
        table(name=table1_name, engine="File(Parquet)", create="ATTACH")

    with Then(
        "I check that the new table is able to read the data from the file correctly"
    ):
        check_query_output(query=f"SELECT * FROM {table1_name}")


@TestOutline(Scenario)
@Examples(
    "compression_type",
    [
        (
            "none",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_None("1.0")),
        ),
        (
            "gzip",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Gzip("1.0")),
        ),
        (
            "br",
            Requirement(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Brotli("1.0")),
        ),
        (
            "lz4",
            Requirement(
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4("1.0"),
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4Raw("1.0"),
            ),
        ),
    ],
)
def insert_into_engine_from_file(self, compression_type):
    """Check that that data read from a Parquet file using the INFILE clause in INSERT query is
    correctly written into a table with a Parquet FILE engine.
    """

    node = self.context.node

    table_name = "table_" + getuid()

    with Given("I have a table with a Parquet type file engine"):
        table(name=table_name, engine="File(Parquet)")

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data.Parquet' COMPRESSION {compression_type} FORMAT Parquet"
        )

    with Then("I check that the table contains correct data"):
        check_query_output(query=f"SELECT * FROM {table_name}")


@TestOutline(Scenario)
@Examples(
    "compression_type",
    [
        (
            "none",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_None("1.0")),
        ),
        (
            "gzip",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Gzip("1.0")),
        ),
        (
            "br",
            Requirement(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Brotli("1.0")),
        ),
        (
            "lz4",
            Requirement(
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4("1.0"),
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4Raw("1.0"),
            ),
        ),
    ],
)
def engine_select_output_to_file(self, compression_type):
    """Check that data is correctly written into a Parquet file when using SELECT query with OUTFILE"""

    node = self.context.node

    table_name = "table_" + getuid()

    with Given("I have a table with a Parquet type file engine"):
        table(name=table_name, engine="File(Parquet)")

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table_name)

    with When("I select data from the table and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE '/var/lib/clickhouse/user_files/select_output_to_file.Parquet' COMPRESSION {compression_type} FORMAT Parquet"
        )

    with Then("I check that data was written into the Parquet file correctly"):
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/select_output_to_file.Parquet"
        )


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def engine(self):
    """Check that File table engine correctly reads and writes Parquet format."""

    Scenario(run=insert_into_engine)
    Scenario(run=select_from_engine)
    Scenario(run=engine_to_file_to_engine)
    Scenario(run=insert_into_engine_from_file)
    Scenario(run=engine_select_output_to_file)


@TestScenario
def insert_into_function_manual_cast_types(self):
    """Check that when data is inserted into a table with file(Parquet) table function with manually defined structure,
    it is written into the source file correctly.
    """
    node = self.context.node

    table_name = "table_" + getuid()
    file_name = "file_" + getuid()

    with When("I insert test data into file function in Parquet format"):
        insert_test_data(
            name=f"FUNCTION file('{file_name}.Parquet', 'Parquet', {generate_all_column_types()})"
        )

    with Then("I check the file specified by the file function has correct data"):
        check_source_file(path=f"/var/lib/clickhouse/user_files/{file_name}.Parquet")


@TestScenario
def insert_into_function_auto_cast_types(self):
    """Check that when data is inserted into a table with file(Parquet) table function with automatically defined structure,
    it is written into the source file correctly.
    """
    node = self.context.node

    table_name = "table_" + getuid()
    file_name = "file_" + getuid()

    with When("I insert test data into file function in Parquet format"):
        insert_test_data(name=f"FUNCTION file('{file_name}.Parquet', 'Parquet')")

    with Then("I check the file specified by the file function has correct data"):
        check_source_file(path=f"/var/lib/clickhouse/user_files/{file_name}.Parquet")


@TestScenario
def select_from_function_manual_cast_types(self):
    """Check that when data is selected from a file(Parquet) table function with manually cast column types,
    it is read correctly.
    """

    with Then("I check that the table contains correct data"):
        check_query_output(
            query=f"SELECT * FROM file('/var/lib/clickhouse/data.Parquet', 'Parquet', {generate_all_column_types()})"
        )


@TestScenario
def select_from_function_auto_cast_types(self):
    """Check that when data is selected from a file(Parquet) table function with automatic cast column types,
    it is read correctly.
    """

    with Then("I check that the table contains correct data"):
        check_query_output(
            query=f"SELECT * FROM file('/var/lib/clickhouse/data.Parquet', 'Parquet')"
        )


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File("1.0"))
def function(self, node=None):
    """Check that File table function correctly reads and writes Parquet format."""
    Scenario(run=insert_into_function_manual_cast_types)
    Scenario(run=insert_into_function_auto_cast_types)
    Scenario(run=select_from_function_manual_cast_types)
    Scenario(run=select_from_function_auto_cast_types)


@TestFeature
@Name("file")
def feature(self, node="clickhouse1"):
    """Run checks for File table engine and table function using Parquet format."""

    self.context.node = self.context.cluster.node(node)

    Suite(run=engine)
    Suite(run=function)
