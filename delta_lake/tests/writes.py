"""INSERT into a Delta table, and the statements that must stay rejected.

``deltalake`` reads the table back after each committed insert. The log
check compares the ``_delta_log/*.json`` files before and after the
statement: a rejected statement leaves them unchanged, and a committed
insert adds exactly one file and replaces none.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from helpers.common import check_clickhouse_version, getuid
from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Unity_Insert,
    RQ_SRS_050_ClickHouse_DeltaLake_Writes_AppendVisible,
    RQ_SRS_050_ClickHouse_DeltaLake_Writes_Cast,
    RQ_SRS_050_ClickHouse_DeltaLake_Writes_Insert,
    RQ_SRS_050_ClickHouse_DeltaLake_Writes_NoMutation,
    RQ_SRS_050_ClickHouse_DeltaLake_Writes_Setting,
)
from delta_lake.tests.steps import (
    column,
    create_database,
    create_delta_table,
    read_with_deltalake,
)
from delta_lake.tests.steps.access import create_engine_table
from delta_lake.tests.steps.query import (
    catalog_source,
    delta_function,
    expect_error,
    expect_log_unchanged,
    expect_one_new_commit,
    expect_query_lines,
    log_files,
    try_query,
    writes_setting,
)

COLUMNS = (
    column("name", "STRING", "string", "string"),
    column("value", "LONG", "bigint", "long"),
)

ROWS = (("Alice", 20), ("Bob", 30), ("Charlie", 40))

EXPECTED = ["Alice\t20", "Bob\t30", "Charlie\t40"]


def lines(rows):
    return [f"{name}\t{value}" for name, value in sorted(rows)]


def unregistered_table():
    return create_delta_table(
        columns=COLUMNS, rows=ROWS, register=False, create_schema=False
    )


@TestStep(Given)
def create_source_table(self, rows, node=None):
    """A MergeTree table holding ``rows``. Drop it when the scenario ends."""
    node = self.context.node if node is None else node
    name = f"source_{getuid()}"
    values = ", ".join(f"('{name_}', {value})" for name_, value in rows)
    try:
        node.query(
            f"CREATE TABLE {name} (name String, value Int64) "
            "ENGINE = MergeTree ORDER BY name"
        )
        node.query(f"INSERT INTO {name} VALUES {values}")
        yield name
    finally:
        with Finally(f"drop table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Name("insert needs the setting")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Writes_Setting("1.0"))
def insert_needs_setting(self):
    """INSERT fails while writes are off, and the log is unchanged."""
    setting = writes_setting(self)

    with Given("a Delta table attached with ENGINE = DeltaLake"):
        table = unregistered_table()
        name = create_engine_table(url=table.http_url)

    with And("I record the commit files"):
        before = log_files(table=table)

    with When(f"I insert with {setting} = 0"):
        result = try_query(
            sql=f"SET {setting} = 0; INSERT INTO {name} VALUES ('Dave', 50)"
        )

    with Then("the insert fails and names the setting"):
        expect_error(result=result, message=setting)

    with And("no commit was added"):
        expect_log_unchanged(table=table, before=before)

    with And("the rows are unchanged"):
        expect_query_lines(
            sql=f"SELECT name, value FROM {name} ORDER BY name", expected=EXPECTED
        )


@TestScenario
@Name("insert select")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Writes_Insert("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Writes_AppendVisible("1.0"),
)
def insert_select(self):
    """INSERT SELECT from MergeTree appends one commit that deltalake can read."""
    setting = writes_setting(self)
    new_row = ("Dave", 50)

    with Given("a Delta table attached with ENGINE = DeltaLake"):
        table = unregistered_table()
        name = create_engine_table(url=table.http_url)

    with And("a MergeTree table holding the new row"):
        source = create_source_table(rows=[new_row])

    with And("I record the commit files"):
        before = log_files(table=table)

    with When(f"I insert from MergeTree with {setting} = 1"):
        self.context.node.query(
            f"SET {setting} = 1; INSERT INTO {name} SELECT name, value FROM {source}"
        )

    with Then("SELECT returns the old rows and the new row"):
        expect_query_lines(
            sql=f"SELECT name, value FROM {name} ORDER BY name",
            expected=lines(ROWS + (new_row,)),
        )

    with And("deltalake reads the same rows from the same path"):
        found = read_with_deltalake(table=table, columns=["name", "value"])
        assert found == sorted(ROWS + (new_row,)), error(found)

    with And("one commit file was added and none was replaced"):
        expect_one_new_commit(table=table, before=before)


@TestScenario
@Name("insert through unity")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Unity_Insert("1.0"))
def insert_through_unity(self):
    """INSERT into unity.`schema.table` commits to the table location."""
    setting = writes_setting(self)

    with Given("a Delta table registered in Unity"):
        table = create_delta_table(columns=COLUMNS, rows=ROWS)

    modes = [(False, ("Dave", 50))]
    if check_clickhouse_version(">=26.10")(self):
        modes.append((True, ("Eve", 60)))

    expected = list(ROWS)
    for unity_v2, new_row in modes:
        mode = "Unity v2" if unity_v2 else "Unity"
        with When(f"{mode} is opened"):
            database = create_database(unity_v2=unity_v2)
            source = catalog_source(database, table)

        with And("I record the commit files"):
            before = log_files(table=table)

        with And(f"I insert {new_row[0]} through {mode}"):
            self.context.node.query(
                f"SET {setting} = 1; "
                f"INSERT INTO {source} VALUES ('{new_row[0]}', {new_row[1]})"
            )
            expected.append(new_row)

        with Then("the catalog SELECT returns the new row"):
            expect_query_lines(
                sql=f"SELECT name, value FROM {source} ORDER BY name",
                expected=lines(expected),
            )

        with And("deltalake reads the new row"):
            found = read_with_deltalake(table=table, columns=["name", "value"])
            assert found == sorted(expected), error(found)

        with And("one commit file was added"):
            expect_one_new_commit(table=table, before=before)


@TestScenario
@Name("mutations are rejected")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Writes_NoMutation("1.0"))
def mutations_rejected(self):
    """DELETE, UPDATE, and ALTER mutations fail and leave the log alone."""
    setting = writes_setting(self)
    statements = (
        "DELETE FROM {name} WHERE name = 'Alice'",
        "UPDATE {name} SET value = 0 WHERE name = 'Alice'",
        "ALTER TABLE {name} DELETE WHERE name = 'Alice'",
        "ALTER TABLE {name} UPDATE value = 0 WHERE name = 'Alice'",
    )

    with Given("a Delta table attached with ENGINE = DeltaLake"):
        table = unregistered_table()
        name = create_engine_table(url=table.http_url)

    with And("I record the commit files"):
        before = log_files(table=table)

    for statement in statements:
        sql = statement.format(name=name)
        with When(f"I run {sql} with {setting} = 1"):
            result = try_query(sql=f"SET {setting} = 1; {sql}")

        with Then("the statement fails"):
            expect_error(result=result)

        with And("no commit was added"):
            expect_log_unchanged(table=table, before=before)

    with And("the rows are unchanged"):
        expect_query_lines(
            sql=f"SELECT name, value FROM {name} ORDER BY name", expected=EXPECTED
        )


@TestScenario
@Name("accurate write cast")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Writes_Cast("1.0"))
def accurate_write_cast(self):
    """300 into a byte column fails with the accurate cast and commits without it.

    The insert goes through ``deltaLake()``, which casts to the Delta type.
    An engine table converts the value to its own column type first, the
    same as any other ClickHouse table, so the setting never sees 300 there.
    """
    setting = writes_setting(self)
    data = pa.table(
        {"id": pa.array([1], pa.int64()), "b": pa.array([1], pa.int8())}
    )

    with Given("a Delta table with a byte column"):
        table = create_delta_table(
            columns=(), data=data, register=False, create_schema=False
        )
        function = delta_function(self, table.http_url)

    with And("I record the commit files"):
        before = log_files(table=table)

    with When("I insert 300 with delta_lake_accurate_write_cast = 1"):
        result = try_query(
            sql=f"SET {setting} = 1; SET delta_lake_accurate_write_cast = 1; "
            f"INSERT INTO TABLE FUNCTION {function} "
            "SELECT toInt64(2) AS id, toInt16(300) AS b"
        )

    with Then("the insert fails"):
        expect_error(result=result)

    with And("no commit was added"):
        expect_log_unchanged(table=table, before=before)

    with When("I insert 300 with delta_lake_accurate_write_cast = 0"):
        self.context.node.query(
            f"SET {setting} = 1; SET delta_lake_accurate_write_cast = 0; "
            f"INSERT INTO TABLE FUNCTION {function} "
            "SELECT toInt64(2) AS id, toInt16(300) AS b"
        )

    with Then("the insert commits"):
        expect_one_new_commit(table=table, before=before)
        expect_query_lines(
            sql=f"SELECT count() FROM {function} WHERE id = 2", expected=["1"]
        )


@TestFeature
@Name("delta writes")
def feature(self):
    """Delta Lake INSERT and the rejected mutations."""
    Scenario(test=insert_needs_setting)()
    Scenario(test=insert_select)()
    Scenario(test=insert_through_unity)()
    Scenario(test=mutations_rejected)()
    Scenario(test=accurate_write_cast)()
