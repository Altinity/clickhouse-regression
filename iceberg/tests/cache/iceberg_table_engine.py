from testflows.core import *
from helpers.common import getuid

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine


@TestFeature
def cache(self, minio_root_user, minio_root_password, node=None):
    """
    Test caching when selecting from a ClickHouse table with the Iceberg engine.
    """
    if node is None:
        node = self.context.node

    namespace = f"namespace_{getuid()}"
    table_name = f"iceberg_table_{getuid()}"
    clickhouse_iceberg_table_name = "clickhouse_iceberg_table_" + getuid()

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"create {namespace}.{table_name} table with data"):
        table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            with_data=True,
            number_of_rows=100,
        )

    with And("create table with Iceberg engine"):
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=clickhouse_iceberg_table_name,
            url="http://minio:9000/warehouse/data",
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
        )

    with And("read data from ClickHouse table with Iceberg engine"):
        node.query(f"SELECT * FROM {clickhouse_iceberg_table_name}")


@TestFeature
@Name("iceberg table engine")
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=cache)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
