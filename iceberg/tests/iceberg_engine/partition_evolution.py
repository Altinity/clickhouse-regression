import random
import pyarrow as pa
from datetime import date
from testflows.core import *


from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    BooleanType,
    DateType,
    DoubleType,
    IntegerType,
    ListType,
    LongType,
    MapType,
    StringType,
)
from pyiceberg.partitioning import PartitionSpec
from pyiceberg.table.sorting import SortOrder
from pyiceberg.transforms import (
    BucketTransform,
    DayTransform,
    HourTransform,
    IdentityTransform,
    MonthTransform,
    TruncateTransform,
    VoidTransform,
    YearTransform,
)
from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.common as common
import iceberg.tests.steps.iceberg_engine as iceberg_engine


random.seed(42)


def is_transform_valid_for_column(column, transform):
    """Check if transform is valid for column."""
    if column != "date_col" and isinstance(
        transform, (MonthTransform, YearTransform, DayTransform, HourTransform)
    ):
        return False
    if column == "date_col" and isinstance(
        transform, (TruncateTransform, HourTransform)
    ):
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


@TestStep(When)
def add_field_to_partition_spec(
    self, table, column_transform_pair, partition_name=None
):
    """Add field to partition spec."""
    field_name, transform = column_transform_pair

    if field_name in self.context.partition_spec:
        return

    if partition_name is None:
        partition_name = f"{field_name}_{getuid()}"

    with By(f"add field {field_name} to partition spec"):
        with table.update_spec() as update:
            update.add_field(field_name, transform, partition_name)

            self.context.partition_spec[field_name] = partition_name
            note(
                f"Partition spec after adding field {field_name} with transform {transform}: {self.context.partition_spec}"
            )


@TestStep(When)
def remove_field_from_partition_spec(self, table, remove_field=None):
    """Remove field from partition spec."""
    if remove_field is None:
        if not self.context.partition_spec:
            return
        remove_field = random.choice(list(self.context.partition_spec.keys()))

    with By(f"remove field {remove_field} from partition spec"):
        with table.update_spec() as update:
            update.remove_field(self.context.partition_spec[remove_field])

        del self.context.partition_spec[remove_field]
        note(
            f"Partition spec after removing field {remove_field}: {self.context.partition_spec}"
        )


@TestStep(Given)
def insert_data_in_merge_tree_table(self, merge_tree_table, data):
    """Insert data in MergeTree table."""
    merge_tree_data_str = common.transform_to_clickhouse_format(data)
    self.context.node.query(
        f"INSERT INTO {merge_tree_table} VALUES {merge_tree_data_str}"
    )


@TestStep(Given)
def add_data(self, iceberg_table, num_rows=10):
    """Add num_rows rows to table."""
    bool_values = [True, False]
    long_values = [1000, 2000, 3000, 4000, 5000]
    double_values = [456.78, 6.7, 8.9, 10.1, 12.3]
    string_values = ["Alice", "Bob", "Charlie", "Masha", "Dasha", "Sasha", "Pasha"]
    date_values = [
        date(2024, 3, 1),
        date(2023, 5, 15),
        date(2022, 6, 21),
        date(2021, 11, 2),
        date(2020, 1, 3),
        date(2019, 9, 4),
    ]

    data = [
        {
            "boolean_col": random.choice(bool_values),
            "long_col": random.choice(long_values),
            "double_col": random.choice(double_values),
            "string_col": random.choice(string_values),
            "date_col": random.choice(date_values),
            "list_col": [random.choice(string_values)],
            "map_col": {random.choice(string_values): random.randint(1, 100)},
        }
        for _ in range(num_rows)
    ]
    schema = pa.schema(
        [
            ("boolean_col", pa.bool_()),
            ("long_col", pa.int64()),
            ("double_col", pa.float64()),
            ("string_col", pa.string()),
            ("date_col", pa.date32()),
            ("list_col", pa.list_(pa.string())),
            ("map_col", pa.map_(pa.string(), pa.int32())),
        ]
    )

    df = pa.Table.from_pylist(data, schema=schema)
    iceberg_table.append(df)

    return data


@TestStep(Given)
def create_merge_tree_table(self, table_name=None, node=None):
    """Create MergeTree table."""
    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = f"merge_tree_table_{getuid()}"

    try:
        node.query(
            f"""
            CREATE TABLE {table_name} (
                boolean_col Nullable(Bool), 
                long_col Nullable(Int64), 
                double_col Nullable(Float64), 
                string_col Nullable(String),
                date_col Nullable(Date),
                list_col Array(Nullable(String)),
                map_col Map(String, Nullable(Int64))
            ) 
            ENGINE = MergeTree 
            ORDER BY tuple()
            """
        )
        yield table_name

    finally:
        with Finally("drop table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestScenario
def partition_evolution_check(self, minio_root_user, minio_root_password, action_list):
    """
    Check that Clickhouse can read Iceberg tables after partition spec
    changes specified in action_list.
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_db_{getuid()}"
    clickhouse_iceberg_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"

    with Given("initialize partition spec"):
        self.context.partition_spec = {}

    with And("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
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
                name="list_col",
                field_type=ListType(
                    element_type=StringType(), element_id=7, element_required=False
                ),
                required=False,
            ),
            NestedField(
                field_id=8,
                name="map_col",
                field_type=MapType(
                    key_type=StringType(),
                    value_type=IntegerType(),
                    key_id=9,
                    value_id=10,
                    value_required=False,
                ),
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

    with And("create MergeTree table with same schema"):
        merge_tree_table_name = create_merge_tree_table()

    with And("insert same data in Iceberg and MergeTree tables"):
        data = add_data(
            iceberg_table=table,
            num_rows=5,
        )
        insert_data_in_merge_tree_table(
            merge_tree_table=merge_tree_table_name,
            data=data,
        )

    with And(
        """change partition spec and insert data after each action 
        to both Iceberg and MergeTree tables"""
    ):
        for num, action in enumerate(action_list):
            with By(f"apply action #{num} - {action.__name__}"):
                action(table=table)
                data = add_data(
                    iceberg_table=table,
                    num_rows=5,
                )
                insert_data_in_merge_tree_table(
                    merge_tree_table=merge_tree_table_name,
                    data=data,
                )
                note(f"Table partition spec: {table.spec()}")

    with Then("verify data via PyIceberg"):
        df = table.scan().to_pandas()
        note(f"PyIceberg data:\n{df}")

    with And(
        """check that data in MergeTree table is the same as in 
        Iceberg table after all changes in partition spec"""
    ):
        common.compare_data_in_two_tables(
            table_name1=merge_tree_table_name,
            table_name2=clickhouse_iceberg_table_name,
        )


@TestFeature
@Name("partition evolution")
def feature(self, minio_root_user, minio_root_password):
    """Check that Clickhouse can read Iceberg tables, which partition spec
    has changed over time."""

    with Given("define all possible transforms"):
        transforms = [
            IdentityTransform(),
            BucketTransform(num_buckets=4),
            TruncateTransform(width=3),
            MonthTransform(),
            YearTransform(),
            DayTransform(),
            HourTransform(),
        ]

    with And("define all possible columns that can be used for partitioning"):
        columns = [
            "boolean_col",
            "long_col",
            "double_col",
            "string_col",
            "date_col",
        ]

    with And("define all possible column-transform pairs"):
        column_transform_pairs = [
            (col, transform)
            for col in columns
            for transform in transforms
            if is_transform_valid_for_column(col, transform)
        ]

    with And("add all possible `add field` actions"):
        actions = []
        for column_transform_pair in column_transform_pairs:
            actions.append(
                partial(
                    add_field_to_partition_spec,
                    column_transform_pair=column_transform_pair,
                )
            )

    with And("add `remove field` actions (1/3 of `add field` actions)"):
        for _ in range(len(actions) // 3):
            actions.append(remove_field_from_partition_spec)

    for num in range(100):
        action_list = random.sample(actions, 10)
        Scenario(name=f"#{num}", test=partition_evolution_check)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            action_list=action_list,
        )
