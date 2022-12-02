from helpers.common import *


@TestScenario
def compatibility_inf_nan(self, function, node=None):
    """Check that aggregate functions on different ClickHouse versions are compatible among themselves by
    ."""#todo

    if node is None:
        node = self.context.node

    with Given(
        "I have self.context.cluster.clickhouse_versions that contains all specified clickhouse versions"
    ):
        assert len(self.context.cluster.clickhouse_versions) >= 2, error()

    clickhouse_version0 = self.context.cluster.clickhouse_versions[0]
    clickhouse_version1 = self.context.cluster.clickhouse_versions[1]

    try:

        with Then(f"I check output on clickhouse-{clickhouse_version0}"):
            expected_result = node.query(f"SELECT hex({function}(x,y))  FROM "
                                         f"values('x Float64, y Float64', (0, 1), (1, 2.3), "
                                         f"(inf,nan), (6.7,3), (4,4), (5, 1)) FORMAT JSONEachRow").output

        with When(f"I change clickhouse version on affected version {clickhouse_version1}"):
            node.change_clickhouse_binary_path(
                clickhouse_number=1
            )

        with Then(f"I check output on clickhouse-{clickhouse_version1} and on clickhouse-{clickhouse_version0} are identical"):
            actual_result = node.query(f"SELECT hex({function}(x,y))  FROM "
                                         f"values('x Float64, y Float64', (0, 1), (1, 2.3), "
                                         f"(inf,nan), (6.7,3), (4,4), (5, 1)) FORMAT JSONEachRow").output
            assert expected_result == actual_result, error()

    finally:
        with Finally("I revert clickhouse version back"):
            node.change_clickhouse_binary_path(
                clickhouse_number=0
            )

            with Then(f"I check clickhouse version is {clickhouse_version0}"):
                r = node.query("SELECT version()")
                assert r.output == clickhouse_version0, error()


@TestModule
@Requirements()
@Name("compatibility inf nan")
def feature(self, node="clickhouse1"):
    """Check that aggregate functions on different ClickHouse versions are compatible among themselves
    with inf and nan in function parameters."""

    functions = ["corrStableState",
                 "covarPopStableState",
                 "covarSampStableState",
                 ]
    self.context.node = self.context.cluster.node(node)

    for function in functions:
        with Feature(f"{function} function"):
            Scenario(test=compatibility_inf_nan)(function=function)