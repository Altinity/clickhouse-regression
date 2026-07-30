from testflows.core import *
from testflows.asserts import error

from helpers.common import (
    getuid,
    check_clickhouse_version,
    check_if_antalya_build,
)

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine
import iceberg.tests.steps.common as common

EXPECTED_PARTITION_KEY = "name"
EXPECTED_SORTING_KEY = "name asc"

def _assert_on_antalya_26_1_plus(test):
    return check_if_antalya_build(test) and check_clickhouse_version(">=26.1")(test)


def _keys_from_metadata_without_snapshot(test):
    """PR 1874: keys readable from table metadata before any data snapshot."""
    return (
        check_if_antalya_build(test)
        and check_clickhouse_version(">26.3.10.20001")(test)
    )


def assert_system_table_keys(node, table_name, partition_key, sorting_key):
    actual_partition_key = node.query(
        f"SELECT partition_key FROM system.tables WHERE name = '{table_name}'"
    ).output.strip()
    actual_sorting_key = node.query(
        f"SELECT sorting_key FROM system.tables WHERE name = '{table_name}'"
    ).output.strip()

    assert actual_partition_key == partition_key, error()
    assert actual_sorting_key == sorting_key, error()


@TestScenario
def system_tables_partition_sorting_keys(self, minio_root_user, minio_root_password):
    """Check that system.tables exposes partition_key and sorting_key for Iceberg table engine.
    Verifies PR: https://github.com/Altinity/ClickHouse/pull/1432.
    Verifies PR: https://github.com/Altinity/ClickHouse/pull/1874.
    """
    node = self.context.node
    namespace = f"iceberg_{getuid()}"
    table_name = f"name_{getuid()}"
    keys_from_metadata = _keys_from_metadata_without_snapshot(self)

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"create {namespace}.{table_name} table with three columns and no data"):
        iceberg_table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            with_data=False,
        )

    with And("create table with Iceberg engine that reads this Iceberg table"):
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=table_name,
            url="http://minio:9000/warehouse/data",
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
        )

    with Then("check partition_key and sorting_key in system.tables before first insert"):
        if _assert_on_antalya_26_1_plus(self):
            if keys_from_metadata:
                assert_system_table_keys(
                    node,
                    table_name,
                    EXPECTED_PARTITION_KEY,
                    EXPECTED_SORTING_KEY,
                )
            else:
                assert_system_table_keys(node, table_name, "", "")

    with And("read from the empty table"):
        common.get_select_query_result(table_name=table_name)

    with And("check partition_key and sorting_key after reading empty table"):
        if _assert_on_antalya_26_1_plus(self):
            if keys_from_metadata:
                assert_system_table_keys(
                    node,
                    table_name,
                    EXPECTED_PARTITION_KEY,
                    EXPECTED_SORTING_KEY,
                )
            else:
                assert_system_table_keys(node, table_name, "", "name")

    with And("insert data into Iceberg table and check system.tables"):
        df = pa.Table.from_pylist(
            [
                {
                    "name": "alice",
                    "double": 1.23,
                    "integer": 42,
                }
            ]
        )
        iceberg_table.append(df)

    with And("check partition_key and sorting_key after data is inserted"):
        if _assert_on_antalya_26_1_plus(self):
            assert_system_table_keys(
                node,
                table_name,
                EXPECTED_PARTITION_KEY,
                EXPECTED_SORTING_KEY,
            )
