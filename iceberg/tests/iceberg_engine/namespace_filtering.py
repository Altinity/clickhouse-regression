from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from testflows.combinatorics import combinations


import random

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

random.seed(42)

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

invalid_namespace_paths = [
    "ns1.ns11.ns111.ns1111",
    "ns1.ns11.ns112.ns1121",
    "ns1.ns12.ns121.ns1211",
    "ns1.ns12.ns122.ns1221",
    "ns2.ns21.ns211.ns2111",
    "ns2.ns21.ns212.ns2121",
    "ns2.ns22.ns221.ns2211",
    "ns2.ns22.ns222.ns2221",
    "ns2.ns1",
    "ns2.ns1.*",
    "ns2.ns1.ns11",
    "ns2.ns1.ns11.*",
    "ns2.ns1.ns11.ns111",
    "ns2.ns1.ns11.ns111.*",
    "ns2.ns1.ns11.ns112",
    "ns2.ns1.ns11.ns112.*",
]


def model(namespace_filter, namespace_path):
    """Return expected output of select query for a given namespace filter
    and namespace paths.
    """
    allowed_namespaces = namespace_filter.split(",")
    for allowed_namespace in allowed_namespaces:
        if allowed_namespace.endswith(".*"):
            if namespace_path.startswith(allowed_namespace[:-2]) and (namespace_path != allowed_namespace[:-2]):
                return True
        else:
            if namespace_path == allowed_namespace:
                return True
    return False


def check_select_from_table(database_name, namespace, table_name, is_allowed=True):
    """Check that select from table succeeds."""
    exitcode, message = 0, None
    if not is_allowed:
        exitcode = FILTERED_EXITCODE
        message = FILTERED_ERROR_MESSAGE

    result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns="count()",
        exitcode=exitcode,
        message=message,
    ).output

    if is_allowed:
        assert result.strip() == "10", error()


def check_table_is_visible(database_name, namespace, table_name, is_allowed=True):
    """Check that table is visible in system.tables."""
    node = current().context.node
    result = node.query(
        f"SELECT name FROM system.tables WHERE database='{database_name}' AND name='{namespace}.{table_name}'",
        settings=[("show_data_lake_catalogs_in_system_tables", 1)],
    ).output

    if is_allowed:
        assert result.strip() == f"{namespace}.{table_name}", error()
    else:
        assert result.strip() == "", error()

    result = node.query(
        f"SHOW TABLES FROM {database_name}",
        settings=[("show_data_lake_catalogs_in_system_tables", 1)],
    ).output
    if is_allowed:
        assert f"{namespace}.{table_name}" in result, error()
    else:
        assert f"{namespace}.{table_name}" not in result, error()


@TestStep(Given)
def create_namespace_filtering_setup(self, minio_root_user, minio_root_password):
    """
    Creates 14 namespaces and two tables(table1, table2) in each namespace.
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
                catalog=catalog,
                namespace=names[path],
                table_name="table1",
                with_data=True,
                number_of_rows=10,
            )
            catalog_steps.create_iceberg_table_with_three_columns(
                catalog=catalog,
                namespace=names[path],
                table_name="table2",
                with_data=True,
                number_of_rows=10,
            )

    return names, prefix


@TestScenario
def no_namespace_filter_all_tables_visible(self, minio_root_user, minio_root_password):
    """Check that all tables are visible when no namespace filter is specified."""
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
        )

    with Then("check that all tables are visible"):
        result = node.query(f"SHOW TABLES FROM {database_name}").output.split()
        assert len(result) == 28, error()
        for path in _NAMESPACE_PATHS:
            assert f"{names[path]}.table1" in result, error()
            assert f"{names[path]}.table2" in result, error()

    with And("check that select from all tables succeeds"):
        for path in _NAMESPACE_PATHS:
            for table_name in ["table1", "table2"]:
                full_name = names[path]
                check_select_from_table(database_name=database_name, namespace=full_name, table_name=table_name)


@TestScenario
def single_namespace_filter(self, minio_root_user, minio_root_password):
    """Check that only tables from the specified namespace are visible when a
    single namespace is specified in the namespaces filter."""
    node = self.context.node

    with Given("create 14 namespaces and table1, table2 in each namespace"):
        names, prefix = create_namespace_filtering_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("create database with namespaces filter = ns1 only"):
        database_name = f"datalake_{getuid()}"
        ns_allowed = f"{prefix}_ns1"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            namespaces=ns_allowed,
        )

    with Then("check that only tables from the specified namespace are visible"):
        result = node.query(
            f"SELECT name FROM system.tables WHERE database='{database_name}' ORDER BY name",
            settings=[("show_data_lake_catalogs_in_system_tables", 1)],
        )
        for path in _NAMESPACE_PATHS:
            full_name = names[path]
            is_allowed = model(namespace_filter=ns_allowed, namespace_path=full_name)

            for table_name in ["table1", "table2"]:
                check_table_is_visible(
                    database_name=database_name, namespace=full_name, table_name=table_name, is_allowed=is_allowed
                )
                check_select_from_table(
                    database_name=database_name, namespace=full_name, table_name=table_name, is_allowed=is_allowed
                )

    with And("create datalake catalog database with filter ns1.*"):
        database_name = f"datalake_{getuid()}"
        ns_allowed = f"{prefix}_ns1"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            namespaces=f"{ns_allowed}.*",
        )

    with And("check that only tables under ns1.* are visible"):
        for path in _NAMESPACE_PATHS:
            full_name = names[path]
            is_allowed = model(namespace_filter=f"{ns_allowed}.*", namespace_path=full_name)
            note(f"full_name: {full_name}, is_allowed: {is_allowed}")
            for table_name in ["table1", "table2"]:
                check_table_is_visible(
                    database_name=database_name, namespace=full_name, table_name=table_name, is_allowed=is_allowed
                )
                check_select_from_table(
                    database_name=database_name, namespace=full_name, table_name=table_name, is_allowed=is_allowed
                )


@TestScenario
def check_namespace_filter(self, namespace_filter, minio_root_user, minio_root_password, prefix):
    """Check that the namespace filter is applied correctly."""
    with Given("create database with namespace filter"):
        database_name = f"datalake_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            namespaces=namespace_filter,
        )

    with When("detach/attach database"):
        self.context.node.query(f"DETACH DATABASE {database_name}")
        self.context.node.query(f"ATTACH DATABASE {database_name}")

    with Then("check that the namespace filter is applied correctly"):
        for namespace in _NAMESPACE_PATHS:
            is_allowed = model(namespace_filter=namespace_filter, namespace_path=f"{prefix}_{namespace}")
            for table_name in ["table1", "table2"]:
                check_table_is_visible(
                    database_name=database_name,
                    namespace=f"{prefix}_{namespace}",
                    table_name=table_name,
                    is_allowed=is_allowed,
                )
                check_select_from_table(
                    database_name=database_name,
                    namespace=f"{prefix}_{namespace}",
                    table_name=table_name,
                    is_allowed=is_allowed,
                )


@TestFeature
def check_namespace_filter_with_wildcard(self, minio_root_user, minio_root_password):
    """Check that only tables from the specified namespace are visible when a
    wildcard is specified in the namespaces filter."""
    node = self.context.node

    with Given("create 14 namespaces and table1, table2 in each namespace"):
        names, prefix = create_namespace_filtering_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("define all possible wildcard filters"):
        single_wildcard_filters = [f"{prefix}_{path}" for path in _NAMESPACE_PATHS] + [
            f"{prefix}_{path}.*" for path in _NAMESPACE_PATHS
        ]
        all_combinations = []

        for i in range(6):
            combinations_of_length_i = list(combinations(single_wildcard_filters, i))
            all_combinations.extend([", ".join(combo) for combo in combinations_of_length_i])

        sample = random.sample(all_combinations, min(100, len(all_combinations)))

    with Then("check each filter from the sample of filters"):
        for num, namespace_filter in enumerate(sample):
            Scenario(name=f"#{num}", test=check_namespace_filter)(
                namespace_filter=namespace_filter,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                prefix=prefix,
            )


@TestFeature
@Name("namespace filtering")
def feature(self, minio_root_user, minio_root_password):
    """Namespace filter tests for DataLakeCatalog (REST catalog)."""
    # Scenario(test=no_namespace_filter_all_tables_visible)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Scenario(test=single_namespace_filter)(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(test=check_namespace_filter_with_wildcard)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
