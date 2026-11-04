"""Sanity check for a Delta Lake table registered in the suite's Unity Catalog.

``create_delta_table`` writes the table and registers it. ClickHouse opens
the catalog with ``use_unity_catalog_v2`` off and on. Both modes expose the
table as ``ENGINE = DeltaLake`` and return the written rows. The v2 flag
does not turn this table into an Iceberg table.
"""

from testflows.asserts import error
from testflows.core import *

from helpers.common import check_clickhouse_version
from delta_lake.tests.steps import (
    column,
    create_database,
    create_delta_table,
    expect_delta_table,
    select_rows,
)

ROWS = (
    ("Alice", 20),
    ("Bob", 30),
    ("Charlie", 40),
)

COLUMNS = (
    column("name", "STRING", "string", "string"),
    column("value", "LONG", "bigint", "long"),
)

EXPECTED = [
    "Alice\t20",
    "Bob\t30",
    "Charlie\t40",
]


@TestScenario
@Name("read rows")
def read_rows(self):
    """Write a Delta table with deltalake and read it from ClickHouse."""

    with Given("a Delta table written by deltalake and registered in Unity"):
        table = create_delta_table(columns=COLUMNS, rows=ROWS)

    with When("ClickHouse opens Unity without the Iceberg v2 catalog"):
        database = create_database(unity_v2=False)

    with Then("ClickHouse lists the table as DeltaLake"):
        expect_delta_table(database=database, table=table)

    with And("SELECT returns the written rows"):
        result = select_rows(
            database=database,
            table=table,
            columns=["name", "value"],
            order_by="name",
        )
        assert result.output.splitlines() == EXPECTED, error(result.output)

    if check_clickhouse_version(">=26.10")(self):
        with And("ClickHouse opens the same catalog with Unity v2"):
            database = create_database(unity_v2=True)

        with And("Unity v2 keeps the table as DeltaLake"):
            expect_delta_table(database=database, table=table)

        with And("Unity v2 returns the written rows"):
            result = select_rows(
                database=database,
                table=table,
                columns=["name", "value"],
                order_by="name",
            )
            assert result.output.splitlines() == EXPECTED, error(result.output)


@TestFeature
@Name("delta sanity")
def feature(self):
    """Delta Lake tables in the local Unity Catalog."""
    Scenario(test=read_rows)()
