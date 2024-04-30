import itertools


from helpers.tables import common_columns
from helpers.tables import is_numeric, unwrap
from helpers.datatypes import Float64


from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("covarPop")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop("1.0"))
def scenario(
    self,
    func="covarPop({params})",
    table=None,
    decimal=False,
    date=False,
    datetime=False,
    extended_precision=False,
    snapshot_id=None,
):
    """Check covarPop aggregate function."""
    if check_clickhouse_version(">=24.3")(self) and check_current_cpu("aarch64")(self):
        clickhouse_version = ">=24.3"
    else:
        clickhouse_version = ">=23.2"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(
            f"SELECT {func.format(params='1,1')}, any(toTypeName(1)),  any(toTypeName(1))"
        )

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='number,number')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(0)"
        )

    with Check("single row"):
        execute_query(
            f"SELECT {func.format(params='number,number+1')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number,even')}, any(toTypeName(number)), any(toTypeName(even)) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5,number+10')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Nullable(Int8), y Nullable(Int8)', (0, 1), (1, NULL), (NULL,NULL), (NULL,3), (4,4), (5, 1))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Nullable(Int8), y Nullable(Int8)', (NULL, NULL))"
        )

    with Check("inf, -inf, nan"):
        for permutation in permutations_with_replacement(["inf", "-inf", "nan"], 2):
            x, y = permutation
            with Check(f"{x},{y}"):
                execute_query(
                    f"SELECT {func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y))  FROM values('x Float64, y Float64', (0, 1), (1, 2.3), ({x},{y}), (6.7,3), (4,4), (5, 1))"
                )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number, number+1')}), any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("example"):
        execute_query(
            f"SELECT {func.format(params='y,x')}, any(toTypeName(y)), any(toTypeName(x)) FROM values('x Int8, y Float64', (0,0.1), (1,0.34), (2,.88), (3,-1.23), (4,-3.3), (5,5.4))"
        )

    with Check("datatypes"):
        with Pool(3) as executor:
            for column in table.columns:
                col_name, col_type = column.name, column.datatype.name

                if not is_numeric(
                    column.datatype,
                    decimal=decimal,
                    date=date,
                    datetime=datetime,
                    extended_precision=extended_precision,
                ):
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

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name
                    # we already cover Float64 data type above so skip it here
                    if isinstance(unwrap(col1.datatype), Float64) or isinstance(
                        unwrap(col2.datatype), Float64
                    ):
                        continue
                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
