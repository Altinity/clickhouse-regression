from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid

from decimal import Decimal
from datetime import datetime, timedelta, time, date

from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    StringType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    TimestampType,
    BooleanType,
    TimestamptzType,
    DateType,
    TimeType,
    UUIDType,
    BinaryType,
    DecimalType,
    StructType,
    ListType,
    MapType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import (
    IdentityTransform,
    BucketTransform,
    MonthTransform,
    YearTransform,
    DayTransform,
    HourTransform,
    TruncateTransform,
    VoidTransform,
)

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

import random
import string
import pyarrow as pa


_PRIMITIVE_TYPES = [
    StringType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    TimestampType,
    BooleanType,
    TimestamptzType,
    DateType,
    TimeType,
    # UUIDType,
    BinaryType,
    DecimalType,
]


@TestStep(When)
def add_field_to_partition_spec(
    self, table, column_transform_pair, partition_name=None
):
    """Add field to partition spec."""
    field_name, transform = column_transform_pair

    if partition_name is None:
        partition_name = f"{field_name}_{getuid()}"

    with By(f"add field {field_name} to partition spec"):
        with table.update_spec() as update:
            update.add_field(field_name, transform, partition_name)

            self.context.partition_spec.append(partition_name)
            note(
                f"Partition spec after adding field {field_name} with transform {transform}: {self.context.partition_spec}"
            )


@TestStep(When)
def remove_field_from_partition_spec(self, table):
    """Remove field from partition spec."""
    if self.context.partition_spec:
        remove_field = random.choice(self.context.partition_spec)
        with By(f"remove field {remove_field} from partition spec"):
            with table.update_spec() as update:
                update.remove_field(remove_field)

            self.context.partition_spec.remove(remove_field)
            note(
                f"Partition spec after removing field {remove_field}: {self.context.partition_spec}"
            )


@TestScenario
def partition_evolution_check(self, minio_root_user, minio_root_password, action_list):
    """
    Check that ClickHouse Iceberg engine is able to read data from Iceberg table
    after partition evolution.
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_db_{getuid()}"

    self.context.partition_spec = []

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:5000/",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            rest_catalog_url="http://ice-rest-catalog:5000",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with When("define schema and create table"):
        schema = Schema(
            NestedField(
                field_id=1, name="boolean_col", field_type=BooleanType(), required=False
            ),
            NestedField(
                field_id=2, name="long_col", field_type=LongType(), required=False
            ),
            NestedField(
                field_id=3, name="double_col", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=4, name="string_col", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=5, name="date_col", field_type=DateType(), required=False
            ),
            NestedField(
                field_id=6,
                name="datetime_col",
                field_type=TimestampType(),
                required=False,
            ),
        )

        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("insert some data into table"):
        df = pa.Table.from_pylist(
            [
                {
                    "boolean_col": True,
                    "long_col": 1000,
                    "double_col": 456.78,
                    "string_col": "Alice",
                    "date_col": date(2024, 1, 1),
                    "datetime_col": datetime(2024, 1, 1, 12, 0, 0),
                },
                {
                    "boolean_col": False,
                    "long_col": 2000,
                    "double_col": 456.78,
                    "string_col": "Bob",
                    "date_col": date(2023, 5, 15),
                    "datetime_col": datetime(2023, 5, 15, 12, 0, 0),
                },
                {
                    "boolean_col": True,
                    "long_col": 3000,
                    "double_col": 6.7,
                    "string_col": "Charlie",
                    "date_col": date(2022, 1, 1),
                    "datetime_col": datetime(2022, 1, 1, 12, 0, 0),
                },
                {
                    "boolean_col": False,
                    "long_col": 4000,
                    "double_col": 8.9,
                    "string_col": "1",
                    "date_col": date(2021, 1, 1),
                    "datetime_col": datetime(2021, 1, 1, 12, 0, 0),
                },
            ]
        )
        table.append(df)

    with And("add new field to partition spec"):
        note(f"Spec before adding new field: {table.spec}")
        for action in action_list:
            action(table=table)
        note(f"Spec after adding new field: {table.spec}")

    with Then("verify data via PyIceberg"):
        df = table.scan().to_pandas()
        note(f"PyIceberg data:\n{df}")

    with And("verify data via ClickHouse"):
        self.context.node.query(
            f"DESCRIBE TABLE {database_name}.\\`{namespace}.{table_name}\\`"
        )
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
        )


@TestFeature
@Name("partition evolution")
def feature(self, minio_root_user, minio_root_password):
    """Check that ClickHouse Iceberg engine supports reading all Iceberg data types."""
    transforms = [
        IdentityTransform(),
        BucketTransform(num_buckets=4),
        TruncateTransform(width=3),
        MonthTransform(),
        YearTransform(),
        DayTransform(),
        HourTransform(),
        VoidTransform(),
    ]
    columns = [
        "boolean_col",
        "long_col",
        "double_col",
        "string_col",
        "date_col",
        "datetime_col",
    ]

    def is_transform_valid_for_column(column, transform):
        if "date" not in column and isinstance(
            transform, (MonthTransform, YearTransform, DayTransform, HourTransform)
        ):
            return False
        if column == "date_col" and isinstance(
            transform, (TruncateTransform, HourTransform)
        ):
            return False
        if column == "datetime_col" and isinstance(transform, (TruncateTransform)):
            return False
        if column == "boolean_col" and isinstance(
            transform, (BucketTransform, TruncateTransform)
        ):
            return False
        if column == "double_col" and isinstance(
            transform, (BucketTransform, TruncateTransform)
        ):
            return False
        return True

    column_transform_pairs = [
        (col, transform)
        for col in columns
        for transform in transforms
        if is_transform_valid_for_column(col, transform)
    ]

    actions = []

    with By("add all possible partial add field actions"):
        for column_transform_pair in column_transform_pairs:
            actions.append(
                partial(
                    add_field_to_partition_spec,
                    column_transform_pair=column_transform_pair,
                )
            )

    with And("add remove actions (1/3 of add actions)"):
        for _ in range(len(actions) // 3):
            actions.append(remove_field_from_partition_spec)

    for num in range(100):
        action_list = random.sample(actions, 10)
        Scenario(name=f"#{num}", test=partition_evolution_check)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            action_list=action_list,
        )
