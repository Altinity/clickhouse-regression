from testflows.core import *
from testflows.asserts import snapshot, values, error

from helpers.common import (
    getuid,
    check_clickhouse_version,
    get_settings_value,
    compare_with_expected,
)

from decimal import Decimal
from pyiceberg.schema import Schema
from pyiceberg.types import (
    BooleanType,
    StringType,
    LongType,
    DoubleType,
    DecimalType,
    StructType,
    NestedField,
    ListType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
from iceberg.tests.steps.common import random_string


@TestScenario
def sanity(self, minio_root_user, minio_root_password):
    """Sanity check for DataLakeCatalog database engine in ClickHouse."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"datalake_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("read data in ClickHouse from table from DataLakeCatalog database"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "" in result.output, error()

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )
        table.append(df)

    with And("scan with PyIceberg and display data"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in ClickHouse from table from DataLakeCatalog database"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()


@TestScenario
def sort_order(self, minio_root_user, minio_root_password):
    """Test that ClickHouse preserves the sort order of the Iceberg table."""
    namespace = f"iceberg_{getuid()}"
    table_name = f"name_{getuid()}"
    database_name = f"datalake_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        schema = Schema(
            NestedField(
                field_id=1, name="string", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="double", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=3, name="integer", field_type=LongType(), required=False
            ),
            NestedField(
                field_id=4, name="boolean", field_type=BooleanType(), required=False
            ),
            NestedField(
                field_id=5,
                name="struct",
                field_type=StructType(
                    NestedField(
                        field_id=4,
                        name="created_by",
                        field_type=StringType(),
                        required=False,
                    ),
                ),
                required=False,
            ),
            NestedField(
                field_id=6,
                name="decimal",
                field_type=DecimalType(9, 2),
                required=False,
            ),
        )

        sort_order = SortOrder(SortField(source_id=1, transform=IdentityTransform()))
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=sort_order,
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        length = 100
        string_values = [random_string(length=10) for _ in range(length)]
        double_values = [float(i + 2.5) for i in range(length)]
        integer_values = [i for i in range(length)]
        boolean_values = [False for _ in range(length)]
        struct_values = [{"created_by": f"name_{i}"} for i in range(length)]
        decimal_values = [Decimal(i + 0.5) for i in range(length)]

        data = [
            {
                "string": string_values[i],
                "double": double_values[i],
                "integer": integer_values[i],
                "boolean": boolean_values[i],
                "struct": struct_values[i],
                "decimal": decimal_values[i],
            }
            for i in range(length)
        ]
        arrow_schema = pa.schema(
            [
                ("string", pa.string()),
                ("double", pa.float64()),
                ("integer", pa.int64()),
                ("boolean", pa.bool_()),
                ("struct", pa.struct([pa.field("created_by", pa.string())])),
                ("decimal", pa.decimal128(9, 2)),
            ]
        )
        df = pa.Table.from_pylist(data, schema=arrow_schema)
        table.append(df)

    with And("scan with PyIceberg and display data"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in ClickHouse from table from DataLakeCatalog database"):
        for i in range(100):
            result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns="string",
                format="Values",
            )
            assert (
                ",".join(f"('{i}')" for i in string_values) == result.output.strip()
            ), error()


@TestScenario
def recreate_table(self, minio_root_user, minio_root_password):
    """Check that ClickHouse can read correct data after recreating
    the table with same name.
    """
    node = self.context.node
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"datalake_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )
        table.append(df)

    with Then("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("check the tables in the database after deleting the table"):
        result = node.query(f"SHOW TABLES from {database_name}")
        assert table_name not in result.output, error()

    with And("recreate table with same name"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("insert one row to recreated table"):
        df = pa.Table.from_pylist(
            [
                {"name": "David", "double": 20.0, "integer": 27},
            ]
        )
        table.append(df)

    with And("verify that ClickHouse reads the new data （one row）"):
        for retry in retries(count=11, delay=1):
            with retry:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
                assert "David\t20\t27" in result.output, error()


@TestScenario
def multiple_tables(self, minio_root_user, minio_root_password):
    """Check that ClickHouse can read correct data from multiple tables
    in same database.
    """
    namespace = f"iceberg_{getuid()}"
    database_name = f"datalake_{getuid()}"
    table_name_1 = f"table_1_{getuid()}"
    table_name_2 = f"table_2_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"create two tables under namespace {namespace}"):
        table_1 = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name_1
        )
        table_2 = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name_2
        )

    with And(f"insert different data into both tables"):
        df1 = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
            ]
        )
        table_1.append(df1)
        df2 = pa.Table.from_pylist(
            [
                {"name": "David", "double": 20.0, "integer": 27},
                {"name": "Eve", "double": 30.0, "integer": 35},
            ]
        )
        table_2.append(df2)

    with And("scan and display data with PyIceberg"):
        data1 = table_1.scan().to_pandas()
        data2 = table_2.scan().to_pandas()
        note(data1)
        note(data2)

    with Then("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("check that both tables are created in the database"):
        result = self.context.node.query(f"SHOW TABLES from {database_name}")
        assert table_name_1 in result.output, error()
        assert table_name_2 in result.output, error()

    with And("verify that ClickHouse reads correct data from both tables"):
        for retry in retries(count=10, delay=1):
            with retry:
                result_1 = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name_1,
                    format="Values",
                    order_by="tuple(*)",
                )
                assert (
                    result_1.output.strip() == "('Alice',195.23,20),('Bob',123.45,30)"
                ), error()
                result_2 = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name_2,
                    format="Values",
                    order_by="tuple(*)",
                )
                assert (
                    result_2.output.strip() == "('David',20,27),('Eve',30,35)"
                ), error()


@TestScenario
def recreate_table_and_database(self, minio_root_user, minio_root_password):
    """Check that ClickHouse can read correct data after recreating
    the table and recreating the database with same names.
    """
    node = self.context.node
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"datalake_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )
        table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("read data from the table from DataLakeCatalog database"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "Alice\t195.23\t20" in result.output, error()
        assert "Bob\t123.45\t30" in result.output, error()
        assert "Charlie\t67.89\t40" in result.output, error()

    with And(f"delete table {namespace}.{table_name}"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("check that the table is not visible in the database"):
        result = node.query(f"SHOW TABLES from {database_name}")
        assert table_name not in result.output, error()

    with And("recreate iceberg table with same name"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("insert one row to recreated table"):
        df = pa.Table.from_pylist(
            [
                {"name": "David", "double": 20.0, "integer": 27},
            ]
        )
        table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("verify that ClickHouse reads the new data （one row）"):
        for retry in retries(count=11, delay=1):
            with retry:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
                assert "David\t20\t27" in result.output, error()

    with Then("recreate database with DataLakeCatalog engine and verify data"):
        for _ in range(5):
            with By("recreate database"):
                iceberg_engine.drop_database(database_name=database_name)
                iceberg_engine.create_experimental_iceberg_database(
                    database_name=database_name,
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                )
            with And("verify that ClickHouse reads the new data （one row）"):
                for retry in retries(count=11, delay=1):
                    with retry:
                        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                            database_name=database_name,
                            namespace=namespace,
                            table_name=table_name,
                        )
                        assert "David\t20\t27" in result.output, error()


@TestScenario
def rename_database(self, minio_root_user, minio_root_password):
    """Check that renaming of database with DataLakeCatalog engine is not supported."""
    node = self.context.node
    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("check that renaming of DataLakeCatalog database is not supported"):
        new_database_name = f"new_iceberg_database_{getuid()}"
        database_engine_name = (
            "Iceberg" if check_clickhouse_version("<25.3")(self) else "DataLakeCatalog"
        )
        node.query(
            f"RENAME DATABASE {database_name} TO {new_database_name}",
            exitcode=48,
            message=f"DB::Exception: {database_engine_name}: RENAME DATABASE is not supported. (NOT_IMPLEMENTED)",
        )


@TestScenario
def rename_table_from_iceberg_database(self, minio_root_user, minio_root_password):
    """Check that renaming of iceberg table from DataLakeCatalog database is not supported."""
    node = self.context.node
    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("check that rename table from Iceberg database is not supported"):
        new_table_name = f"new_table_{getuid()}"
        database_engine_name = (
            "Iceberg" if check_clickhouse_version("<25.3")(self) else "DataLakeCatalog"
        )
        node.query(
            f"RENAME TABLE {database_name}.\\`{namespace}.{table_name}\\` TO {new_table_name}",
            exitcode=48,
            message=f"DB::Exception: {database_engine_name}: renameTable() is not supported. (NOT_IMPLEMENTED)",
        )


@TestScenario
def use_database(self, minio_root_user, minio_root_password, node=None):
    """Check `USE database` statement with DataLakeCatalog engine."""
    node = self.context.node if node is None else node
    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("check that `USE database` statement works"):
        result = node.query(
            f"USE {database_name}; SELECT currentDatabase(); SHOW TABLES;"
        )
        assert f"{namespace}.{table_name}" in result.output, error()

    with And("check that the current database is set to the correct database"):
        result = node.query(f"USE {database_name}; SELECT currentDatabase()")
        assert result.output.strip() == f"{database_name}", error()


@TestScenario
def array_join(self, minio_root_user, minio_root_password):
    """Check `ARRAY JOIN` with List column from Iceberg table."""
    node = self.context.node
    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        schema = Schema(
            NestedField(
                field_id=16,
                name="list",
                field_type=ListType(
                    element_type=StringType(), element_id=17, element_required=False
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

    with And("insert data into the table"):
        df = pa.Table.from_pylist(
            [
                {"list": ["a", "b", "c", "abc"]},
            ]
        )
        table.append(df)

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("read data from the table"):
        result = node.query(
            f"""
                SELECT list, a 
                FROM {database_name}.\\`{namespace}.{table_name}\\` 
                ARRAY JOIN list AS a
                ORDER BY tuple(*)
                FORMAT Values
            """
        )
        assert (
            result.output.strip()
            == "(['a','b','c','abc'],'a'),(['a','b','c','abc'],'b'),(['a','b','c','abc'],'c'),(['a','b','c','abc'],'abc')"
        ), error()


@TestScenario
def show_data_lake_catalogs_in_system_tables(
    self, minio_root_user, minio_root_password, node=None
):
    """Check show_data_lake_catalogs_in_system_tables setting."""
    node = self.context.node if node is None else node
    namespace = f"iceberg_namespace"
    table_name = f"table_name"
    database_name = f"iceberg_database_name"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name, with_data=True
        )

    with When("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then(
        "check that show_data_lake_catalogs_in_system_tables setting is enabled before 25.10"
    ):
        value = get_settings_value(
            setting_name="show_data_lake_catalogs_in_system_tables"
        )
        if check_clickhouse_version("<=25.9")(self):
            assert value == "1", error()
        else:
            assert value == "0", error()

    with And("check that iceberg table is visible in system.tables table"):
        if value == "1":
            iceberg_engine.check_values_in_system_tables(
                table_name=f"{namespace}.{table_name}", database=database_name
            )

    with And(
        "set the setting to 0 and check that iceberg table is not visible in system.tables table"
    ):
        result = node.query(
            f"""
            SET show_data_lake_catalogs_in_system_tables = 0;
            SELECT name FROM system.tables WHERE name = '{namespace}.{table_name}'
        """
        )
        compare_with_expected(expected="", output=result)

    with And(
        "set the setting to 1 and check that iceberg table is visible in system.tables table"
    ):
        result = node.query(
            f"""
            SET show_data_lake_catalogs_in_system_tables = 1;
            SELECT name FROM system.tables WHERE name = '{namespace}.{table_name}'
        """
        )
        compare_with_expected(expected=f"{namespace}.{table_name}", output=result)


@TestScenario
def show_tables_queries(self, minio_root_user, minio_root_password, node=None):
    """Check that SHOW TABLES query is not affected by show_data_lake_catalogs_in_system_tables setting."""
    node = self.context.node if node is None else node
    namespace = f"iceberg_namespace"
    table_name = f"table_name"
    database_name = f"iceberg_database_name"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name, with_data=True
        )

    with When("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And(
        "get result of show table query when show_data_lake_catalogs_in_system_tables is enabled"
    ):
        result_with_setting = node.query(
            f"SET show_data_lake_catalogs_in_system_tables = 1; SHOW TABLES FROM {database_name}"
        ).output

    with And(
        "get result of show table query when show_data_lake_catalogs_in_system_tables is disabled"
    ):
        result_without_setting = node.query(
            f"SET show_data_lake_catalogs_in_system_tables = 0; SHOW TABLES FROM {database_name}"
        ).output

    with Then("compare results"):
        assert result_with_setting == result_without_setting, error()


@TestScenario
def show_databases_queries(self, minio_root_user, minio_root_password, node=None):
    """Check that SHOW DATABASES query is not affected by show_data_lake_catalogs_in_system_tables setting."""
    node = self.context.node if node is None else node
    namespace = f"iceberg_namespace"
    table_name = f"table_name"
    database_name = f"iceberg_database_name"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name, with_data=True
        )

    with When("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And(
        "get result of SHOW DATABASES query when show_data_lake_catalogs_in_system_tables is enabled"
    ):
        result_with_setting = node.query(
            f"SET show_data_lake_catalogs_in_system_tables = 1; SHOW DATABASES"
        ).output

    with And(
        "get result of SHOW DATABASES query when show_data_lake_catalogs_in_system_tables is disabled"
    ):
        result_without_setting = node.query(
            f"SET show_data_lake_catalogs_in_system_tables = 0; SHOW DATABASES"
        ).output

    with And("compare results"):
        assert result_with_setting == result_without_setting, error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Sanity checks for DataLakeCatalog database engine in ClickHouse."""
    # Scenario(test=sanity)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=sort_order)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=recreate_table)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=multiple_tables)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=recreate_table_and_database)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=rename_database)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=rename_table_from_iceberg_database)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=use_database)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=array_join)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=show_data_lake_catalogs_in_system_tables)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=show_tables_queries)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=show_databases_queries)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
