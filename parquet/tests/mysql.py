from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MySQL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
def mysql_engine_to_parquet_file_to_mysql_engine(self):
    """Check that ClickHouse reads data from a table with a MySQL table engine into a Parquet file and back into a table with a MySQL table engine correctly."""
    self.context.snapshot_id = get_snapshot_id()
    mysql_node = self.context.cluster.node("mysql1")
    node = self.context.node
    compression_type = self.context.compression_type

    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()
    columns = mysql_test_columns()
    table_def = "(" + ",".join([mysql_conversion(column) for column in columns]) + ")"
    path = f"'/var/lib/clickhouse/user_files/{table0_name}_{compression_type}.Parquet'"

    with Given(f"I have two tables in MySQL"):
        mysql_node.command(
            f"mysql -D default -u user --password=password -e 'CREATE TABLE default.{table0_name} {table_def};'"
        )
        mysql_node.command(
            f"mysql -D default -u user --password=password -e 'CREATE TABLE default.{table1_name} {table_def};'"
        )

    with And(f"I have two tables in ClickHouse with a MySQL table engine"):
        table0 = create_table(
            name=table0_name,
            engine=f"MySQL('mysql1:3306', 'default', '{table0_name}', 'user', 'password')",
            columns=columns,
        )
        table1 = create_table(
            name=table1_name,
            engine=f"MySQL('mysql1:3306', 'default', '{table1_name}', 'user', 'password')",
            columns=columns,
        )

    with When("I populate the MySQL table with test data through the ClickHouse table"):
        table0.insert_test_data(row_count=1, cardinality=1)

    with And(
        "I select data from the ClickHouse table and write it into a Parquet file"
    ):
        node.query(
            f"SELECT * FROM {table0_name} INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with And("I write the data from the Parquet file into the other ClickHouse table"):
        node.query(
            f"INSERT INTO {table1_name} FROM INFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then("I check the data on the second table"):
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
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_TableFunctions_MySQL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
def mysql_function_to_parquet_file_to_mysql_function(self):
    """Check that ClickHouse correctly writes data from mysql table function into parquet file and back into mysql table function."""
    self.context.snapshot_id = get_snapshot_id()
    mysql_node = self.context.cluster.node("mysql1")
    node = self.context.node
    compression_type = self.context.compression_type

    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()
    columns = mysql_test_columns()
    table_def = "(" + ",".join([mysql_conversion(column) for column in columns]) + ")"
    path = f"'/var/lib/clickhouse/user_files/{table0_name}_{compression_type}.Parquet'"

    with Given(f"I have two tables in MySQL"):
        mysql_node.command(
            f"mysql -D default -u user --password=password -e 'CREATE TABLE default.{table0_name} {table_def};'"
        )
        mysql_node.command(
            f"mysql -D default -u user --password=password -e 'CREATE TABLE default.{table1_name} {table_def};'"
        )

    with And("I generate test data"):
        columns_values = [
            column.values(row_count=1, cardinality=1) for column in mysql_test_columns()
        ]

    with And(
        "I populate one of the mysql tables with the test data using the `mysql` table funtion"
    ):
        node.query(
            f"""
            INSERT INTO FUNCTION mysql('mysql1:3306', 'default', '{table0_name}', 'user', 'password')
            VALUES {"(" + ",".join([next(column_values) for column_values in columns_values]) + ")"}
            """
        )

    with When(
        "I select data from the `mysql` table function and write it into a Parquet file"
    ):
        node.query(
            f"SELECT * FROM mysql('mysql1:3306', 'default', '{table0_name}', 'user', 'password') INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with And(
        "I read the data from the Parquet file into the other MySQL table using the `mysql` table function"
    ):
        node.query(
            f"INSERT INTO FUNCTION mysql('mysql1:3306', 'default', '{table1_name}', 'user', 'password') FROM INFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then("I check the data on the second table"):
        with Pool(3) as executor:
            for column in columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM mysql('mysql1:3306', 'default', '{table1_name}', 'user', 'password')"
                )
            join()


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
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"),
            ),
        ),
    ],
)
@Name("mysql")
def feature(self, compression_type):
    """Run checks for clickhouse using Parquet format using `MySQL` table engine and `mysql` table function."""
    self.context.compression_type = compression_type
    self.context.node = self.context.cluster.node("clickhouse1")

    Scenario(run=mysql_engine_to_parquet_file_to_mysql_engine)
    Scenario(run=mysql_function_to_parquet_file_to_mysql_function)
