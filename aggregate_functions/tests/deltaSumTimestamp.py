from helpers.tables import is_numeric, is_nullable
from helpers.tables import common_columns

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSumTimestamp,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("deltaSumTimestamp")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSumTimestamp("1.0")
)
def scenario(
    self,
    func="deltaSumTimestamp({params})",
    table=None,
    decimal=True,
    both_arguments_with_the_same_datatype=False,
    snapshot_id=None,
):
    """Check deltaSumTimestamp aggregate function."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id, clickhouse_version=">=23.12"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    exitcode, message = None, None
    if check_clickhouse_version(">=24.11")(self):
        exitcode, message = 43, "DB::Exception: Illegal type"

    with Check("constant"):
        execute_query(
            f"SELECT {func.format(params='1,1')}, any(toTypeName(1)), any(toTypeName(1))",
            exitcode=exitcode,
            message=message,
        )

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='number,number+1')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(0)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number,number+1')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='toInt64(number-5),toInt64(number+10)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)",
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Nullable(Int8), y Nullable(Int8)', (0, 1), (1, NULL), (NULL,NULL), (NULL,3), (4,4), (5, 1))",
            exitcode=exitcode,
            message=message,
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Nullable(Int8), y Nullable(Int8)', (NULL, NULL))",
            exitcode=exitcode,
            message=message,
        )

    with Check("inf, -inf, nan"):
        for permutation in permutations_with_replacement(["inf", "-inf", "nan"], 2):
            x, y = permutation
            with Check(f"{x},{y}"):
                execute_query(
                    f"SELECT {func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Float64, y Float64', (0, 1), (1, 2.3), ({x},{y}), (6.7,3), (4,4), (5, 1))"
                )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number, number+1')}), any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Scenario("datatypes"):
        with Scenario(
            "permutations",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if col in common_columns()
                    and is_numeric(
                        col.datatype, decimal=False, date=True, datetime=True
                    )
                    and (
                        not is_nullable(col.datatype)
                        if check_clickhouse_version(">=24.11")(self)
                        else True
                    )
                ]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name

                    if both_arguments_with_the_same_datatype:
                        if col1_type != col2_type:
                            continue

                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
