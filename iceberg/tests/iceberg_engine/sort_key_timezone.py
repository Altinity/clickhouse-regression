from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import pyarrow as pa

from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import TimestampType, TimestamptzType, LongType
from pyiceberg.partitioning import PartitionSpec
from pyiceberg.table.sorting import SortOrder, SortField, SortDirection, NullOrder
from pyiceberg.transforms import HourTransform, MonthTransform, YearTransform, DayTransform

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


def run_sort_key_timezone_scenario(
    self,
    minio_root_user,
    minio_root_password,
    transform,
    timezone,
    timestamps_us,
    timestamp_type=None,
    arrow_timestamp_type=None,
):
    """Create an Iceberg table with the given temporal sort-order transform,
    insert rows, then SELECT via DataLakeCatalog with iceberg_partition_timezone set.
    Regression for https://github.com/Altinity/ClickHouse/issues/1487.
    """
    node = self.context.node
    namespace = f"iceberg_{getuid()}"
    table_name = f"sort_tz_{getuid()}"
    database_name = f"datalake_{getuid()}"

    if timestamp_type is None:
        timestamp_type = TimestampType()

    if arrow_timestamp_type is None:
        arrow_timestamp_type = pa.timestamp("us")

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(
        f"create {namespace}.{table_name} with {transform.__class__.__name__} sort order on {timestamp_type.__class__.__name__}"
    ):
        schema = Schema(
            NestedField(field_id=1, name="ts", field_type=timestamp_type, required=False),
            NestedField(field_id=2, name="val", field_type=LongType(), required=False),
        )
        sort_order = SortOrder(
            SortField(
                source_id=1,
                transform=transform,
                direction=SortDirection.ASC,
                null_order=NullOrder.NULLS_FIRST,
            )
        )
        iceberg_table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=sort_order,
        )

    with And("insert rows into the Iceberg table"):
        df = pa.table(
            {
                "ts": pa.array(timestamps_us, type=arrow_timestamp_type),
                "val": pa.array(list(range(1, len(timestamps_us) + 1))),
            }
        )
        iceberg_table.append(df)

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with Then(f"SELECT with iceberg_partition_timezone='{timezone}' must succeed"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            order_by="val",
            iceberg_partition_timezone=timezone,
        )
        assert result.exitcode == 0, error(f"SELECT failed with: {result.output}")

    with And("returned row count matches inserted data"):
        result = node.query(
            f"SELECT count() FROM {database_name}.\\`{namespace}.{table_name}\\`",
            settings=[("iceberg_partition_timezone", timezone)],
        )
        assert result.output.strip() == str(len(timestamps_us)), error(
            f"Expected {len(timestamps_us)} rows, got {result.output.strip()}"
        )


@TestScenario
def sort_key_with_day_transform_and_utc_timezone(self, minio_root_user, minio_root_password):
    """Regression test for issue #1487: DayTransform sort key with iceberg_partition_timezone = 'UTC'."""
    run_sort_key_timezone_scenario(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        transform=DayTransform(),
        timezone="UTC",
        timestamps_us=[
            1700000000000000,  # 2023-11-14 22:13:20 UTC
            1700086400000000,  # 2023-11-15 22:13:20 UTC
            1700172800000000,  # 2023-11-16 22:13:20 UTC
        ],
    )


@TestScenario
def sort_key_with_hour_transform_and_utc_timezone(self, minio_root_user, minio_root_password):
    """Check that HourTransform sort key does not cause parse failure with iceberg_partition_timezone set."""
    run_sort_key_timezone_scenario(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        transform=HourTransform(),
        timezone="UTC",
        timestamps_us=[
            1700000000000000,  # 2023-11-14 22:13:20
            1700007200000000,  # 2023-11-15 00:13:20 (+2h)
            1700014400000000,  # 2023-11-15 02:13:20 (+4h)
        ],
    )


@TestScenario
def sort_key_with_month_transform_and_utc_timezone(self, minio_root_user, minio_root_password):
    """Check that MonthTransform sort key does not cause parse failure with iceberg_partition_timezone set."""
    run_sort_key_timezone_scenario(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        transform=MonthTransform(),
        timezone="UTC",
        timestamps_us=[
            1696118400000000,  # 2023-10-01 00:00:00
            1698796800000000,  # 2023-11-01 00:00:00
            1701388800000000,  # 2023-12-01 00:00:00
        ],
    )


@TestScenario
def sort_key_with_year_transform_and_utc_timezone(self, minio_root_user, minio_root_password):
    """Check that YearTransform sort key does not cause parse failure with iceberg_partition_timezone set."""
    run_sort_key_timezone_scenario(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        transform=YearTransform(),
        timezone="UTC",
        timestamps_us=[
            1640995200000000,  # 2022-01-01 00:00:00
            1672531200000000,  # 2023-01-01 00:00:00
            1704067200000000,  # 2024-01-01 00:00:00
        ],
    )


@TestScenario
def sort_key_with_day_transform_and_positive_utc_offset_timezone(
    self, minio_root_user, minio_root_password
):
    """Check that DayTransform sort key does not cause parse failure when
    iceberg_partition_timezone is a positive-offset timezone with a slash (e.g. 'Asia/Istanbul').
    """
    run_sort_key_timezone_scenario(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        transform=DayTransform(),
        timezone="Asia/Istanbul",
        timestamps_us=[
            1700000000000000,  # 2023-11-14 22:13:20 UTC
            1700086400000000,  # 2023-11-15 22:13:20 UTC
            1700172800000000,  # 2023-11-16 22:13:20 UTC
        ],
    )


@TestScenario
def sort_key_with_day_transform_and_negative_utc_offset_timezone(
    self, minio_root_user, minio_root_password
):
    """Check that DayTransform sort key does not cause parse failure when
    iceberg_partition_timezone is a negative-offset timezone (e.g. 'America/New_York').
    """
    run_sort_key_timezone_scenario(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        transform=DayTransform(),
        timezone="America/New_York",
        timestamps_us=[
            1700000000000000,  # 2023-11-14 22:13:20 UTC  (17:13:20 New York)
            1700086400000000,  # 2023-11-15 22:13:20 UTC  (17:13:20 New York +1 day)
            1700172800000000,  # 2023-11-16 22:13:20 UTC  (17:13:20 New York +2 days)
        ],
    )


@TestScenario
def sort_key_with_day_transform_and_timestamptz_type(self, minio_root_user, minio_root_password):
    """Check that DayTransform sort key on a TimestamptzType column does not cause
    parse failure when iceberg_partition_timezone is set.
    """
    run_sort_key_timezone_scenario(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        transform=DayTransform(),
        timezone="UTC",
        timestamp_type=TimestamptzType(),
        arrow_timestamp_type=pa.timestamp("us", tz="UTC"),
        timestamps_us=[
            1700000000000000,  # 2023-11-14 22:13:20 UTC
            1700086400000000,  # 2023-11-15 22:13:20 UTC
            1700172800000000,  # 2023-11-16 22:13:20 UTC
        ],
    )


@TestFeature
@Name("sort key timezone")
def feature(self, minio_root_user, minio_root_password):
    """Tests for Iceberg sort-key timezone fix (issue #1487).
    Covers all temporal transforms, both TimestampType and TimestamptzType,
    and UTC / positive-offset / negative-offset timezones.
    """
    Scenario(test=sort_key_with_day_transform_and_utc_timezone)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=sort_key_with_hour_transform_and_utc_timezone)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=sort_key_with_month_transform_and_utc_timezone)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=sort_key_with_year_transform_and_utc_timezone)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=sort_key_with_day_transform_and_positive_utc_offset_timezone)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=sort_key_with_day_transform_and_negative_utc_offset_timezone)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=sort_key_with_day_transform_and_timestamptz_type)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
