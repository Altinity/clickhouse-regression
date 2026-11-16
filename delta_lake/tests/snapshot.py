"""Read the latest snapshot after another ``deltalake`` commit.

Each scenario writes a table, registers it in Unity, and opens the Unity
databases before the next commit. ``deltaLake()`` and every catalog must
then return the rows of the new commit. A catalog that keeps the first
snapshot fails here even when the sanity read passes.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from helpers.common import check_clickhouse_version
from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Read_Projection,
    RQ_SRS_050_ClickHouse_DeltaLake_Read_Snapshot,
)
from delta_lake.tests.steps import (
    column,
    commit_delta_table,
    create_database,
    create_delta_table,
)
from delta_lake.tests.steps.query import (
    catalog_source,
    delta_function,
    expect_query_lines,
    query_lines,
)

COLUMNS = (
    column("name", "STRING", "string", "string"),
    column("value", "LONG", "bigint", "long"),
)

ROWS = (("Alice", 20), ("Bob", 30), ("Charlie", 40))

SCHEMA = pa.schema([pa.field("name", pa.string()), pa.field("value", pa.int64())])


def frame(rows):
    return pa.Table.from_pylist(
        [{"name": name, "value": value} for name, value in rows], schema=SCHEMA
    )


def lines(rows):
    return [f"{name}\t{value}" for name, value in sorted(rows)]


def readers(self, table):
    """``deltaLake()`` plus Unity, and Unity v2 on 26.10 and newer."""
    sources = [delta_function(self, table.http_url)]
    with By("opening Unity without use_unity_catalog_v2"):
        sources.append(catalog_source(create_database(unity_v2=False), table))
    if check_clickhouse_version(">=26.10")(self):
        with By("opening Unity v2"):
            sources.append(catalog_source(create_database(unity_v2=True), table))
    return sources


def expect_all(sources, selected, expected, order_by="name"):
    for source in sources:
        with Then(f"{source} returns the snapshot rows"):
            expect_query_lines(
                sql=f"SELECT {selected} FROM {source} ORDER BY {order_by}",
                expected=expected,
            )


@TestScenario
@Name("overwrite")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Snapshot("1.0"))
def overwrite(self):
    """After mode overwrite, only the new rows come back."""
    new_rows = (("Dave", 50), ("Eve", 60))

    with Given("a registered Delta table with three rows"):
        table = create_delta_table(columns=COLUMNS, rows=ROWS)

    with And("every reader sees the first commit"):
        sources = readers(self, table)
        expect_all(sources, "name, value", lines(ROWS))

    with When("deltalake overwrites the table with two other rows"):
        commit_delta_table(table=table, data=frame(new_rows), mode="overwrite")

    expect_all(sources, "name, value", lines(new_rows))


@TestScenario
@Name("append")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Snapshot("1.0"))
def append(self):
    """After mode append, the old rows and the new rows come back."""
    new_rows = (("Dave", 50),)

    with Given("a registered Delta table with three rows"):
        table = create_delta_table(columns=COLUMNS, rows=ROWS)

    with And("every reader sees the first commit"):
        sources = readers(self, table)
        expect_all(sources, "name, value", lines(ROWS))

    with When("deltalake appends one row"):
        commit_delta_table(table=table, data=frame(new_rows), mode="append")

    expect_all(sources, "name, value", lines(ROWS + new_rows))


@TestScenario
@Name("empty table")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Snapshot("1.0"))
def empty_table(self):
    """A commit with a schema and no rows reads as zero rows with columns."""

    with Given("a registered Delta table written with zero rows"):
        table = create_delta_table(columns=COLUMNS, data=frame(()))

    sources = readers(self, table)

    for source in sources:
        with Then(f"count() of {source} is 0"):
            expect_query_lines(sql=f"SELECT count() FROM {source}", expected=["0"])

        with And(f"DESCRIBE {source} still lists the columns"):
            described = query_lines(sql=f"DESCRIBE TABLE {source}")
            names = [line.split("\t")[0] for line in described]
            assert names[:2] == ["name", "value"], error(described)


@TestScenario
@Name("projection")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Projection("1.0"))
def projection(self):
    """SELECT of one column returns that column with the values of SELECT *."""

    with Given("a registered Delta table with three rows"):
        table = create_delta_table(columns=COLUMNS, rows=ROWS)

    for source in readers(self, table):
        with When(f"I read every column of {source}"):
            everything = query_lines(sql=f"SELECT * FROM {source} ORDER BY name")

        with Then("SELECT value returns only the value column"):
            expect_query_lines(
                sql=f"SELECT value FROM {source} ORDER BY name",
                expected=[line.split("\t")[1] for line in everything],
            )


@TestFeature
@Name("delta snapshot")
def feature(self):
    """The latest Delta snapshot through deltaLake() and Unity."""
    Scenario(test=overwrite)()
    Scenario(test=append)()
    Scenario(test=empty_table)()
    Scenario(test=projection)()
