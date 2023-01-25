from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *


@TestFeature
@Name("list in multiple chunks")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Insert("1.0"))
def feature(self, node="clickhouse1"):
    """Run checks that clickhouse successfully reads from a parquet file with monotonically increasing offsets."""
    self.context.snapshot_id = get_snapshot_id()
    self.context.node = self.context.cluster.node(node)
    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(
            engine="Memory",
            columns=[
                Column(name="list", datatype=Array(UInt64())),
                Column(name="json", datatype=Nullable(String())),
            ],
            name=table_name,
        )

    with When("I insert data from a parquet file"):
        self.context.node.command(
            "cp /var/lib/test_files/list_monotonically_increasing_offsets.parquet /var/lib/clickhouse/user_files/list_monotonically_increasing_offsets.parquet"
        )
        self.context.node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/list_monotonically_increasing_offsets.parquet' FORMAT Parquet"
        )

    with Then(
        "I check that the data was successfully written into the ClickHouse table"
    ):
        execute_query(f"SELECT * FROM {table_name}")
