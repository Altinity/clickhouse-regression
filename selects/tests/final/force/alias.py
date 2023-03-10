import tests.steps as select
from helpers.common import check_clickhouse_version
from selects.requirements.automatic_final_modifier import *
from tests.steps.main_steps import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_As("1.0"))
def simple_select_as(self):
    """Check `SELECT some_col as new_some_col`."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between `SELECT column as new_column` query with `FINAL` clause "
                "and `SELECT column as new_column` query with --final setting enabled."
            ):
                select.as_result_check(table=table)

            with And(
                "Compare results between `SELECT column as new_column` query with --final "
                "and `SELECT column as new_column` query without `FINAL` and without --final."
            ):
                select.as_negative_result_check(table=table)


@TestScenario
def simple_select_count_with_alias(self):
    """Check `SELECT count()` clause with expression column as alias column."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and some not supported views",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between count() query with expression column as alias with `FINAL`  clause "
                "and count() query with expression column as alias column with --final setting enabled."
            ):
                select.count_result_check_with_alias(table=table)


@TestScenario
def simple_select_distinct_with_alias(self):
    """Check SELECT query with `DISTINCT` clause with expression column as alias column."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between distinct query with expression column as alias column with `FINAL`  clause "
                "and distinct query with expression column as alias column with --final setting enabled."
            ):
                select.distinct_result_check_with_alias(table=table)


@TestScenario
def simple_select_limit_by_with_alias(self):
    """Check SELECT query with `LIMIT BY` clause with expression column as alias."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between `SELECT LIMIT BY` query with expression column as alias with `FINAL`  clause "
                "and `SELECT LIMIT BY` query with expression column as alias with --final setting enabled."
            ):
                select.limit_by_result_check_with_alias(table=table)


@TestScenario
def simple_select_limit_with_alias(self):
    """Check SELECT query with `LIMIT` clause with expression column as alias."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.endswith("nview_final")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between `SELECT LIMIT` query with expression column as alias with `FINAL` clause "
                "and `SELECT LIMIT` query with expression column as alias with --final setting enabled."
            ):
                select.limit_result_check_with_alias(table=table)


@TestScenario
def expression_alias_in_aggregate_function(self, node=None):
    """Alias of expression used in aggregate function."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"local_numbers_{getuid()}"

    try:
        with Given("I create table with ReplacingMergeTreeEngine"):
            node.query(
                f"CREATE TABLE {name} (number UInt64) ENGINE = ReplacingMergeTree PRIMARY KEY number"
            )

        with When("I insert some duplicate data in it"):
            for i in range(10):
                node.query(f"INSERT INTO {name} VALUES ({i});")
                node.query(f"INSERT INTO {name} VALUES ({i});")
                node.query(f"INSERT INTO {name} VALUES ({i});")

        with Then("I select result check without and with --final"):
            assert (
                node.query(
                    f"SELECT (number = 1) AND (number = 2) AS value, sum(value) OVER () FROM {name} FINAL "
                    "WHERE 1;"
                ).output.strip()
                == node.query(
                    f"SELECT (number = 1) AND (number = 2) AS value, sum(value) OVER () FROM {name} WHERE 1;",
                    settings=[("final", 1)],
                ).output.strip()
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
def aggregrate_alias_from_subquery(self, node=None):
    """Alias of aggregrate function from a subquery that contains an alias of expression used in a window function."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"local_numbers_{getuid()}"

    try:
        with Given("I create table with ReplacingMergeTree engine"):
            node.query(
                f"CREATE TABLE {name} (number UInt64) ENGINE = ReplacingMergeTree ORDER BY number"
            )

        with When("I insert some duplicate data in it"):
            for i in range(20):
                node.query(f"INSERT INTO {name} VALUES ({i});")
                node.query(f"INSERT INTO {name} VALUES ({i});")
                node.query(f"INSERT INTO {name} VALUES ({i});")

        with Then("select result check without and with --final"):
            assert (
                node.query(
                    "SELECT time, round(exp_smooth,10), bar(exp_smooth, -9223372036854775807, 1048575, 50) AS bar FROM "
                    "(SELECT 2 OR (number = 0) OR (number >= 1) AS value, number AS time, "
                    "exponentialTimeDecayedSum(2147483646)(value, time) OVER (RANGE BETWEEN CURRENT ROW AND CURRENT ROW) "
                    f"AS exp_smooth FROM {name} FINAL WHERE 10) WHERE 25"
                ).output.strip()
                == node.query(
                    "SELECT time, round(exp_smooth,10), bar(exp_smooth, -9223372036854775807, 1048575, 50) AS bar FROM "
                    "(SELECT 2 OR (number = 0) OR (number >= 1) AS value, number AS time, "
                    "exponentialTimeDecayedSum(2147483646)(value, time) OVER (RANGE BETWEEN CURRENT ROW AND CURRENT ROW) "
                    f"AS exp_smooth FROM {name} WHERE 10)  WHERE 25",
                    settings=[("final", 1)],
                ).output.strip()
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
def group_order_by_multiple_alias_with_override_column(self, node=None):
    """Multiple aliases of expressions used in GROUP BY and ORDER BY where one alias overrides a name of a table column."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"table_alias_{getuid()}"

    try:
        with Given("I create table form the issue"):
            node.query(
                f"CREATE TABLE {name} (id String, device UUID) ENGINE = ReplacingMergeTree() ORDER BY tuple();"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES ('notEmpty', '417ddc5d-e556-4d27-95dd-a34d84e46a50');"
            )
            node.query(
                f"INSERT INTO {name} VALUES ('', '417ddc5d-e556-4d27-95dd-a34d84e46a50');"
            )
            node.query(
                f"INSERT INTO {name} VALUES ('', '00000000-0000-0000-0000-000000000000');"
            )

        with Then("select result check without and with --final"):
            assert (
                node.query(
                    "SELECT if(empty(id), toString(device), id) AS device, multiIf( notEmpty(id),'a', "
                    f"device == '00000000-0000-0000-0000-000000000000', 'b', 'c' ) AS device_id_type, count() FROM {name} "
                    "FINAL GROUP BY device, device_id_type ORDER BY device;"
                ).output.strip()
                == node.query(
                    "SELECT if(empty(id), toString(device), id) AS device, multiIf( notEmpty(id),'a', "
                    f"device == '00000000-0000-0000-0000-000000000000', 'b', 'c' ) AS device_id_type, count() FROM {name} "
                    "GROUP BY device, device_id_type ORDER BY device;",
                    settings=[("final", 1)],
                ).output.strip()
            )
    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
def group_order_by_multiple_alias_with_aggregate_new_alias(self, node=None):
    """Multiple aliases of expressions used to reference aggregate function results as well as calculating
    new alias using an expression that contains other aliases with aliases used in GROUP BY and ORDER BY."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"table_alias_{getuid()}"

    try:
        with Given("I create table form the issue"):
            node.query(
                f"CREATE TABLE {name}(timestamp DateTime,col1 Float64,col2 Float64,col3 Float64)"
                " ENGINE = ReplacingMergeTree() ORDER BY tuple();"
            )

        with When("I insert data in this table"):
            node.query(f"INSERT INTO {name} VALUES ('2023-02-20 00:00:00', 1, 2, 3);")

        with Then("select result check without and with --final"):
            assert (
                node.query(
                    "SELECT argMax(col1, timestamp) AS col1, argMax(col2, timestamp) AS col2, col1 / col2 AS final_col "
                    f"FROM {name} FINAL GROUP BY col3 ORDER BY final_col DESC;"
                ).output.strip()
                == node.query(
                    "SELECT argMax(col1, timestamp) AS col1, argMax(col2, timestamp) AS col2, col1 / col2 AS final_col "
                    f"FROM {name} GROUP BY col3 ORDER BY final_col DESC;",
                    settings=[("final", 1)],
                ).output.strip()
            )

            assert (
                node.query(
                    "SELECT argMax(col1, timestamp) AS col1, col1 / 10 AS final_col, final_col + 1 AS final_col2"
                    f" FROM {name} FINAL GROUP BY col3;"
                ).output.strip()
                == node.query(
                    "SELECT argMax(col1, timestamp) AS col1, col1 / 10 AS final_col, final_col + 1 AS final_col2"
                    f" FROM {name} GROUP BY col3;",
                    settings=[("final", 1)],
                ).output.strip()
            )
    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
def select_nested_subquery_with_alias(self, node=None):
    """Check SELECT query with nested 3 lvl subquery with expression column as alias."""
    if node is None:
        node = self.context.node

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                and not table.name.startswith("expr_subquery")
                and not table.name.endswith("wview_final")
                and not table.name.endswith("_nview")
                and not table.name.endswith("_lview")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT count()*100 as count_alias FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM {table.name}"
                    f"{' FINAL' if table.final_modifier_available else ''})))"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT count()*100 as count_alias FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM {table.name})))",
                    settings=[("final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestOutline
def select_prewhere_where_subquery_with_alias(self, node=None, clause=None):
    """Check SELECT query with `PREWHERE`/`WHERE' with subquery with expression column as alias in select and in subquery."""
    if node is None:
        node = self.context.node

    table_pairs = []

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core")
                and not table.name.startswith("Merge")
                and not table.name.startswith("ReplicatedMerge")
                and not table.name.startswith("Log")
                and not table.name.startswith("StripeLog")
                and not table.name.startswith("TinyLog")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    with And("I create list of table pairs for this test"):
        for table1 in tables:
            for table2 in self.context.tables:
                if table2.name.startswith("expr_subquery"):
                    table_pairs.append((table1, table2))

    for table1, table2 in table_pairs:
        with When(f"I have {table1.name} and subquery table {table2.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT id*10 as new_id FROM {table1.name} FINAL {clause}"
                    f" x = (SELECT x/2 as x2 FROM {table2.name} FINAL) "
                    f"ORDER BY id FORMAT JSONEachRow;"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT id*10 as new_id FROM {table1.name} {clause} x = (SELECT x/2 as x2 FROM {table2.name}) "
                    f"ORDER BY id FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestScenario
def select_prewhere_subquery_with_alias(self):
    """Check query with `PREWHERE` with subquery with expression column as alias."""
    select_prewhere_where_subquery_with_alias(clause="PREWHERE")


@TestScenario
def select_where_subquery_with_alias(self):
    """Check query with`WHERE` with subquery with expression column as alias in select and in subquery."""
    select_prewhere_where_subquery_with_alias(clause="WHERE")


@TestOutline
def select_prewhere_where_in_subquery_with_alias(self, node=None, clause=None):
    """Check SELECT query with `PREWHERE`/`WHERE' with `IN` statement subquery
    with expression column as alias in select and in subquery."""
    if node is None:
        node = self.context.node

    table_pairs = []

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "tables",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core")
                and not table.name.startswith("Merge")
                and not table.name.startswith("ReplicatedMerge")
                and not table.name.startswith("Log")
                and not table.name.startswith("StripeLog")
                and not table.name.startswith("TinyLog")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    with And("I create list of table pairs for this test"):
        for table1 in tables:
            for table2 in self.context.tables:
                if table2.name.startswith("expr_subquery"):
                    table_pairs.append((table1, table2))

    for table1, table2 in table_pairs:
        with When(f"I have {table1.name} and subquery table {table2.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT id*10 as new_id FROM {table1.name} FINAL {clause}"
                    f" x IN (SELECT x/2 as x FROM {table2.name} FINAL) "
                    f"ORDER BY id FORMAT JSONEachRow;"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT id*10 as new_id FROM {table1.name} {clause} x IN (SELECT x/2 as x2 FROM {table2.name}) "
                    f"ORDER BY id FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestScenario
def select_prewhere_in_subquery_with_alias(self):
    """Check query with `PREWHERE` with `IN` statement subquery
    with expression column as alias in select and in subquery."""
    select_prewhere_where_in_subquery_with_alias(clause="PREWHERE")


@TestScenario
def select_where_in_subquery_with_alias(self):
    """Check query with `WHERE` with `IN` statement subquery
    with expression column as alias in select and in subquery."""
    select_prewhere_where_in_subquery_with_alias(clause="WHERE")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableSchema_Alias("1.0"))
@Name("alias")
def feature(self):
    """Parallel queries tests for force select final."""
    if check_clickhouse_version("<23.2.1.2440")(self):
        skip(
            reason="force_select_final alias is only supported on ClickHouse version >= 23.2.1.2440"
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
