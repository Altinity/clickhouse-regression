from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Insert("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Read("1.0"),
)
def insert_into_function(self):
    """Check that when data is inserted into `remote` table function it is written into the source file correctly."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I have a table"):
        table = create_table(name=table_name, engine="Memory", columns=table_columns)

    with And("I have a Parquet file"):
        node.command(
            f"cp /var/lib/test_files/data_{compression_type}.Parquet /var/lib/clickhouse/user_files/data_{compression_type}.Parquet"
        )

    with And("I read the data from the Parquet file into the `remote` table function"):
        node.query(
            f"INSERT INTO FUNCTION remote('127.0.0.1', 'default', '{table_name}') FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' FORMAT Parquet"
        )

    with Then("I check the table has correct data"):
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
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Select("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Write("1.0"),
)
def select_from_function(self):
    """Check that when data is selected from a `remote` table function into a Parquet file it is written correctly."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()
    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet'"
    columns = generate_all_column_types(include=parquet_test_columns())

    with Given(f"I have two tables"):
        table = create_table(name=table_name, engine="Memory", columns=columns)

    with And("I populate the first table with test values"):
        table.insert_test_data()

    with When(
        "I select data from the `remote` table function and write it into a Parquet file"
    ):
        node.query(
            f"SELECT * FROM remote('127.0.0.1', 'default', '{table_name}') INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then("I check the Parquet file"):
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet",
            compression=f"'{compression_type.lower()}'",
        )


@TestOutline(Feature)
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
@Name("remote")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_Remote("1.0"))
def feature(self, compression_type):
    """Run checks for ClickHouse using Parquet format using `remote` table function."""
    self.context.compression_type = compression_type
    self.context.node = self.context.cluster.node("clickhouse1")

    Scenario(run=insert_into_function)
    Scenario(run=select_from_function)
