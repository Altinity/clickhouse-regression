from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"))
def insert_into_engine(self):
    """Check that when data is inserted into a table with `S3` engine, it is written into the source file correctly."""
    self.context.snapshot_id = get_snapshot_id()
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()

    with Given("I have a table with S3 engine"):
        table = create_table(
            name=table_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table.insert_test_data()

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file_on_s3(
            file=table_name + ".Parquet",
            compression_type=f"'{compression_type.lower()}'",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"))
def select_from_engine(self):
    """Check that when a table with `S3` engine is attached on top of a Parquet file, it reads the data correctly."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    compression_type = self.context.compression_type
    uid = getuid()
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I upload parquet data to s3"):
        copy_file_to_host(
            src_node="clickhouse1",
            src_path=f"/var/lib/test_files/data_{compression_type}.Parquet",
            host_filename=f"data_{uid}_{compression_type}.Parquet",
        )
        upload_file_to_s3(
            file_src=f"/tmp/test_files/data_{uid}_{compression_type}.Parquet",
            file_dest=f"data/parquet/{table_name}.Parquet",
        )

    with When("I create a table with a `S3` engine on top of a Parquet file"):
        table = create_table(
            name=table_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet')",
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
def engine_to_file_to_engine(self):
    """Check that when data is inserted into a table with `S3` engine,
    the data can be read back correctly from the source file using a different table with `S3` engine.
    """
    self.context.snapshot_id = get_snapshot_id()
    compression_type = self.context.compression_type
    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()
    columns = generate_all_column_types(include=parquet_test_columns())

    with Given("I have a table with `S3` engine"):
        table0 = create_table(
            name=table0_name,
            engine=f"S3('{self.context.uri}{table0_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
            columns=columns,
        )

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table0.insert_test_data()

    with Check(
        "I check that the data inserted into the table was correctly written into the file"
    ):
        check_source_file_on_s3(
            file=table0_name + ".Parquet",
            compression_type=f"'{compression_type.lower()}'",
            reference_table_name=table0_name,
        )

    with When("I create a table with a `S3` engine on top of a Parquet file"):
        table1 = create_table(
            name=table1_name,
            engine=f"S3('{self.context.uri}{table0_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
            columns=columns,
        )

    with Check(
        "I check that the table reads the data correctly by checking the table columns"
    ):
        with Pool(3) as executor:
            for column in columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM {table1_name}"
                )
            join()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"))
def insert_into_engine_from_file(self):
    """Check that that data read from a Parquet file using the `INFILE` clause in `INSERT` query is
    correctly written into a table with a `S3` engine."""
    self.context.snapshot_id = get_snapshot_id()
    compression_type = self.context.compression_type
    node = self.context.node
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I create a table with a `S3` engine"):
        table = create_table(
            name=table_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet')",
            columns=table_columns,
        )

    with When("I insert data into the table from a Parquet file"):
        node.command(
            f"cp /var/lib/test_files/data_{compression_type}.Parquet /var/lib/clickhouse/user_files/data_{compression_type}.Parquet"
        )
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' FORMAT Parquet",
            settings=[("allow_suspicious_low_cardinality_types", 1)],
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
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"))
def engine_select_output_to_file(self):
    """Check that data is correctly written into a Parquet file when using `SELECT` query with `OUTFILE` clause on a table with `S3` engine."""
    self.context.snapshot_id = get_snapshot_id()
    compression_type = self.context.compression_type
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a table with `S3` engine"):
        table = create_table(
            name=table_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table.insert_test_data()

    with When("I select data from the table and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE '/var/lib/clickhouse/user_files/{table_name}.Parquet' COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Check(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file_on_s3(
            file=table_name + ".Parquet",
            compression_type=f"'{compression_type.lower()}'",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"),
)
def insert_into_function(self):
    """Check that when data is inserted into `s3` table function with manually defined structure,
    it is written into the source file correctly.
    """
    self.context.snapshot_id = get_snapshot_id()
    compression_type = self.context.compression_type
    node = self.context.node
    file_name = "file_" + getuid()

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

    with When("I insert test data into `s3` table function in Parquet format"):
        node.query(
            f"INSERT INTO FUNCTION s3('{self.context.uri}{file_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{func_def}', '{compression_type.lower()}') VALUES {','.join(total_values)}",
            settings=[("allow_suspicious_low_cardinality_types", 1)],
        )

    with Check(
        "I check that the data inserted into the table function was correctly written to the file"
    ):
        check_source_file_on_s3(
            file=file_name + ".Parquet",
            compression_type=f"'{compression_type.lower()}'",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_TypeConversionFunction("1.0"),
)
def select_from_function_manual_cast_types(self):
    """Check that when data is selected from an `s3` table function with manually cast column types,
    it is read correctly.
    """
    self.context.snapshot_id = get_snapshot_id()
    compression_type = self.context.compression_type
    uid = getuid()
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns
    table_def = ",".join([column.full_definition() for column in table_columns])

    with Given("I upload parquet data to s3"):
        copy_file_to_host(
            src_node="clickhouse1",
            src_path=f"/var/lib/test_files/data_{compression_type}.Parquet",
            host_filename=f"data_{uid}_{compression_type}.Parquet",
        )
        upload_file_to_s3(
            file_src=f"/tmp/test_files/data_{uid}_{compression_type}.Parquet",
            file_dest=f"data/parquet/{table_name}.Parquet",
        )

    with Check("I check that the `s3` table function reads data correctly"):
        with Pool(3) as executor:
            for column in table_columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM \
                    s3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{table_def}')"
                )
            join()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_AutoTypecast("1.0"),
)
def select_from_function_auto_cast_types(self):
    """Check that when data is selected from an `s3` table function with automatic cast column types,
    it is read correctly.
    """
    self.context.snapshot_id = get_snapshot_id(clickhouse_version="<22.6")
    compression_type = self.context.compression_type
    uid = getuid()
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I upload parquet data to s3"):
        copy_file_to_host(
            src_node="clickhouse1",
            src_path=f"/var/lib/test_files/data_{compression_type}.Parquet",
            host_filename=f"data_{uid}_{compression_type}.Parquet",
        )
        upload_file_to_s3(
            file_src=f"/tmp/test_files/data_{uid}_{compression_type}.Parquet",
            file_dest=f"data/parquet/{table_name}.Parquet",
        )

    with Check("I check that the `s3` table function reads data correctly"):
        with Pool(3) as executor:
            for column in table_columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM \
                    s3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet')"
                )
            join()


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_S3("1.0"))
def engine(self):
    """Check that table with `S3` engine correctly reads and writes Parquet format."""

    with Pool(2) as executor:
        Scenario(run=insert_into_engine, parallel=True, executor=executor)
        Scenario(run=select_from_engine, parallel=True, executor=executor)
        Scenario(run=engine_to_file_to_engine, parallel=True, executor=executor)
        Scenario(run=insert_into_engine_from_file, parallel=True, executor=executor)
        Scenario(run=engine_select_output_to_file, parallel=True, executor=executor)
        join()


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"))
def function(self):
    """Check that `s3` table function correctly reads and writes Parquet format."""

    with Pool(3) as executor:
        Scenario(run=insert_into_function, parallel=True, executor=executor)
        Scenario(
            run=select_from_function_manual_cast_types, parallel=True, executor=executor
        )
        Scenario(
            run=select_from_function_auto_cast_types, parallel=True, executor=executor
        )
        join()


@TestOutline
def outline(self, compression_type):
    """Run checks for ClickHouse using Parquet format using `S3` table engine and `s3` table function."""
    self.context.compression_type = compression_type
    self.context.node = self.context.cluster.node("clickhouse1")

    Suite(run=engine)
    Suite(run=function)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0"))
def none(self):
    """Run checks for ClickHouse Parquet format using `S3` table engine and `s3` table function
    with NONE compression type."""
    outline(compression_type="NONE")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"))
def gzip(self):
    """Run checks for ClickHouse Parquet format using `S3` table engine and `s3` table function
    with GZIP compression type."""
    outline(compression_type="GZIP")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4(self):
    """Run checks for ClickHouse Parquet format using `S3` table engine and `s3` table function
    with LZ4 compression type."""
    outline(compression_type="LZ4")


@TestFeature
@Name("s3")
def feature(self):
    """Run checks for ClickHouse using Parquet format using `S3` table engine and `s3` table function
    using different compression types."""

    with Feature("compression type"):
        with Pool(3) as executor:
            Feature(name="=NONE ", run=none, parallel=True, executor=executor)
            Feature(name="=GZIP ", run=gzip, parallel=True, executor=executor)
            Feature(name="=LZ4 ", run=lz4, parallel=True, executor=executor)
            join()
