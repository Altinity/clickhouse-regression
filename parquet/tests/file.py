from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *


@TestScenario
def insert_into_engine(self):
    """Check that when data is inserted into a table with `File(Parquet)` engine, it is written into the source file correctly."""

    node = self.context.node

    table_name = "table_" + getuid()

    with Given("I have a table with a `File(Parquet)` engine"):
        table(name=table_name, engine="File(Parquet)")

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table_name)

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table_name}/data.Parquet /var/lib/clickhouse/user_files/{table_name}.Parquet"
        )
        check_source_file(path=f"/var/lib/clickhouse/user_files/{table_name}.Parquet")


@TestScenario
def select_from_engine(self):
    """Check that when a table with `File(Parquet)` engine is attached on top of a Parquet file, it reads the data correctly."""

    node = self.context.node

    table_name = "table_" + getuid()
    table_def = node.command(
        "cat /var/lib/clickhouse/user_files/clickhouse_table_def.txt"
    ).output.strip()

    node.command(f"mkdir /var/lib/clickhouse/user_files/{table_name}")
    node.command(
        f"cp /var/lib/clickhouse/user_files/data_NONE.Parquet /var/lib/clickhouse/user_files/{table_name}/data.Parquet"
    )

    with Given(
        "I attach a table with a `File(Parquet)` engine on top of a Parquet file"
    ):
        table(
            name=table_name,
            engine="File(Parquet)",
            create="ATTACH",
            path=table_name,
            table_def=table_def,
        )

    with Then("I check that the table reads the data correctly"):
        check_query_output(
            query=f"SELECT * FROM {table_name}",
            snap_name="Select from FILE engine into file",
        )


@TestScenario
def engine_to_file_to_engine(self):
    """Check that when data is inserted into a table with `File(Parquet)` engine,
    the data can be read back correctly from the source file using a different table with `File(Parquet)` engine."""

    node = self.context.node

    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()

    with Given("I have a table with `File(Parquet)` engine"):
        table(name=table0_name, engine="File(Parquet)")

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table0_name)

    with Then(
        "I check that the data inserted into the table was correctly written into the file"
    ):
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/user_files/{table0_name}.Parquet"
        )
        check_source_file(path=f"/var/lib/clickhouse/user_files/{table0_name}.Parquet")

    with When("I copy of the Parquet source file to a new directory"):
        node.command(f"mkdir /var/lib/clickhouse/user_files/{table1_name}")
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/user_files/{table1_name}/data.Parquet"
        )

    with And(
        "I attach a new table on top of the Parquet source file created by the previous table"
    ):
        table(
            name=table1_name,
            engine="File(Parquet)",
            create="ATTACH",
            path=f"/var/lib/clickhouse/user_files/{table1_name}/",
        )

    with Then(
        "I check that the new table is able to read the data from the file correctly"
    ):
        check_query_output(query=f"SELECT * FROM {table1_name}")


@TestOutline(Scenario)
@Examples(
    "compression_type",
    [
        (
            "NONE",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_None("1.0")),
        ),
        (
            "GZIP",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Gzip("1.0")),
        ),
        (
            "BROTLI",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Brotli("1.0")
            ),
        ),
        (
            "LZ4",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4("1.0"),
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4Raw("1.0"),
            ),
        ),
    ],
)
def insert_into_engine_from_file(self, compression_type):
    """Check that that data read from a Parquet file using the `INFILE` clause in `INSERT` query is
    correctly written into a table with a `File(Parquet)` engine.
    """

    node = self.context.node
    table_name = "table_" + getuid()
    table_def = self.context.parquet_table_def

    if compression_type != "NONE":
        xfail(
            "DB::Exception: inflateReset failed: data error: While executing ParquetBlockInputFormat: While executing File: data for INSERT was parsed from file. (ZLIB_INFLATE_FAILED)"
        )

    with Given("I have a table with a `File(Parquet)` engine"):
        table(name=table_name, engine="File(Parquet)", table_def=table_def)

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet{'.' + compression_type if compression_type != 'NONE' else ''}' COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then("I check that the table contains correct data"):
        check_query_output(
            query=f"SELECT * FROM {table_name}",
            snap_name="Insert into FILE engine from file",
        )


@TestOutline(Scenario)
@Examples(
    "compression_type",
    [
        (
            "NONE",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_None("1.0")),
        ),
        (
            "GZIP",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Gzip("1.0")),
        ),
        (
            "BROTLI",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Brotli("1.0")
            ),
        ),
        (
            "LZ4",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4("1.0"),
                RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4Raw("1.0"),
            ),
        ),
    ],
)
def engine_select_output_to_file(self, compression_type):
    """Check that data is correctly written into a Parquet file when using `SELECT` query with `OUTFILE` clause on a table with `File(Parquet)` engine."""

    node = self.context.node

    table_name = "table_" + getuid()
    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet{'.' + compression_type if compression_type != 'NONE' else ''}'"

    with Given("I have a table with a `File(Parquet)` engine"):
        table(name=table_name, engine="File(Parquet)")

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table_name)

    with When("I select data from the table and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then("I check that data was written into the Parquet file correctly"):
        node.command(f"cp {path} /var/lib/clickhouse/user_files/{table_name}.Parquet")
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table_name}.Parquet",
            compression=f"'{compression_type.lower()}'",
        )


@TestScenario
def insert_into_function_manual_cast_types(self):
    """Check that when data is inserted into `file` table function with manually defined structure,
    it is written into the source file correctly.
    """

    xfail("create empty parquet file with appropriate columns.")

    node = self.context.node
    file_name = "file_" + getuid()
    table_def = node.command(
        "cat /var/lib/clickhouse/user_files/clickhouse_table_def.txt"
    ).output.strip()

    with When("I insert test data into file table function in Parquet format"):
        node.command(
            f"cp /var/lib/clickhouse/user_files/data_NONE.Parquet /var/lib/clickhouse/user_files/{file_name}.Parquet"
        )
        insert_test_data(
            name=f"FUNCTION file('{file_name}.Parquet', 'Parquet', '{table_def[1:-1]}')",
        )

    with Then("I check the file specified in the `file` function has correct data"):
        check_source_file(path=f"/var/lib/clickhouse/user_files/{file_name}.Parquet")


@TestScenario
def insert_into_function_auto_cast_types(self):
    """Check that when data is inserted into `file` table function with automatically defined structure,
    it is written into the source file correctly.
    """

    xfail("create empty parquet file with appropriate columns.")

    node = self.context.node
    file_name = "file_" + getuid()

    with When("I insert test data into `file` function in Parquet format"):
        node.command(
            f"cp /var/lib/clickhouse/user_files/data_NONE.Parquet /var/lib/clickhouse/user_files/{file_name}.Parquet"
        )
        insert_test_data(name=f"FUNCTION file('{file_name}.Parquet', 'Parquet')")

    with Then("I check the file specified in the `file` function has correct data"):
        check_source_file(path=f"/var/lib/clickhouse/user_files/{file_name}.Parquet")


@TestScenario
def select_from_function_manual_cast_types(self):
    """Check that when data is selected from a `file` table function with manually cast column types,
    it is read correctly.
    """

    node = self.context.node
    table_def = node.command(
        "cat /var/lib/clickhouse/user_files/clickhouse_table_def.txt"
    ).output.strip()

    with Then("I check that the `file` table function contains correct data"):
        check_query_output(
            query=f"SELECT * FROM file('data_NONE.Parquet', 'Parquet', '{table_def[1:-1]}')"
        )


@TestScenario
def select_from_function_auto_cast_types(self):
    """Check that when data is selected from a `file` table function with automatic cast column types,
    it is read correctly.
    """

    with Then("I check that the `file` table function contains correct data"):
        check_query_output(
            query=f"SELECT * FROM file('data_NONE.Parquet', 'Parquet')",
            snap_name="select from file function, auto cast types",
        )


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def engine(self):
    """Check that table with `File(Parquet)` engine correctly reads and writes Parquet format."""
    Scenario(run=insert_into_engine)
    Scenario(run=select_from_engine)
    Scenario(run=engine_to_file_to_engine)
    Scenario(run=insert_into_engine_from_file)
    Scenario(run=engine_select_output_to_file)


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File("1.0"))
def function(self):
    """Check that `file` table function correctly reads and writes Parquet format."""
    Scenario(run=insert_into_function_manual_cast_types)
    Scenario(run=insert_into_function_auto_cast_types)
    Scenario(run=select_from_function_manual_cast_types)
    Scenario(run=select_from_function_auto_cast_types)


@TestFeature
@Name("file")
def feature(self, node="clickhouse1"):
    """Run checks for `File(Parquet)` table engine and `file` table function when used with Parquet format."""

    self.context.node = self.context.cluster.node(node)

    Suite(run=engine)
    Suite(run=function)
