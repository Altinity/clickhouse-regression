"""ClickHouse -> Iceberg data type coverage for EXPORT PARTITION.

Planned scenarios cover, per primitive / nested type:

    * integers   : Int8 / Int16 / Int32 / Int64 / UInt* (including max/min)
    * floats     : Float32 / Float64, NaN / +inf / -inf handling
    * strings    : String, FixedString, LowCardinality(String)
    * binary     : Binary (UUID, Binary, FixedString(16))
    * decimals   : Decimal(P, S) for various precision / scale combinations
    * date/time  : Date, Date32, DateTime, DateTime64(p, tz)
    * enums      : Enum8 / Enum16 -> Iceberg string
    * bool       : Bool
    * array/map  : Array(T), Map(String, T), nested arrays
    * nullable   : Nullable(T) variants for every primitive above
    * low card.  : LowCardinality(Nullable(String)) for partition columns

Each scenario inserts representative values, exports, and reads back through
all three paths:

    1. ClickHouse (SELECT from destination)
    2. icebergS3 table function (fresh metadata, no cache)
    3. PyIceberg scan() (independent implementation)
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; data type coverage scenarios pending implementation."""
    skip("datatype scenarios pending implementation")


@TestFeature
@Name("datatypes")
def feature(self, minio_root_user, minio_root_password):
    """ClickHouse -> Iceberg data type coverage."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
