from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *


@TestFeature
@Name("chunked array")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ChunkedArray("1.0"))
def feature(self, node="clickhouse1"):
    """Run checks that clickhouse successfully read and writes Parquet chunked array datatype."""
    self.context.snapshot_id = get_snapshot_id()
    self.context.node = self.context.cluster.node(node)
    node = self.context.node
    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(
            engine="Memory",
            columns=[Column(name="arr", datatype=Array(Map(String(), UInt32())))],
            name=table_name,
        )

    with And("I have a parquet file with a chunked array"):
        node.command("python3 /var/lib/data/generate_chunked_file.py")

    with When("I insert data from a parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/chunked_array_test_file.parquet' FORMAT Parquet"
        )

    with Then(
        "I check that the data was successfully written into the ClickHouse table"
    ):
        execute_query(f"SELECT * FROM {table_name}")
