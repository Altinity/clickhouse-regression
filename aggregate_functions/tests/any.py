from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Any,
)


@TestFeature
@Name("any")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Any("1.0"))
def feature(self, func="any({params})", table=None):
    """Check any aggregate function."""
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

    with Check("some negative values"):
        execute_query(f"SELECT {func.format(params='number-5')} FROM numbers(1, 10)")

    with Check("first non-NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(Int8)', NULL, NULL, NULL, 3, 4, 5)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, NULL)')} FROM numbers(10)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}) FROM numbers(1, 10)"
        )

    with Check("with another aggregate function"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))"
        )

    with Check("with another aggregate function and group by"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'hello'), (NULL, NULL), (5, 'you')) GROUP BY y"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}  FROM values('x Float64', ({v}))"
            )

    for column in table.columns:
        column_name, column_type = column.split(" ", 1)

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")
