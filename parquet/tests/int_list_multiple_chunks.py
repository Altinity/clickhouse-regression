from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *


@TestFeature
@Name("list in multiple chunks")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_ChunkedColumns("1.0"))
def feature(self, node="clickhouse1"):
    """Run checks that clickhouse successfully reads from a parquet file with a list split into multiple chunks."""
    self.context.snapshot_id = get_snapshot_id()
    self.context.node = self.context.cluster.node(node)
    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(
            engine="Memory",
            columns=[Column(name="arr", datatype=Array(UInt64()))],
            name=table_name,
        )

    with When("I insert data from a parquet file"):
        self.context.node.command(
            "cp /var/lib/test_files/int-list-zero-based-chunked-array.parquet /var/lib/clickhouse/user_files/int-list-zero-based-chunked-array.parquet"
        )
        self.context.node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/int-list-zero-based-chunked-array.parquet' FORMAT Parquet"
        )

    with Then(
        "I check that the data was successfully written into the ClickHouse table"
    ):
        if check_clickhouse_version(">23.8")(self):
            order = "ALL"
        else:
            order = "tuple(*)"

        execute_query(f"SELECT * FROM {table_name} ORDER BY {order}")
