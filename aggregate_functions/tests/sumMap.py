from helpers.tables import is_numeric, is_string

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumMap,
)


@TestFeature
@Name("sumMap")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumMap("1.0"))
def feature(self, func="sumMap({params})", table=None):
    """Check sumMap aggregate function."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='map(1,1)')}")

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='map(number,number)')} FROM numbers(0)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='map(even,number)')} FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='map(number-5,number-10)')} FROM numbers(1, 10)"
        )

    with Check("one to many"):
        execute_query(
            f"SELECT {func.format(params='map(number%2,number)')} FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='map(x,y)')}  FROM values('x Int8, y Nullable(Int8)', (0, 1), (1, NULL), (2,NULL), (2,1), (3,4), (2, 1))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='map(x,y)')}  FROM values('x Int8, y Nullable(Int8)', (1, NULL))"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            params = "map('a',x)"
            execute_query(
                f"SELECT {func.format(params=params)}  FROM values('x Float64', (0), (2.3), ({v}), (6.7), (4), (5))"
            )

    with Check(f"inf, -inf, nan"):
        params = "map('a',x)"
        execute_query(
            f"SELECT {func.format(params=params)}  FROM values('x Float64', (nan), (2.3), (inf), (6.7), (-inf), (5))"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='map(number, number+1)')}) FROM numbers(1, 10)"
        )

    with Check("NULL in strings"):
        execute_query(
            f"SELECT {func.format(params='a, b')} FROM values('a Array(String), b Array(Int64)', (['1\\0', '2\\0\\0'], [2, 2]), (['\\03\\0\\0\\0', '3'], [1, 1]))"
        )

    with Check("datatypes"):
        xfail("not implemented")
