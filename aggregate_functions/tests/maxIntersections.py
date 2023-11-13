from helpers.tables import common_columns
from helpers.tables import is_numeric, unwrap
from helpers.datatypes import Float64


from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersections,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)} FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("maxIntersections")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersections("1.0")
)
def scenario(
    self,
    func="maxIntersections({params})",
    table=None,
    decimal=False,
    date=False,
    datetime=False,
    extended_precision=False,
    snapshot_id=None,
):
    """Check maxIntersections aggregate function."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id)

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1,1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number,number')} FROM numbers(0)")

    with Check("single row"):
        execute_query(f"SELECT {func.format(params='number,number+1')} FROM numbers(1)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number,even')} FROM numbers(10) GROUP BY even",
            message=f"DB::Exception:",
            exitcode=43,
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5,number-10')} FROM numbers(1, 10)"
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

    with Check("example_1"):
        execute_query(
            f"SELECT {func.format(params='y,x')} FROM values('x Float64, y Float64', (0,0.1), (1,0.34), (2,.88), (3,-1.23), (4,-3.3), (5,5.4))"
        )

    with Check("example_2"):
        execute_query(
            f"SELECT {func.format(params='x,y')} FROM values('x UInt32, y UInt32', (1,3), (1,6), (2,5), (3,7))"
        )

    with Check("datatypes"):
        with Check(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if col in common_columns()
                    and is_numeric(
                        col.datatype,
                        decimal=decimal,
                        date=date,
                        datetime=datetime,
                        extended_precision=extended_precision,
                    )
                ]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()
                note(permutation)

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name
                    if col1_type != col2_type:
                        continue
                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
