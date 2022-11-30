from helpers.common import *


# @TestScenario
# def compatibility_check(self, node=None):
#     """Check that aggregate functions on different ClickHouse versions are compatible among themselves."""
#
#     if node is None:
#         node = self.context.node
#
#     with Given(
#         "I have self.context.cluster.clickhouse_versions that contains all specified clickhouse versions"
#     ):
#         assert len(self.context.cluster.clickhouse_versions) >= 2, error()
#
#     with And("I get two first clickhouse versions"):
#         clickhouse_version0 = self.context.cluster.clickhouse_versions[0]
#         clickhouse_version1 = self.context.cluster.clickhouse_versions[1]
#
#     with Then(f"I create table with aggregation on the clickhouse-{clickhouse_version0}"):
#         node.query("CREATE TABLE check_state Engine=MergeTree() "
#                    "ORDER BY number AS SELECT number, argMaxState('01234567890123456789012', number) "
#                    "AS s FROM numbers(1000) GROUP BY number;")
#
#     with Then(f"I check output on clickhouse-{clickhouse_version0}"):
#         expected_result = node.query("SELECT argMaxMerge(s) FROM check_state").output
#
#     try:
#         with When("I change clickhouse version"):
#             self.context.cluster.change_clickhouse_version(
#                 clickhouse_version=clickhouse_version1
#             )
#
#         with Then(f"I check output on clickhouse-{clickhouse_version1}"):
#             actual_result = node.query("SELECT argMaxMerge(s) FROM check_state").output
#             assert expected_result == actual_result, error()
#
#     finally:
#         with Finally("I revert clickhouse version back"):
#             self.context.cluster.change_clickhouse_version(
#                 clickhouse_version=clickhouse_version0
#             )
#
#             with Then(f"I check clickhouse version is {clickhouse_version0}"):
#                 r = node.query("SELECT version()")
#                 assert r.output == clickhouse_version0, error()


@TestScenario
def compatibility_aggregate_function(self, aggregate_function, engine, params, value, node=None):
    """Check that aggregate functions on different ClickHouse versions are compatible among themselves."""
    if node is None:
        node = self.context.node

    table_name = "table_" + getuid()

    with Given(
        "I have self.context.cluster.clickhouse_versions that contains all specified clickhouse versions"
    ):
        assert len(self.context.cluster.clickhouse_versions) >= 2, error()

    with And("I get two first clickhouse versions"):
        clickhouse_version0 = self.context.cluster.clickhouse_versions[0]
        clickhouse_version1 = self.context.cluster.clickhouse_versions[1]

    try:
        with Then(f"I create table with aggregation on the clickhouse-{clickhouse_version0} and insert data into it"):
            node.query(f"CREATE TABLE {table_name} "
                       f"(number Int32, s AggregateFunction({aggregate_function}, {params}))"
                       f" Engine={engine}() ORDER BY number")
            node.query(f"INSERT INTO {table_name} SELECT number, {aggregate_function}State({value}) "
                       "AS s FROM numbers(1000) GROUP BY number;")

        with Then(f"I check output on clickhouse-{clickhouse_version0}"):
            expected_result = node.query(f"SELECT {aggregate_function}Merge(s) FROM {table_name}").output

        with When("I change clickhouse version"):
            node.change_clickhouse_binary_path(
                clickhouse_number=1
            )
        pause()

        with Then(f"I check output on clickhouse-{clickhouse_version1} and on clickhouse-{clickhouse_version0} are indentical"):
            actual_result = node.query(f"SELECT {aggregate_function}Merge(s) FROM {table_name}").output
            assert expected_result == actual_result, error()

    finally:
        with Finally("I revert clickhouse version back"):
            node.change_clickhouse_binary_path(
                clickhouse_number=0
            )

            with Then(f"I check clickhouse version is {clickhouse_version0}"):
                r = node.query("SELECT version()")
                assert r.output == clickhouse_version0, error()

        with And("I delete table"):
            node.query(f"DROP TABLE {table_name} SYNC")


@TestModule
@Requirements()
@Name("compatibility")
def feature(self, node="clickhouse1"):
    """Check that aggregate functions on different ClickHouse versions are compatible among themselves."""

    aggregate_functions_params_values = [
        ("argMax", "String, UInt64", "'01234567890123456789', number"),
        ("argMax", "String, UInt64", "'01234567890123456789', number"),
        ("argMin", "String, UInt64", "'01234567890123456789', number"),
        ("max", "String", "char(number)"),
        ("min", "String", "char(number)"),
        ("any", "String", "char(number)"),
        ("singleValueOrNull", "String", "char(number)"),
        ]

    engines = ["MergeTree",
               "AggregatingMergeTree"]
    for aggregate_function_param_value in aggregate_functions_params_values:
        for engine in engines:
            with Feature(f"{aggregate_function_param_value[0]} function on {engine} engine"):
                self.context.node = self.context.cluster.node(node)
                Scenario(test=compatibility_aggregate_function)(
                    aggregate_function=aggregate_function_param_value[0], engine=engine,
                    params=aggregate_function_param_value[1], value=aggregate_function_param_value[2])