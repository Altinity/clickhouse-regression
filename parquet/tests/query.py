from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestOutline(Scenario)
@Examples(
    "engine",
    [
        (
            "Memory",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Memory("1.0")
            ),
        ),
        (
            "MergeTree() ORDER BY uint8",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_MergeTree("1.0")
            ),
        ),
        (
            "ReplicatedMergeTree('/clickhouse/tables/{shard}/table_name', '{replica}') ORDER BY uint8",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplicatedMergeTree(
                    "1.0"
                )
            ),
        ),
        (
            "Distributed(replicated_cluster, default, table_name)",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed("1.0")
            ),
        ),
    ],
)
def insert_into_table_from_file(self, engine):
    """Insert data from Parquet files into tables with different engines using FROM INFILE clause."""
    node = self.context.node
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()

    if "ReplicatedMergeTree" in engine:
        engine = engine.replace("table_name", table_name)

    if "Distributed" in engine:
        dist_table_name = "dist_table_" + getuid()
        engine = engine.replace("table_name", dist_table_name)

        with Given("I have a table for the distributed table to look at"):
            table(
                name=dist_table_name,
                engine="Memory",
                table_def=node.command(
                    "cat /var/lib/clickhouse/user_files/clickhouse_table_def.txt"
                ).output.strip(),
            )

    with Given(f"I have a table with a {engine} engine"):
        table(
            name=table_name,
            engine=engine,
            table_def=node.command(
                "cat /var/lib/clickhouse/user_files/clickhouse_table_def.txt"
            ).output.strip(),
        )

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Then("I check that the table contains correct data"):
        check_query_output(query=f"SELECT * FROM {table_name}")


@TestOutline(Scenario)
@Examples(
    "engine",
    [
        (
            "Memory",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Memory("1.0")
            ),
        ),
        (
            "MergeTree() ORDER BY uint8",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_MergeTree("1.0")
            ),
        ),
        (
            "ReplicatedMergeTree('/clickhouse/tables/{shard}/table_name', '{replica}') ORDER BY uint8",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplicatedMergeTree(
                    "1.0"
                )
            ),
        ),
        (
            "Distributed(replicated_cluster, default, table_name)",
            Requirements(
                RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed("1.0")
            ),
        ),
    ],
)
def select_from_table_into_file(self, engine):
    """Select data from tables with different engines and write to Parquet files using INTO OUTFILE clause."""
    node = self.context.node
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()
    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet{'.' + compression_type if compression_type != 'none' else ''}'"

    if "ReplicatedMergeTree" in engine:
        engine = engine.replace("table_name", table_name)

    if "Distributed" in engine:
        dist_table_name = "dist_table_" + getuid()
        engine = engine.replace("table_name", dist_table_name)

        with Given("I have a table for the distributed table to look at"):
            table(
                name=dist_table_name,
                engine="Memory",
            )

    with Given(f"I have a table with a {engine} engine"):
        table(name=table_name, engine=engine)

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
            snap_name="Select from table into file " + engine,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Select_MaterializedView("1.0"))
def select_from_mat_view_into_file(self):
    """Select data from materialized view and write to Parquet files using INTO OUTFILE clause."""
    node = self.context.node
    compression_type = self.context.compression_type
    table_name = "table_" + getuid()
    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet{'.' + compression_type if compression_type != 'none' else ''}'"

    with Given(f"I have a table with a Memory engine"):
        table(name=table_name, engine="Memory")

    with And(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        insert_test_data(name=table_name)

    try:
        with Given("I have a mat_view on the table"):
            node.query(
                f"CREATE MATERIALIZED VIEW {table_name}_view ENGINE = Memory AS SELECT * FROM {table_name}",
                settings=[("allow_suspicious_low_cardinality_types", 1)],
            )

        with When("I select data from the table and write it into a Parquet file"):
            node.query(
                f"SELECT * FROM {table_name}_view INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
            )

        with Then("I check that data was written into the Parquet file correctly"):
            node.command(
                f"cp {path} /var/lib/clickhouse/user_files/{table_name}.Parquet"
            )
            check_source_file(
                path=f"/var/lib/clickhouse/user_files/{table_name}.Parquet",
                compression=f"'{compression_type.lower()}'",
            )

    finally:
        with Finally("I drop the materialized view"):
            node.query(f"DROP VIEW IF EXISTS {table_name}_view")


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
@Name("query")
def feature(self, compression_type):
    """Check that ClickHouse correctly reads and write Parquet files when using
    `FROM INFILE` clause in SELECT query and `INTO OUTFILE` clause in INSERT query.
    """

    self.context.compression_type = compression_type
    self.context.node = self.context.cluster.node("clickhouse1")

    Scenario(run=insert_into_table_from_file)
    Scenario(run=select_from_table_into_file)
    Scenario(run=select_from_mat_view_into_file)
