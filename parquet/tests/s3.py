from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestScenario
def insert_into_engine(self):
    """Check that when data is inserted into a table with `S3` engine, it is written into the source file correctly."""

    compression_type = self.context.compression_type
    table_name = "table_" + getuid()

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with And("I have a table with S3 engine"):
        table(
            name=table_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
        )

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table_name)

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file_on_s3(
            file=table_name + ".Parquet", compression_type=compression_type
        )


@TestScenario
def select_from_engine(self):
    """Check that when a table with `S3` engine is attached on top of a Parquet file, it reads the data correctly."""

    xfail("TODO: create Parquet files")

    compression_type = self.context.compression_type
    table_name = "table_" + getuid()

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with And("I upload parquet data to s3"):
        upload_file_to_s3(
            file_src="/var/lib/clickhouse/user_files/data.Parquet",
            file_dest=f"/{table_name}/data.Parquet",
        )

    with When("I attach a table with a `S3` engine on top of a Parquet file"):
        table(
            name=table_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
            create="ATTACH",
        )

    with Then("I check that the table reads the data correctly"):
        check_query_output(query=f"SELECT * FROM {table_name}")


@TestScenario
def engine_to_file_to_engine(self):
    """Check that when data is inserted into a table with `S3` engine,
    the data can be read back correctly from the source file using a different table with `S3` engine."""

    compression_type = self.context.compression_type
    node = self.context.node

    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with And("I have a table with S3 engine"):
        table(
            name=table0_name,
            engine=f"S3('{self.context.uri}{table0_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
        )

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table0_name)

    with Then(
        "I check that the data inserted into the table was correctly written into the file"
    ):
        check_source_file_on_s3(file=table0_name)

    with When("I attach a table with a `S3` engine on top of a Parquet file"):
        table(
            name=table1_name,
            engine=f"S3('{self.context.uri}{table1_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
            create="CREATE",
        )

    with Then(
        "I check that the new table is able to read the data from the file correctly"
    ):
        check_query_output(query=f"SELECT * FROM {table1_name}")


@TestScenario
def insert_into_engine_from_file(self):
    """Check that that data read from a Parquet file using the `INFILE` clause in `INSERT` query is
    correctly written into a table with a `S3` engine.
    """

    xfail("TODO: create parquet test files.")

    compression_type = self.context.compression_type
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with And("I have a table with S3 engine"):
        table(
            name=table0_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
        )

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data.Parquet' COMPRESSION '{compression_type}' FORMAT Parquet"
        )

    with Then("I check that the table contains correct data"):
        check_query_output(query=f"SELECT * FROM {table_name}")


@TestScenario
def engine_select_output_to_file(self):
    """Check that data is correctly written into a Parquet file when using `SELECT` query with `OUTFILE` clause on a table with `S3` engine."""

    compression_type = self.context.compression_type
    node = self.context.node
    client = self.context.client()
    table_name = "table_" + getuid()

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with And("I have a table with S3 engine"):
        table(
            name=table_name,
            engine=f"S3('{self.context.uri}{table_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
        )

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table_name)

    with When("I select data from the table and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE '/var/lib/clickhouse/user_files/{table_name}.Parquet' COMPRESSION '{compression_type}' FORMAT Parquet"
        )

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file_on_s3(client=client, file=table_name)


@TestScenario
def insert_into_function_manual_cast_types(self):
    """Check that when data is inserted into `s3` table function with manually defined structure,
    it is written into the source file correctly.
    """

    compression_type = self.context.compression_type
    file_name = "file_" + getuid()
    client = self.context.client()

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with When("I insert test data into s3 table function in Parquet format"):
        insert_test_data(
            name=f"FUNCTION s3('{self.context.uri}{file_name}', '{self.context.secret_access_key}', '{self.context.access_key_id}', 'Parquet', '{','.join(generate_all_column_types())}', '{compression_type}')"
        )

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file_on_s3(client=client, file=f"{file_name}.Parquet")


@TestScenario
def insert_into_function_auto_cast_types(self):
    """Check that when data is inserted into `s3` table function with automatically defined structure,
    it is written into the source file correctly.
    """

    compression_type = self.context.compression_type
    file_name = "file_" + getuid()
    client = self.context.client()

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with When("I insert test data into s3 table function in Parquet format"):
        insert_test_data(
            name=f"FUNCTION s3('{self.context.uri}{file_name}', '{self.context.secret_access_key}', '{self.context.access_key_id}', 'Parquet', '{compression_type}')"
        )

    with Then(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file_on_s3(file=f"{file_name}.Parquet")


@TestScenario
def select_from_function_manual_cast_types(self):
    """Check that when data is selected from an `s3` table function with manually cast column types,
    it is read correctly.
    """

    compression_type = self.context.compression_type

    xfail("TODO: add parquet files")

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with And("I upload parquet data to s3"):
        upload_file_to_s3(
            file_src="/var/lib/clickhouse/user_files/data.Parquet",
            file_dest=f"/{table_name}/data.Parquet",
            client=client,
        )

    with Then("I check that the `file` table function contains correct data"):
        check_query_output(
            query=f"SELECT * FROM s3('{self.context.uri}{table_name}/data.Parquet', '{self.context.secret_access_key}', '{self.context.access_key_id}', 'Parquet', '{','.join(generate_all_column_types())}', '{compression_type}')"
        )


@TestScenario
def select_from_function_auto_cast_types(self):
    """Check that when data is selected from an `s3` table function with automatic cast column types,
    it is read correctly.
    """

    compression_type = self.context.compression_type

    xfail("TODO: add parquet files")

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with And("I upload parquet data to s3"):
        upload_file_to_s3(
            file_src="/var/lib/clickhouse/user_files/data.Parquet",
            file_dest=f"/{table_name}/data.Parquet",
            client=client,
        )

    with Then("I check that the `file` table function contains correct data"):
        check_query_output(
            query=f"SELECT * FROM s3('{self.context.uri}{table_name}/data.Parquet', '{self.context.secret_access_key}', '{self.context.access_key_id}', 'Parquet', '{compression_type}')"
        )


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_S3("1.0"))
def engine(self):
    """Check that table with `S3` engine correctly reads and writes Parquet format."""

    Scenario(run=insert_into_engine)
    Scenario(run=select_from_engine)
    Scenario(run=engine_to_file_to_engine)
    Scenario(run=insert_into_engine_from_file)
    Scenario(run=engine_select_output_to_file)


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3("1.0"))
def function(self):
    """Check that `s3` table function correctly reads and writes Parquet format."""
    Scenario(run=insert_into_function_manual_cast_types)
    Scenario(run=insert_into_function_auto_cast_types)
    Scenario(run=select_from_function_manual_cast_types)
    Scenario(run=select_from_function_auto_cast_types)


@TestOutline(Feature)
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
@Name("s3")
def feature(self, compression_type):
    """Run checks for clickhouse using Parquet format using s3 storage."""

    self.context.compression_type = compression_type
    self.context.node = self.context.cluster.node("clickhouse1")

    Suite(run=engine)
    Suite(run=function)
