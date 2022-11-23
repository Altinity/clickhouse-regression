from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Sum,
)


@TestFeature
@Name("sum")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Sum("1.0"))
def feature(self, func="sum({params})", table=None, decimal=True):
    """Check sum aggregate function."""
    self.context.snapshot_id = name.basename(current().name)

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

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}  FROM values('x Float64', (0), (2.3), ({v}), (6.7), (4), (5))"
            )

    with Check(f"inf, -inf, nan"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Float64', (nan), (2.3), (inf), (6.7), (-inf), (5))"
        )

    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        if not is_numeric(column.datatype, decimal=decimal):
            continue

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")
