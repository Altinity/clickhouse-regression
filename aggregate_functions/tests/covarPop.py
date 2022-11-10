import itertools


from helpers.tables import common_columns
from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)} FROM {table.name} FORMAT JSONEachRow"
    )


@TestFeature
@Name("covarPop")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop("1.0"))
def feature(self, func="covarPop({params})", table=None, exclude_types=None):
    """Check covarPop aggregate function."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    if exclude_types is None:
        exclude_types = []

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1,1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number,number')} FROM numbers(0)")

    with Check("single row"):
        execute_query(f"SELECT {func.format(params='number,number+1')} FROM numbers(1)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number,even')} FROM numbers(10) GROUP BY even"
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

    with Check("example"):
        execute_query(
            f"SELECT {func.format(params='y,x')} FROM values('x Int8, y Float64', (0,0.1), (1,0.34), (2,.88), (3,-1.23), (4,-3.3), (5,5.4))"
        )

    with Feature("datatypes"):
        with Pool(3) as executor:
            for column in table.columns:
                col_name, col_type = column.split(" ", 1)

                if not is_numeric(col_type, decimal=False):
                    continue

                Check(
                    f"Float64,{col_type}",
                    test=datatype,
                    parallel=True,
                    executor=executor,
                )(func=func, table=table, col1_name="float64", col2_name=col_name)
                Check(
                    f"{col_type},Float64",
                    test=datatype,
                    parallel=True,
                    executor=executor,
                )(func=func, table=table, col1_name=col_name, col2_name="float64")

            join()

        with Feature(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if col in common_columns
                    and is_numeric(col.split(" ", 1)[-1], decimal=False)
                ]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.split(" ", 1)
                    col2_name, col2_type = col2.split(" ", 1)
                    # we already cover Float64 data type above so skip it here
                    if col1_type == "Float64" or col2_type == "Float64":
                        continue
                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
