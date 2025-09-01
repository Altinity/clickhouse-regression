from testflows.core import *


from helpers.common import getuid

from helpers.tables import *

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine


@TestStep(Given)
def create_test_merge_tree_table(self):
    """Create test merge tree table."""
    node = self.context.node
    table_name = f"mt_table_{getuid()}"
    try:
        with By("create test merge tree table"):
            node.query(
                f"""
                CREATE TABLE {table_name} (id UInt64, year UInt16) 
                ENGINE = MergeTree() 
                PARTITION BY year 
                ORDER BY id
            """
            )

        with And("populate the table"):
            node.query(
                f"INSERT INTO {table_name} VALUES (1, 2020), (2, 2020), (3, 2020), (4, 2021), (1, 2020), (0, 2020)"
            )
            node.query(f"INSERT INTO {table_name} VALUES (5, 2020), (6, 2020)")

        yield table_name

    finally:
        with Finally("drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestStep(Given)
def create_test_s3_table(self):
    """Create test s3 table."""
    node = self.context.node
    table_name = f"s3_table_{getuid()}"
    try:
        node.query(
            f"""
            CREATE TABLE {table_name} (id UInt64, year UInt16) 
            ENGINE = S3(s3_conn, filename='{table_name}', format=Parquet, partition_strategy='hive') 
            PARTITION BY year
            ORDER BY id
        """
        )
        yield table_name

    finally:
        with Finally("drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Run Ice tests."""
    ice_node = self.context.ice_node
    node = self.context.node

    with Given("check ice version"):
        version = ice_node.command("ice -V").output

    with And("create test merge tree table"):
        mt_table_name = create_test_merge_tree_table()

    with And("create test s3 table"):
        s3_table_name = create_test_s3_table()

    with When("export partition from merge tree table to s3 table"):
        partition_ids = ["2020", "2021"]
        for partition_id in partition_ids:
            node.query(
                f"""
                ALTER TABLE {mt_table_name} 
                EXPORT PARTITION ID '{partition_id}' 
                TO TABLE {s3_table_name} 
                SETTINGS 
                    allow_experimental_export_merge_tree_partition = 1, 
                    export_merge_tree_partition_background_execution = 0
                """
            )

    with And("create database with Iceberg engine"):
        database_name = f"iceberg_database_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            rest_catalog_url="http://ice-rest-catalog:5000",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with Then(
        "create iceberg table with partitioning and sort order using schema from parquet file"
    ):
        iceberg_table_name = f"iceberg_table_{getuid()}"
        ice_node.command(
            f'ice create-table default.{iceberg_table_name} -p --schema-from-parquet s3://warehouse/{s3_table_name}/year=2020/*.parquet --partition=\'[{{"column":"year","transform":"identity"}}]\' --sort=\'[{{"column":"id"}}]\''
        )

    with And("run ice insert command"):
        for partition_id in partition_ids:
            ice_node.command(
                f"ice insert default.{iceberg_table_name} -p s3://warehouse/{s3_table_name}/year={partition_id}/*.parquet"
            )

    with And("read data from iceberg table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace="default",
            table_name=iceberg_table_name,
            object_storage_cluster=None,
        )
        note(result.output)

    with And("check show create table"):
        node.query(
            f"SHOW CREATE TABLE {database_name}.\\`default.{iceberg_table_name}\\`"
        )
