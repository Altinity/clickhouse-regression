"""Catalog statements around a Delta table registered in Unity.

The table is the sanity table: ``name`` and ``value``, rows Alice, Bob,
and Charlie. The row values are covered by ``sanity.py``. These scenarios
check how the Unity database exposes that table.
"""

from testflows.asserts import error
from testflows.core import *

from helpers.common import check_clickhouse_version, getuid
from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_Check,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_CreateDatabase,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_DeltaTable,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_Enable,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_Names,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_Show,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_StorageKeys,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_SystemTables,
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_V2,
)
from delta_lake.tests.steps import (
    column,
    create_database,
    create_delta_table,
    expect_delta_table,
)
from delta_lake.tests.steps.catalog import database_sql, unity_enable_setting
from delta_lake.tests.steps.query import (
    catalog_source,
    catalog_tables_setting,
    expect_error,
    expect_query_lines,
    query_lines,
    try_query,
)

COLUMNS = (
    column("name", "STRING", "string", "string"),
    column("value", "LONG", "bigint", "long"),
)

ROWS = (("Alice", 20), ("Bob", 30), ("Charlie", 40))

EXPECTED = ["Alice\t20", "Bob\t30", "Charlie\t40"]

EXPECTED_TYPES = [("name", "Nullable(String)"), ("value", "Nullable(Int64)")]

WRONG_SECRET = "wrong-secret"


def sanity_table():
    return create_delta_table(columns=COLUMNS, rows=ROWS)


def v2_modes(self):
    """``use_unity_catalog_v2`` off, and on for 26.10 and newer."""
    if check_clickhouse_version(">=26.10")(self):
        return (False, True)
    return (False,)


def mode_name(unity_v2):
    return "Unity v2" if unity_v2 else "Unity"


@TestScenario
@Name("enable setting")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Unity_Enable("1.0"))
def enable_setting(self):
    """CREATE DATABASE fails while the Unity setting is off."""
    node = self.context.node
    name = f"delta_off_{getuid()}"

    try:
        with When("I create the database with the setting off"):
            result = try_query(
                sql=f"SET {unity_enable_setting(self)} = 0; "
                + database_sql(
                    name,
                    self.context.rustfs_access_key,
                    self.context.rustfs_secret_key,
                )
            )

        with Then("the statement fails"):
            expect_error(result=result, message=unity_enable_setting(self))

        with And("SHOW DATABASES does not list it"):
            databases = query_lines(sql="SHOW DATABASES")
            assert name not in databases, error(databases)
    finally:
        with Finally("I drop the database if it was created"):
            node.query(f"DROP DATABASE IF EXISTS {name}")


@TestScenario
@Name("table names")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Unity_Names("1.0"))
def table_names(self):
    """The table name is schema.table and needs backticks."""

    with Given("the sanity table in Unity"):
        table = sanity_table()

    for unity_v2 in v2_modes(self):
        with When(f"{mode_name(unity_v2)} is opened"):
            database = create_database(unity_v2=unity_v2)

        with Then("schema.table without backticks fails"):
            result = try_query(
                sql=f"SELECT * FROM {database}.{table.namespace}.{table.name}"
            )
            expect_error(result=result, forbidden="Alice")

        with And("the backtick form returns the rows"):
            expect_query_lines(
                sql=f"SELECT name, value FROM {catalog_source(database, table)} "
                "ORDER BY name",
                expected=EXPECTED,
            )


@TestScenario
@Name("show statements")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_Show("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_DeltaTable("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_V2("1.0"),
)
def show_statements(self):
    """SHOW TABLES, SHOW CREATE, SHOW COLUMNS, and DESCRIBE.

    With v2 on, the engine stays DeltaLake and the columns stay the same.
    ``SHOW COLUMNS`` reads ``system.columns``, so it needs the setting
    that puts catalog tables in system tables.
    """

    with Given("the sanity table in Unity"):
        table = sanity_table()

    for unity_v2 in v2_modes(self):
        with When(f"{mode_name(unity_v2)} is opened"):
            database = create_database(unity_v2=unity_v2)
            source = catalog_source(database, table)

        with Then("SHOW TABLES and SHOW CREATE describe a DeltaLake table"):
            expect_delta_table(database=database, table=table)

        with And("DESCRIBE lists the log types"):
            described = query_lines(sql=f"DESCRIBE TABLE {source}")
            found = [tuple(line.split("\t")[:2]) for line in described]
            assert found == EXPECTED_TYPES, error(described)

        with And("SHOW COLUMNS lists the same types"):
            shown = query_lines(
                sql=f"SHOW COLUMNS FROM {source} "
                f"SETTINGS {catalog_tables_setting(self)} = 1"
            )
            found = [tuple(line.split("\t")[:2]) for line in shown]
            assert found == EXPECTED_TYPES, error(shown)


@TestScenario
@Name("wrong storage secret")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_CreateDatabase("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_StorageKeys("1.0"),
)
def wrong_storage_secret(self):
    """The storage secret is checked on read, not on CREATE DATABASE."""

    with Given("the sanity table in Unity"):
        table = sanity_table()

    with When("I open Unity with a wrong aws_secret_access_key"):
        database = create_database(secret_key=WRONG_SECRET)

    with Then("SELECT fails and returns no row"):
        result = try_query(
            sql=f"SELECT name FROM {catalog_source(database, table)}"
        )
        expect_error(result=result, forbidden="Alice")


@TestScenario
@Name("check database")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Unity_Check("1.0"))
def check_database(self):
    """CHECK DATABASE succeeds for the suite catalog."""

    with Given("the suite Unity database"):
        database = create_database()

    with Then("CHECK DATABASE succeeds"):
        self.context.node.query(f"CHECK DATABASE {database}")


@TestScenario
@Name("system tables")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Unity_SystemTables("1.0"))
def system_tables(self):
    """Catalog tables are in system.tables only with the setting on."""
    setting = catalog_tables_setting(self)

    with Given("the sanity table in Unity"):
        table = sanity_table()

    for unity_v2 in v2_modes(self):
        with When(f"{mode_name(unity_v2)} is opened"):
            database = create_database(unity_v2=unity_v2)

        sql = (
            "SELECT name FROM system.tables "
            f"WHERE database = '{database}' "
            f"AND name = '{table.namespace}.{table.name}'"
        )

        with Then(f"system.tables does not list the table with {setting} = 0"):
            expect_query_lines(sql=f"{sql} SETTINGS {setting} = 0", expected=[])

        with And(f"system.tables lists it with {setting} = 1"):
            expect_query_lines(
                sql=f"{sql} SETTINGS {setting} = 1",
                expected=[f"{table.namespace}.{table.name}"],
            )


@TestFeature
@Name("delta unity")
def feature(self):
    """Unity database statements for a Delta table."""
    Scenario(test=enable_setting)()
    Scenario(test=table_names)()
    Scenario(test=show_statements)()
    Scenario(test=wrong_storage_secret)()
    Scenario(test=check_database)()
    Scenario(test=system_tables)()
