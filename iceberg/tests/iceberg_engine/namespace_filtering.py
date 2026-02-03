from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from testflows.combinatorics import combinations


import random

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.common as common_steps
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

_INVALID_NAMESPACE_PATHS = [
    "ns1.ns21",
    "ns3",
    "ns3.*",
    "ns3.ns11.ns112",
    "ns1.ns12.ns212.*",
    "ns2.ns12.ns121.ns121.*",
]


def model(namespace_filter, namespace_path):
    """Return whether the namespace is allowed by the filter."""
    allowed_namespaces = [ns.strip() for ns in namespace_filter.split(",")]
    for allowed_namespace in allowed_namespaces:
        if allowed_namespace.endswith(".*"):
            if namespace_path.startswith(allowed_namespace[:-1]):
                return True
        else:
            if namespace_path == allowed_namespace:
                return True
    return False


def check_select_from_table(database_name, namespace, table_name, is_allowed=True):
    """Check that select from table succeeds if is_allowed else fails with the
    filtered namespace error."""
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
    """Check that table is visible in system.tables if is_allowed else not visible."""
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


def check_drop_table(database_name, namespace, table_name, is_allowed=True):
    """Check that drop table succeeds if is_allowed else fails with the filtered namespace error."""
    exitcode, message = 0, None
    if not is_allowed:
        exitcode = FILTERED_EXITCODE
        message = FILTERED_ERROR_MESSAGE

    current().context.node.query(
        f"DROP TABLE {database_name}.\\`{namespace}.{table_name}\\`", exitcode=exitcode, message=message
    )
    if is_allowed:
        result = (
            current()
            .context.node.query(
                f"SHOW TABLES FROM {database_name}", settings=[("show_data_lake_catalogs_in_system_tables", 1)]
            )
            .output.split()
        )
        assert f"{namespace}.{table_name}" not in result, error()


@TestStep(Given)
def create_namespace_filtering_setup(self, minio_root_user, minio_root_password):
    """
    Creates 14 namespaces and two tables(table1, table2) in each namespace.
    Returns dict path -> full name (e.g. names["ns1"], names["ns1.ns11"]).
    """
    prefix = f"nf_{getuid()}"
    names = {path: f"{prefix}_{path}" for path in _NAMESPACE_PATHS}

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with By("creating namespaces in parent-before-child order"):
        for path in _NAMESPACE_PATHS:
            catalog_steps.create_namespace(catalog=catalog, namespace=names[path])

    with And("creating table1 and table2 in each namespace"):
        for path in _NAMESPACE_PATHS:
            for table_name in ["table1", "table2"]:
                catalog_steps.create_iceberg_table_with_three_columns(
                    catalog=catalog,
                    namespace=names[path],
                    table_name=table_name,
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
            namespaces=None,
        )

    with Then("check that all tables are visible"):
        result = node.query(
            f"SHOW TABLES FROM {database_name}", settings=[("show_data_lake_catalogs_in_system_tables", 1)]
        ).output.split()
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
def joins_with_namespace_filter_sanity_check(self, minio_root_user, minio_root_password):
    """Check that joins with namespace filter work correctly."""
    node = self.context.node
    database_name = f"datalake_{getuid()}"

    with Given("create 14 namespaces and table1, table2 in each namespace"):
        names, prefix = create_namespace_filtering_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("create database with namespaces filter: ns1, ns2"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            namespaces=f"{prefix}_ns1, {prefix}_ns2",
        )

    with Then("check that joins with namespace filter work correctly"):
        result = node.query(
            f"""
            SELECT count() FROM {database_name}.\\`{prefix}_ns1.table1\\` 
            JOIN {database_name}.\\`{prefix}_ns2.table2\\` 
            ON True
            """,
            settings=[("show_data_lake_catalogs_in_system_tables", 1)],
        )
        assert result.output.strip() == "100", error()

    with And("check that join with filtered namespace fails"):
        node.query(
            f"""
            SELECT * FROM {database_name}.\\`{prefix}_ns1.ns11.table1\\` 
            JOIN {database_name}.\\`{prefix}_ns2.table2\\` 
            ON {database_name}.\\`{prefix}_ns1.ns11.table1\\`.name = {database_name}.\\`{prefix}_ns2.table2\\`.name
            """,
            settings=[("show_data_lake_catalogs_in_system_tables", 1)],
            exitcode=FILTERED_EXITCODE,
            message=FILTERED_ERROR_MESSAGE,
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

    with Given("create 14 namespaces and table1, table2 in each namespace"):
        names, prefix = create_namespace_filtering_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("define all possible wildcard filters and sample 100 of them with length <= 5"):
        single_wildcard_filters = (
            [f"{prefix}_{path}" for path in _NAMESPACE_PATHS]
            + [f"{prefix}_{path}.*" for path in _NAMESPACE_PATHS]
            + [f"{prefix}_{path}" for path in _INVALID_NAMESPACE_PATHS]
        )
        all_combinations = []

        for i in range(6):
            combinations_of_length_i = list(combinations(single_wildcard_filters, i))
            all_combinations.extend([", ".join(combo) for combo in combinations_of_length_i])

        sample = random.sample(all_combinations, min(100, len(all_combinations)))

    for num, namespace_filter in enumerate(sample):
        Scenario(name=f"#{num}", test=check_namespace_filter)(
            namespace_filter=namespace_filter,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            prefix=prefix,
        )


@TestScenario
def check_drop_table_with_namespace_filter(self, minio_root_user, minio_root_password, namespace_filter):
    """Check that drop table works for allowed namespaces and fails for filtered namespaces."""
    database_name = f"datalake_{getuid()}"

    with Given("create 14 namespaces and table1, table2 in each namespace"):
        names, prefix = create_namespace_filtering_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    prefixed_filter = ", ".join(f"{prefix}_{p.strip()}" for p in namespace_filter.split(","))

    with When("create database with namespace filter"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            namespaces=prefixed_filter,
        )

    with Then("check that drop table works for allowed namespaces and fails for filtered namespaces"):
        for namespace in _NAMESPACE_PATHS:
            is_allowed = model(namespace_filter=prefixed_filter, namespace_path=f"{prefix}_{namespace}")
            for table_name in ["table1", "table2"]:
                check_drop_table(
                    database_name=database_name,
                    namespace=f"{prefix}_{namespace}",
                    table_name=table_name,
                    is_allowed=is_allowed,
                )


@TestScenario
def drop_table_with_namespace_filter(self, minio_root_user, minio_root_password):
    """Check that drop table works for allowed namespaces and fails for filtered namespaces."""
    node = self.context.node

    with Given("define all possible wildcard filters"):
        single_wildcard_filters = (
            [f"{path}" for path in _NAMESPACE_PATHS]
            + [f"{path}.*" for path in _NAMESPACE_PATHS]
            + [f"{path}" for path in _INVALID_NAMESPACE_PATHS]
        )
        all_combinations = []

        for i in range(6):
            combinations_of_length_i = list(combinations(single_wildcard_filters, i))
            all_combinations.extend([", ".join(combo) for combo in combinations_of_length_i])

        sample = random.sample(all_combinations, min(50, len(all_combinations)))

    for num, namespace_filter in enumerate(sample):
        Scenario(name=f"#{num}", test=check_drop_table_with_namespace_filter)(
            namespace_filter=namespace_filter,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
@Name("namespace filtering")
def feature(self, minio_root_user, minio_root_password):
    """Namespace filter tests for DataLakeCatalog."""
    Feature(test=check_namespace_filter_with_wildcard)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=no_namespace_filter_all_tables_visible)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Feature(test=drop_table_with_namespace_filter)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=joins_with_namespace_filter_sanity_check)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
