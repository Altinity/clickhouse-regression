"""Namespace filter tests for DataLakeCatalog.

See namespace_filtering_test_cases.md for the full list of test cases.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

FILTERED_ERROR_MESSAGE = "DB::Exception: Namespace"
FILTERED_EXITCODE = 245


_NAMESPACE_PATHS = [
    "ns1",
    "ns1.ns11",
    "ns1.ns12",
    "ns1.ns11.ns111",
    "ns1.ns11.ns112",
    "ns1.ns12.ns121",
    "ns1.ns12.ns122",
    "ns2",
    "ns2.ns21",
    "ns2.ns22",
    "ns2.ns21.ns211",
    "ns2.ns21.ns212",
    "ns2.ns22.ns221",
    "ns2.ns22.ns222",
]


@TestStep(Given)
def create_namespace_filtering_setup(self, minio_root_user, minio_root_password):
    """
    Creates 14 namespaces and table1, table2 in each namespace.
    Returns dict path -> full name (e.g. names["ns1"], names["ns1.ns11"]).
    """
    prefix = f"nf_{getuid()}"
    names = {path: f"{prefix}_{path}" for path in _NAMESPACE_PATHS}

    with By("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with By("creating namespaces in parent-before-child order"):
        for path in _NAMESPACE_PATHS:
            catalog_steps.create_namespace(catalog=catalog, namespace=names[path])

    with And("creating table1 and table2 in each namespace with tables"):
        for path in _NAMESPACE_PATHS:
            catalog_steps.create_iceberg_table_with_three_columns(
                catalog=catalog, namespace=names[path], table_name="table1"
            )
            catalog_steps.create_iceberg_table_with_three_columns(
                catalog=catalog, namespace=names[path], table_name="table2"
            )

    return names, prefix


@TestScenario
def no_namespace_filter_all_tables_visible(self, minio_root_user, minio_root_password):
    """Create full setup, create database without namespaces filter, then verify all tables are visible."""
    node = self.context.node
    database_name = f"datalake_{getuid()}"

    with Given("create 14 namespaces and table1, table2 in each namespace"):
        names, _ = create_namespace_filtering_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("create database without namespaces filter"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )
        pause()

    with Then("check that all tables are visible"):
        result = node.query(f"SHOW TABLES FROM {database_name}").output.split()
        assert len(result) == 28, error()
        for path in _NAMESPACE_PATHS:
            assert f"{names[path]}.table1" in result, error()
            assert f"{names[path]}.table2" in result, error()


@TestScenario
def single_namespace_filter(self, minio_root_user, minio_root_password):
    """Check if only one namespace is specified, only tables from that namespace are visible."""
    node = self.context.node
    database_name = f"datalake_{getuid()}"

    with Given("create 14 namespaces and table1, table2 in each namespace"):
        names, prefix = create_namespace_filtering_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("create database with namespaces filter = ns1 only"):
        ns_allowed = f"{prefix}_ns1"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
            namespaces=ns_allowed,
        )
        pause()

    with Then("system.tables lists only tables from allowed namespace"):
        result = node.query(
            f"SELECT name FROM system.tables WHERE database='{database_name}' ORDER BY name",
            settings=[("show_data_lake_catalogs_in_system_tables", 1)],
        )
        for path in _NAMESPACE_PATHS:
            if ns_allowed in path:
                assert f"{names[path]}.table1" in result.output, error()
                assert f"{names[path]}.table2" in result.output, error()
            else:
                assert f"{names[path]}.table1" not in result.output, error()
                assert f"{names[path]}.table2" not in result.output, error()

    with And("check that select from allowed namespace succeeds"):
        for path in _NAMESPACE_PATHS:
            if ns_allowed in path:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name, namespace=names[path], table_name="table1", columns="count()"
                ).output
                assert result.strip() == "10", error()
            else:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=names[path],
                    table_name="table1",
                    columns="count()",
                    exitcode=FILTERED_EXITCODE,
                    message=FILTERED_ERROR_MESSAGE,
                ).output


@TestFeature
@Name("namespace filtering")
def feature(self, minio_root_user, minio_root_password):
    """Namespace filter tests for DataLakeCatalog (REST catalog)."""
    Scenario(test=no_namespace_filter_all_tables_visible)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=no_namespace_filter_all_tables_visible)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
