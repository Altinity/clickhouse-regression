from testflows.core import *
from testflows.asserts import error

import pyarrow as pa
import iceberg.tests.steps.alter_support as alter_steps
import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import getuid
from helpers.tables import create_table
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import NestedField, Schema
from pyiceberg.table.sorting import SortField, SortOrder
from pyiceberg.transforms import IdentityTransform
from pyiceberg.types import DoubleType, LongType, StringType


@TestScenario
def alter_column_in_sequence(self, minio_root_user, minio_root_password):
    """
    Check that ALTER operations are supported when executed in sequence.
    Random sequence of ALTER operations will be executed on Iceberg and MergeTree tables.
    Results after each alter operation must be the same in both tables.
    """
    namespace = f"namespace_{getuid()}"
    iceberg_table_name = f"iceberg_table_{getuid()}"
    merge_tree_table_name = f"merge_tree_table_{getuid()}"

    with Given("create iceberg catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create DataLakeCatalog database"):
        database_name = f"datalake_db_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("create MergeTree and Iceberg catalog tables with the same schema"):
        columns = alter_steps.alter_support_schema_columns()
        merge_tree_table = create_table(
            name=merge_tree_table_name,
            engine="MergeTree()",
            columns=columns,
            order_by="tuple()",
        )
        clickhouse_iceberg_table_name = (
            f"{database_name}.\\`{namespace}.{iceberg_table_name}\\`"
        )
        catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=iceberg_table_name,
            schema=alter_steps.alter_support_iceberg_schema(),
            location=catalog_steps.table_s3_location(namespace, iceberg_table_name),
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )
        iceberg_table = alter_steps.TableRef(
            name=clickhouse_iceberg_table_name,
            columns=columns,
            engine="Iceberg",
        )
        alter_steps.insert_random_rows_into_tables(
            tables=[merge_tree_table, iceberg_table],
            row_count=10,
        )

    with And("track columns for meaningful alters"):
        self.context.columns = [
            {"name": column.name, "type": column.datatype.name} for column in columns
        ]

    with Then("run random sequence of alter actions and compare results"):
        alter_steps.run_random_alter_sequence_and_compare(
            merge_tree_table_name=merge_tree_table_name,
            iceberg_table_name=clickhouse_iceberg_table_name,
            num_actions=300,
        )


@TestScenario
def alter_add_add_drop_column(self, minio_root_user, minio_root_password):
    """Check that a column remains droppable after another column is added.
    Test to reproduce https://github.com/Altinity/ClickHouse/issues/2085."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"datalake_db_{getuid()}"
    clickhouse_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"

    with Given("create iceberg catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create an unpartitioned Iceberg table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=Schema(
                NestedField(1, "name", StringType(), required=False),
            ),
            location=catalog_steps.table_s3_location(namespace, table_name),
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("insert one row"):
        table.append(pa.Table.from_pylist([{"name": "Alice"}]))

    with When("add two columns one after another"):
        alter_steps.add_column(
            table_name=clickhouse_table_name,
            column_name="column_a",
            column_type="Nullable(String)",
        )
        alter_steps.add_column(
            table_name=clickhouse_table_name,
            column_name="column_b",
            column_type="Nullable(Int64)",
        )

    with And("both added columns are visible"):
        result = self.context.node.query(
            f"SELECT * FROM {clickhouse_table_name} FORMAT TabSeparated"
        )
        assert result.output == "Alice\t\\N\t\\N", error()

    with And("run SHOW CREATE TABLE"):
        result = self.context.node.query(f"SHOW CREATE TABLE {clickhouse_table_name}")
        assert "`name` Nullable(String)" in result.output, error()
        assert "`column_a` Nullable(String)" in result.output, error()
        assert "`column_b` Nullable(Int64)" in result.output, error()

    with And("drop the first added column"):
        alter_steps.drop_column(
            table_name=clickhouse_table_name,
            column_name="column_a",
        )

    with Then("the remaining schema and data are correct"):
        result = self.context.node.query(
            f"SELECT * FROM {clickhouse_table_name} FORMAT TabSeparated"
        )
        assert result.output == "Alice\t\\N", error()

        refreshed_table = catalog.load_table(f"{namespace}.{table_name}")
        assert [field.name for field in refreshed_table.schema().fields] == [
            "name",
            "column_b",
        ], error()


@TestScenario
def alter_drop_partition_column(self, minio_root_user, minio_root_password):
    """Check that Iceberg rejects dropping a column used by its partition spec."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"datalake_db_{getuid()}"
    clickhouse_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"

    with Given("create iceberg catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("define schema partitioned by name and sorted by double"):
        schema = Schema(
            NestedField(1, "name", StringType(), required=False),
            NestedField(2, "double", DoubleType(), required=False),
            NestedField(3, "integer", LongType(), required=False),
        )
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1001,
                transform=IdentityTransform(),
                name="name",
            )
        )
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location=catalog_steps.table_s3_location(namespace, table_name),
            partition_spec=partition_spec,
            sort_order=SortOrder(),
        )

    with And("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("insert data into the Iceberg table"):
        table.append(
            pa.Table.from_pylist([{"name": "Alice", "double": 195.23, "integer": 20}])
        )

    with When("try to drop the partition source column, expecting rejection"):
        alter_steps.drop_column_expecting_rejection(
            table_name=clickhouse_table_name,
            column_name="name",
        )

    with Then("check that the partition column and table data remain unchanged"):
        result = self.context.node.query(
            f"SELECT name, double, integer FROM {clickhouse_table_name} "
            "FORMAT TabSeparated"
        )
        assert result.output == "Alice\t195.23\t20", error()
        refreshed_table = catalog.load_table(f"{namespace}.{table_name}")
        assert refreshed_table.schema().find_field("name").field_id == 1, error()
        assert refreshed_table.spec().fields[0].source_id == 1, error()


@TestScenario
def alter_drop_sorting_column(self, minio_root_user, minio_root_password):
    """Check that Iceberg rejects dropping a column used by its active sort order."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"datalake_db_{getuid()}"
    clickhouse_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"

    with Given("create iceberg catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("define schema sorted by double"):
        schema = Schema(
            NestedField(1, "name", StringType(), required=False),
            NestedField(2, "double", DoubleType(), required=False),
            NestedField(3, "integer", LongType(), required=False),
        )
        sort_order = SortOrder(SortField(source_id=2, transform=IdentityTransform()))
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location=catalog_steps.table_s3_location(namespace, table_name),
            partition_spec=PartitionSpec(),
            sort_order=sort_order,
        )

    with And("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("insert data into the Iceberg table"):
        table.append(
            pa.Table.from_pylist([{"name": "Alice", "double": 195.23, "integer": 20}])
        )

    with When("try to drop the sort-order source column, expecting rejection"):
        alter_steps.drop_column_expecting_rejection(
            table_name=clickhouse_table_name,
            column_name="double",
        )

    with Then("check that the sort column and table data remain unchanged"):
        result = self.context.node.query(
            f"SELECT name, double, integer FROM {clickhouse_table_name} "
            "FORMAT TabSeparated"
        )
        assert result.output == "Alice\t195.23\t20", error()
        refreshed_table = catalog.load_table(f"{namespace}.{table_name}")
        assert refreshed_table.schema().find_field("double").field_id == 2, error()
        assert refreshed_table.metadata.default_sort_order_id == 1, error()
        assert refreshed_table.sort_order().fields[0].source_id == 2, error()


@TestFeature
@Name("alter support")
def feature(self, minio_root_user, minio_root_password):
    """Check that ALTER TABLE operations are supported for iceberg tables from
    DataLakeCatalog database."""
    Scenario(test=alter_column_in_sequence)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_drop_partition_column)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_drop_sorting_column)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_add_add_drop_column)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
