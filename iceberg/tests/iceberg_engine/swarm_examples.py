#!/usr/bin/env python3

from testflows.core import *

from helpers.common import getuid, check_clickhouse_version, check_if_not_antalya_build

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def swarm_examples(self, minio_root_user, minio_root_password, node=None):
    """Swarm examples."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"database_{getuid()}"

    if node is None:
        node = self.context.node

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with When(f"create namespace and create {namespace}.{table_name} table"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
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

    with And("select directly from S3 data using the swarm cluster"):
        node.query(
            f"""
            SELECT hostName() AS host, count()
            FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
            GROUP BY host
            SETTINGS use_hive_partitioning=1, object_storage_cluster='swarm'
            """
        )

    with And("select directly from S3 data using the swarm cluster without GROUP BY"):
        node.query(
            f"""
            SELECT hostName() AS host, count()
            FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
            GROUP BY host
            SETTINGS use_hive_partitioning=1, object_storage_cluster='swarm'
            """
        )

    with And("select Iceberg table data"):
        node.query(
            f"""
            SELECT hostName() AS host, count()
            FROM icebergS3Cluster('swarm', 'http://minio:9000/warehouse/data', '{minio_root_user}', '{minio_root_password}')
            GROUP BY host
            SETTINGS object_storage_cluster = 'swarm'"""
        )

    with And("select Iceberg actual table data with GROUP BY"):
        node.query(
            f"""
                SELECT hostName() AS host, *
                FROM s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
                SETTINGS use_hive_partitioning=1
            """
        )

    with And("select Iceberg actual table data with GROUP BY"):
        exitcode, message = None, None
        if check_clickhouse_version("<25.8") and check_if_not_antalya_build(self):
            exitcode = 70
            message = "DB::Exception: Conversion from AggregateFunction(groupArray, LowCardinality(String)) to AggregateFunction(groupArray, Nullable(String)) is not supported: While executing Remote."

        node.query(
            f"""
                SELECT hostName() AS host, arrayStringConcat(groupArray(name), ', ') AS names, sum(integer) AS total_age
                FROM s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
                SETTINGS use_hive_partitioning=1
            """,
            exitcode=exitcode,
            message=message,
        )


@TestFeature
@Name("swarm")
def feature(self, minio_root_user, minio_root_password):
    """Run swarm examples."""
    Scenario(test=swarm_examples)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
