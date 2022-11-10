from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Sum,
)


@TestFeature
@Name("sum")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Sum("1.0"))
def feature(self, func="sum({params})", table=None):
    """Check sum aggregate function."""
    self.context.snapshot_id = func.split("(",1)[0]

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(0)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')} FROM numbers(10) GROUP BY even"
        )

    for column in table.columns:
        column_name, column_type = column.split(" ", 1)

        if not is_numeric(column_type):
            continue

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")
