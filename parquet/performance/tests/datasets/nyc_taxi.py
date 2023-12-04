from testflows.core import *
from helpers.common import getuid, check_clickhouse_version


@TestStep(Given)
def create_parquet_file_nyc_taxi(
    self,
    threads: str,
    max_memory_usage: int,
    compression: str = None,
):
    """Prepare data in Parquet format using the hits dataset from
    https://altinity-clickhouse-data.s3.amazonaws.com/nyc_taxi_rides/data/tripdata_native/data-*.bin.gz
    """

    clickhouse_node = self.context.clickhouse_node
    table_name = "nyc_taxi_" + getuid()
    parquet_file = "nyc_taxi_parquet_" + getuid() + ".parquet"
    with Given("I create the table populated with data from nyc taxi in clickhouse"):
        clickhouse_node.query(
            f"CREATE TABLE {table_name} ENGINE = MergeTree ORDER BY tuple() AS SELECT * FROM s3("
            f"'https://altinity-clickhouse-data.s3.amazonaws.com/nyc_taxi_rides/data"
            f"/tripdata_native/data-*.bin.gz', 'Native') SETTINGS max_threads={threads}, max_insert_threads={threads}, input_format_parallel_parsing=0, max_memory_usage={max_memory_usage}",
            progress=True,
            timeout=3600,
        )

        insert_into_parquet = (
            f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS "
            f"max_insert_threads = {threads}, max_memory_usage={max_memory_usage}"
        )

        if check_clickhouse_version(">=23.3")(self):
            insert_into_parquet += (
                f", output_format_parquet_compression_method='{compression}'"
            )

        clickhouse_node.query(
            insert_into_parquet,
            timeout=3600,
        )

        clickhouse_node.command(
            f"mv {parquet_file} /var/lib/clickhouse/user_files", exitcode=0
        )

    yield parquet_file
    clickhouse_node.query(f"DROP TABLE {table_name}")
