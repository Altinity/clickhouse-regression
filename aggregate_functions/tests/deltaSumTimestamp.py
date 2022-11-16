from helpers.tables import is_numeric
from helpers.tables import common_columns

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSumTimestamp,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)} FROM {table.name} FORMAT JSONEachRow"
    )


@TestFeature
@Name("deltaSumTimestamp")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSumTimestamp("1.0")
)
def feature(self, func="deltaSumTimestamp({params})", table=None, decimal=True):
    """Check deltaSumTimestamp aggregate function."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1,1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number,number+1')} FROM numbers(0)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number,number+1')} FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5,number+10')} FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,y')}  FROM values('x Nullable(Int8), y Nullable(Int8)', (0, 1), (1, NULL), (NULL,NULL), (NULL,3), (4,4), (5, 1))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x,y')}  FROM values('x Nullable(Int8), y Nullable(Int8)', (NULL, NULL))"
        )

    with Check("inf, -inf, nan"):
        for permutation in permutations_with_replacement(["inf", "-inf", "nan"], 2):
            x, y = permutation
            with Check(f"{x},{y}"):
                execute_query(
                    f"SELECT {func.format(params='x,y')}  FROM values('x Float64, y Float64', (0, 1), (1, 2.3), ({x},{y}), (6.7,3), (4,4), (5, 1))"
                )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number, number+1')}) FROM numbers(1, 10)"
        )

    with Feature("datatypes"):
        with Feature(
            "permutations",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if col in common_columns
                    and is_numeric(
                        col.split(" ", 1)[-1], decimal=False, date=True, datetime=True
                    )
                ]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.split(" ", 1)
                    col2_name, col2_type = col2.split(" ", 1)

                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
