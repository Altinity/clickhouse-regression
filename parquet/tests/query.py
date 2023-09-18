from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Memory("1.0"))
def insert_into_memory_table_from_file(self):
    """Insert data from Parquet files into table with Memory engine using FROM INFILE clause."""
    engine = "Memory"
    Scenario(test=insert_into_table_from_file)(engine=engine)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_MergeTree("1.0"))
def insert_into_mergetree_table_from_file(self):
    """Insert data from Parquet files into table with MergeTree engine using FROM INFILE clause."""
    engine = "MergeTree() ORDER BY uint8"
    Scenario(test=insert_into_table_from_file)(engine=engine)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplicatedMergeTree("1.0")
)
def insert_into_replicated_mergetree_table_from_file(self):
    """Insert data from Parquet files into table with ReplicatedMergeTree engine using FROM INFILE clause."""
    table_name = "table_" + getuid()
    engine = (
        "ReplicatedMergeTree('/clickhouse/tables/{shard}/"
        + table_name
        + "', '{replica}') ORDER BY uint8"
    )
    Scenario(test=insert_into_table_from_file)(engine=engine, table_name=table_name)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed("1.0"))
def insert_into_distributed_table_from_file(self):
    """Insert data from Parquet files into table with Distributed engine using FROM INFILE clause."""
    table_name = "table_" + getuid()
    dist_table_name = "dist_table_" + getuid()
    engine = f"Distributed(replicated_cluster, default, {dist_table_name})"

    with Given("I have a table for the distributed table to look at"):
        create_table(
            name=dist_table_name,
            engine="Memory",
            columns=self.context.parquet_table_columns,
        )

    Scenario(test=insert_into_table_from_file)(engine=engine, table_name=table_name)


@TestOutline
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
def insert_into_table_from_file(self, engine, table_name=None):
    """Insert data from Parquet files into tables with different engines using FROM INFILE clause."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    compression_type = self.context.compression_type
    table_columns = self.context.parquet_table_columns

    if table_name is None:
        table_name = "table_" + getuid()

    with Given(f"I have a table with a {engine} engine"):
        create_table(
            name=table_name,
            engine=engine,
            columns=table_columns,
        )

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' FORMAT Parquet"
        )

    with Check("I check that the table contains correct data"):
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
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Memory("1.0"))
def select_from_memory_table_into_file(self):
    """Select data from table with Memory engine and write to Parquet file using INTO OUTFILE clause."""
    engine = "Memory"
    Scenario(test=select_from_table_into_file)(engine=engine)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_MergeTree("1.0"))
def select_from_mergetree_table_into_file(self):
    """Select data from table with MergeTree engine and write to Parquet file using INTO OUTFILE clause."""
    engine = "MergeTree() ORDER BY uint8"
    Scenario(test=select_from_table_into_file)(engine=engine)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplicatedMergeTree("1.0")
)
def select_from_replicated_mergetree_table_into_file(self):
    """Select data from table with ReplicatedMergeTree engine and write to Parquet file using INTO OUTFILE clause."""
    table_name = "table_" + getuid()
    engine = (
        "ReplicatedMergeTree('/clickhouse/tables/{shard}/"
        + table_name
        + "', '{replica}') ORDER BY uint8"
    )
    Scenario(test=select_from_table_into_file)(engine=engine, table_name=table_name)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed("1.0"))
def select_from_distributed_table_into_file(self):
    """Select data from table with Distributed engine and write to Parquet file using INTO OUTFILE clause."""
    table_name = "table_" + getuid()
    dist_table_name = "dist_table_" + getuid()
    engine = f"Distributed(replicated_cluster, default, {dist_table_name})"

    with Given("I have a table for the distributed table to look at"):
        create_table(
            name=dist_table_name,
            engine="Memory",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    Scenario(test=select_from_table_into_file)(engine=engine, table_name=table_name)


@TestOutline
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
def select_from_table_into_file(self, engine, table_name=None):
    """Select data from tables with different engines and write to Parquet files using INTO OUTFILE clause."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    compression_type = self.context.compression_type

    if table_name is None:
        table_name = "table_" + getuid()

    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet'"

    with Given(f"I have a table with a {engine} engine"):
        table = create_table(
            name=table_name,
            engine=engine,
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with And(
        "I populate table with test data",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
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
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_Select_MaterializedView("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
def select_from_mat_view_into_file(self):
    """Select data from materialized view and write to Parquet files using INTO OUTFILE clause."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()
    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet{'.' + compression_type if compression_type != 'none' else ''}'"

    with Given("I have a table with a Memory engine"):
        table = create_table(
            name=table_name,
            engine="Memory",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    try:
        with And("I have a materialized view on the table"):
            node.query(
                f"CREATE MATERIALIZED VIEW {table_name}_view ENGINE = Memory AS SELECT * FROM {table_name}",
                settings=[("allow_suspicious_low_cardinality_types", 1)],
            )

        with And(
            "I populate table with test data",
            description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
        ):
            table.insert_test_data()

        with When(
            "I select data from the materialized view and write it into a Parquet file"
        ):
            node.query(
                f"SELECT * FROM {table_name}_view INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
            )

        with Check("I check that data was written into the Parquet file correctly"):
            node.command(
                f"cp {path} /var/lib/clickhouse/user_files/{table_name}.Parquet"
            )
            check_source_file(
                path=f"/var/lib/clickhouse/user_files/{table_name}.Parquet",
                compression=f"'{compression_type.lower()}'",
                reference_table_name=table_name,
            )

    finally:
        with Finally("I drop the materialized view"):
            node.query(f"DROP VIEW IF EXISTS {table_name}_view")


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Projections("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported("1.0"),
)
def insert_into_table_with_projection_from_file(self):
    """Insert data from a Parquet file into a table with a projection using FROM INFILE clause."""
    self.context.snapshot_id = get_snapshot_id()
    node = self.context.node
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()
    projection_name = "proj_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given(f"I have a table with a MergeTree engine"):
        create_table(
            name=table_name,
            engine="MergeTree() ORDER BY uint8",
            columns=table_columns,
        )

    with And("I have a projection on the table"):
        node.query(
            f"ALTER TABLE {table_name} ADD PROJECTION {projection_name} (SELECT * ORDER BY tuple(list_map_bool_uint8))"
        )

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' FORMAT Parquet"
        )

    with Check("I check that the table contains correct data"):
        with Pool(6) as executor:
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


@TestOutline(Feature)
def outline(self, compression_type):
    """Check that ClickHouse correctly reads and writes Parquet files when using
    `FROM INFILE` clause in SELECT query and `INTO OUTFILE` clause in INSERT query
    using specified compression type.
    """
    self.context.compression_type = compression_type

    Scenario(run=insert_into_memory_table_from_file)
    Scenario(run=insert_into_mergetree_table_from_file)
    Scenario(run=insert_into_replicated_mergetree_table_from_file)
    Scenario(run=insert_into_distributed_table_from_file)

    Scenario(run=select_from_memory_table_into_file)
    Scenario(run=select_from_mergetree_table_into_file)
    Scenario(run=select_from_replicated_mergetree_table_into_file)
    Scenario(run=select_from_distributed_table_into_file)

    Scenario(run=select_from_mat_view_into_file)
    Scenario(run=insert_into_table_with_projection_from_file)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0"))
def none(self):
    """Check that ClickHouse correctly reads and writes Parquet files when using
    `FROM INFILE` clause in SELECT query and `INTO OUTFILE` clause in INSERT query
    using the NONE compression type.
    """
    outline(compression_type="NONE")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"))
def gzip(self):
    """Check that ClickHouse correctly reads and writes Parquet files when using
    `FROM INFILE` clause in SELECT query and `INTO OUTFILE` clause in INSERT query
    using the GZIP compression type.
    """
    outline(compression_type="GZIP")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4(self):
    """Check that ClickHouse correctly reads and writes Parquet files when using
    `FROM INFILE` clause in SELECT query and `INTO OUTFILE` clause in INSERT query
    using the LZ4 compression type.
    """
    outline(compression_type="LZ4")


@TestFeature
@Name("query")
def feature(self):
    """Check that ClickHouse correctly reads and writes Parquet files when using
    `FROM INFILE` clause in SELECT query and `INTO OUTFILE` clause in INSERT query
    using different compression types.
    """
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
