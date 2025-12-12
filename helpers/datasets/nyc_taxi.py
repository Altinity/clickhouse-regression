from testflows.core import *

def nyc_columns():
    return [
        {"name": "trip_id", "type": "UInt64"},
        {"name": "pickup_datetime", "type": "DateTime"},
        {"name": "dropoff_datetime", "type": "DateTime"},
        {"name": "pickup_longitude", "type": "Float64"},
        {"name": "pickup_latitude", "type": "Float64"},
        {"name": "dropoff_longitude", "type": "Float64"},
        {"name": "dropoff_latitude", "type": "Float64"},
        {"name": "passenger_count", "type": "UInt8"},
        {"name": "trip_distance", "type": "Float32"},
        {"name": "fare_amount", "type": "Float32"},
        {"name": "extra", "type": "Float32"},
        {"name": "tip_amount", "type": "Float32"},
        {"name": "tolls_amount", "type": "Float32"},
        {"name": "total_amount", "type": "Float32"},
        {"name": "payment_type", "type": "String"},
        {"name": "pickup_ntaname", "type": "String"},
        {"name": "dropoff_ntaname", "type": "String"},
    ]

@TestStep
def nyc_taxi(
    self,
    table_name,
    partition_by="pickup_datetime",
    from_range=0,
    to_range=2,
    node=None,
):

    if node is None:
        node = self.context.node

    node.query(
        f"""CREATE TABLE {table_name}
(
    trip_id UInt64,
    pickup_datetime DateTime,
    dropoff_datetime DateTime,
    pickup_longitude Float64,
    pickup_latitude Float64,
    dropoff_longitude Float64,
    dropoff_latitude Float64,
    passenger_count UInt8,
    trip_distance Float32,
    fare_amount Float32,
    extra Float32,
    tip_amount Float32,
    tolls_amount Float32,
    total_amount Float32,
    payment_type String,
    pickup_ntaname String,
    dropoff_ntaname String
)
ENGINE = MergeTree
PARTITION BY {partition_by}
ORDER BY (pickup_datetime, trip_id);
"""
    )

    node.query(
        f"""INSERT INTO {table_name}
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
    'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/trips_{{{from_range}..{to_range}}}.gz',
    NOSIGN,
    'TabSeparatedWithNames'
)  SETTINGS max_partitions_per_insert_block = 0, max_memory_usage = 20000000000;
"""
    )
