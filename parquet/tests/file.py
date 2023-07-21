from testflows.core import *
from parquet.requirements import *
from helpers.common import *

from parquet.tests.common import (
    generate_all_column_types,
    parquet_test_columns,
    check_source_file,
    execute_query_step,
)
from helpers.tables import create_table, attach_table


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def insert_into_engine(self):
    """Check that when data is inserted into a table with `File(Parquet)` engine, it is written into the source file correctly."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    table_name_parquet_file = "table_" + getuid()
    table_name_merge_tree = "table_" + getuid()

    with Given("I have a table with a `MergeTree` engine"):
        table = create_table(
            name=table_name_merge_tree,
            engine="MergeTree",
            order_by="tuple()",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with And(
        "I populate table with test data",
        description="inserted data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table.insert_test_data()

    with Then("I create a new table with `File(Parquet)`"):
        create_table(
            name=table_name_parquet_file,
            engine="File(Parquet)",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with And("populate it with values from the first table"):
        node.query(
            f"INSERT INTO {table_name_parquet_file} SELECT * FROM {table_name_merge_tree}"
        )

    with Check("I check the data inserted into a new table"):
        table1 = node.query(f"SELECT * FROM {table_name_merge_tree}")
        table2 = node.query(f"SELECT * FROM {table_name_parquet_file}")
        assert table1.output.strip() == table2.output.strip(), error()

    with Check(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table_name_parquet_file}/data.Parquet /var/lib/clickhouse/user_files/{table_name_parquet_file}.Parquet"
        )
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table_name_parquet_file}.Parquet",
            reference_table_name=table_name_merge_tree,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported("1.0"))
def select_from_engine(self):
    """Check that when a table with `File(Parquet)` engine is attached on top of a Parquet file, it reads the data correctly."""
    node = self.context.node
    self.context.snapshot_id = get_snapshot_id()
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I move the Parquet file into the table directory"):
        node.command(f"mkdir /var/lib/clickhouse/user_files/{table_name}")
        node.command(
            f"cp /var/lib/test_files/data_NONE.Parquet /var/lib/clickhouse/user_files/{table_name}/data.Parquet"
        )

    with Given(
        "I attach a table with a `File(Parquet)` engine on top of a Parquet file"
    ):
        table = attach_table(
            name=table_name,
            engine="File(Parquet)",
            path=table_name,
            columns=table_columns,
        )

    with Then(
        "I check that the table reads the data correctly by checking the table columns"
    ):
        with Pool(3) as executor:
            for column in table_columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM {table_name}"
                )
            join()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def engine_to_file_to_engine(self):
    """Check that when data is inserted into a table with `File(Parquet)` engine,
    the data can be read back correctly from the source file using a different table with `File(Parquet)` engine.
    """
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()

    with Given("I have a table with `File(Parquet)` engine"):
        table0 = create_table(
            name=table0_name,
            engine="File(Parquet)",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with When(
        "I insert data into the table",
        description="inserted data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table0.insert_test_data()

    with Then(
        "I check that the data inserted into the table was correctly written into the file"
    ):
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/user_files/{table0_name}.Parquet"
        )
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table0_name}.Parquet",
            reference_table_name=table0_name,
        )

    with When("I copy of the Parquet source file to a new directory"):
        node.command(f"mkdir /var/lib/clickhouse/user_files/{table1_name}")
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/user_files/{table1_name}/data.Parquet"
        )

    with And(
        "I attach a new table on top of the Parquet source file created by the previous table"
    ):
        table1 = attach_table(
            name=table1_name,
            engine="File(Parquet)",
            path=f"/var/lib/clickhouse/user_files/{table1_name}/",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with Then(
        "I check that the new table is able to read the data from the file correctly"
    ):
        with Pool(3) as executor:
            for column in table1.columns:
                r = node.query(
                    f"SELECT {column.name}, toTypeName({column.name}) FROM {table0_name}"
                    + " FORMAT JSONEachRow",
                    exitcode=0,
                )

                Check(
                    test=execute_query_step,
                    name=f"{column.datatype.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM {table1.name}",
                    expected=r.output.strip(),
                )
            join()


@TestOutline(Scenario)
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import("1.0"))
@Examples(
    "compression_type",
    [
        (
            "NONE",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0")),
        ),
        (
            "GZIP",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0")),
        ),
        (
            "LZ4",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0")),
        ),
    ],
)
def insert_into_engine_from_file(self, compression_type):
    """Check that that data read from a Parquet file using the `INFILE` clause in `INSERT` query is
    correctly written into a table with a `File(Parquet)` engine.
    """
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I have a table with a `File(Parquet)` engine"):
        table = create_table(
            name=table_name, engine="File(Parquet)", columns=table_columns
        )

    with And("I have a Parquet file"):
        node.command(
            f"cp /var/lib/test_files/data_{compression_type}.Parquet /var/lib/clickhouse/user_files/data_{compression_type}.Parquet"
        )

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' FORMAT Parquet"
        )

    with Then("I check that the table columns contain correct data"):
        with Pool(3) as executor:
            for column in table_columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM {table_name}"
                )
            join()


@TestOutline(Scenario)
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export("1.0"),
)
@Examples(
    "compression_type",
    [
        (
            "NONE",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0")),
        ),
        (
            "GZIP",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0")),
        ),
        (
            "LZ4",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0")),
        ),
    ],
)
def engine_select_output_to_file(self, compression_type):
    """Check that data is correctly written into a Parquet file when using `SELECT` query with `OUTFILE` clause on a table with `File(Parquet)` engine."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    table_name = "table_" + getuid()
    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet'"

    with Given("I have a table with a `File(Parquet)` engine"):
        table = create_table(
            name=table_name,
            engine="File(Parquet)",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with When(
        "I insert data into the table",
        description="inserted data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table.insert_test_data()

    with When("I select data from the table and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then("I check that data was written into the Parquet file correctly"):
        node.command(f"cp {path} /var/lib/clickhouse/user_files/{table_name}.Parquet")
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table_name}.Parquet",
            compression=f"'{compression_type.lower()}'",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import("1.0"))
def insert_into_function_manual_cast_types(self):
    """Check that when data is inserted into `file` table function with manually defined structure,
    it is written into the source file correctly."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    file_name = "file_" + getuid()
    table_name = "table_" + getuid()
    columns = generate_all_column_types(include=parquet_test_columns())
    func_def = ",".join([column.full_definition() for column in columns])
    columns_values = [column.values(row_count=2, cardinality=10) for column in columns]
    total_values = []

    for row in range(2):
        total_values.append(
            "("
            + ",".join([next(column_values) for column_values in columns_values])
            + ")"
        )

    with Given("I have a table with a `MergeTree` engine"):
        table = create_table(
            name=table_name,
            engine="MergeTree",
            order_by="tuple()",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with When(
        "I insert data into the `file` table function",
        description="inserted data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        node.query(
            f"INSERT INTO FUNCTION file('{file_name}.Parquet', 'Parquet', '{func_def}') VALUES {','.join(total_values)}",
            settings=[("allow_suspicious_low_cardinality_types", 1)],
        )

    with Then(
        "I insert the data from the 'file' table function into a MergeTree engine table"
    ):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/{file_name}.Parquet' FORMAT Parquet"
        )

    with And("I check the specified file has correct data"):
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{file_name}.Parquet",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def insert_into_function_auto_cast_types(self):
    """Check that when data is inserted into `file` table function with automatically defined structure,
    it is written into the source file correctly."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    file_name = "file_" + getuid()
    table_name = "table_" + getuid()

    with Given("I have a table with a `File(Parquet)` engine"):
        table = create_table(
            name=table_name,
            engine="File(Parquet)",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with And(
        "I populate table with test data",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table.insert_test_data(row_count=2, cardinality=10)

    with When("I copy the Parquet file created by the table"):
        node.command(
            f"cp /var/lib/clickhouse/data/default/{table_name}/data.Parquet /var/lib/clickhouse/user_files/{file_name}.Parquet"
        )

    with And("I generate test values"):
        columns_values = [
            column.values(row_count=2, cardinality=10) for column in table.columns
        ]

        total_values = []

        for row in range(2):
            total_values.append(
                "("
                + ",".join([next(column_values) for column_values in columns_values])
                + ")"
            )

    with And("I insert data into the `file` table function"):
        node.query(
            f"INSERT INTO FUNCTION file('{file_name}.Parquet', 'Parquet') VALUES {','.join(total_values)}",
            settings=[("engine_file_allow_create_multiple_files", 1)],
        )

    with Then("I check that the created file has correct data"):
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{file_name}.1.Parquet",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import("1.0"))
def select_from_function_manual_cast_types(self):
    """Check that when data is selected from a `file` table function with manually cast column types,
    it is read correctly."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    table_columns = self.context.parquet_table_columns
    table_def = ",".join([column.full_definition() for column in table_columns])

    with When("I check that the `file` table function reads data correctly"):
        with Pool(3) as executor:
            for column in table_columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM file('data_NONE.Parquet', 'Parquet', '{table_def}')"
                )
            join()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import("1.0"))
def select_from_function_auto_cast_types(self):
    """Check that when data is selected from a `file` table function with automatic cast column types,
    it is read correctly."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version="<22.6")
    table_columns = self.context.parquet_table_columns

    with When("I check that the `file` table function reads data correctly"):
        with Pool(3) as executor:
            for column in table_columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM file('data_NONE.Parquet', 'Parquet')"
                )
            join()


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
    """Run checks for ClickHouse using Parquet format using `File(Parquet)` table engine and `file` table function."""
    self.context.node = self.context.cluster.node(node)

    Suite(run=engine)
    Suite(run=function)
