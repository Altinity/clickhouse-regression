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
    https://datasets.clickhouse.com/hits_compatible/athena_partitioned/hits_%7B0..99%7D.parquet.
    """

    clickhouse_node = self.context.clickhouse_node
    table_name = "nyc_taxi_" + getuid()
    parquet_file = "nyc_taxi_parquet_" + getuid() + ".parquet"
    with Given(
        "I create a hits table in clickhouse and populate it with the ontime airlines dataset"
    ):
        clickhouse_node.query(
            f"""
CREATE TABLE {table_name} (
    trip_id             UInt32,
    pickup_datetime     DateTime,
    dropoff_datetime    DateTime,
    pickup_longitude    Nullable(Float64),
    pickup_latitude     Nullable(Float64),
    dropoff_longitude   Nullable(Float64),
    dropoff_latitude    Nullable(Float64),
    passenger_count     UInt8,
    trip_distance       Float32,
    fare_amount         Float32,
    extra               Float32,
    tip_amount          Float32,
    tolls_amount        Float32,
    total_amount        Float32,
    payment_type        Enum('CSH' = 1, 'CRE' = 2, 'NOC' = 3, 'DIS' = 4, 'UNK' = 5),
    pickup_ntaname      LowCardinality(String),
    dropoff_ntaname     LowCardinality(String)
)
ENGINE = MergeTree
PRIMARY KEY (pickup_datetime, dropoff_datetime);
"""
        )

        clickhouse_node.query(
            f"""
            INSERT INTO {table_name}
SELECT
    trip_id,
    pickup_datetime,
    dropoff_datetime,
    pickup_longitude,
    pickup_latitude,
    dropoff_longitude,
    dropoff_latitude,
    passenger_count,
    trip_distance,
    fare_amount,
    extra,
    tip_amount,
    tolls_amount,
    total_amount,
    payment_type,
    pickup_ntaname,
    dropoff_ntaname
FROM s3(
    'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/trips_{{0..2}}.gz',
    'TabSeparatedWithNames'
);
            """,
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
