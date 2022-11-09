from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max,
)


@TestFeature
@Name("max")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max("1.0"))
def feature(self, func="max({params})", table=None):
    """Check max aggregate function."""
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

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")