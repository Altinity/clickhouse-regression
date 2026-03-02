from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine


@TestScenario
def system_tables_partition_sorting_keys(self, minio_root_user, minio_root_password):
    """Check that system.tables exposes partition_key and sorting_key for Iceberg table engine.

    Verifies PR: https://github.com/Altinity/ClickHouse/pull/1432
    """
    node = self.context.node
    namespace = f"iceberg_{getuid()}"
    table_name = f"name_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"create {namespace}.{table_name} table with three columns"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            with_data=True,
        )

    with And("create table with Iceberg engine that reads this Iceberg table"):
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=table_name,
            url="http://minio:9000/warehouse/data",
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
        )

    with Then("check partition_key and sorting_key in system.tables"):
        partition_key = node.query(
            f"SELECT partition_key FROM system.tables WHERE name = '{table_name}'"
        ).output.strip()
        sorting_key = node.query(
            f"SELECT sorting_key FROM system.tables WHERE name = '{table_name}'"
        ).output.strip()

        if check_if_antalya_build(self) and check_clickhouse_version(">=26.1")(self):
            assert partition_key == "name", error()
            assert sorting_key == "name asc", error()

