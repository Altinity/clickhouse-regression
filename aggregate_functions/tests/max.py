from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max,
)


@TestScenario
def checks(self, func="max({params})"):
    """Check that max() calculates the maximum across a group of values."""
    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(0)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')} FROM numbers(10) GROUP BY even"
        )

@TestScenario
def datatypes(self, func="max({params})", table=None):
    """Check that max() calculates the minimum across different data types."""
    if table is None:
        table = self.context.table

    for column in table.columns:
        column_name, column_type = column.split(" ", 1)

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")


@TestFeature
@Name("max")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max("1.0"))
def feature(self, node="clickhouse1"):
    """Check max aggregate function."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
