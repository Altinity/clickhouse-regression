from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Avg,
)


@TestFeature
@Name("avg")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Avg("1.0"))
def feature(self, func="avg({params})", table=None, exclude_types=None):
    """Check avg aggregate function."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    if exclude_types is None:
        exclude_types = []

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(0)")

    with Check("single row"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(1)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')} FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(f"SELECT {func.format(params='number-5')} FROM numbers(1, 10)")

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(Int8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(Int8)', NULL)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}) FROM numbers(1, 10)"
        )

    with Check("doc example"):
        execute_query(
            f"SELECT {func.format(params='x')} FROM values('x Int8', 0, 1, 2, 3, 4, 5)"
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
        column_name, column_type = column.split(" ", 1)

        if not is_numeric(column_type):
            continue

        if column_type in exclude_types:
            continue

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")
