import tests.steps as select
from helpers.common import check_clickhouse_version
from selects.requirements.automatic_final_modifier import *
from tests.steps.main_steps import *


@TestScenario
def expression_in_aggregate_alias(self, node=None):
    """Alias of expression used in aggregate function."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"local_numbers_{getuid()}"

    try:
        with Given("I create local numbers table with ReplacingMergeTreeEngine"):
            node.query(
                f"CREATE TABLE {name} (number UInt64) ENGINE = ReplacingMergeTree PRIMARY KEY number"
            )

        with When("I insert some duplicate data in it"):
            for i in range(10):
                node.query(f"INSERT INTO {name} VALUES ({i});")
                node.query(f"INSERT INTO {name} VALUES ({i});")
                node.query(f"INSERT INTO {name} VALUES ({i});")

        with Then("select result check without and with --final"):
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
def aggregrate_from_subquery_alias(self, node=None):
    """Alias of aggregrate function from a subquery that contains an alias of expression used in a window function."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"local_numbers_{getuid()}"

    try:
        with Given("I create local numbers table with ReplacingMergeTree engine"):
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
def group_order_by_alias_with_override_column_name(self, node=None):
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
