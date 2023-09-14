from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_PostgreSQL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
def postgresql_engine_to_parquet_file_to_postgresql_engine(self):
    """Check that ClickHouse reads data from a `PostgreSQL` table engine into a Parquet file and
    writes the data back into a `PostgreSQL` table engine correctly."""
    self.context.snapshot_id = get_snapshot_id()
    postgresql_node = self.context.cluster.node("postgres1")
    node = self.context.node
    compression_type = self.context.compression_type
    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()
    columns = postgresql_test_columns()
    table_def = (
        "(" + ",".join([postgresql_conversion(column) for column in columns]) + ")"
    )
    path = f"'/var/lib/clickhouse/user_files/{table0_name}_{compression_type}.Parquet'"

    with Given(f"I have a table {table0_name} on PostgreSQL"):
        postgresql_node.command(
            f"PGPASSWORD=password psql -U user -d default -c 'CREATE TABLE {table0_name} {table_def};'"
        )

    with And(f"I have another table {table1_name} on PostgreSQL"):
        postgresql_node.command(
            f"PGPASSWORD=password psql -U user -d default -c 'CREATE TABLE {table1_name} {table_def};'"
        )

    with And(
        f"I have a table {table0_name} on ClickHouse with a `PostgreSQL` table engine"
    ):
        table0 = create_table(
            name=table0_name,
            engine=f"PostgreSQL('postgres1:5432', 'default', '{table0_name}', 'user', 'password')",
            columns=columns,
        )

    with And(
        f"I have another table {table1_name} on ClickHouse with a `PostgreSQL` table engine"
    ):
        table1 = create_table(
            name=table1_name,
            engine=f"PostgreSQL('postgres1:5432', 'default', '{table1_name}', 'user', 'password')",
            columns=columns,
        )

    with When(
        "I insert test data into the PostgreSQL table through the ClickHouse table"
    ):
        table0.insert_test_data()

    with And(f"I select data from {table0_name} and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM {table0_name} INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with And(f"I read the data from the Parquet file into {table1_name}"):
        node.query(
            f"INSERT INTO {table1_name} FROM INFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then(f"I check the data on the table"):
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
    RQ_SRS_032_ClickHouse_Parquet_TableFunctions_PostgreSQL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
def postgresql_function_to_parquet_file_to_postgresql_function(self):
    """Check that ClickHouse reads data from a `postgresql` table function into a Parquet file and
    writes the data back into a `postgresql` table function correctly."""
    self.context.snapshot_id = get_snapshot_id()
    postgresql_node = self.context.cluster.node("postgres1")
    node = self.context.node
    compression_type = self.context.compression_type
    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()
    columns = postgresql_test_columns()
    table_def = (
        "(" + ",".join([postgresql_conversion(column) for column in columns]) + ")"
    )
    path = f"'/var/lib/clickhouse/user_files/{table0_name}_{compression_type}.Parquet'"

    with Given(f"I have a table {table0_name} on PostgreSQL"):
        postgresql_node.command(
            f"PGPASSWORD=password psql -U user -d default -c 'CREATE TABLE {table0_name} {table_def};'"
        )

    with And(f"I have another table {table1_name} on PostgreSQL"):
        postgresql_node.command(
            f"PGPASSWORD=password psql -U user -d default -c 'CREATE TABLE {table1_name} {table_def};'"
        )

    with And("I generate test values"):
        columns_values = [
            column.values(row_count=5, cardinality=10)
            for column in postgresql_test_columns()
        ]

    with And(
        f"I populate {table0_name} with test data using the `postgresql` table funtion"
    ):
        node.query(
            f"""
            INSERT INTO FUNCTION postgresql('postgres1:5432', 'default', '{table0_name}', 'user', 'password')
            VALUES {"(" + ",".join([next(column_values) for column_values in columns_values]) + ")"}
            """
        )

    with When("I select data from the table function and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM postgresql('postgres1:5432', 'default', '{table0_name}', 'user', 'password') INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with And(
        "I read the data from the Parquet file into the other MySQL table using the `postgresql` table function"
    ):
        node.query(
            f"INSERT INTO FUNCTION postgresql('postgres1:5432', 'default', '{table1_name}', 'user', 'password') FROM INFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then(f"I check the data on the table"):
        with Pool(3) as executor:
            for column in columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM postgresql('postgres1:5432', 'default', {table1_name}, 'user', 'password')"
                )
            join()


@TestOutline(Feature)
def outline(self, compression_type):
    """Run checks for ClickHouse using Parquet format using `PostgreSQL` table engine and `postgresql` table function
    using specified compression type."""
    self.context.compression_type = compression_type

    Scenario(run=postgresql_engine_to_parquet_file_to_postgresql_engine)
    Scenario(run=postgresql_function_to_parquet_file_to_postgresql_function)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0"))
def none(self):
    """Run checks for ClickHouse using Parquet format using `PostgreSQL` table engine and `postgresql` table function
    using the NONE compression type."""
    outline(compression_type="NONE")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"))
def gzip(self):
    """Run checks for ClickHouse using Parquet format using `PostgreSQL` table engine and `postgresql` table function
    using the GZIP compression type."""
    outline(compression_type="GZIP")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4(self):
    """Run checks for ClickHouse using Parquet format using `PostgreSQL` table engine and `postgresql` table function
    using the LZ4 compression type."""
    outline(compression_type="LZ4")


@TestFeature
@Name("postgresql")
def feature(self):
    """Run checks for ClickHouse using Parquet format using `PostgreSQL` table engine and `postgresql` table function
    using different compression types."""
    self.context.node = self.context.cluster.node("clickhouse1")

    with Feature("compression type"):
        with Pool(3) as executor:
            Feature(
                name="=NONE ",
                run=none,
                parallel=self.context.parallel_run,
                executor=executor,
            )
            Feature(
                name="=GZIP ",
                run=gzip,
                parallel=self.context.parallel_run,
                executor=executor,
            )
            Feature(
                name="=LZ4 ",
                run=lz4,
                parallel=self.context.parallel_run,
                executor=executor,
            )
            join()
