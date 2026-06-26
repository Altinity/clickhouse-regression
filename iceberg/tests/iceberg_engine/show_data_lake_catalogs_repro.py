#!/usr/bin/env python3
from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def similar_table_names_hint(self, minio_root_user, minio_root_password):
    """
    Create multiple tables with similar names across namespaces and
    check that the hint is not shown when show_data_lake_catalogs_in_system_tables is set to 0.
    """
    node = self.context.node

    with Given("define database and namespaces"):
        ns1 = "schema1"
        ns2 = "schema2"
        database_name = f"datalake_{getuid()}"

    with And("define similar table names"):
        tables = [
            (ns1, "table"),
            (ns1, "table_1"),
            (ns1, "table_2"),
            (ns2, "table"),
            (ns2, "table_1"),
            (ns2, "table_2"),
        ]

    with And("create catalog and namespaces"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=ns1)
        catalog_steps.create_namespace(catalog=catalog, namespace=ns2)

    with And("create tables with similar names in both namespaces"):
        for namespace, table_name in tables:
            catalog_steps.create_iceberg_table_with_three_columns(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                with_data=True,
                number_of_rows=5,
            )

    with When("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then(
        "with show_data_lake_catalogs_in_system_tables=0, system.tables must not show catalog tables"
    ):
        result = node.query(
            f"""
            SET show_data_lake_catalogs_in_system_tables = 0;
            SELECT name FROM system.tables WHERE database = '{database_name}'
            """
        )
        assert result.output.strip() == "", error()

    with And("SHOW TABLES FROM must work (explicit operation)"):
        result = node.query(
            f"""
            SET show_data_lake_catalogs_in_system_tables = 0;
            SHOW TABLES FROM {database_name}
            """
        )
        for namespace, table_name in tables:
            assert f"{namespace}.{table_name}" in result.output, error()

    with And("with show_data_lake_catalogs_in_system_tables=0, hint must not be shown"):
        with By("dropping non-existent table with similar name"):
            result = node.query(
                f"""
                SET show_data_lake_catalogs_in_system_tables = 0;
                DROP TABLE {database_name}.\\`{ns1}.tabl\\`
                """,
                no_checks=True,
            )
            if check_clickhouse_version(">=26.4")(self) or check_if_antalya_build(self):
                for namespace, table_name in tables:
                    assert f"{namespace}.{table_name}" not in result.output, error()

                assert result.exitcode == 60, error()
                assert (
                    f"DB::Exception: Table {database_name}.`{ns1}.tabl` does not exist."
                    in result.output
                ), error()
            else:
                assert result.exitcode == 60, error()
                assert (
                    f"DB::Exception: Table {database_name}.`{ns1}.tabl` does not exist. Maybe you meant {database_name}.`{ns1}.table`?. (UNKNOWN_TABLE)"
                    in result.output
                ), error()


@TestFeature
@Name("show_data_lake_catalogs hint")
def feature(self, minio_root_user, minio_root_password):
    """Test show_data_lake_catalogs hint behavior."""
    Scenario(test=similar_table_names_hint)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
