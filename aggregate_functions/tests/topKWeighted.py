from testflows.core import *
from aggregate_functions.tests.steps import *

from helpers.tables import common_columns
from helpers.tables import is_numeric, is_integer, is_unsigned_integer

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopKWeighted,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("topKWeighted")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopKWeighted("1.0"))
def scenario(self, func="topKWeighted({params})", table=None, snapshot_id=None):
    """Check topKWeighted aggregate function by using the same checks as for avgWeighted
    as well as functions specific checks."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id, clickhouse_version=">=23.2")

    if table is None:
        table = self.context.table

    params = "({params})"

    _func = func.replace(params, f"(3){params}")

    if 'Merge' in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    with Check("constant"):
        execute_query(f"SELECT {_func.format(params='1,1')}, any(toTypeName(1)), any(toTypeName(1))")

    with Check("zero rows"):
        execute_query(f"SELECT {_func.format(params='number,number')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(0)")

    with Check("single row"):
        execute_query(
            f"SELECT {_func.format(params='number,number+1')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {_func.format(params='number,even')}, any(toTypeName(number)), any(toTypeName(even)) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {_func.format(params='number-5,number+10')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {_func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y))  FROM values('x Nullable(Int8), y Nullable(Int8)', (0, 1), (1, NULL), (NULL,NULL), (NULL,3), (4,4), (5, 1))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {_func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Nullable(Int8), y Nullable(Int8)', (NULL, NULL))"
        )

    for x in ["inf", "-inf", "nan"]:
        with Check(f"{x}"):
            execute_query(
                f"SELECT {_func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Float64, y Int64', (0, 1), (1, 2), ({x},3), (6.7,3), (4,4), (5, 1))"
            )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({_func.format(params='number, number+1')}), any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("example"):
        execute_query(
            f"SELECT {_func.format(params='y,x')}, any(toTypeName(y)), any(toTypeName(x)) FROM values('x Int8, y Float64', (0,0.1), (1,0.34), (2,.88), (3,-1.23), (4,-3.3), (5,5.4))"
        )

    with Scenario("datatypes"):
        with Scenario(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                columns = [col for col in table.columns if col in common_columns()]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name

                    if not (
                        is_unsigned_integer(col2.datatype) or is_integer(col2.datatype)
                    ):
                        continue

                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()

    with Check("K values"):
        for k in range(1, 10):
            with When(f"{k}"):
                _func = func.replace(params, f"({k}){params}")
                execute_query(
                    f"SELECT {_func.format(params='bitAnd(number, 7), number % 2')} FROM numbers(100)"
                )

    with Check("custom load factor"):
        _func = func.replace(params, f"(5,5){params}")
        execute_query(
            f"SELECT {_func.format(params='bitAnd(number, 7),number % 2')} FROM numbers(56)"
        )
