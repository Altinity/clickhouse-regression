from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FirstValue,
)


@TestFeature
@Name("first_value")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FirstValue("1.0"))
def feature(self, func="first_value({params})", table=None):
    """Check first_value aggregate function."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

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

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(Int8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(Int8)', NULL)"
        )

    with Check("string that ends with \\0"):
        execute_query(
            f"SELECT {func.format(params='x')} FROM values('x String', 'hello\0\0')"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}  FROM values('x Float64', ({v}))"
            )

    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")
