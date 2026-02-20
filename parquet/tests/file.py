import re
from testflows.core import *
from parquet.requirements import *
from helpers.common import *

from parquet.tests.common import (
    generate_all_column_types,
    parquet_test_columns,
    check_source_file,
    execute_query_step,
)
from helpers.tables import create_table, attach_table, Column
from helpers.datatypes import Date


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def insert_into_engine(self):
    """Check that when data is inserted into a table with `File(Parquet)` engine, it is written into the source file correctly."""
    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
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
        table1 = node.query(
            f"SELECT * FROM {table_name_merge_tree} FORMAT TabSeparated"
        )
        table2 = node.query(
            f"SELECT * FROM {table_name_parquet_file} FORMAT TabSeparated"
        )
        assert table1.output.strip() == table2.output.strip(), error()

    with Check(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        if check_clickhouse_version(">=24.10")(self):
            symlink = node.command(
                f"readlink -f /var/lib/clickhouse/data/default/{table_name_parquet_file}"
            ).output.strip()
            node.command(
                f"cp {symlink} /var/lib/clickhouse/user_files/{table_name_parquet_file}.Parquet"
            )
        else:
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
    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
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

    with Check(
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
    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
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

    with Check(
        "I check that the data inserted into the table was correctly written into the file"
    ):
        if check_clickhouse_version(">=24.10")(self):
            symlink = node.command(
                f"readlink -f /var/lib/clickhouse/data/default/{table0_name}"
            ).output.strip()
            node.command(
                f"cp {symlink} /var/lib/clickhouse/user_files/{table0_name}.Parquet"
            )
        else:
            node.command(
                f"cp /var/lib/clickhouse/data/default/{table0_name}/data.Parquet /var/lib/clickhouse/user_files/{table0_name}.Parquet"
            )

        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table0_name}.Parquet",
            reference_table_name=table0_name,
        )

    with When("I copy of the Parquet source file to a new directory"):
        node.command(f"mkdir /var/lib/clickhouse/user_files/{table1_name}")
        if check_clickhouse_version(">=24.10")(self):
            node.command(
                f"cp {symlink} /var/lib/clickhouse/user_files/{table1_name}/data.Parquet"
            )
        else:
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

    with Check(
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
    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
    node = self.context.node
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I have a table with a `File(Parquet)` engine"):
        table = create_table(
            name=table_name, engine="File(Parquet)", columns=table_columns
        )

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' FORMAT Parquet"
        )

    with Check("I check that the table columns contain correct data"):
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
    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
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

    with Check("I check that data was written into the Parquet file correctly"):
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
    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
    node = self.context.node
    file_name = "file_" + getuid()
    table_name = "table_" + getuid()
    columns = generate_all_column_types(include=parquet_test_columns())
    func_def = ",".join([column.full_definition() for column in columns])
    columns_values = [column.values(row_count=2, cardinality=1) for column in columns]
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

    with Check("I check the specified file has correct data"):
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{file_name}.Parquet",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def insert_into_function_auto_cast_types(self):
    """Check that when data is inserted into `file` table function with automatically defined structure,
    it is written into the source file correctly."""
    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
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
        table.insert_test_data(row_count=2)

    with When("I copy the Parquet file created by the table"):
        if check_clickhouse_version(">=24.10")(self):
            symlink = node.command(
                f"readlink -f /var/lib/clickhouse/data/default/{table_name}"
            ).output.strip()
            node.command(
                f"cp {symlink} /var/lib/clickhouse/user_files/{file_name}.Parquet"
            )
        else:
            node.command(
                f"cp /var/lib/clickhouse/data/default/{table_name}/data.Parquet /var/lib/clickhouse/user_files/{file_name}.Parquet"
            )

    with And("I generate test values"):
        columns_values = [
            column.values(row_count=2, cardinality=1) for column in table.columns
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

    with Check("I check that the created file has correct data"):
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{file_name}.1.Parquet",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import("1.0"))
def select_from_function_manual_cast_types(self):
    """Check that when data is selected from a `file` table function with manually cast column types,
    it is read correctly."""

    if check_clickhouse_version(">=24.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    elif check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
    node = self.context.node
    table_columns = self.context.parquet_table_columns
    table_def = ",".join([column.full_definition() for column in table_columns])

    with Check("I check that the `file` table function reads data correctly"):
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
    if check_clickhouse_version(">=26.1")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=26.1")
    elif check_clickhouse_version("<22.6")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version="<22.6")
    else:
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    table_columns = self.context.parquet_table_columns

    with Check("I check that the `file` table function reads data correctly"):
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


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def date_as_uint16(self):
    """Check that when data is inserted into a `file` table function with `output_format_parquet_date_as_uint16` setting,
    dates are written as UINT16 and can be read back correctly."""
    node = self.context.node
    file_name = f"date_as_uint16_{getuid()}.parquet"

    with Given(
        "I insert data into the `file` table function with `output_format_parquet_date_as_uint16` setting"
    ):
        node.query(
            f"INSERT INTO FUNCTION file('{file_name}') SELECT toDate('2025-08-12') as d",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with Then("I select from the parquet file to verify the data"):
        r = node.query(f"SELECT * FROM file('{file_name}')")
        assert r.output.strip() == "20312", error()

    with And("I describe the parquet file to check the schema"):
        r = node.query(f"DESC file('{file_name}')")
        expected_date_type = (
            "UInt16" if check_clickhouse_version(">=26.1")(self) else "Nullable(UInt16)"
        )
        assert "d" in r.output and expected_date_type in r.output, error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def date_as_uint16_multiple_dates(self):
    """Check that multiple dates are correctly written as UINT16 when using `output_format_parquet_date_as_uint16` setting."""
    node = self.context.node
    file_name = f"date_as_uint16_multiple_{getuid()}.parquet"

    with Given(
        "I insert multiple dates into the `file` table function with `output_format_parquet_date_as_uint16` setting"
    ):
        node.query(
            f"INSERT INTO FUNCTION file('{file_name}') SELECT d FROM (SELECT toDate('1970-01-01') as d UNION ALL SELECT toDate('2025-08-12') UNION ALL SELECT toDate('2100-12-31'))",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with Then("I select from the parquet file to verify the data"):
        r = node.query(f"SELECT * FROM file('{file_name}') ORDER BY d")
        expected_dates = ["0", "20312", "47846"]
        assert r.output.strip().split("\n") == expected_dates, error()

    with And("I describe the parquet file to check the schema"):
        r = node.query(f"DESC file('{file_name}')")
        expected_date_type = (
            "UInt16" if check_clickhouse_version(">=26.1")(self) else "Nullable(UInt16)"
        )
        assert "d" in r.output and expected_date_type in r.output, error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def date_as_uint16_nullable(self):
    """Check that nullable dates are correctly written as UINT16 when using `output_format_parquet_date_as_uint16` setting."""
    node = self.context.node
    file_name = f"date_as_uint16_nullable_{getuid()}.parquet"
    table_name = f"table_{getuid()}"

    with Given("I create a table with nullable Date column"):
        node.query(f"CREATE TABLE {table_name} (d Nullable(Date)) ENGINE = Memory")

    with And("I insert data including NULL values"):
        node.query(
            f"INSERT INTO {table_name} VALUES (toDate('2025-08-12')), (NULL), (toDate('1970-01-01'))"
        )

    with When(
        "I export data to parquet file with `output_format_parquet_date_as_uint16` setting"
    ):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE '/var/lib/clickhouse/user_files/{file_name}' FORMAT Parquet",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with Then("I select from the parquet file to verify the data including NULLs"):
        r = node.query(
            f"SELECT * FROM file('/var/lib/clickhouse/user_files/{file_name}') ORDER BY d NULLS LAST"
        )
        lines = r.output.strip().split("\n")
        assert len(lines) == 3, error()
        assert lines[0] == "0", error()
        assert lines[1] == "20312", error()
        assert lines[2] == "\\N", error()

    with And("I describe the parquet file to check the schema"):
        r = node.query(f"DESC file('/var/lib/clickhouse/user_files/{file_name}')")
        expected_date_type = (
            "UInt16" if check_clickhouse_version(">=26.1")(self) else "Nullable(UInt16)"
        )
        assert "d" in r.output and expected_date_type in r.output, error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def date_as_uint16_round_trip(self):
    """Check that dates written as UINT16 can be read back and written again correctly."""
    node = self.context.node
    file_name1 = f"date_as_uint16_roundtrip1_{getuid()}.parquet"
    file_name2 = f"date_as_uint16_roundtrip2_{getuid()}.parquet"
    table_name = f"table_{getuid()}"

    with Given("I create a table with Date column"):
        node.query(f"CREATE TABLE {table_name} (d Date) ENGINE = Memory")

    with And("I insert test dates"):
        node.query(
            f"INSERT INTO {table_name} VALUES (toDate('1970-01-01')), (toDate('2025-08-12')), (toDate('2100-12-31'))"
        )

    with When(
        "I export data to first parquet file with `output_format_parquet_date_as_uint16` setting"
    ):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE '/var/lib/clickhouse/user_files/{file_name1}' FORMAT Parquet",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with And(
        "I read from the first parquet file and write to a second parquet file with the same setting"
    ):
        node.query(
            f"SELECT * FROM file('/var/lib/clickhouse/user_files/{file_name1}') INTO OUTFILE '/var/lib/clickhouse/user_files/{file_name2}' FORMAT Parquet",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with Then("I verify both files contain the same data"):
        r1 = node.query(
            f"SELECT * FROM file('/var/lib/clickhouse/user_files/{file_name1}') ORDER BY d"
        )
        r2 = node.query(
            f"SELECT * FROM file('/var/lib/clickhouse/user_files/{file_name2}') ORDER BY d"
        )
        assert r1.output.strip() == r2.output.strip(), error()

    with And(
        "I verify the original table data matches the round-trip data by converting UInt16 back to Date"
    ):
        r_original = node.query(f"SELECT * FROM {table_name} ORDER BY d")
        r_final = node.query(
            f"SELECT toDate('1970-01-01') + INTERVAL d DAY FROM file('/var/lib/clickhouse/user_files/{file_name2}') ORDER BY d"
        )
        assert r_original.output.strip() == r_final.output.strip(), error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def date_as_uint16_file_engine(self):
    """Check that dates are correctly written as UINT16 when using `File(Parquet)` engine with `output_format_parquet_date_as_uint16` setting."""
    node = self.context.node
    table_name = f"table_{getuid()}"

    with Given("I create a table with `File(Parquet)` engine"):
        create_table(
            name=table_name,
            engine="File(Parquet)",
            columns=[Column(name="d", datatype=Date())],
        )

    with When(
        "I insert data into the table with `output_format_parquet_date_as_uint16` setting"
    ):
        node.query(
            f"INSERT INTO {table_name} VALUES (toDate('1970-01-01')), (toDate('2025-08-12')), (toDate('2100-12-31'))",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with Then("I select from the table to verify the data"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY d")
        expected_dates = ["1970-01-01", "2025-08-12", "2100-12-31"]
        assert r.output.strip().split("\n") == expected_dates, error()

    with And("I check the parquet file schema"):
        if check_clickhouse_version(">=24.10")(self):
            symlink = node.command(
                f"readlink -f /var/lib/clickhouse/data/default/{table_name}"
            ).output.strip()
            parquet_file = symlink
        else:
            parquet_file = f"/var/lib/clickhouse/data/default/{table_name}/data.Parquet"

        r = node.query(f"DESC file('{parquet_file}')")
        expected_date_type = (
            "UInt16" if check_clickhouse_version(">=26.1")(self) else "Nullable(UInt16)"
        )
        assert "d" in r.output and expected_date_type in r.output, error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def date_as_uint16_edge_cases(self):
    """Check that edge case dates (epoch, min/max valid dates) are correctly written as UINT16."""
    node = self.context.node
    file_name = f"date_as_uint16_edges_{getuid()}.parquet"

    with Given(
        "I insert edge case dates into the `file` table function with `output_format_parquet_date_as_uint16` setting"
    ):
        node.query(
            f"INSERT INTO FUNCTION file('{file_name}') SELECT d FROM (SELECT toDate('1970-01-01') as d UNION ALL SELECT toDate('1970-01-02') UNION ALL SELECT toDate('2149-06-05'))",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with Then("I select from the parquet file to verify the edge case data"):
        r = node.query(f"SELECT * FROM file('{file_name}') ORDER BY d")
        expected_dates = ["0", "1", "65534"]
        assert r.output.strip().split("\n") == expected_dates, error()

    with And("I describe the parquet file to check the schema"):
        r = node.query(f"DESC file('{file_name}')")
        expected_date_type = (
            "UInt16" if check_clickhouse_version(">=26.1")(self) else "Nullable(UInt16)"
        )
        assert "d" in r.output and expected_date_type in r.output, error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"))
def date_as_uint16_with_other_columns(self):
    """Check that dates are correctly written as UINT16 when mixed with other column types."""
    node = self.context.node
    file_name = f"date_as_uint16_mixed_{getuid()}.parquet"

    with Given(
        "I insert data with date and other columns into the `file` table function with `output_format_parquet_date_as_uint16` setting"
    ):
        node.query(
            f"INSERT INTO FUNCTION file('{file_name}') SELECT toDate('2025-08-12') as d, 42 as i, 'test' as s",
            settings=[("output_format_parquet_date_as_uint16", 1)],
        )

    with Then("I select from the parquet file to verify all columns"):
        r = node.query(f"SELECT * FROM file('{file_name}')")
        assert "20312" in r.output and "42" in r.output and "test" in r.output, error()

    with And("I describe the parquet file to check the schema"):
        r = node.query(f"DESC file('{file_name}')")
        expected_date_type = (
            "UInt16" if check_clickhouse_version(">=26.1")(self) else "Nullable(UInt16)"
        )
        assert "d" in r.output and expected_date_type in r.output, error()
        assert "i" in r.output, error()
        assert "s" in r.output, error()


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File("1.0"))
def engine(self):
    """Check that table with `File(Parquet)` engine correctly reads and writes Parquet format."""
    with Pool(5) as executor:
        Scenario(
            run=insert_into_engine,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_from_engine,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=engine_to_file_to_engine,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=insert_into_engine_from_file,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=engine_select_output_to_file,
            parallel=True,
            executor=executor,
        )
        join()


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File("1.0"))
def function(self):
    """Check that `file` table function correctly reads and writes Parquet format."""
    with Pool(5) as executor:
        Scenario(
            run=insert_into_function_manual_cast_types,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=insert_into_function_auto_cast_types,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_from_function_manual_cast_types,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_from_function_auto_cast_types,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=date_as_uint16,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=date_as_uint16_multiple_dates,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=date_as_uint16_nullable,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=date_as_uint16_round_trip,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=date_as_uint16_edge_cases,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=date_as_uint16_with_other_columns,
            parallel=True,
            executor=executor,
        )
        join()


@TestFeature
@Name("file")
def feature(self, node="clickhouse1"):
    """Run checks for ClickHouse using Parquet format using `File(Parquet)` table engine and `file` table function."""
    self.context.node = self.context.cluster.node(node)

    with Pool(2) as executor:
        Feature(run=engine, parallel=True, executor=executor)
        Feature(run=function, parallel=True, executor=executor)
        join()
