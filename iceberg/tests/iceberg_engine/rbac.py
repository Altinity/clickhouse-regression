from testflows.core import *
from testflows.asserts import error

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import create_user, getuid


@TestScenario
def rbac_sanity(self, minio_root_user, minio_root_password):
    """Test basic RBAC with tables from Iceberg engine."""

    with Given("create catalog and Iceberg table with data"):
        table_name, namespace = (
            catalog_steps.create_catalog_and_iceberg_table_with_data(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
        )

    with Then("create database with Iceberg engine"):
        database_name = "datalake"
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            rest_catalog_url="http://ice-rest-catalog:5000",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "true	1000	456.78	Alice	2024-01-01" in result.output, error()
        assert "true	3000	6.7	Charlie	2022-01-01" in result.output, error()
        assert "false	2000	456.78	Bob	2023-05-15" in result.output, error()
        assert "false	4000	8.9	1	2021-01-01" in result.output, error()

    with Then("create new clickhouse user"):
        user_name = f"test_user_{getuid()}"
        create_user(name=user_name)

    with And("try to read from iceberg table with new user"):
        exitcode, message = 241, f"DB::Exception: {user_name}: Not enough privileges."
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            user=user_name,
            exitcode=exitcode,
            message=message,
        )

    with And("grant read access to the table"):
        self.context.node.query(
            f"GRANT SELECT ON {database_name}.\\`{namespace}.{table_name}\\` TO {user_name}"
        )

    with And("try to read from iceberg table with new user"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            user=user_name,
        )
        assert "true	1000	456.78	Alice	2024-01-01" in result.output, error()
        assert "true	3000	6.7	Charlie	2022-01-01" in result.output, error()
        assert "false	2000	456.78	Bob	2023-05-15" in result.output, error()
        assert "false	4000	8.9	1	2021-01-01" in result.output, error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=rbac_sanity)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
