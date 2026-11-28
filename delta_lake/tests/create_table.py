"""CREATE TABLE ... ENGINE = DeltaLake at a location with no ``_delta_log``.

Creating a table needs ``allow_delta_lake_create_table = 1`` and the
writes setting. ``deltalake`` must be able to open the log ClickHouse
writes.
"""

from testflows.asserts import error
from testflows.core import *

from deltalake import DeltaTable as DeltaTableReader

from helpers.common import getuid
from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Create_NewTable,
    RQ_SRS_050_ClickHouse_DeltaLake_Create_NoPartition,
    RQ_SRS_050_ClickHouse_DeltaLake_Create_RegisterInUnity,
)
from delta_lake.tests.steps import (
    DeltaTable,
    create_database,
    create_schema,
    list_keys,
)
from delta_lake.tests.steps.access import engine_arguments
from delta_lake.tests.steps.catalog import (
    _delete_prefix,
    _drop_table,
    _storage_options,
)
from delta_lake.tests.steps.query import (
    catalog_source,
    expect_error,
    expect_query_lines,
    query_lines,
    try_query,
    writes_setting,
)

COLUMNS_SQL = "(id Int64, name String, n Nullable(Int32))"

EXPECTED_TYPES = [
    ("id", "Int64"),
    ("name", "String"),
    ("n", "Nullable(Int32)"),
]

EXPECTED_LOG_SCHEMA = [
    ("id", "long", False),
    ("name", "string", False),
    ("n", "integer", True),
]


def create_settings(self):
    return f"SET {writes_setting(self)} = 1; SET allow_delta_lake_create_table = 1; "


@TestStep(Given)
def new_location(self, namespace=None):
    """A table location with nothing in it. Delete whatever lands there later."""
    table = DeltaTable(namespace or f"new_{getuid()}", f"tbl_{getuid()}")
    try:
        yield table
    finally:
        with Finally(f"delete files {table.prefix}"):
            _delete_prefix(
                f"{table.prefix}/",
                self.context.rustfs_access_key,
                self.context.rustfs_secret_key,
            )


@TestStep(Given)
def create_new_table(self, table, sql_suffix="", node=None):
    """Run CREATE TABLE at ``table``. Drop the ClickHouse table later."""
    node = self.context.node if node is None else node
    name = f"delta_new_{getuid()}"
    arguments = engine_arguments(
        table.http_url, self.context.rustfs_access_key, self.context.rustfs_secret_key
    )
    try:
        result = node.query(
            create_settings(self)
            + f"CREATE TABLE {name} {COLUMNS_SQL} ENGINE = DeltaLake({arguments})"
            + sql_suffix,
            no_checks=True,
            retry_count=0,
        )
        yield name, result
    finally:
        with Finally(f"drop table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


def log_keys(table):
    return [key for key in list_keys(prefix=table.prefix) if "_delta_log" in key]


@TestScenario
@Name("new table")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Create_NewTable("1.0"))
def new_table(self):
    """CREATE TABLE writes one commit that deltalake opens, and reads zero rows."""

    with Given("an empty location"):
        table = new_location()

    with When("I create a table with three columns"):
        name, result = create_new_table(table=table)
        assert result.exitcode == 0, error(result.output)

    with Then("the location has the first commit"):
        keys = log_keys(table)
        assert keys == [f"{table.prefix}/_delta_log/{0:020d}.json"], error(keys)

    with And("SELECT returns zero rows"):
        expect_query_lines(sql=f"SELECT count() FROM {name}", expected=["0"])

    with And("DESCRIBE lists the CREATE TABLE types"):
        described = query_lines(sql=f"DESCRIBE TABLE {name}")
        found = [tuple(line.split("\t")[:2]) for line in described]
        assert found == EXPECTED_TYPES, error(described)

    with And("deltalake opens the log with the same columns"):
        options = _storage_options(
            self.context.rustfs_access_key, self.context.rustfs_secret_key
        )
        schema = DeltaTableReader(table.location, storage_options=options).schema()
        found = [(f.name, f.type.type, f.nullable) for f in schema.fields]
        assert found == EXPECTED_LOG_SCHEMA, error(found)


@TestScenario
@Name("partition by is rejected")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Create_NoPartition("1.0"))
def partition_by_rejected(self):
    """PARTITION BY fails and writes no log."""

    with Given("an empty location"):
        table = new_location()

    with When("I create the table with PARTITION BY name"):
        _, result = create_new_table(table=table, sql_suffix=" PARTITION BY name")

    with Then("the statement fails"):
        expect_error(result=result, message="doesn't support PARTITION_BY")

    with And("the location has no _delta_log"):
        keys = log_keys(table)
        assert keys == [], error(keys)


@TestScenario
@Name("create in unity")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Create_RegisterInUnity("1.0"))
def create_in_unity(self):
    """CREATE TABLE inside the Unity database registers the table there."""

    with Given("a Unity schema and the suite database"):
        namespace = create_schema()
        database = create_database()

    with And("an empty location in that schema"):
        table = new_location(namespace=namespace)

    try:
        with When("I create the table through the Unity database"):
            arguments = engine_arguments(
                table.http_url,
                self.context.rustfs_access_key,
                self.context.rustfs_secret_key,
            )
            result = try_query(
                sql=create_settings(self)
                + f"CREATE TABLE {catalog_source(database, table)} "
                f"{COLUMNS_SQL} ENGINE = DeltaLake({arguments})"
            )

        with Then("the statement succeeds"):
            assert result.exitcode == 0, error(result.output)

        with And("SHOW TABLES lists it"):
            tables = query_lines(sql=f"SHOW TABLES FROM {database}")
            assert f"{namespace}.{table.name}" in tables, error(tables)

        with And("SELECT through Unity returns zero rows"):
            expect_query_lines(
                sql=f"SELECT count() FROM {catalog_source(database, table)}",
                expected=["0"],
            )
    finally:
        with Finally("I drop the table from Unity"):
            _drop_table(namespace, table.name)


@TestFeature
@Name("delta create table")
def feature(self):
    """CREATE TABLE for new Delta tables."""
    Scenario(test=new_table)()
    Scenario(test=partition_by_rejected)()
    Scenario(test=create_in_unity)()
